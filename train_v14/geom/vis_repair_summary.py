"""Summarise vis_repair.py outputs: per arm, start (round 0) vs final adopted program vs best round, by family."""
import json, sys, numpy as np
for path in sys.argv[1:]:
    R = [json.loads(l) for l in open(path)]
    rows = []
    for r in R:
        h = [x for x in r["hist"] if "iou" in x]
        if not h: continue
        start = h[0]["iou"] if h[0]["round"] == 0 else None
        adopted = [x for x in h if x.get("exec", True)]; final = adopted[-1]["iou"] if adopted else 0.0
        r1 = next((x["iou"] for x in h if x["round"] == 1 and x.get("exec")), start)
        rows.append((r["key"][0], start, r1, final, max(x["iou"] for x in h)))
    for fam in ("ALL", "A", "F"):
        s = [x for x in rows if fam == "ALL" or x[0] == fam]
        if not s: continue
        st = np.array([x[1] if x[1] is not None else 0 for x in s]); r1 = np.array([x[2] or 0 for x in s]); fi = np.array([x[3] for x in s]); be = np.array([x[4] for x in s])
        print(f"{path.split('/')[-1]:14s} {fam:3s} n={len(s):3d} start {st.mean():.3f}  round1 {r1.mean():.3f}  final {fi.mean():.3f} (helped {int((fi>st+0.05).sum())} hurt {int((fi<st-0.05).sum())})  best-round {be.mean():.3f}")
