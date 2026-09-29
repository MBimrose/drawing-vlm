"""Summarise vr_serve.py outputs: start (e55 vote pick) vs repair draw 1, mean / best of the K repairs, and simple
label-free accept rules (agreement vote over {start} + repairs by pairwise code identity is not available offline,
so: 'first-exec repair' and 'keep start if no repair executes')."""
import json, sys, numpy as np
for path in sys.argv[1:]:
    try: R = [json.loads(l) for l in open(path)]
    except FileNotFoundError: print(path, "missing"); continue
    for fam in ("ALL", "A", "F"):
        rows = [r for r in R if fam == "ALL" or r["key"][0] == fam]
        if not rows: continue
        st = np.array([r["hist"][0]["iou"] for r in rows])
        dr = [r.get("draws") or [] for r in rows]
        fe = np.array([next((d["iou"] for d in ds if d["exec"]), s) for ds, s in zip(dr, st)])
        mn = np.array([np.mean([d["iou"] for d in ds]) if ds else s for ds, s in zip(dr, st)])
        be = np.array([max([d["iou"] for d in ds] + [s]) for ds, s in zip(dr, st)])
        ex = np.mean([d["exec"] for ds in dr for d in ds]) if any(dr) else 0
        print(f"{path.split('/')[-1]:28s} {fam:3s} n={len(rows):3d} start {st.mean():.3f} first-exec repair {fe.mean():.3f} (helped {int((fe>st+0.05).sum())} hurt {int((fe<st-0.05).sum())}) mean repair {mn.mean():.3f} best(start+K) {be.mean():.3f} exec {ex:.0%}")
