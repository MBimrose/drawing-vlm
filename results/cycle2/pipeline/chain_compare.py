"""Cycle 2: compare repair chains / multi-start systems on the real bench (IoU vs GT, evaluation only; all selection
label-free). A system = one chain file (final = last adopted program, multistart_combine.py rule) or several chain files
joined with '+' (multi-start: per part the chain final with the highest v3). Prints mean / ABC / Fusion / >=0.85 and
paired deltas (3,000-sample bootstrap, rng 0; helped/hurt = |d| > 0.05) on common keys.
    python chain_compare.py name=c1.jsonl[+c2.jsonl+c3.jsonl] ... --pairs a:b,a:c"""
import argparse, json
import numpy as np
ap = argparse.ArgumentParser(); ap.add_argument("systems", nargs="+"); ap.add_argument("--pairs", default="")
ap.add_argument("--start", action="store_true", help="also report the chain-1 start of each system")
a = ap.parse_args()
def final(r):
    h = r["hist"]; x = h[0]
    for y in h[1:]:
        if y.get("adopted"): x = y
    return x
S = {}
for spec in a.systems:
    n, fs = spec.split("=", 1)
    ch = [{json.loads(l)["key"]: json.loads(l) for l in open(f)} for f in fs.split("+")]
    S[n] = {k: max((final(c[k]) for c in ch if k in c), key=lambda x: x.get("v3", 0))["iou"] for k in ch[0]}
    if a.start: S[n + "_start"] = {k: ch[0][k]["hist"][0]["iou"] for k in ch[0]}
def row(n, d):
    v = np.array(list(d.values())); ab = [x for k, x in d.items() if k.startswith("A_")]; fu = [x for k, x in d.items() if k.startswith("F_")]
    return f"| {n} | {len(v)} | {v.mean():.3f} | {np.mean(ab):.3f} | {np.mean(fu):.3f} | {np.mean(v >= 0.85):.0%} |"
print("| system | n | mean | ABC | Fusion | >=0.85 |\n|---|---|---|---|---|---|")
for n, d in S.items(): print(row(n, d))
rng = np.random.default_rng(0)
def ci(x):
    bs = [rng.choice(x, len(x)).mean() for _ in range(3000)]; return np.percentile(bs, 2.5), np.percentile(bs, 97.5)
if a.pairs:
    print("\n| paired | n | all | ABC | Fusion | +/- |\n|---|---|---|---|---|---|")
    for p in a.pairs.split(","):
        x, y = p.split(":"); ks = sorted(set(S[x]) & set(S[y]))
        d = np.array([S[x][k] - S[y][k] for k in ks]); lo, hi = ci(d)
        da = np.array([S[x][k] - S[y][k] for k in ks if k.startswith("A_")]); df = np.array([S[x][k] - S[y][k] for k in ks if k.startswith("F_")])
        la, ha = ci(da); lf, hf = ci(df)
        print(f"| {x} − {y} | {len(ks)} | {d.mean():+.3f} [{lo:+.3f}, {hi:+.3f}] | {da.mean():+.3f} [{la:+.3f}, {ha:+.3f}] | "
              f"{df.mean():+.3f} [{lf:+.3f}, {hf:+.3f}] | +{int((d > 0.05).sum())}/−{int((d < -0.05).sum())} |")
