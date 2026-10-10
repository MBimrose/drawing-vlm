"""Verifier / score quality on stored candidates (2026-10-07 selection study): pooled + per-part Spearman with true IoU,
AUROC at IoU >= 0.8, and per-part pairwise ranking accuracy among executing candidates whose IoU differs by >= 0.05.
    python sel_vquality.py name=cands.json:preds.json ...
"""
import json, sys
import numpy as np
from scipy.stats import rankdata, spearmanr


def auroc(s, y):
    s, y = np.asarray(s, float), np.asarray(y, bool); n1, n0 = y.sum(), (~y).sum()
    if not n1 or not n0: return float("nan")
    r = rankdata(s); return float((r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


for spec in sys.argv[1:]:
    n, rest = spec.split("=", 1); cf, pf = rest.split(":")
    pr = json.load(open(pf)); P, I, per, pa, pt = [], [], [], 0, 0
    for p in json.load(open(cf))["candidates"]:
        cs = sorted(p["cands"], key=lambda c: int(c.get("draw", 0)))
        v = pr[p["key"]]
        xs = [(v[j][0], float(c["iou"])) for j, c in enumerate(cs) if c.get("exec") and v[j] is not None]
        P += [x[0] for x in xs]; I += [x[1] for x in xs]
        if len(xs) >= 3 and np.std([x[1] for x in xs]) > 0 and np.std([x[0] for x in xs]) > 0:
            per.append(spearmanr([x[0] for x in xs], [x[1] for x in xs])[0])
        for a in range(len(xs)):
            for b in range(a + 1, len(xs)):
                if abs(xs[a][1] - xs[b][1]) >= 0.05:
                    pt += 1; pa += (xs[a][0] - xs[b][0]) * (xs[a][1] - xs[b][1]) > 0
    print(f"{n:16s} n={len(P):5d} pos>=.8 {np.mean(np.array(I) >= 0.8)*100:4.1f}%  spearman pooled {spearmanr(P, I)[0]:.3f} "
          f"per-part {np.mean(per):.3f} (n={len(per)})  AUROC>=.8 {auroc(P, np.array(I) >= 0.8):.3f}  pair-acc {pa/max(1,pt):.3f} ({pt} pairs)")
