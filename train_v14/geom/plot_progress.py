"""House-style progress figures across the whole fine-tune series.

Three panels, each a single bench — never two benches in one series:

  ood_progress.svg          146 held-out REAL drawings (Fusion 360 + ABC), K=8. Greedy first
                            draw, agreement vote, served policy. Same bench for every run.
  synth_progress_single.svg 96 held-out synthetic parts (Zero-To-CAD-1m derived), the in-training
                            geometry eval, protocol v2. Greedy single shot and the same shot after
                            the execution-repair loop — the only two policies that existed before
                            best-of-N sampling, so this reaches back to e1.
  synth_progress_bo8.svg    the full 1,030-part certified pool, K=8: first draw vs agreement vote,
                            i.e. what sampling buys in distribution.

Runs after the drafting engine changed (e55, e57, e58 on draftwright 0.4.23) are drawn with
hollow markers and separated by a rule wherever they were SCORED on the redrawn sheets, because
the parts are the same but the drawings are not. The real bench was never redrawn, so that
figure is continuous.

Style: King Lab guide — Arial (Nimbus Sans where absent), 13pt bold labels at labelpad=10, 11pt
bold ticks, inward major+minor ticks on all four sides, plasma(0->0.8) x the o/s/d/^ cycle,
frameless bold legend, limits cropped to the band, SVG out.

    python plot_progress.py [--history results/figures/history.json]
"""
from __future__ import annotations

import argparse
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FormatStrFormatter, MultipleLocator

# Measured replicate spread, per bench (RECIPE: seed replicates e18 and e34).
NOISE_REAL = 0.02    # 146-part real bench, best-of-8
NOISE_96 = 0.04      # 96-part synthetic pool, single shot - seed-to-seed spread
NOISE_FULL = 0.02    # 1,030-part certified pool, best-of-8
MARKERS = ["o", "s", "d", "^", "v"]


def house_style():
    installed = {f.name for f in matplotlib.font_manager.fontManager.ttflist}
    fam = next((f for f in ("Arial", "Helvetica", "Nimbus Sans", "DejaVu Sans") if f in installed), "sans-serif")
    plt.rcParams.update({"font.family": fam, "font.weight": "bold", "svg.fonttype": "none",
                         "axes.unicode_minus": False})
    return fam


def finish(ax, xlab, ylab, xlim, ylim, xmaj, xmin, ymaj, ymin, yfmt="%.2f", legend_loc="upper left"):
    ax.set_xlabel(xlab, fontsize=13, fontweight="bold", labelpad=10)
    ax.set_ylabel(ylab, fontsize=13, fontweight="bold", labelpad=10)
    ax.xaxis.set_major_locator(MultipleLocator(xmaj)); ax.xaxis.set_minor_locator(MultipleLocator(xmin))
    ax.yaxis.set_major_locator(MultipleLocator(ymaj)); ax.yaxis.set_minor_locator(MultipleLocator(ymin))
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    ax.xaxis.set_major_formatter(FormatStrFormatter("%.0f"))
    ax.yaxis.set_major_formatter(FormatStrFormatter(yfmt))
    ax.tick_params(which="both", direction="in", top=True, right=True, labelsize=11)
    ax.tick_params(which="major", length=6, width=1.1)
    ax.tick_params(which="minor", length=3, width=0.8)
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_fontweight("bold")
    for s in ax.spines.values():
        s.set_linewidth(1.1)
    ax.legend(fontsize=11, frameon=False, loc=legend_loc, handlelength=2.2,
              prop={"weight": "bold", "size": 11})


