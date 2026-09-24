"""H5: how much learning signal does RFT's IoU>=0.8 cutoff discard? Best-of-K distribution and, per part,
the gap between the best draw and the median draw (what a relative/dense reward could learn from)."""
import json, sys, numpy as np
d = json.load(open(sys.argv[1]))["candidates"]
B = []; G = []
for p in d:
    i = [float(c.get("iou") or 0) for c in p["cands"]]
    if not i: continue
    B.append(max(i)); G.append(max(i) - float(np.median(i)))
B = np.array(B); G = np.array(G)
print(f"[{sys.argv[2]}] parts {len(B)}")
for lo, hi in ((0, .2), (.2, .4), (.4, .6), (.6, .8), (.8, 1.01)):
    m = (B >= lo) & (B < hi)
    print(f"   best-of-8 [{lo:.1f},{hi:.1f}) {m.mean():6.1%}   mean best-minus-median {G[m].mean():.3f}")
m = (B >= .4) & (B < .8)
print(f"   RFT (>=0.8) uses {np.mean(B>=.8):.1%} of parts; parts with a best draw 0.4-0.8 AND >= 0.15 above their median: {np.mean(m & (G>=.15)):.1%}")
