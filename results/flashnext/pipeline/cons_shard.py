"""In-dist pipeline (2026-10-14): run consistency_rerank.py on part-shards in parallel and merge (the K=16 pairwise matrix in
one process is GIL-bound: K=8 on this pool took 100 min, K=16 has 4.3x the pairs). Every part is scored independently by
consistency_rerank.py (re-execute candidates, pairwise iou_pair with a fixed MC seed, mean agreement), so the merged file has
the same per-part content as a single run; the top-level metric dicts are recomputed from the merged per_part exactly as
consistency_rerank.py's metrics() does.
    python cons_shard.py split <cands.json> <dir> <n>      -> <dir>/shard_i.json
    python cons_shard.py merge <cands.json> <dir> <n> <out_consistency.json>"""
import json, os, sys

mode, src, d, n = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
data = json.load(open(src))
if mode == "split":
    os.makedirs(d, exist_ok=True)
    for i in range(n):
        sh = dict(data, candidates=data["candidates"][i::n])
        json.dump(sh, open(f"{d}/shard_{i}.json", "w"))
        print(f"shard {i}: {len(sh['candidates'])} parts")
else:
    out = sys.argv[5]
    S = [json.load(open(f"{d}/shard_{i}_consistency.json")) for i in range(n)]
    per_part, parts = {}, {}
    for s in S:
        per_part.update(s["per_part"]); parts.update({p["key"]: p for p in s["parts"]})
    keys = [p["key"] for p in data["candidates"]]
    assert sorted(keys) == sorted(per_part) == sorted(parts), "missing parts"
    res = {}
    for name in ("first_exec", "consistency", "cons_hybrid", "verifier", "oracle"):
        ious = [per_part[k][name] for k in keys]; m = len(ious); s_ = sorted(ious)
        res[name] = {"iou_mean": sum(ious) / m, "iou_median": s_[m // 2], "frac_iou85": sum(i >= 0.85 for i in ious) / m,
                     "frac_iou50": sum(i >= 0.5 for i in ious) / m}
        print(f"{name:12s} mean={res[name]['iou_mean']:.3f} median={res[name]['iou_median']:.3f} "
              f"iou85={res[name]['frac_iou85']:.3f} iou50={res[name]['frac_iou50']:.3f}")
    res["per_part"] = {k: per_part[k] for k in keys}
    res["parts"] = [parts[k] for k in keys]
    tmp = out + ".tmp"; json.dump(res, open(tmp, "w"), indent=1); os.replace(tmp, out)
    print(f"[cons] re-executed {sum(sum(p['exec']) for p in res['parts'])} candidates (merged {n} shards) -> {out}")