def save(fig, root, name):
    out = os.path.join(root, "results/figures", name)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, format="svg", dpi=300, bbox_inches="tight")
    fig.savefig(out.replace(".svg", ".png"), format="png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"[plot] wrote {out}")


def series(ax, x, y, color, marker, label, hollow=None, noise=NOISE_REAL):
    """One policy. `hollow` marks the runs scored on the redrawn 0.4.23 sheets: they are drawn
    open and are NOT joined to the earlier points, because that is a different set of drawings."""
    ok = ~np.isnan(y)
    kw = dict(markersize=6, linewidth=1.6, capsize=3, elinewidth=1, alpha=1.0, color=color)
    solid = ok & ~hollow if hollow is not None else ok
    ax.errorbar(x[solid], y[solid], yerr=noise, fmt=marker + "-",
                markeredgecolor="black", markeredgewidth=0.4, label=label, **kw)
    if hollow is not None and (hollow & ok).any():
        h = hollow & ok
        ax.errorbar(x[h], y[h], yerr=noise, fmt=marker + "-", markerfacecolor="white",
                    markeredgecolor=color, markeredgewidth=1.6, **kw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm")
    ap.add_argument("--history", default="results/figures/history.json")
    a = ap.parse_args()
    fam = house_style()
    hp = a.history if os.path.isabs(a.history) else os.path.join(a.root, a.history)
    rows = json.load(open(hp))
    col = lambda rs, k: np.array([r.get(k, np.nan) if r.get(k) is not None else np.nan for r in rs], float)

    # ---------- 1. real parts, out of distribution ----------
    rr = [r for r in rows if r.get("real_first_exec") is not None]
    x = col(rr, "e")
    c = plt.cm.plasma(np.linspace(0, 0.8, 3))
    fig, ax = plt.subplots(figsize=(6, 6))
    series(ax, x, col(rr, "real_first_exec"), c[0], MARKERS[0], "Greedy first draw")
    series(ax, x, col(rr, "real_consistency"), c[1], MARKERS[1], "Best-of-8, agreement vote")
    series(ax, x, col(rr, "real_gated"), c[2], MARKERS[2], "Served policy (vote + verifier gate)")
    finish(ax, "Fine-tune experiment", "Mean volumetric IoU, 146 held-out real parts",
           (x.min() - 0.6, x.max() + 0.6), (0.40, 0.58), 2, 1, 0.02, 0.005)
    save(fig, a.root, "ood_progress.svg")
    print(f"   real bench: {len(rr)} runs, e{int(x.min())}..e{int(x.max())}")

    # ---------- 2. Zero-To-CAD-1m derived, the deep history ----------
    sr = [r for r in rows if r.get("synth96_greedy") is not None]
    x2 = col(sr, "e"); dw = np.array([bool(r["dw423"]) for r in sr])
    c = plt.cm.plasma(np.linspace(0, 0.8, 2))
    fig, ax = plt.subplots(figsize=(6, 6))
    series(ax, x2, col(sr, "synth96_greedy"), c[0], MARKERS[0], "Greedy single shot", hollow=dw, noise=NOISE_96)
    series(ax, x2, col(sr, "synth96_repaired"), c[1], MARKERS[1], "After execution-repair loop",
           hollow=dw, noise=NOISE_96)
    if dw.any():
        ax.axvline(x2[dw].min() - 0.5, color="0.45", linestyle="--", linewidth=1.1, zorder=1)
        ax.text(x2[dw].min() - 0.9, 0.325, "sheets redrawn (0.4.23); open markers", rotation=90, fontsize=9,
                fontweight="bold", color="0.35", va="bottom", ha="right")
    finish(ax, "Fine-tune experiment", "Mean volumetric IoU, 96 held-out synthetic parts",
           (x2.min() - 1.2, x2.max() + 0.8), (0.30, 0.90), 5, 1, 0.10, 0.02, yfmt="%.1f")
    save(fig, a.root, "synth_progress_single.svg")
    print(f"   synthetic 96: {len(sr)} runs, e{int(x2.min())}..e{int(x2.max())}")

    # ---------- 3. Zero-To-CAD-1m derived, what sampling buys ----------
    fr = [r for r in rows if r.get("full_first") is not None]
    x3 = col(fr, "e"); dw3 = np.array([bool(r["dw423"]) for r in fr])
    c = plt.cm.plasma(np.linspace(0, 0.8, 2))
    fig, ax = plt.subplots(figsize=(6, 6))
    series(ax, x3, col(fr, "full_first"), c[0], MARKERS[0], "Greedy first draw", hollow=dw3, noise=NOISE_FULL)
    series(ax, x3, col(fr, "full_vote"), c[1], MARKERS[1], "Best-of-8, agreement vote",
           hollow=dw3, noise=NOISE_FULL)
    finish(ax, "Fine-tune experiment", "Mean volumetric IoU, 1,030-part certified pool",
           (x3.min() - 0.8, x3.max() + 0.8), (0.82, 0.95), 5, 1, 0.02, 0.005, legend_loc="lower right")
    save(fig, a.root, "synth_progress_bo8.svg")
    print(f"   synthetic full pool: {len(fr)} runs, e{int(x3.min())}..e{int(x3.max())}")
    print(f"[plot] font={fam}")


if __name__ == "__main__":
    main()
