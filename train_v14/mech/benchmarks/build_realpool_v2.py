"""Real-part pool v2 for GRPO (2026-10-07).

CADBench is exhausted: its 12,000 STEP parts (bench0/0F/1A/1B; MCB + Objaverse carry no STEP)
were all consumed by corpora 1-3/abccode/benches (4,860 file_ids) and corpus 4 (the remaining
7,148, of which prep kept 3,203 and 3,007 rendered). So pool v2 draws from the other real source
already rendered in the exact corpus-4 sheet format: the DeepCAD full split (Onshape user parts,
`deepcad/corpus_full`, draftwright 0.4.23 + font patch 5.25, render_ext.py/worker_v11 VLM_MODE=1 via
render_isolated.sh, eval_cache_v15.pkl + gt_meshes_v15, 87,328 kept, e55 K=8 scored).

  select: re-apply the corpus-4 prep filters (min_faces 6, max_aspect 15, max_faces 400; the DeepCAD
          prep ran looser at 3 / 40), drop every file_id in any data/*/manifest.json (the corpus-4
          exclusion rule; also covers CADBench's DeepCAD subset B_*) and the DeepCAD gate bench, and
          require a sheet + GT mesh in the certified pool. Writes e55 K=8 stats per part.
  pack:   subset eval cache + GT meshes for a key list -> a self-contained bench dir.
  mine:   hard rule of results/h6c/real4_hard_keys.txt on the RL generator's scored K=4 draws -> keys file,
          e55-vs-RL stats (<keys>_stats.json), e55 K=8 baseline subset for paired joins.

    python build_realpool_v2.py select --out <dir>
    python build_realpool_v2.py pack --out <dir> --keys <keys.txt>
    python build_realpool_v2.py mine --select <dir>/select_e55.json --scored '<glob>.scored.jsonl' --partials '<glob>.partial.json' --keys <mine order>
        --out <hard_keys.txt> [--e55-out <bo8 subset.json>]
"""
import argparse, collections, glob, json, os, pickle, re, shutil, statistics, sys

DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
DC = f"{DV}/deepcad/corpus_full"
DATA = f"{DV}/train_v14/mech/benchmarks/data"


def used_file_ids():
    used = set()
    for m in glob.glob(os.path.join(DATA, "*", "manifest.json")):
        try:
            parts = json.load(open(m)).get("parts", {})
        except Exception:
            continue
        for k in (parts if isinstance(parts, dict) else []):
            mm = re.match(r"^[A-Z]_(.+)_(easy|medium|hard|code|x)$", k) or re.match(r"^[A-Z]_(\d+)$", k)
            if mm:
                used.add(mm.group(1))
    return used


