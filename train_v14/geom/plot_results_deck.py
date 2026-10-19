"""Results-section charts in the house plotting style (bold Arial, 6x6 square panel, inward ticks on all four
sides, plasma + marker cycle for multi-series, Illinois dark blue for single-series, SVG out):

  repair_loop        real bench: mean IoU after each repair round, single chain vs 3-chain multi-start
  faces_vs_iou       synthetic pool: GT B-rep face count vs medoid IoU
  exectime_vs_iou    synthetic pool: medoid program execution time vs medoid IoU
  iou_hist           synthetic pool: histogram of medoid IoU
  iou_survival       synthetic pool: fraction of parts at or above an IoU threshold (first draw / medoid / oracle)

Data: results_deck_data.py (parts.json) and repair_curve.py (repair_curve.json).
    .venv/bin/python train_v14/geom/plot_results_deck.py
"""
import json
import os

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager as fm  # noqa: E402
from matplotlib.ticker import FixedLocator, FormatStrFormatter, MultipleLocator, NullFormatter  # noqa: E402

DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
D = f"{DV}/results/figures/results_deck"
ILLINI_BLUE = "#13294B"
MARKERS = ["o", "s", "d", "^", "v"]
for f in ("NimbusSans-Regular.otf", "NimbusSans-Bold.otf"):   # Arial-metric; SVG relabelled Arial on save
    p = f"/usr/share/fonts/urw-base35/{f}"
    if os.path.exists(p):
        fm.fontManager.addfont(p)
plt.rcParams["font.family"] = "Nimbus Sans"
plt.rcParams["svg.fonttype"] = "none"


def palette(n):
    return plt.cm.plasma(np.linspace(0, 0.75, n))


def style(ax, xlabel, ylabel, xmaj=None, xmin=None, ymaj=None, ymin=None, xlim=None, ylim=None, xfmt="%.1f", yfmt="%.1f"):
    """Locators -> limits -> formatters -> label styling (the order that keeps the bold tick labels)."""
    ax.set_xlabel(xlabel, fontsize=13, fontweight="bold", labelpad=10)
    ax.set_ylabel(ylabel, fontsize=13, fontweight="bold", labelpad=10)
    if xmaj is not None: ax.xaxis.set_major_locator(xmaj if not isinstance(xmaj, float) else MultipleLocator(xmaj))
    if xmin is not None: ax.xaxis.set_minor_locator(xmin if not isinstance(xmin, float) else MultipleLocator(xmin))
    if ymaj is not None: ax.yaxis.set_major_locator(ymaj if not isinstance(ymaj, float) else MultipleLocator(ymaj))
    if ymin is not None: ax.yaxis.set_minor_locator(ymin if not isinstance(ymin, float) else MultipleLocator(ymin))
    if xlim: ax.set_xlim(*xlim)
    if ylim: ax.set_ylim(*ylim)
    if xfmt: ax.xaxis.set_major_formatter(FormatStrFormatter(xfmt))
    if yfmt: ax.yaxis.set_major_formatter(FormatStrFormatter(yfmt))
    ax.xaxis.set_minor_formatter(NullFormatter()); ax.yaxis.set_minor_formatter(NullFormatter())
    ax.tick_params(which="both", direction="in", top=True, right=True, bottom=True, left=True)
    ax.tick_params(which="major", labelsize=11)
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_fontweight("bold")


def note(ax, text, loc="lower right"):
    x, ha = (0.96, "right") if "right" in loc else (0.04, "left")
    y, va = (0.05, "bottom") if "lower" in loc else (0.95, "top")
    ax.text(x, y, text, transform=ax.transAxes, ha=ha, va=va, fontsize=12, fontweight="bold")


def save(fig, name):
    for ext in ("svg", "png"):
        fig.savefig(f"{D}/{name}.{ext}", format=ext, dpi=300, bbox_inches="tight")
    s = open(f"{D}/{name}.svg").read().replace("Nimbus Sans", "Arial"); open(f"{D}/{name}.svg", "w").write(s)
    plt.close(fig); print("wrote", name)


