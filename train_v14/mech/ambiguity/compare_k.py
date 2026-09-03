"""Convention-prompt run vs stored baseline on the same 242 parts, first K draws,
same medoid selector.  python compare_k.py <K>"""
import json, os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); K = int(sys.argv[1]); O = os.path.join(HERE, "out")
c = json.load(open(f"{O}/bo{K}_underdet_convention_consistency.json"))
b = json.load(open(f"{O}/bo{K}_underdet_baseline_from_matrices.json"))
a = {r["key"]: r for r in json.load(open(f"{O}/analysis_e24.json"))["per_part"]}
keys = list(c["per_part"])
print(f"K={K}, n={len(keys)}; convention executed {sum(sum(p['exec']) for p in c['parts'])}/{len(keys)*K}")
print(f"{'policy':12s} {'baseline':>16s} {'convention':>16s} {'delta':>8s}  up>0.05 down<-0.05")
for pol in ("first_exec", "consistency", "oracle"):
    bv = np.array([b["per_part"][k][pol] for k in keys]); cv = np.array([c["per_part"][k][pol] for k in keys]); d = cv - bv
    print(f"{pol:12s} {bv.mean():.3f} ({np.mean(bv>=.85):.0%})    {cv.mean():.3f} ({np.mean(cv>=.85):.0%})   {d.mean():+.3f}   {np.sum(d>0.05):3d} {np.sum(d<-0.05):3d}")
env = [k for k in keys if a[k]["env_axes"]]; rest = [k for k in keys if not a[k]["env_axes"]]
wrong = [k for k in env if "modal_ext" in a[k] and abs(a[k]["modal_ext"] - a[k]["gt_ext"][a[k]["env_axes"][0]]) / a[k]["gt_ext"][a[k]["env_axes"][0]] > 0.03]
for lab, ks in (("env-axis dropped (114)", env), ("other dropped (128)", rest), ("modal length wrong (16)", wrong)):
    for pol in ("consistency", "oracle"):
        bv = np.array([b["per_part"][k][pol] for k in ks]); cv = np.array([c["per_part"][k][pol] for k in ks])
        print(f"  {lab:24s} {pol:12s} base={bv.mean():.3f} ({np.mean(bv>=.85):.0%})  conv={cv.mean():.3f} ({np.mean(cv>=.85):.0%})  delta={cv.mean()-bv.mean():+.3f}")
# medoid agreement (confidence) under both
def agree(parts):
    v = []
    for p in parts:
        idx = [j for j, e in enumerate(p["exec"]) if e]
        if len(idx) > 1: v.append(max(np.mean([p["pair_iou"][j][i] for i in idx if i != j]) for j in idx))
    return np.mean(v)
print(f"mean medoid agreement: convention={agree(c['parts']):.3f}")