def select(a):
    os.makedirs(a.out, exist_ok=True)
    man = json.load(open(f"{DC}/manifest.json"))["parts"]
    gate = set(json.load(open(f"{DATA}/deepcad_gate/manifest.json"))["parts"])
    used = used_file_ids()
    print(f"[pool2] {len(man)} DeepCAD parts, {len(used)} used file_ids, {len(gate)} gate keys", flush=True)
    cache = pickle.load(open(f"{DC}/eval_cache_v15.pkl", "rb"))
    cert = set(cache["pools"].get("certified", cache["samples"]))
    del cache
    bo = json.load(open(f"{DC}/results_vllm/bo8_full_e55_vllm.json"))["candidates"]
    e55 = {}
    for row in bo:
        ious = [float(c.get("iou") or 0.0) if c.get("exec") else 0.0 for c in row["cands"]]
        if ious:
            e55[row["key"]] = ious
    del bo
    rej = collections.Counter(); keep = {}
    for k, v in man.items():
        fid = k.split("_", 1)[1]
        if k in gate: rej["gate_bench"] += 1; continue
        if fid in used: rej["used_file_id"] += 1; continue
        if v.get("solids", 1) != 1: rej["multi_body"] += 1; continue
        if v["faces"] < a.min_faces: rej["faces_lt_min"] += 1; continue
        if v["faces"] > a.max_faces: rej["faces_gt_max"] += 1; continue
        if v["aspect"] > a.max_aspect: rej["aspect"] += 1; continue
        if k not in cert: rej["not_certified"] += 1; continue
        if not os.path.exists(f"{DC}/gt_meshes_v15/{k}.stl"): rej["no_gt_mesh"] += 1; continue
        if k not in e55: rej["no_e55_score"] += 1; continue
        keep[k] = e55[k]
    print(f"[pool2] kept {len(keep)} rejected {dict(rej)}", flush=True)
    stats = {k: {"mean": statistics.fmean(s), "max": max(s), "first": s[0], "var": statistics.pvariance(s)}
             for k, s in keep.items()}
    json.dump({"rejected": dict(rej), "filters": vars(a), "e55": stats}, open(f"{a.out}/select_e55.json", "w"))
    hard = [k for k, s in stats.items() if s["max"] > 0.1 and s["mean"] < 0.75 and s["var"] > 0]
    print(f"[pool2] e55-hard (max>0.1, mean<0.75, var>0): {len(hard)}", flush=True)
    for thr in (0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.01):
        n = sum(1 for s in stats.values() if s["mean"] < thr)
        print(f"  e55 mean8 < {thr}: {n}", flush=True)
    print(f"  e55 max8 <= 0.1: {sum(1 for s in stats.values() if s['max'] <= 0.1)}", flush=True)
    print(f"  e55 mean8 first {statistics.fmean(s['first'] for s in stats.values()):.3f} "
          f"best {statistics.fmean(s['max'] for s in stats.values()):.3f}", flush=True)


def pack(a):
    keys = [ln.strip() for ln in open(a.keys) if ln.strip()]
    os.makedirs(f"{a.out}/gt_meshes_v15", exist_ok=True)
    src = a.src or DC     # any bench dir holding these keys (e.g. the mining subset) -- smaller pickle to load
    cache = pickle.load(open(f"{src}/eval_cache_v15.pkl", "rb"))
    man = json.load(open(f"{DC}/manifest.json"))
    samples = {k: cache["samples"][k] for k in keys if k in cache["samples"]}
    miss = [k for k in keys if k not in samples]
    for k in samples:
        dst = f"{a.out}/gt_meshes_v15/{k}.stl"
        if not os.path.exists(dst):
            shutil.copy2(f"{src}/gt_meshes_v15/{k}.stl", dst)
    ks = list(samples)
    out = {"samples": samples, "pools": {"certified": ks, "all": ks}}
    pickle.dump(out, open(f"{a.out}/eval_cache_v15.pkl", "wb"))
    if not os.path.lexists(f"{a.out}/eval_cache_v14.pkl"):
        os.symlink("eval_cache_v15.pkl", f"{a.out}/eval_cache_v14.pkl")
    open(f"{a.out}/traces_v14.json", "w").write("{}")
    open(f"{a.out}/legacy_keys_v14.txt", "a").close()
    json.dump({**{k: v for k, v in man.items() if k != "parts"},
               "source": DC, "pool_v2_filters": {"min_faces": 6, "max_aspect": 15, "max_faces": 400},
               "parts": {k: man["parts"][k] for k in ks}}, open(f"{a.out}/manifest.json", "w"), indent=1)
    print(f"[pool2] packed {len(ks)} parts ({len(miss)} missing) -> {a.out}", flush=True)


