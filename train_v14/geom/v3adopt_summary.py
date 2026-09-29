"""vis_repair --adopt v3 output: final = last adopted program (label-free), per round, with paired bootstrap CI vs start."""
import json, sys, numpy as np
R = [json.loads(l) for l in open(sys.argv[1])]
rows = []
for r in R:
    h = r["hist"]; st = h[0]["iou"]; cur = st; traj = [st]
    for rd in range(1, 10):
        for x in h:
            if x["round"] == rd and x.get("adopted"): cur = x["iou"]
        traj.append(cur)
    rows.append((r["key"][0], st, traj, max(x.get("iou", 0) for x in h)))
F = np.array([x[0] for x in rows]); rng = np.random.default_rng(0)
nr = max(x["round"] for r in R for x in r["hist"])
for fam in ("ALL", "A", "F"):
    idx = np.arange(len(rows)) if fam == "ALL" else np.where(F == fam)[0]
    st = np.array([rows[i][1] for i in idx])
    line = [f"{fam:3s} n={len(idx):3d} start {st.mean():.3f}"]
    for rd in range(1, nr + 1):
        fi = np.array([rows[i][2][rd] for i in idx]); d = fi - st
        bs = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(3000)]
        line.append(f"r{rd} {fi.mean():.3f} ({d.mean():+.3f} [{np.percentile(bs,2.5):+.3f},{np.percentile(bs,97.5):+.3f}] +{int((d>0.05).sum())}/-{int((d<-0.05).sum())})")
    line.append(f"best {np.mean([rows[i][3] for i in idx]):.3f}")
    print("  ".join(line))
