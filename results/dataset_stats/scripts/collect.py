"""Collect per-program static stats (AST + Qwen tokens + think-trace + drawing annotations) for every
dataset, and write the execution / STEP task list for run_exec.py. Run on a compute node
(run_all.sbatch); reads ~60 GB of tars.

    python collect.py            # -> out/static_<ds>.jsonl, out/exec_tasks.jsonl, out/collect_meta.json

Datasets (ds):
  plain        tars_v14_dw423 GT programs (Zero-To-CAD-derived converter code), every row; flag
               `in_tier` = kept by the e55 plain-tier filter (not exec-bad, not legacy renderer, uuid
               residue not 0 [frozen eval] / 7 [legacy holdout]) — data_v14.build_plain_dataset_v2.
  reasoning    v14_bundle certified Kimi-K3 traces + GT code (52,131 train rows).
  rft_synth    rft_strict90_all_dw423: the generator's own accepted programs on synthetic parts
               (e55 RFT base tier, 77 shards).
  rft_real     rft_real_union5_dw423: accepted own programs on real CADBench training parts.
  abc_gt       rft_real_abccode_train: ABC ground-truth-code tier (762 rows).
  eval_synth   the 1,027-part synthetic eval pool (keys of results/grpo_eval/full_e55ctl.json), GT
               code from fullpool_dw423/eval_cache_v15.pkl, GT STEP from its gt_meshes_v15.
  bench_b      280 held-out real parts, results/bench_b/bench (STEP only; no GT code exists).
  real144      144-part real dev bench, ext_bench_dw423_perm (STEP only).
  pred_<model>_<bench>_{d0,vote}   generated programs (draw 0 / consistency-vote pick).
  repair_fam / repair_real         repairer tiers (start program in user.txt -> target code.py).
Exec sampling is deterministic: md5(id) % 10000 < rate.
"""
from __future__ import annotations

import difflib
import glob
import hashlib
import io
import json
import os
import pickle
import re
import sys
import tarfile
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from code_ast import NAME2CAT, analyze, trace_stats  # noqa: E402

DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
WDS = f"{DV}/step_to_drw/wds_dataset"
OUT = os.path.join(os.path.dirname(HERE), "out")
TOK_PATH = f"{DV}/models/Qwen3.8-27B/tokenizer.json"
_TOK = None


def tok(s: str) -> int:
    global _TOK
    if _TOK is None:
        from tokenizers import Tokenizer
        _TOK = Tokenizer.from_file(TOK_PATH)
    return len(_TOK.encode(s, add_special_tokens=False).ids) if s else 0


def h(x: str) -> int:
    return int(hashlib.md5(x.encode()).hexdigest(), 16) % 10000


def code_row(ds, rid, code, think=None, **extra):
    a = analyze(code)
    a["calls"] = {k: v for k, v in a.get("calls", {}).items() if k in NAME2CAT}
    r = {"ds": ds, "id": rid, "tokens": tok(code), **a, **extra}
    if think is not None:
        r["think"] = trace_stats(think)
        r["think"]["tokens"] = tok(think)
    return r


def drawing_stats(meta: dict) -> dict:
    ann = meta.get("annotations", {}) or {}
    kinds = [v.get("kind") for v in ann.values()]
    return {"n_ann": len(ann), "n_dim": kinds.count("Dimension"), "n_leader": kinds.count("Leader"),
            "n_hole_callout": sum(1 for k in ann if k.startswith("hc_")),
            "n_unplaced": len(meta.get("dims_unplaced", []) or []),
            "projection": meta.get("projection"), "renderer": meta.get("renderer")}


# ---------------------------------------------------------------- plain (tars_v14_dw423)
def _lines(p):
    try:
        return set(l.strip() for l in open(p) if l.strip())
    except FileNotFoundError:
        return set()


BAD = LEG = UNP = None


def _init_plain():
    global BAD, LEG, UNP
    BAD = _lines(f"{WDS}/exec_bad_keys_v14.txt")
    LEG = _lines(f"{WDS}/legacy_keys_v14.txt")
    UNP = _lines(f"{WDS}/unplaced_keys_v14.txt")


def plain_shard(tp):
    side = {}
    sp = tp[:-4] + ".renderers.json"
    if os.path.exists(sp):
        try:
            side = json.load(open(sp))
        except Exception:
            side = {}
    rows, tasks = [], []
    with tarfile.open(tp) as tf:
        for m in tf:
            if not m.name.endswith(".py"):
                continue
            key = m.name[:-3]
            code = tf.extractfile(m).read().decode("utf-8", "replace")
            uuid = key.rsplit("_v", 1)[0]
            res = int(uuid[:8], 16) % 50
            in_tier = key not in BAD and key not in LEG and res not in (0, 7)
            r = code_row("plain", key, code, in_tier=in_tier, exec_bad=key in BAD,
                         unplaced=key in UNP, residue=res)
            if key in side:
                r["drawing"] = drawing_stats(side[key])
            rows.append(r)
            if in_tier and h(key) < 50:  # 0.5 %
                tasks.append({"id": f"plain/{key}", "ds": "plain", "code": code})
    return rows, tasks


