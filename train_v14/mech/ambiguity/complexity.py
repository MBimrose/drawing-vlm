"""Is the underdetermined deficit about the missing dimension, or about sheet
complexity (the renderer drops dimensions on crowded sheets)?  Compare vote IoU
vs annotation count within determinate sheets, and a count-matched slice."""
import json, os, numpy as np
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
sc = json.load(open(os.path.join(HERE, "pool_sidecar.json")))
cons = json.load(open(os.path.join(DV, "results/bo8_full_e24_consistency_v2.json")))
un = set(l.strip() for l in open(os.path.join(HERE, "keys_underdet.txt")) if l.strip())
rows = []
for u, vs in sc.items():
    v = list(vs.values())[0]
    n_ann = len(v["annotations"]); n_pl = len(v["dims_placed"]); n_un = len(v["dims_unplaced"])
    pp = cons["per_part"][u]
    rows.append(dict(u=u, under=u in un, n_ann=n_ann, n_placed=n_pl, n_unplaced=n_un, n_total=n_pl + n_un,
                     vote=pp["consistency"], oracle=pp["oracle"], first=pp["first_exec"]))
U = [r for r in rows if r["under"]]; D = [r for r in rows if not r["under"]]
f = lambda rs, k: (np.mean([r[k] for r in rs]), np.mean([r[k] >= 0.85 for r in rs]))
print(f"underdet n={len(U)} ann={np.mean([r['n_ann'] for r in U]):.1f} dims_total={np.mean([r['n_total'] for r in U]):.1f} placed={np.mean([r['n_placed'] for r in U]):.1f} vote={f(U,'vote')[0]:.3f} oracle={f(U,'oracle')[0]:.3f}")
print(f"determ   n={len(D)} ann={np.mean([r['n_ann'] for r in D]):.1f} dims_total={np.mean([r['n_total'] for r in D]):.1f} placed={np.mean([r['n_placed'] for r in D]):.1f} vote={f(D,'vote')[0]:.3f} oracle={f(D,'oracle')[0]:.3f}")
print("\nvote/oracle by total dimension count (placed+unplaced), determinate vs underdetermined:")
bins = [(0, 6), (7, 9), (10, 12), (13, 16), (17, 999)]
for lo, hi in bins:
    d = [r for r in D if lo <= r["n_total"] <= hi]; u = [r for r in U if lo <= r["n_total"] <= hi]
    s = f"dims {lo:2d}-{hi if hi<999 else '+':>3}: det n={len(d):3d}"
    if d: s += f" vote={f(d,'vote')[0]:.3f} ({f(d,'vote')[1]:.0%}) oracle={f(d,'oracle')[0]:.3f}"
    s += f" | under n={len(u):3d}"
    if u: s += f" vote={f(u,'vote')[0]:.3f} ({f(u,'vote')[1]:.0%}) oracle={f(u,'oracle')[0]:.3f}"
    print(s)
# count-matched determinate slice: for every underdetermined part, sample determinate parts with the same n_total
rng = np.random.default_rng(0)
byn = defaultdict(list)
for r in D: byn[r["n_total"]].append(r)
matched = []
for r in U:
    pool = byn.get(r["n_total"]) or byn.get(r["n_total"] - 1) or byn.get(r["n_total"] + 1) or byn.get(r["n_total"] - 2) or byn.get(r["n_total"] + 2)
    if pool: matched.append(pool[rng.integers(len(pool))])
print(f"\ncount-matched determinate slice n={len(matched)}: vote={f(matched,'vote')[0]:.3f} ({f(matched,'vote')[1]:.0%}) oracle={f(matched,'oracle')[0]:.3f}  vs underdet vote={f(U,'vote')[0]:.3f} oracle={f(U,'oracle')[0]:.3f}")
# correlation within determinate
x = np.array([r["n_total"] for r in D]); y = np.array([r["vote"] for r in D])
print(f"determinate: corr(n_dims, vote IoU) = {np.corrcoef(x, y)[0,1]:.3f}; underdet: {np.corrcoef([r['n_total'] for r in U],[r['vote'] for r in U])[0,1]:.3f}")
