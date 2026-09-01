"""Merge sharded bestofn_verifier_eval outputs (one per GPU worker) into one
candidate file with recomputed first-exec / oracle-by-k metrics, in the exact
format consistency_rerank.py consumes.

    python merge_bo_shards.py <out.json> <shard1.json> [<shard2.json> ...]
"""
import json, sys
out, srcs = sys.argv[1], sys.argv[2:]
parts, k, temp, ckpt = [], None, None, None
for p in srcs:
    d = json.load(open(p))
    parts.extend(d["candidates"]); k = d["metrics"]["k"]; temp = d["metrics"].get("temperature"); ckpt = d.get("ckpt")
parts.sort(key=lambda p: p["key"])
n = len(parts)
def first_exec(cs):
    ex = [c["iou"] for c in cs if c["exec"]]
    return ex[0] if ex else 0.0
fe = [first_exec(p["cands"]) for p in parts]
ocurve = {}
for kk in sorted({1, 2, 4, 8, 12, 16, k}):
    if kk > k: continue
    ocurve[str(kk)] = sum(max([c["iou"] for c in p["cands"][:kk] if c["exec"]] or [0.0]) for p in parts) / n
metrics = {"n": n, "k": k, "temperature": temp, "n_exec": sum(c["exec"] for p in parts for c in p["cands"]),
           "first_exec_mean": sum(fe) / n, "first_exec_iou85": sum(v >= 0.85 for v in fe) / n,
           "oracle_by_k": ocurve, "shards": len(srcs)}
json.dump({"metrics": metrics, "ckpt": ckpt, "verifier": "", "candidates": parts}, open(out, "w"))
print(json.dumps(metrics, indent=1))
