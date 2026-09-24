"""H3: do real sheets underdetermine the part? Among rendered candidates, how many match the input sheet's
views as well as correct candidates do, yet have low IoU? (render_compare v3 = 0.5 silhouette + 0.5 edge, per view)."""
import json, sys, numpy as np
d = json.load(open(sys.argv[1]))
rows = [(p["key"], i, c["iou"], c["v3"], c["sil3"], c["edge3"]) for p in d["parts"] for i, c in enumerate(p["cands"]) if c.get("v3", 0) > 0]
R = np.array([(r[2], r[3], r[4], r[5]) for r in rows]); fam = np.array([r[0][0] for r in rows])
iou, v3, sil, edge = R.T
print(f"rendered candidates {len(R)} over {len(set(r[0] for r in rows))} parts")
good = iou >= 0.9
for q in (10, 25, 50):
    thr = np.percentile(v3[good], q)
    m = v3 >= thr
    print(f"v3 >= p{q} of correct cands ({thr:.3f}): {m.sum():4d} cands, of which IoU<0.5 {np.mean(iou[m] < 0.5):.1%}, IoU 0.5-0.9 {np.mean((iou[m] >= 0.5) & (iou[m] < 0.9)):.1%}, >=0.9 {np.mean(iou[m] >= 0.9):.1%}")
for F in "AF":
    thr = np.percentile(v3[good], 25); m = (v3 >= thr) & (fam == F)
    print(f"  {F}: sheet-consistent (>= p25) {m.sum()} cands, IoU<0.5 among them {np.mean(iou[m] < 0.5):.1%}")
print("v3 by IoU bucket:", {f"[{lo},{hi})": round(float(v3[(iou >= lo) & (iou < hi)].mean()), 3) for lo, hi in ((0, .3), (.3, .5), (.5, .7), (.7, .9), (.9, 1.01))})
thr = np.percentile(v3[good], 25)
amb = sorted([r for r in rows if r[3] >= thr and r[2] < 0.5], key=lambda r: -r[3])[:12]
json.dump([{"key": k, "draw": i, "iou": a, "v3": b} for k, i, a, b, _, _ in amb], open(sys.argv[2], "w"), indent=1)
print("top sheet-consistent low-IoU cases ->", sys.argv[2])
for r in amb[:6]: print("  ", r[0][:28], "draw", r[1], "iou %.2f v3 %.3f" % (r[2], r[3]))