# ---------------------------------------------------------------- generic tar of code.py/think.txt
def tar_rows(args):
    ds, tp, rate = args
    rows, tasks = [], []
    files = {}
    with tarfile.open(tp) as tf:
        for m in tf:
            n = m.name
            for suf in (".code.py", ".think.txt", ".trace.txt", ".meta.json", ".user.txt"):
                if n.endswith(suf):
                    files.setdefault(n[: -len(suf)], {})[suf] = tf.extractfile(m).read().decode("utf-8", "replace")
    for key, f in files.items():
        code = f.get(".code.py")
        if code is None:
            continue
        think = f.get(".think.txt", f.get(".trace.txt"))
        meta = {}
        try:
            meta = json.loads(f.get(".meta.json", "{}"))
        except Exception:
            pass
        extra = {"iou": meta.get("iou"), "shard": os.path.basename(tp)}
        if ds.startswith("repair"):
            u = f.get(".user.txt", "")
            m = re.search(r"```python\n(.*?)```", u, re.S)
            start = m.group(1) if m else ""
            sa = analyze(start)
            extra.update({"cand_iou": meta.get("cand_iou"), "src_key": meta.get("src_key"),
                          "start_tokens": tok(start), "start_sloc": sa.get("sloc"),
                          "start_feature_ops_static": sa.get("feature_ops_static"),
                          "diff_ratio": difflib.SequenceMatcher(None, start, code).ratio()})
            sl, cl = start.splitlines(), code.splitlines()
            d = list(difflib.unified_diff(sl, cl, lineterm="", n=0))
            extra["diff_added"] = sum(1 for l in d if l.startswith("+") and not l.startswith("+++"))
            extra["diff_removed"] = sum(1 for l in d if l.startswith("-") and not l.startswith("---"))
        r = code_row(ds, key, code, think=think, **extra)
        rows.append(r)
        if rate and h(key) < rate:
            tasks.append({"id": f"{ds}/{key}", "ds": ds, "code": code})
    return rows, tasks


def write_rows(ds, rows):
    with open(f"{OUT}/static_{ds}.jsonl", "w") as fo:
        for r in rows:
            fo.write(json.dumps(r) + "\n")