def mine(a):
    """Hard rule of results/h6c/real4_hard_keys.txt (0.1 < max, mean < 0.75, var > 0), here on the RL generator's
    K=4 draws; e55-vs-RL difficulty stats on the same parts; e55 K=8 baseline subset for paired joins."""
    sel = json.load(open(a.select))["e55"]
    # scores straight from the score_partials.py resume logs (<out>.scored.jsonl, several scorers may share parts) and
    # the draw lists from the generation partials: a draw without code scores 0; a part is complete when every code
    # draw has a record (so finalizing does not wait for a scorer's pass to end)
    rec = {}
    for f in glob.glob(a.scored):
        for ln in open(f):
            try: r = json.loads(ln)
            except Exception: continue
            rec[(r["key"], r["draw"])] = float(r["iou"] or 0.0) if r["exec"] else 0.0
    rl = {}; incomplete = 0; ngen = 0
    for f in sorted(glob.glob(a.partials)):
        d = json.load(open(f))
        for key, cs in zip(d["keys"], d["cands"]):
            ngen += 1
            cs = sorted(cs, key=lambda c: c.get("draw", 0))
            if len(cs) != a.k or any(c.get("code") and (key, c["draw"]) not in rec for c in cs):
                incomplete += 1; continue
            rl[key] = [rec[(key, c["draw"])] if c.get("code") else 0.0 for c in cs]
    print(f"[pool2] {ngen} generated parts, {len(rl)} fully scored, {incomplete} incomplete", flush=True)
    if incomplete and not a.allow_incomplete:
        sys.exit(f"{incomplete} parts not fully scored yet")
    st = {k: {"mean": statistics.fmean(v), "max": max(v), "first": v[0], "var": statistics.pvariance(v)} for k, v in rl.items()}
    hard = [k for k, s in st.items() if s["max"] > 0.1 and s["mean"] < 0.75 and s["var"] > 0]
    order = [ln.strip() for ln in open(a.keys) if ln.strip()] if a.keys else sorted(st)
    hs = set(hard); hard = [k for k in order if k in hs]
    open(a.out, "w").write("\n".join(hard) + "\n")
    f = statistics.fmean
    def summ(keys, src):
        return {"n": len(keys), "first": f(src[k]["first"] for k in keys), "mean": f(src[k]["mean"] for k in keys),
                "best": f(src[k]["max"] for k in keys), "best_ge80": f(src[k]["max"] >= 0.8 for k in keys)}
    ks = sorted(st)
    rep = {"generated": ngen, "incomplete": incomplete, "rule": "RL K=4 (t10s120, draw 0 greedy + 3 at T 0.7): 0.1 < max, mean < 0.75, var > 0",
           "mined": len(ks), "hard": len(hard),
           "e55_K8_on_mined": summ(ks, sel), "rl_K4_on_mined": summ(ks, st),
           "e55_K8_on_hard": summ(hard, sel), "rl_K4_on_hard": summ(hard, st),
           "rl_mean_ge_0.75": sum(st[k]["mean"] >= 0.75 for k in ks),
           "rl_max_le_0.1": sum(st[k]["max"] <= 0.1 for k in ks),
           "rl_zero_var": sum(st[k]["var"] == 0 for k in ks),
           "paired_delta_mean_rl_minus_e55": f(st[k]["mean"] - sel[k]["mean"] for k in ks),
           "paired_delta_first_rl_minus_e55": f(st[k]["first"] - sel[k]["first"] for k in ks)}
    json.dump(rep, open(a.out.replace(".txt", "_stats.json"), "w"), indent=1)
    print(json.dumps(rep, indent=1), flush=True)
    if a.e55_out:
        want = set(hard); rows = [r for r in json.load(open(f"{DC}/results_vllm/bo8_full_e55_vllm.json"))["candidates"]
                                  if r["key"] in want]
        json.dump({"metrics": {"n": len(rows), "k": 8, "source": "bo8_full_e55_vllm.json subset (DeepCAD full pass)"},
                   "candidates": rows}, open(a.e55_out, "w"))
        print(f"[pool2] e55 K=8 baseline subset {len(rows)} -> {a.e55_out}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["select", "pack", "mine"])
    ap.add_argument("--out", required=True); ap.add_argument("--keys", default="")
    ap.add_argument("--select", default=""); ap.add_argument("--scored", default="", help="glob of *.scored.jsonl")
    ap.add_argument("--partials", default="", help="glob of generation .partial.json"); ap.add_argument("--allow-incomplete", action="store_true"); ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--e55-out", default=""); ap.add_argument("--src", default="")
    ap.add_argument("--min-faces", type=int, default=6); ap.add_argument("--max-faces", type=int, default=400)
    ap.add_argument("--max-aspect", type=float, default=15.0)
    a = ap.parse_args()
    {"select": select, "pack": pack, "mine": mine}[a.cmd](a)
