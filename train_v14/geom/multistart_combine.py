"""Label-free multi-start combination: per part, the final adopted program of each repair chain (different e55 starting
candidates) competes on v3; keep the highest. Reports mean IoU with a paired CI vs chain 1 and vs the e55 pick."""
import json, sys, numpy as np
chains = [{json.loads(l)["key"]: json.loads(l) for l in open(f)} for f in sys.argv[1:]]
def final(r):
    h = r["hist"]; x = h[0]
    for y in h[1:]:
        if y.get("adopted"): x = y
    return x
keys = sorted(set(chains[0]))
start = np.array([chains[0][k]["hist"][0]["iou"] for k in keys]); c1 = np.array([final(chains[0][k])["iou"] for k in keys])
best = []; orc = []
for k in keys:
    fs = [final(c[k]) for c in chains if k in c]
    best.append(max(fs, key=lambda x: x.get("v3", 0))["iou"]); orc.append(max(x["iou"] for x in fs))
best = np.array(best); F = np.array([k[0] for k in keys]); rng = np.random.default_rng(0)
def ci(a, b):
    d = a - b; bs = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(3000)]; return f"{d.mean():+.3f} [{np.percentile(bs,2.5):+.3f},{np.percentile(bs,97.5):+.3f}]"
print(f"n={len(keys)} e55 pick {start.mean():.3f} | chain1 {c1.mean():.3f} | multi-start v3-pick {best.mean():.3f} (vs chain1 {ci(best,c1)}, vs e55 {ci(best,start)}) | oracle over chains {np.mean(orc):.3f}")
print(f"  ABC {best[F=='A'].mean():.3f}  Fusion {best[F=='F'].mean():.3f}")
