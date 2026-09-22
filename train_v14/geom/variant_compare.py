"""Matched-part comparison of best-of-N runs on bench variants (same parts, different sheets).
Per family: first draw, mean candidate, agreement vote (medoid of the consistency pair_iou;
exec/iou from the CANDIDATES file), oracle, exec rate; paired bootstrap CI of variant - base.
    python variant_compare.py --base <stem> --var <stem> [--var <stem>...]    (stem = results/ext/bo8_..._<run>)
"""
import argparse, json, numpy as np

def load(stem):
    C = {p["key"]: p for p in json.load(open(stem + ".json"))["candidates"]}
    import os
    K = {p["key"]: p for p in json.load(open(stem + "_consistency.json"))["parts"]} if os.path.exists(stem + "_consistency.json") else {}
    out = {}
    for k, p in C.items():
        cs = p["cands"]; iou = [float(c.get("iou") or 0) for c in cs]; ex = [bool(c.get("exec")) for c in cs]
        pw = K.get(k, {}).get("pair_iou")
        idx = [i for i in range(len(cs)) if ex[i]]
        v = None
        if idx and pw:
            def s(i): return sum((pw[i][j] or 0) for j in idx if j != i and pw[i] is not None and j < len(pw[i]))
            v = max(idx, key=s)
        elif idx:
            v = idx[0]
        out[k] = {"first": iou[0], "mean": float(np.mean(iou)), "vote": iou[v] if v is not None else 0.0,
                  "oracle": max(iou) if iou else 0.0, "exec": float(np.mean(ex))}
    return out

ap = argparse.ArgumentParser(); ap.add_argument("--base"); ap.add_argument("--var", action="append"); a = ap.parse_args()
B = load(a.base); rng = np.random.default_rng(0)
for vs in a.var:
    V = load(vs); ks = sorted(set(B) & set(V))
    print(f"\n{vs.split('/')[-1]}  vs  {a.base.split('/')[-1]}   matched parts {len(ks)}")
    for fam in ("ALL", "A", "F"):
        kk = [k for k in ks if fam == "ALL" or k[0] == fam]
        line = f"  [{fam}] n={len(kk):3d}"
        for m in ("first", "mean", "vote", "oracle", "exec"):
            b = np.array([B[k][m] for k in kk]); v = np.array([V[k][m] for k in kk]); d = v - b
            bs = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(2000)]
            line += f"  {m} {b.mean():.3f}->{v.mean():.3f} ({d.mean():+.3f} [{np.percentile(bs, 2.5):+.3f},{np.percentile(bs, 97.5):+.3f}])"
            if m in ("vote",): pass
        print(line)
