"""Baseline best-of-K (K<8) medoid selection for a key list, from the stored
8x8 agreement matrices (results/bo8_full_e24_consistency_v2.json) — the same
selector as consistency_rerank.py applied to the first K draws."""
import json, os, sys, numpy as np
DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"; HERE = os.path.dirname(os.path.abspath(__file__))
K = int(sys.argv[1]); keys = [l.strip() for l in open(os.path.join(HERE, "keys_underdet.txt")) if l.strip()]
cons = json.load(open(os.path.join(DV, "results/bo8_full_e24_consistency_v2.json")))
parts = {p["key"]: p for p in cons["parts"]}
out = {}
for k in keys:
    p = parts[k]; idx = [j for j in range(K) if p["exec"][j]]
    if not idx:
        out[k] = {"first_exec": 0.0, "consistency": 0.0, "oracle": 0.0}; continue
    ag = {j: (np.mean([p["pair_iou"][j][i] for i in idx if i != j]) if len(idx) > 1 else 0.0) for j in idx}
    med = max(idx, key=lambda j: ag[j])
    out[k] = {"first_exec": p["iou"][idx[0]], "consistency": p["iou"][med], "oracle": max(p["iou"][j] for j in idx)}
for pol in ("first_exec", "consistency", "oracle"):
    v = np.array([out[k][pol] for k in keys])
    print(f"baseline K={K} {pol:12s} mean={v.mean():.4f} iou85={np.mean(v >= 0.85):.3f} median={np.median(v):.3f}")
json.dump({"per_part": out, "k": K}, open(os.path.join(HERE, f"out/bo{K}_underdet_baseline_from_matrices.json"), "w"), indent=1)
