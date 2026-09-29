"""One-round v3 gate from vr_serve.py records (draws carry inline v3): keep the best-v3 executing repair if its v3 beats
the start's by the margin. Paired bootstrap CI vs start, by family."""
import json, sys, numpy as np
path = sys.argv[1]; margins = [float(x) for x in sys.argv[2:]] or [0.05, 0.1, 0.15]
R = [json.loads(l) for l in open(path)]; rng = np.random.default_rng(0)
for m in margins:
    S, M, F = [], [], []
    for r in R:
        s = r["hist"][0]; ds = [d for d in (r.get("rounds") or [[]])[0] if d.get("exec")]
        b = max(ds, key=lambda d: d.get("v3", 0), default=None)
        S.append(s["iou"]); M.append(b["iou"] if b and b.get("v3", 0) > s.get("v3", 0) + m else s["iou"]); F.append(r["key"][0])
    S, M, F = map(np.array, (S, M, F)); out = []
    for fam in ("ALL", "A", "F"):
        i = np.arange(len(S)) if fam == "ALL" else np.where(F == fam)[0]
        if not len(i): continue
        d = M[i] - S[i]; bs = [d[rng.integers(0, len(i), len(i))].mean() for _ in range(3000)]
        out.append(f"{fam} {S[i].mean():.3f}->{M[i].mean():.3f} ({d.mean():+.3f} [{np.percentile(bs,2.5):+.3f},{np.percentile(bs,97.5):+.3f}])")
    print(f"{path.split('/')[-1]} margin {m}: " + "  ".join(out))
