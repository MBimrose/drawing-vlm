"""Union of best-of-N candidate files from DIFFERENT models on the same parts
(e.g. two seeds of one recipe) into one candidate file, so consistency_rerank
can vote across models. Parts present in every input only; each candidate is
tagged with its source model.

    python union_bo.py <out.json> <bo_a.json> <bo_b.json> [...]
"""
import json
import os
import sys

out, srcs = sys.argv[1], sys.argv[2:]
data = [json.load(open(p)) for p in srcs]
by_key = []
for d, p in zip(data, srcs):
    tag = os.path.basename(p).replace(".json", "")
    m = {}
    for part in d["candidates"]:
        for c in part["cands"]:
            c["src"] = tag
        m[part["key"]] = part["cands"]
    by_key.append(m)
keys = sorted(set.intersection(*(set(m) for m in by_key)))
parts = [{"key": k, "cands": [c for m in by_key for c in m[k]]} for k in keys]
k_total = sum(d["metrics"]["k"] for d in data)
json.dump({"metrics": {"k": k_total, "n": len(parts), "sources": srcs},
           "ckpt": [d.get("ckpt") for d in data], "verifier": "", "candidates": parts},
          open(out, "w"))
print(f"[union] {len(parts)} parts x {k_total} candidates from {len(srcs)} models -> {out}")
