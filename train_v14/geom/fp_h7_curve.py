"""H7: best-of-K ceiling vs K on the K=128 run (first k draws of each part = the k-draw run)."""
import json, sys, numpy as np
d = json.load(open(sys.argv[1]))["candidates"]
base = {p["key"]: p for p in json.load(open(sys.argv[2]))["candidates"]}
print(f"parts {len(d)}  draws/part {np.median([len(p['cands']) for p in d]):.0f}")
for k in (1, 2, 4, 8, 16, 32, 64, 128):
    b = [max(float(c.get("iou") or 0) for c in p["cands"][:k]) for p in d]
    print(f"  K={k:4d}  mean best {np.mean(b):.3f}   >=0.85 {np.mean(np.array(b)>=0.85):.0%}   >=0.7 {np.mean(np.array(b)>=0.7):.0%}")
b8 = [max(float(c.get("iou") or 0) for c in base[p["key"]]["cands"]) for p in d if p["key"] in base]
print(f"  (stored e55 K=8 run on the same parts: {np.mean(b8):.3f})")
