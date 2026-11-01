"""Flash-Next pipeline stage table (2026-10-21): vote mean IoU per bench for any scored runs, plus paired deltas.
Runs are <dir>:<name> (files <dir>/<bench>_<name>.json + _consistency.json, the main-table protocol). Paired 2,000-sample
bootstrap 95% CIs over the parts both runs scored (rng 0, as build_ablation_table.py).
    python compare_stage.py --runs results/ablations:e59 results/flashnext/grpo:fn1s40 results/grpo_eval:ent_t10_s120 \
        --pairs fn1s40-e59 fn1s40-ent_t10_s120
"""
import argparse
import json
import os

import numpy as np

BENCH = [("full", "Synthetic (1,027)"), ("real", "Real-144 (dev)"), ("benchb", "Held-out 280")]
# bench-B files of the 27B GRPO runs live in results/bench_b/eval
ALT = {"benchb": ["results/bench_b/eval"]}


def load(d, b, n):
    for dd in [d] + ALT.get(b, []):
        f, cf = f"{dd}/{b}_{n}.json", f"{dd}/{b}_{n}_consistency.json"
        if os.path.exists(f) and os.path.exists(cf):
            break
    else:
        return None
    out = {p["key"]: None for p in json.load(open(f))["candidates"]}
    for k, v in json.load(open(cf))["per_part"].items():
        if k in out:
            out[k] = float(v["consistency"])
    return out if all(v is not None for v in out.values()) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--pairs", nargs="*", default=[])
    a = ap.parse_args()
    rng = np.random.default_rng(0)
    R = {}
    for r in a.runs:
        d, n = r.rsplit(":", 1)
        for b, _ in BENCH:
            R[(b, n)] = load(d, b, n)
    names = [r.rsplit(":", 1)[1] for r in a.runs]
    print("| Run | " + " | ".join(t for _, t in BENCH) + " |\n|---|" + "---|" * len(BENCH))
    for n in names:
        print(f"| {n} | " + " | ".join("—" if R[(b, n)] is None else f"{np.mean(list(R[(b, n)].values())):.3f}"
                                      for b, _ in BENCH) + " |")
    if a.pairs:
        print("\n| Paired delta (vote) | " + " | ".join(t for _, t in BENCH) + " |\n|---|" + "---|" * len(BENCH))
    for p in a.pairs:
        x, y = p.split("-", 1)
        cells = []
        for b, _ in BENCH:
            rx, ry = R.get((b, x)), R.get((b, y))
            if rx is None or ry is None:
                cells.append("—"); continue
            ks = sorted(set(rx) & set(ry))
            dd = np.array([rx[k] - ry[k] for k in ks])
            bs = [rng.choice(dd, len(dd)).mean() for _ in range(2000)]
            cells.append(f"{dd.mean():+.3f} [{np.percentile(bs, 2.5):+.3f}, {np.percentile(bs, 97.5):+.3f}] (n={len(ks)})")
        print(f"| {x} − {y} | " + " | ".join(cells) + " |")


if __name__ == "__main__":
    main()