def main():
    os.makedirs(OUT, exist_ok=True)
    meta = {}
    all_tasks = []
    _init_plain()
    with Pool(16, initializer=_init_plain) as pool:
        # plain
        shards = sorted(glob.glob(f"{WDS}/tars_v14_dw423/*.tar"))
        rows = []
        for i, (r, t) in enumerate(pool.imap_unordered(plain_shard, shards, chunksize=4)):
            rows += r
            all_tasks += t
            if i % 250 == 0:
                print(f"[plain] {i}/{len(shards)} shards {len(rows)} rows", flush=True)
        write_rows("plain", rows)
        meta["plain"] = {"shards": len(shards), "rows": len(rows),
                         "in_tier": sum(r["in_tier"] for r in rows)}
        print("[plain]", meta["plain"], flush=True)
        del rows
        # tar-based tiers: (ds, glob, exec rate per 10k)
        specs = [("reasoning", f"{DV}/v14_bundle/shards/train-*.tar", 300),
                 ("rft_synth", f"{DV}/rft_strict90_all_dw423/shards/*.tar", 100),
                 ("rft_real", f"{DV}/rft_real_union5_dw423/shards/*.tar", 1000),
                 ("abc_gt", f"{DV}/rft_real_abccode_train/shards/*.tar", 10000),
                 ("repair_fam", f"{DV}/results/repair/tier_rp_fam/shards/*.tar", 0),
                 ("repair_real", f"{DV}/results/repair/tier_rp_c4/shards/*.tar", 0),
                 ("repair_real", f"{DV}/results/repair/tier_rp_rft_corpus_dw423/shards/*.tar", 0),
                 ("repair_real", f"{DV}/results/repair/tier_rp_rft_corpus2_dw423/shards/*.tar", 0)]
        acc: dict[str, list] = {}
        for ds, g, rate in specs:
            jobs = [(ds, tp, rate) for tp in sorted(glob.glob(g))]
            for r, t in pool.imap_unordered(tar_rows, jobs):
                acc.setdefault(ds, []).extend(r)
                if ds == "abc_gt":  # both renderings share code: exec unique programs only
                    seen = {hashlib.md5(x["code"].encode()).hexdigest() for x in all_tasks if x["ds"] == "abc_gt"}
                    for x in t:
                        hh = hashlib.md5(x["code"].encode()).hexdigest()
                        if hh not in seen:
                            seen.add(hh)
                            all_tasks.append(x)
                else:
                    all_tasks += t
            print(f"[{ds}] {len(acc[ds])} rows", flush=True)
        for ds, rows in acc.items():
            write_rows(ds, rows)
            meta[ds] = {"rows": len(rows)}

    # eval_synth
    keys = [c["key"] for c in json.load(open(f"{DV}/results/grpo_eval/full_e55ctl.json"))["candidates"]]
    fp = f"{DV}/train_v14/mech/benchmarks/data/fullpool_dw423"
    cache = pickle.load(open(f"{fp}/eval_cache_v15.pkl", "rb"))
    rm = cache.get("render_meta", {})
    rows = []
    for k in keys:
        s = cache["samples"][k]
        r = code_row("eval_synth", k, s["code"], think=s.get("trace") or None)
        if k in rm:
            r["drawing"] = drawing_stats(rm[k])
        rows.append(r)
        all_tasks.append({"id": f"eval_synth/{k}", "ds": "eval_synth", "code": s["code"]})
        all_tasks.append({"id": f"eval_synth_step/{k}", "ds": "eval_synth_step",
                          "step": f"{fp}/gt_meshes_v15/{k}.step"})
    write_rows("eval_synth", rows)
    meta["eval_synth"] = {"rows": len(rows)}
    del cache

    # real benches (STEP only)
    for ds, bdir in (("bench_b", f"{DV}/results/bench_b/bench"),
                     ("real144", f"{DV}/train_v14/mech/benchmarks/data/ext_bench_dw423_perm")):
        c = pickle.load(open(f"{bdir}/eval_cache_v15.pkl", "rb"))
        ks = sorted(c["samples"])
        side = {}
        for sp in glob.glob(f"{bdir}/render/renderers.json") + glob.glob(f"{bdir}/renderers.json"):
            side.update({kk.rsplit("_v", 1)[0]: v for kk, v in json.load(open(sp)).items()})
        rows = []
        missing = []
        for k in ks:
            stp = f"{bdir}/step_mm/{k}.step"
            if not os.path.exists(stp):
                missing.append(k)
                continue
            r = {"ds": ds, "id": k, "family": k[0]}
            if k in side:
                r["drawing"] = drawing_stats(side[k])
            rows.append(r)
            all_tasks.append({"id": f"{ds}/{k}", "ds": ds, "step": stp})
        write_rows(ds, rows)
        meta[ds] = {"rows": len(rows), "missing_step": missing, "drawing_meta": sum("drawing" in r for r in rows)}

    # predictions
    preds = {"e55": {"full": "results/grpo_eval/full_e55ctl", "benchb": "results/bench_b/eval/benchb_e55ctl",
                     "real": "results/grpo_eval/real_e55ctl"},
             "glimmer": {"full": "results/american_vlm/full_glftpf", "benchb": "results/american_vlm/benchb_glftpf",
                         "real": "results/american_vlm/real_glftpf"}}
    for model, benches in preds.items():
        for bench, stem in benches.items():
            d = json.load(open(f"{DV}/{stem}.json"))
            cons = json.load(open(f"{DV}/{stem}_consistency.json"))["per_part"]
            r0, rv = [], []
            for c in d["candidates"]:
                k = c["key"]
                cands = sorted(c["cands"], key=lambda x: x["draw"])
                d0 = cands[0]
                r0.append(code_row(f"pred_{model}_{bench}_d0", k, d0.get("code") or "", think=d0.get("think") or None,
                                   exec=d0.get("exec"), iou=d0.get("iou")))
                v = cons.get(k, {}).get("consistency")
                pick = None
                if v is not None:
                    for x in cands:
                        if x.get("iou") is not None and abs(x["iou"] - v) < 1e-9 and x.get("exec"):
                            pick = x
                            break
                if pick is not None:
                    ds = f"pred_{model}_{bench}_vote"
                    rv.append(code_row(ds, k, pick.get("code") or "", think=pick.get("think") or None,
                                       exec=pick.get("exec"), iou=pick.get("iou"), draw=pick["draw"]))
                    if bench in ("full", "benchb"):
                        all_tasks.append({"id": f"{ds}/{k}", "ds": ds, "code": pick["code"]})
            write_rows(f"pred_{model}_{bench}_d0", r0)
            write_rows(f"pred_{model}_{bench}_vote", rv)
            meta[f"pred_{model}_{bench}"] = {"d0": len(r0), "vote_matched": len(rv), "parts": len(d["candidates"])}

    with open(f"{OUT}/exec_tasks.jsonl", "w") as fo:
        for t in all_tasks:
            fo.write(json.dumps(t) + "\n")
    meta["exec_tasks"] = {}
    for t in all_tasks:
        meta["exec_tasks"][t["ds"]] = meta["exec_tasks"].get(t["ds"], 0) + 1
    json.dump(meta, open(f"{OUT}/collect_meta.json", "w"), indent=1)
    print(json.dumps(meta["exec_tasks"]), flush=True)


if __name__ == "__main__":
    main()
