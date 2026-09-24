"""H2b: are missed real dimensions rounded (prior toward nice numbers) or absent? Per printed value: exact hit,
loose hit (within 5%), and whether the value itself is 'round' (integer or .5)."""
import json, re, sys, numpy as np
sys.path.insert(0, "train_v14/geom")
from fp_h2_dimrecall import sheet_vals, code_vals
bo = json.load(open(sys.argv[1]))["candidates"]; rend = json.load(open(sys.argv[2]))
side = {k.rsplit("_v", 1)[0]: v for k, v in rend.items() if v}
S = []
for p in bo:
    s = side.get(p["key"]) or side.get(p["key"].rsplit("_v", 1)[0])
    if not s: continue
    sv = sheet_vals(s.get("annotations") or {})
    for c in p["cands"][:8]:
        if not c.get("code"): continue
        cv = code_vals(c["code"])
        for v in sv:
            ex = any(abs(x - t) <= max(0.05, 0.01 * t) for t in (v, v / 2, 2 * v) for x in cv)
            lo = any(abs(x - t) <= 0.05 * t for t in (v, v / 2, 2 * v) for x in cv)
            rnd = abs(v * 2 - round(v * 2)) < 1e-6
            S.append((rnd, ex, lo))
S = np.array(S)
print(f"[{sys.argv[3]}] printed values {len(S)}: round (int or .5) {S[:,0].mean():.1%} | exact recall {S[:,1].mean():.3f} "
      f"| within-5% recall {S[:,2].mean():.3f} | exact on round {S[S[:,0]==1,1].mean():.3f} vs non-round {S[S[:,0]==0,1].mean():.3f}"
      f" | near-miss (5% but not exact) on non-round {np.mean(S[S[:,0]==0,2] & ~S[S[:,0]==0,1].astype(bool)):.3f}")
