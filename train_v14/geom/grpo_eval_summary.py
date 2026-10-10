"""Paired held-out comparison of GRPO models against the e55 control (same vLLM path, same parts).

    python grpo_eval_summary.py [--dir results/grpo_eval] [--control e55ctl]

Per bench x model: draw-0 (greedy) IoU, mean candidate IoU (= expected single sampled draw),
first-executing draw, best-of-8 (oracle), exec rate; and the paired delta vs control on the
intersection of parts with a 2,000-sample bootstrap 95% CI.
"""
import argparse
import glob
import json
import os

import numpy as np


def load(f):
    out = {}
    for p in json.load(open(f))["candidates"]:
        c = sorted(p["cands"], key=lambda c: c.get("draw", 0))
        iou = [float(x.get("iou") or 0) for x in c]
        ex = [bool(x.get("exec")) for x in c]
        fe = next((v for v, e in zip(iou, ex) if e), 0.0)
        out[p.get("key") or p.get("part")] = dict(d0=iou[0], mean=float(np.mean(iou)), fe=fe,
                                                  bo=max(iou), ex=float(np.mean(ex)))
    return out


def ci(d, rng):
    bs = [rng.choice(d, len(d)).mean() for _ in range(2000)]
    return np.percentile(bs, 2.5), np.percentile(bs, 97.5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/grpo_eval")
    ap.add_argument("--control", default="e55ctl")
    a = ap.parse_args()
    rng = np.random.default_rng(0)
    M = ("d0", "mean", "fe", "bo", "ex")
    for bench in ("real", "famheld", "indh"):
        files = {os.path.basename(f)[len(bench) + 1:-5]: f for f in glob.glob(f"{a.dir}/{bench}_*.json")
                 if ".shard" not in f and ".partial" not in f and "_consistency" not in f}
        if not files:
            continue
        ctl = load(files[a.control]) if a.control in files else None
        print(f"== {bench}")
        for name in sorted(files, key=lambda n: (n != a.control, n)):
            r = load(files[name])
            row = f"  {name:18s} n={len(r):3d} " + " ".join(f"{m} {np.mean([v[m] for v in r.values()]):.3f}" for m in M)
            if ctl is not None and name != a.control:
                ks = sorted(set(r) & set(ctl))
                for m in ("mean", "fe"):
                    d = np.array([r[k][m] - ctl[k][m] for k in ks])
                    lo, hi = ci(d, rng)
                    row += f" | d{m} {d.mean():+.3f} [{lo:+.3f},{hi:+.3f}]"
            cf = files[name][:-5] + "_consistency.json"
            if bench == "real" and os.path.exists(cf):
                pp = json.load(open(cf))["per_part"]
                row += f" | vote {np.mean([v['consistency'] for v in pp.values()]):.3f}"
                cc = files.get(a.control, "")[:-5] + "_consistency.json"
                if name != a.control and os.path.exists(cc):
                    pc = json.load(open(cc))["per_part"]; ks = sorted(set(pp) & set(pc))
                    for m in ("consistency", "oracle"):
                        d = np.array([pp[k][m] - pc[k][m] for k in ks]); lo, hi = ci(d, rng)
                        row += f" d{m[:4]} {d.mean():+.3f} [{lo:+.3f},{hi:+.3f}]"
            print(row)


if __name__ == "__main__":
    main()
