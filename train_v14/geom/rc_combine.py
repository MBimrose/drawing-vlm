"""Selection by combinations of the three label-free signals on a scored best-of-N run:
candidate agreement (medoid), the expected-IoU verifier, and the render-and-compare sheet score.
Scores are z-normalised within a part and summed with equal weights (nothing is fitted).
    python rc_combine.py --tag bo8_ext_dw423p --run <run> --rc results/ext/rc_<...>.json [--field score]
"""
import argparse, json, os
import numpy as np
ap = argparse.ArgumentParser(); ap.add_argument("--tag", required=True); ap.add_argument("--run", required=True)
ap.add_argument("--rc", required=True); ap.add_argument("--field", default="score"); a = ap.parse_args()
rc = {p["key"]: p["cands"] for p in json.load(open(a.rc))["parts"]}
cons = {p["key"]: p for p in json.load(open(f"results/ext/{a.tag}_{a.run}_consistency.json"))["parts"]}
pp = f"results/ext/{a.tag}_{a.run}_vsel.json.preds.json"; preds = json.load(open(pp)) if os.path.exists(pp) else {}
def z(x):
    x = np.asarray(x, float); s = x.std(); return (x - x.mean()) / s if s > 1e-9 else np.zeros_like(x)
keys = [k for k in rc if k in cons]; res = {}
combos = {"first": (), "vote": ("agree",), "verifier": ("ver",), "render": ("rend",), "vote+render": ("agree", "rend"),
          "verifier+render": ("ver", "rend"), "vote+verifier": ("agree", "ver"), "all three": ("agree", "ver", "rend")}
for name, use in combos.items():
    tot = []
    for k in keys:
        c = cons[k]; iou = np.array(c["iou"], float); ex = np.array(c["exec"], bool); n = len(iou); P = c["pair_iou"]
        agree = np.array([np.mean([P[i][j] for j in range(n) if j != i and ex[j]]) if (ex[i] and ex.sum() > 1) else 0.0 for i in range(n)])
        pv = preds.get(k) or [None] * n
        ver = np.array([(v[0] if isinstance(v, list) else v) if v is not None else 0.0 for v in pv][:n], float)
        rend = np.array([x.get(a.field, 0.0) for x in rc[k]], float)[:n]
        if not ex.any(): tot.append(0.0); continue
        if not use: tot.append(iou[int(np.argmax(ex))]); continue
        s = sum(z(dict(agree=agree, ver=ver, rend=rend)[u]) for u in use); s[~ex] = -1e9
        tot.append(iou[int(np.argmax(s))])
    res[name] = (float(np.mean(tot)), float(np.mean(np.array(tot) >= 0.85)))
for n_, (m, g) in res.items(): print(f"{n_:18s} mean IoU {m:.3f}   >=0.85 {g:.1%}")
print(f"{'ceiling':18s} mean IoU {np.mean([max(cons[k]['iou']) for k in keys]):.3f}   ({len(keys)} parts)")
