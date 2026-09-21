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
        # has_gt filters the parts with no ground-truth mesh; without it the early pool (79 of 96
        # scored) is dragged down by 17 unscorable records and the run's own metric is not reproduced.
        repair[run] = {r["key"]: r.get("iou_centered") or 0.0
                       for r in d["records"] if r.get("key") and r.get("has_gt")}
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
    ap.add_argument("--milestones", default="e1,e2,e5,e7,e12,e16,e18,e19,e22,e24,e30,e34,e38,e40,e46,e51",
                    help="runs to show: the recipe steps that marked an improvement (empty = every run)")
    a = ap.parse_args()
    fam = house_style()
    repair, vote, first = load(a.root)

    # The in-training eval pool was swapped at e19: runs e1-e18 scored a set with NO overlap with
    # the certified pool, e19 onward share 95 of 96 parts with it. Keep only the later pool, so
    # every point below is the same parts.
    shared = None
    for d in vote.values():
        shared = set(d) if shared is None else shared & set(d)
    repair_all = dict(repair)                      # includes the e1-e18 pool, kept for milestones
    repair = {r: d for r, d in repair.items() if len(set(d) & shared) >= 0.9 * len(d)}
    for d in repair.values():
        shared &= set(d)
    shared = sorted(shared)
    if len(shared) < 40:
        raise SystemExit(f"only {len(shared)} parts common to every run; refusing to plot")
    def mean(d, own_ok=False):
        """Mean over the shared parts; with own_ok, fall back to the run's own pool (a different
        set of parts, so those points are marked and never joined to the rest)."""
        if d and all(k in d for k in shared):
            return float(np.mean([d[k] for k in shared]))
        return float(np.mean(list(d.values()))) if (own_ok and d) else np.nan

    # The two evaluations name the same experiment differently ("e34" vs "e34-rft-seed43"), so
    # everything is keyed by experiment number and merged.
    by_e: dict[int, dict] = {}
    for src, key in ((repair_all, "rep"), (vote, "vote"), (first, "first")):
        for r, d in src.items():
            by_e.setdefault(enum(r), {})[key] = d
            by_e[enum(r)].setdefault("name", r)
            if len(r) > len(by_e[enum(r)]["name"]):
                by_e[enum(r)]["name"] = r
    es = sorted(by_e)
    if a.milestones:
        want = {int(w.strip().lstrip("e")) for w in a.milestones.split(",") if w.strip()}
        missing = sorted(want - set(es))
        if missing:
            print(f"[policy] no data for e{missing}")
        es = [e for e in es if e in want]
    runs = [by_e[e]["name"] for e in es]
    # Milestones are far apart in run number; space them evenly and label each, so the figure is
    # read as a sequence of recipe steps rather than a time axis with large empty gaps.
    x = np.arange(len(es), dtype=float) if a.milestones else np.array(es, float)
    # e1-e18 were scored on a different 96-part pool; keep them, but mark them.
    y_rep = np.array([mean(by_e[e].get("rep", {}), own_ok=True) for e in es])
    other_pool = np.array([bool(by_e[e].get("rep")) and not all(k in by_e[e]["rep"] for k in shared)
                           for e in es])
    y_vote = np.array([mean(by_e[e].get("vote", {})) for e in es])
    y_first = np.array([mean(by_e[e].get("first", {})) for e in es])
    dw = np.array([f"e{e}" in DW423 for e in es])

    c = plt.cm.plasma(np.linspace(0, 0.8, 3))
    fig, ax = plt.subplots(figsize=(6, 6))
    series(ax, x, y_rep, c[0], "o", "Greedy + execution-repair loop", hollow=dw | other_pool, noise=NOISE)
    if other_pool.any() and (~other_pool).any():
        cut = (x[other_pool].max() + x[~other_pool].min()) / 2
        ax.axvline(cut, color="0.45", linestyle="--", linewidth=1.1, zorder=1)
        ax.text(cut - 0.12, 0.86, "different eval pool", rotation=90, fontsize=9,
                fontweight="bold", color="0.35", va="bottom", ha="right")
    series(ax, x, y_first, c[1], "s", "Best-of-8, first to execute", hollow=dw, noise=NOISE)
    series(ax, x, y_vote, c[2], "d", "Best-of-8, agreement vote", hollow=dw, noise=NOISE)

    finish(ax, "Fine-tune experiment", f"Mean volumetric IoU, {len(shared)} shared parts",
           (x.min() - 0.5, x.max() + 0.5), (0.40, 0.98), 1, 1, 0.10, 0.02,
           yfmt="%.1f", legend_loc="lower right")
    if a.milestones:      # explicit positions, one per milestone
        from matplotlib.ticker import FixedLocator, NullLocator
        ax.xaxis.set_major_locator(FixedLocator(list(x))); ax.xaxis.set_minor_locator(NullLocator())
        ax.set_xticklabels([f"e{e}" for e in es], fontweight="bold",
                           fontsize=11 if len(es) <= 10 else 9,
                           rotation=0 if len(es) <= 10 else 45, ha="center" if len(es) <= 10 else "right")
    save(fig, a.root, a.out)

    ok = ~np.isnan(y_vote) & ~np.isnan(y_rep)
    print(f"[policy] {len(shared)} parts common to all {len(repair)} repair-loop runs and {len(vote)} best-of-8 runs")
    print(f"  shown: {', '.join(runs)}")
    print(f"  where both exist (n={ok.sum()}): repair {y_rep[ok].mean():.3f} -> "
          f"first-to-execute {y_first[ok].mean():.3f} (+{(y_first-y_rep)[ok].mean():.3f}) -> "
          f"vote {y_vote[ok].mean():.3f} (+{(y_vote-y_first)[ok].mean():.3f}); "
          f"vote over repair +{(y_vote-y_rep)[ok].mean():.3f}")
    print(f"[policy] font={fam}")


if __name__ == "__main__":
    main()
