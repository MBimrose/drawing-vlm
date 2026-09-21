"""The serving-policy step, measured on ONE fixed set of parts.

The two policies that mattered most in distribution were introduced years apart in the run
series, and they were recorded by different evaluations: the execution-repair loop by the
in-training geometry eval (`runs/<run>/geom_eval/final.json`, 96 parts) and the best-of-8
agreement vote by the full-pool best-of-N pass (`results/bo8_full_<run>_consistency.json`,
1,030 parts). Averaging one against the other would compare two benches.

The 96 eval parts are a subset of the 1,030-part pool, so this script intersects them: it keeps
only the part keys present in EVERY run of both evaluations and recomputes both policies over
that fixed set. Every point on the figure is then the same parts, scored the same way, and the
step where the vote arrives is a like-for-like comparison.

    python plot_policy_step.py [--out results/figures/policy_step.svg]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from plot_progress import finish, house_style, save, series

DW423 = {"e55", "e57", "e58", "e59"}
NOISE = 0.04          # replicate spread on a ~95-part pool (RECIPE, seed replicate e34)


def enum(run):
    m = re.match(r"e(\d+)", run)
    return int(m.group(1)) if m else None


def load(root):
    repair, vote, first = {}, {}, {}
    for f in sorted(glob.glob(os.path.join(root, "runs/e*/geom_eval/final.json"))):
        run = f.split(os.sep)[-3]
        if enum(run) is None:
            continue
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if d["metrics"].get("v") != 2:
            continue
        repair[run] = {r["key"]: r.get("iou_centered") or 0.0 for r in d["records"] if r.get("key")}
    for f in sorted(glob.glob(os.path.join(root, "results/bo8_full_e*_consistency.json"))):
        run = re.match(r"bo8_full_(e[\w.-]+)_consistency\.json", os.path.basename(f)).group(1)
        if enum(run) is None:
            continue
        try:
            pp = json.load(open(f))["per_part"]
        except Exception:
            continue
        vote[run] = {k: v.get("consistency") for k, v in pp.items() if v.get("consistency") is not None}
        first[run] = {k: v.get("first_exec") for k, v in pp.items() if v.get("first_exec") is not None}
    return repair, vote, first


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm")
    ap.add_argument("--out", default="policy_step.svg")
    a = ap.parse_args()
    fam = house_style()
    repair, vote, first = load(a.root)

    # The in-training eval pool was swapped at e19: runs e1-e18 scored a set with NO overlap with
    # the certified pool, e19 onward share 95 of 96 parts with it. Keep only the later pool, so
    # every point below is the same parts.
    shared = None
    for d in vote.values():
        shared = set(d) if shared is None else shared & set(d)
    repair = {r: d for r, d in repair.items() if len(set(d) & shared) >= 0.9 * len(d)}
    for d in repair.values():
        shared &= set(d)
    shared = sorted(shared)
    if len(shared) < 40:
        raise SystemExit(f"only {len(shared)} parts common to every run; refusing to plot")
    mean = lambda d: float(np.mean([d[k] for k in shared])) if d and all(k in d for k in shared) else np.nan

    runs = sorted(set(repair) | set(vote), key=lambda r: (enum(r), r))
    x = np.array([enum(r) for r in runs], float)
    y_rep = np.array([mean(repair.get(r, {})) for r in runs])
    y_vote = np.array([mean(vote.get(r, {})) for r in runs])
    y_first = np.array([mean(first.get(r, {})) for r in runs])
    dw = np.array([f"e{enum(r)}" in DW423 for r in runs])

    c = plt.cm.plasma(np.linspace(0, 0.8, 3))
    fig, ax = plt.subplots(figsize=(6, 6))
    series(ax, x, y_rep, c[0], "o", "Greedy + execution-repair loop", hollow=dw, noise=NOISE)
    series(ax, x, y_first, c[1], "s", "Best-of-8, first to execute", hollow=dw, noise=NOISE)
    series(ax, x, y_vote, c[2], "d", "Best-of-8, agreement vote", hollow=dw, noise=NOISE)

    intro = np.nanmin(x[~np.isnan(y_vote)])
    ax.axvline(intro - 0.5, color="0.45", linestyle="--", linewidth=1.1, zorder=1)
    ax.text(intro - 1.0, 0.695, "best-of-8 introduced", rotation=90, fontsize=9,
            fontweight="bold", color="0.35", va="bottom", ha="right")

    finish(ax, "Fine-tune experiment", f"Mean volumetric IoU, {len(shared)} shared parts",
           (x.min() - 1.2, x.max() + 0.8), (0.68, 0.96), 5, 1, 0.05, 0.01,
           yfmt="%.2f", legend_loc="lower right")
    save(fig, a.root, a.out)

    ok = ~np.isnan(y_vote) & ~np.isnan(y_rep)
    print(f"[policy] {len(shared)} parts common to all {len(repair)} repair-loop runs and {len(vote)} best-of-8 runs")
    print(f"  repair loop, e1-e{int(intro)-1}: {np.nanmean(y_rep[x < intro]):.3f}")
    print(f"  where both exist (n={ok.sum()}): repair {y_rep[ok].mean():.3f} -> "
          f"first-to-execute {y_first[ok].mean():.3f} (+{(y_first-y_rep)[ok].mean():.3f}) -> "
          f"vote {y_vote[ok].mean():.3f} (+{(y_vote-y_first)[ok].mean():.3f}); "
          f"vote over repair +{(y_vote-y_rep)[ok].mean():.3f}")
    print(f"[policy] font={fam}")


if __name__ == "__main__":
    main()
