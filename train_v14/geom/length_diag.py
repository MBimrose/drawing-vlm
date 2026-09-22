"""Program length vs score. (a) in-distribution: GT program ops vs model ops and IoU on the certified pool;
(b) per-part length response inside a best-of-K run (does a longer draw score better?).
    python length_diag.py pool <bo_full.json> <eval_cache.pkl>
    python length_diag.py within <bo.json> <abc_sheet_rows.json>
"""
import json, re, sys, pickle, numpy as np
OPS = re.compile(r"\b(Box|Cylinder|Sphere|Cone|Torus|Wedge|extrude|revolve|loft|sweep|fillet|chamfer|offset|Hole|CounterBoreHole|CounterSinkHole|mirror|split|Rectangle|Circle|Polyline|Polygon|Line|make_face|RegularPolygon|SlotOverall|SlotCenterToCenter|GridLocations|PolarLocations|Locations)\b")
nops = lambda c: len(OPS.findall(c or ""))
mode = sys.argv[1]
if mode == "pool":
    bo = json.load(open(sys.argv[2]))["candidates"]; S = pickle.load(open(sys.argv[3], "rb"))["samples"]
    R = []
    for p in bo:
        s = S.get(p["key"]) or S.get(p["key"].rsplit("_v", 1)[0])
        if not s: continue
        cs = p["cands"]; iou = [float(c.get("iou") or 0) for c in cs]
        R.append((nops(s["code"]), np.median([nops(c.get("code")) for c in cs]), iou[0], max(iou), np.mean(iou)))
    R = np.array(R); print("pool parts", len(R))
    for lo, hi in ((0, 5), (5, 8), (8, 12), (12, 16), (16, 999)):
        m = (R[:, 0] >= lo) & (R[:, 0] < hi)
        if m.any(): print(f"  GT ops [{lo},{hi}) n={m.sum():4d}  model ops median {np.median(R[m,1]):5.1f}  first {R[m,2].mean():.3f}  mean {R[m,4].mean():.3f}  oracle {R[m,3].mean():.3f}")
else:
    bo = json.load(open(sys.argv[2]))["candidates"]; rows = {x["key"]: x for x in json.load(open(sys.argv[3]))}
    res = {}
    for p in bo:
        if p["key"] not in rows: continue
        C = [(nops(c.get("code")), float(c.get("iou") or 0)) for c in p["cands"] if c.get("exec")]
        if len(C) < 6: continue
        n = np.array([c[0] for c in C], float); y = np.array([c[1] for c in C])
        if n.std() == 0 or y.std() == 0: continue
        g = ("ABC" if p["key"][0] == "A" else "Fusion") + (" complex" if rows[p["key"]]["faces"] >= 25 else " simple")
        z = (n - n.mean()) / n.std()
        res.setdefault(g, []).append((np.corrcoef(n, y)[0, 1], np.polyfit(z, y, 1)[0], n.max(), np.median(n), y[np.argmax(n)] - np.median(y)))
    for g, v in sorted(res.items()):
        v = np.array(v); print(f"  {g:15s} parts {len(v):3d}  within-part corr(ops,iou) {v[:,0].mean():+.3f}  slope per SD of length {v[:,1].mean():+.3f}  ops median {np.median(v[:,3]):.0f} / longest {np.median(v[:,2]):.0f}  longest-draw minus median-draw {v[:,4].mean():+.3f}")