def spearman(x, y):
    return np.corrcoef(np.argsort(np.argsort(x)), np.argsort(np.argsort(y)))[0, 1]


def repair_loop(rc):
    fig, ax = plt.subplots(figsize=(6, 6)); c = palette(2); r = np.array(rc["rounds"])
    for i, (key, label) in enumerate([("chain1", "Single repair chain"), ("multistart", "Multi-start, 3 chains")]):
        ax.errorbar(r, rc[f"{key}_mean"], yerr=rc[f"{key}_sem"], fmt=MARKERS[i] + "-", color=c[i], markersize=7,
                    capsize=3, elinewidth=1, linewidth=1.5, alpha=1.0, label=label)
    ax.axhline(rc["e55_oracle8"], color="gray", linestyle="--", alpha=0.7, linewidth=1.2, label="Best of 8, no repair")
    style(ax, "Repair round", "Mean IoU", xmaj=FixedLocator(list(r)), ymaj=0.05, ymin=0.01,
          xlim=(-0.4, r[-1] + 0.4), ylim=(0.45, 0.75), xfmt="%.0f", yfmt="%.2f")
    ax.legend(loc="lower right", frameon=False, prop={"weight": "bold", "size": 11})
    save(fig, "repair_loop")


def faces_vs_iou(P):
    x = np.array([p["medoid"] for p in P]); y = np.array([p["faces"] for p in P])
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(x, y, s=18, color=ILLINI_BLUE, alpha=0.5, linewidths=0)
    ax.set_yscale("log")
    style(ax, "Ground-truth IoU", "Face count", xmaj=0.2, xmin=0.05,
          ymaj=FixedLocator([5, 10, 20, 50, 100, 200, 500]), xlim=(0, 1.0), ylim=(4, 500), yfmt="%.0f")
    ax.yaxis.set_minor_locator(FixedLocator([v * m for m in (1, 10, 100) for v in range(2, 10) if 4 <= v * m <= 500]))
    ax.yaxis.set_minor_formatter(NullFormatter())
    note(ax, f"Spearman ρ = {spearman(x, y):.2f}", "upper left")
    save(fig, "faces_vs_iou")


def exectime_vs_iou(P):
    Q = [p for p in P if p.get("exec_sec") is not None]
    x = np.array([p["medoid"] for p in Q]); y = np.array([p["exec_sec"] for p in Q])
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(x, y, s=18, color=ILLINI_BLUE, alpha=0.5, linewidths=0)
    ax.set_yscale("log")
    lo, hi = 10 ** np.floor(np.log10(y.min())), 10 ** np.ceil(np.log10(y.max()))
    style(ax, "Ground-truth IoU", "Execution time (s)", xmaj=0.2, xmin=0.05,
          ymaj=FixedLocator([v for v in (0.01, 0.1, 1, 10, 100) if lo <= v <= hi]), xlim=(0, 1.0), ylim=(lo, hi), yfmt=None)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
    ax.yaxis.set_minor_locator(FixedLocator([v * m for m in (0.01, 0.1, 1, 10) for v in range(2, 10) if lo <= v * m <= hi]))
    for t in ax.get_yticklabels():
        t.set_fontweight("bold")
    note(ax, f"median {np.median(y):.2f} s\nSpearman ρ = {spearman(x, y):.2f}", "upper left")
    save(fig, "exectime_vs_iou")


