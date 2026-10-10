"""Cycle 2 real-bench table (144 parts, ext_bench_dw423_perm; K=8, draw 0 greedy + T 0.7, serv-20 eval daemon files):
per model draw-0 / mean-cand / first-exec / best-of-8 / exec (+ vote when a clean _consistency.json exists), and paired
deltas with 2,000-sample bootstrap 95% CIs (rng 0, = grpo_eval_summary.py) vs the reference models.
    python eval_table.py <model> [<model> ...] [--refs e55ctl,rft1_s20,rft1_rl2_s120,ent_t10_s120]"""
import argparse, json, os
import numpy as np
D = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/grpo_eval"
ap = argparse.ArgumentParser(); ap.add_argument("models", nargs="+"); ap.add_argument("--refs", default="e55ctl,rft1_s20,rft1_rl2_s120,ent_t10_s120")
ap.add_argument("--prefix", default="real", help="bench file prefix: real (144) / benchb (bench B, results/bench_b/eval)")
ap.add_argument("--dir", default=D)
a = ap.parse_args(); D = a.dir
def load(n):
    out = {}
    for p in json.load(open(f"{D}/{a.prefix}_{n}.json"))["candidates"]:
        c = sorted(p["cands"], key=lambda c: c.get("draw", 0))
        iou = [float(x.get("iou") or 0) for x in c]; ex = [bool(x.get("exec")) for x in c]
        out[p["key"]] = dict(d0=iou[0], mean=float(np.mean(iou)), fe=next((v for v, e in zip(iou, ex) if e), 0.0), bo=max(iou),
                             ex=float(np.mean(ex)))
    cf = f"{D}/{a.prefix}_{n}_consistency.json"
    if os.path.exists(cf):
        for k, v in json.load(open(cf))["per_part"].items():
            if k in out: out[k]["vote"] = float(v["consistency"])
    return out
rng = np.random.default_rng(0)
def ci(d):
    bs = [rng.choice(d, len(d)).mean() for _ in range(2000)]
    return np.percentile(bs, 2.5), np.percentile(bs, 97.5)
M = ("vote", "d0", "fe", "mean", "bo", "ex")
names = a.refs.split(",") + [m for m in a.models if m not in a.refs.split(",")]
R = {n: load(n) for n in names if os.path.exists(f"{D}/{a.prefix}_{n}.json")}
print("| model | " + " | ".join(M) + " |\n|---|" + "---|" * len(M))
for n, r in R.items():
    cells = []
    for m in M:
        v = [x[m] for x in r.values() if m in x]
        cells.append(f"{np.mean(v):.3f}" if len(v) == len(r) else ("n/a" if not v else f"{np.mean(v):.3f}*"))
    print(f"| {n} | " + " | ".join(cells) + " |")
for n in a.models:
    if n not in R: continue
    for ref in a.refs.split(","):
        if ref not in R or ref == n: continue
        ks = sorted(set(R[n]) & set(R[ref])); cells = []
        for m in M:
            if not all(m in R[n][k] and m in R[ref][k] for k in ks): cells.append("n/a"); continue
            d = np.array([R[n][k][m] - R[ref][k][m] for k in ks]); lo, hi = ci(d)
            cells.append(f"{d.mean():+.3f} [{lo:+.3f},{hi:+.3f}]")
        print(f"| {n} − {ref} (n={len(ks)}) | " + " | ".join(cells) + " |")
