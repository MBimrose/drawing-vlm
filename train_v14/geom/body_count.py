"""Connected-component (body) count of GT meshes vs score: real bench vs synthetic pool."""
import json, os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iou import load_mesh
from concurrent.futures import ProcessPoolExecutor
def nb(p):
    m = load_mesh(p)
    if m is None: return None
    try: return len(m.split(only_watertight=False))
    except Exception: return None
def run(bo, gt):
    d = json.load(open(bo))["candidates"]; ks = [p["key"] for p in d]
    with ProcessPoolExecutor(24) as ex: n = list(ex.map(nb, [os.path.join(gt, k + ".stl") for k in ks]))
    return [(k, c, np.mean([float(x.get("iou") or 0) for x in p["cands"]])) for k, c, p in zip(ks, n, d) if c]
for name, bo, gt in (("synthetic", "results/bo8_full_e59-rft-c4-repair-dw423.json", "step_to_drw/wds_dataset/gt_meshes_v15"),
                     ("real", "results/ext/bo8_ext_dw423p_e55-rft-real-u5-gt-dw423.json", "train_v14/mech/benchmarks/data/ext_bench_dw423_perm/gt_meshes_v15")):
    R = run(bo, gt); c = np.array([r[1] for r in R]); y = np.array([r[2] for r in R])
    print(f"{name}: n={len(R)} single-body {np.mean(c==1):.1%}  2-3 bodies {np.mean((c>1)&(c<4)):.1%}  4+ {np.mean(c>=4):.1%}   IoU single {y[c==1].mean():.3f}  multi {y[c>1].mean() if (c>1).any() else float('nan'):.3f}")
    if name == "real":
        for fam in "AF":
            m = np.array([r[0][0] == fam for r in R]); print(f"   {fam}: multi-body {np.mean(c[m]>1):.1%}  IoU single {y[m&(c==1)].mean():.3f} multi {y[m&(c>1)].mean() if (m&(c>1)).any() else float('nan'):.3f}")