def faces_vs_exectime(P):
    """Two complexity measures against each other: GT face count vs medoid program execution time (log-log)."""
    Q = [p for p in P if p.get("exec_sec") is not None]
    x = np.array([p["faces"] for p in Q]); y = np.array([p["exec_sec"] for p in Q])
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(x, y, s=18, color=ILLINI_BLUE, alpha=0.5, linewidths=0)
    ax.set_xscale("log"); ax.set_yscale("log")
    ylo, yhi = 10 ** np.floor(np.log10(y.min())), 10 ** np.ceil(np.log10(y.max()))
    # log axes labelled at powers of ten only; everything in between is an unlabelled minor tick
    style(ax, "Face count", "Execution time (s)", xmaj=FixedLocator([10, 100]), xlim=(5, 500),
          ymaj=FixedLocator([v for v in (0.01, 0.1, 1, 10, 100) if ylo <= v <= yhi]), ylim=(ylo, yhi), xfmt="%.0f", yfmt=None)
    ax.xaxis.set_minor_locator(FixedLocator([v * m for m in (1, 10, 100) for v in range(2, 10) if 5 <= v * m <= 500]))
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
    ax.yaxis.set_minor_locator(FixedLocator([v * m for m in (0.01, 0.1, 1, 10) for v in range(2, 10) if ylo <= v * m <= yhi]))
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_fontweight("bold")
    r2 = np.corrcoef(np.log10(x), np.log10(y))[0, 1] ** 2
    note(ax, f"Spearman ρ = {spearman(x, y):.2f}\nr² (log-log) = {r2:.2f}", "upper left")
    save(fig, "faces_vs_exectime")


def iou_hist(P):
    x = np.array([p["medoid"] for p in P])
    fig, ax = plt.subplots(figsize=(6, 6))
    w = np.ones_like(x) * 100 / len(x)
    ax.hist(x, bins=np.arange(0, 1.0001, 0.05), weights=w, color=ILLINI_BLUE, edgecolor="white", linewidth=0.8)
    top = np.ceil(np.histogram(x, bins=np.arange(0, 1.0001, 0.05), weights=w)[0].max() / 10) * 10
    # no y label at 0 so it does not collide with the x-axis "0.0" at the origin
    style(ax, "Ground-truth IoU", "Parts (%)", xmaj=0.2, xmin=0.05, ymaj=FixedLocator(list(np.arange(10, top + 1, 10))),
          ymin=5.0, xlim=(0, 1.0), ylim=(0, top), yfmt="%.0f")
    note(ax, f"n = {len(x)}\nmean {x.mean():.3f}\nmedian {np.median(x):.3f}\nIoU ≥ 0.85: {np.mean(x >= 0.85):.0%}", "upper left")
    save(fig, "iou_hist")


def iou_survival(P):
    t = np.linspace(0, 1, 201); c = palette(3)
    fig, ax = plt.subplots(figsize=(6, 6))
    for i, (k, label) in enumerate([("first", "First executing draw"), ("medoid", "Medoid of 8"), ("oracle", "Best of 8 (oracle)")]):
        x = np.array([p[k] for p in P])
        ax.plot(t, [100 * np.mean(x >= v) for v in t], color=c[i], linewidth=2, label=label,
                marker=MARKERS[i], markevery=20, markersize=7)
    ax.axvline(0.85, color="gray", linestyle="--", alpha=0.7, linewidth=1.2)
    style(ax, "IoU threshold", "Parts at or above threshold (%)", xmaj=FixedLocator([0.5, 0.6, 0.7, 0.8, 0.9, 1.0]), xmin=0.05,
          ymaj=FixedLocator([50, 60, 70, 80, 90, 100]), ymin=5.0,
          xlim=(0.45, 1.0), ylim=(45, 100), yfmt="%.0f")
    ax.legend(loc="lower left", frameon=False, prop={"weight": "bold", "size": 11})
    save(fig, "iou_survival")


if __name__ == "__main__":
    P = json.load(open(f"{D}/data/parts.json")); rc = json.load(open(f"{D}/data/repair_curve.json"))
    repair_loop(rc); faces_vs_iou(P); exectime_vs_iou(P); iou_hist(P); iou_survival(P)
