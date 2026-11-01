"""DeepSeek-V4.1-Flash on the e55 recipe (2026-10-21): one fixed tier for dsv41_lora_train.py, drawn from e55's three
training streams with data_v14's own filters, at e55's mix (rft_frac 0.6, reasoning_frac 0.2, plain 0.2):
  rft        DRAWING_VLM_RFT_SHARDS rft-*.tar (rft_mix_u6_gt_dw423): png + code.py (+ think.txt plan, user.txt, cand.png)
  reasoning  DRAWING_VLM_BUNDLE shards/train-*.tar (certified traces): png + trace.txt + code.py; trace -> think.txt
  plain      DRAWING_VLM_TARS shard_*.tar (tars_v14_dw423): png + py, minus exec-bad, legacy-renderer, val (residue 7)
             and manifest-eval (residue 0) keys -- build_plain_dataset_v2 with exec_filter on, dims_filter off
Rows are drawn uniformly without replacement within each stream (the streams themselves are e55's, including the RFT
mix's replicated real / ABC-GT rows), and e55's image augmentation (data_v14.augment_image) is applied once per row with
a per-row seed. Untraced rows carry no think.txt; dsv41_lora_train.py --think-all trains them in thinking mode with an
empty reasoning span, as collate_v14 renders e55's untraced rows ("<think>\\n</think>code").
Also writes <out>/../prompts.json = e55's served prompt (SYSTEM_PROMPTS["detailed"] + USER_PROMPT), which the trainer
reads next to the tier and gen_openai_bo.py sends at eval. Env: nemotron/env_nemo19.sh (the e55 / e59 paths).
    python build_dsv41_e55_tier.py --n 64000 --out /srv/scratch/bimrose2/dsv41_e55/tier --workers 12
"""
from __future__ import annotations

import argparse
import glob
import io
import json
import os
import random
import sys
import tarfile
import time
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

import data_v14 as dv  # noqa: E402

MIX = (("rft", 0.6), ("reasoning", 0.2), ("plain", 0.2))


def list_stream(name):
    """[(tar, key)] of every row the e55 stream would yield, plus the members each row carries."""
    if name == "rft":
        tars, need = sorted(glob.glob(os.path.join(dv.RFT_SHARDS, "rft-*.tar"))), ("png", "code.py")
    elif name == "reasoning":
        tars, need = sorted(glob.glob(os.path.join(dv.BUNDLE_ROOT, "shards", "train-*.tar"))), ("png", "trace.txt", "code.py")
    else:
        tars, need = dv.all_shards(), ("png", "py")
        bad, legacy = dv.bad_keys(), dv.legacy_keys()
    rows = []
    for tp in tars:
        keys = {}
        with tarfile.open(tp) as t:
            for m in t:   # headers only: tarfile seeks over the member data
                b = os.path.basename(m.name)
                k, _, ext = b.partition(".")   # webdataset key/extension split
                keys.setdefault(k, set()).add(ext)
        for k, exts in keys.items():
            if not all(e in exts for e in need):
                continue
            if name == "plain":
                u = dv.uuid_of_key(k)
                if k in bad or k in legacy or dv.is_val_uuid(u) or dv.is_manifest_eval_uuid(u):
                    continue
            rows.append((tp, k))
    return rows


def pack_tar(job):
    """Extract the selected rows of one source tar, augment the sheet, return [(new_key, {ext: bytes})]."""
    tp, picks, seed = job   # picks: [(global idx, stream, key)]
    want = {k: (i, s) for i, s, k in picks}
    got = {}
    with tarfile.open(tp) as t:
        for m in t:
            k, _, ext = os.path.basename(m.name).partition(".")
            if k in want and m.isfile():
                got.setdefault(k, {})[ext] = t.extractfile(m).read()
    out = []
    for k, (i, s) in want.items():
        g = got[k]
        img = dv.augment_image(dv._decode_png(g["png"]), rng=random.Random(seed * 1_000_003 + i))
        buf = io.BytesIO(); img.save(buf, format="PNG", compress_level=3)
        mem = {"png": buf.getvalue(), "code.py": g["code.py" if s != "plain" else "py"]}
        plan = (g.get("think.txt") if s == "rft" else g.get("trace.txt") if s == "reasoning" else None) or b""
        if plan.strip():
            mem["think.txt"] = plan
        for ext in ("user.txt", "cand.png"):   # RFT repair members, if the mix has any
            if ext in g:
                mem[ext] = g[ext]
        out.append((f"{i:06d}-{s}-{k}", mem))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True, help="total rows (split 60/20/20)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=43)   # e55 / e59 seed
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--per-tar", type=int, default=1000)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    rng = random.Random(a.seed)
    counts = {s: round(f * a.n) for s, f in MIX}
    counts["plain"] = a.n - counts["rft"] - counts["reasoning"]
    picks, manifest = [], {"seed": a.seed, "mix": dict(MIX), "counts": counts, "sources": {}, "pool": {}}
    for s, _ in MIX:
        pool = list_stream(s)
        manifest["pool"][s] = len(pool)
        if len(pool) < counts[s]:
            raise SystemExit(f"stream {s}: only {len(pool)} rows for {counts[s]}")
        picks += [(s, tp, k) for tp, k in rng.sample(pool, counts[s])]
        print(f"[tier] {s}: pool {len(pool)} -> {counts[s]} rows ({time.time()-t0:.0f}s)", flush=True)
    manifest["sources"] = {"rft": dv.RFT_SHARDS, "reasoning": dv.BUNDLE_ROOT, "plain": dv.TARS_ROOT,
                           "bad_keys": dv.BAD_KEYS_FILE, "legacy_keys": dv.LEGACY_KEYS_FILE}
    rng.shuffle(picks)
    by_tar = {}
    for i, (s, tp, k) in enumerate(picks):
        by_tar.setdefault(tp, []).append((i, s, k))
    with open(os.path.join(a.out, "keys.json"), "w") as f:
        json.dump([[i, s, os.path.basename(tp), k] for i, (s, tp, k) in enumerate(picks)], f)
    n_out, w, n_think = 0, None, 0
    with Pool(a.workers) as pool:
        for rows in pool.imap_unordered(pack_tar, [(tp, v, a.seed) for tp, v in sorted(by_tar.items())], chunksize=4):
            for key, mem in rows:
                if n_out % a.per_tar == 0:
                    if w: w.close()
                    w = tarfile.open(os.path.join(a.out, f"e55mix-{n_out // a.per_tar:05d}.tar"), "w")
                for ext, data in mem.items():
                    ti = tarfile.TarInfo(f"{key}.{ext}"); ti.size = len(data); ti.mtime = 0
                    w.addfile(ti, io.BytesIO(data))
                n_out += 1; n_think += "think.txt" in mem
                if n_out % 5000 == 0:
                    print(f"[tier] {n_out}/{a.n} rows written ({time.time()-t0:.0f}s)", flush=True)
    if w: w.close()
    import collate_v14
    from geom_eval_worker import USER_PROMPT
    with open(os.path.join(os.path.dirname(a.out.rstrip("/")), "prompts.json"), "w") as f:
        json.dump({"system": collate_v14.SYSTEM_PROMPTS["detailed"], "user": USER_PROMPT}, f, indent=1)
    manifest.update(rows=n_out, rows_with_plan=n_think, seconds=round(time.time() - t0))
    json.dump(manifest, open(os.path.join(a.out, "manifest.json"), "w"), indent=1)
    print(f"[tier] DONE {n_out} rows ({n_think} with a plan) in {time.time()-t0:.0f}s -> {a.out}", flush=True)


if __name__ == "__main__":
    main()
