import json, os, sys, numpy as np
sys.path.insert(0, "train_v14/geom")
from iou import load_mesh
from shape_diag import thickness
from concurrent.futures import ProcessPoolExecutor
def feat(a):
    k, path = a
    m = load_mesh(path)
    if m is None: return None
    t, V, A = thickness(m); bb = float(np.prod(m.extents))
    return k, (V / bb if bb else 0), t / float(max(m.extents))
def load(bo, gtdir):
    d = json.load(open(bo))["candidates"]
    out = {}
    jobs = [(p["key"], os.path.join(gtdir, p["key"] + ".stl")) for p in d if os.path.exists(os.path.join(gtdir, p["key"] + ".stl"))]
    with ProcessPoolExecutor(24) as ex:
        F = {r[0]: r[1:] for r in ex.map(feat, jobs) if r}
    for p in d:
        if p["key"] not in F: continue
        i = [float(c.get("iou") or 0) for c in p["cands"]]
        out[p["key"]] = dict(fill=F[p["key"]][0], relt=F[p["key"]][1], first=i[0], oracle=max(i), mean=float(np.mean(i)))
    return out
S = load("results/bo8_full_e59-rft-c4-repair-dw423.json", "step_to_drw/wds_dataset/gt_meshes_v15")
R = load("results/ext/bo8_ext_dw423p_e59-rft-c4-repair-dw423.json" if os.path.exists("results/ext/bo8_ext_dw423p_e59-rft-c4-repair-dw423.json") else "results/ext/bo8_ext_dw423p_e55-rft-real-u5-gt-dw423.json", "train_v14/mech/benchmarks/data/ext_bench_dw423_perm/gt_meshes_v15")
print("synthetic parts", len(S), " real parts", len(R))
for name, key, bins in (("fill (V / bbox V)", "fill", [(0,.15),(.15,.3),(.3,.5),(.5,.75),(.75,1.01)]), ("rel thickness", "relt", [(0,.03),(.03,.06),(.06,.12),(.12,.25),(.25,9)])):
    print(f"\nby {name}:            synthetic n / mean-cand / oracle      real n / mean-cand / oracle")
    for lo, hi in bins:
        s = [v for v in S.values() if lo <= v[key] < hi]; r = [v for v in R.values() if lo <= v[key] < hi]
        f = lambda X, m: np.mean([x[m] for x in X]) if X else float("nan")
        print(f"  [{lo:.2f},{hi:.2f})   {len(s):5d} / {f(s,'mean'):.3f} / {f(s,'oracle'):.3f}        {len(r):4d} / {f(r,'mean'):.3f} / {f(r,'oracle'):.3f}")
    print("  share of parts:", "synthetic", [round(np.mean([lo<=v[key]<hi for v in S.values()]),2) for lo,hi in bins], "real", [round(np.mean([lo<=v[key]<hi for v in R.values()]),2) for lo,hi in bins])
# reweight synthetic to real's fill distribution
b=[(0,.15),(.15,.3),(.3,.5),(.5,.75),(.75,1.01)]
w=[np.mean([lo<=v["fill"]<hi for v in R.values()]) for lo,hi in b]
sm=[np.mean([v["mean"] for v in S.values() if lo<=v["fill"]<hi] or [np.nan]) for lo,hi in b]
print(f"\nsynthetic mean-candidate IoU {np.mean([v['mean'] for v in S.values()]):.3f}; reweighted to the real fill mix {np.nansum(np.array(w)*np.array(sm))/np.sum(np.array(w)[~np.isnan(sm)]):.3f}; real {np.mean([v['mean'] for v in R.values()]):.3f}")
