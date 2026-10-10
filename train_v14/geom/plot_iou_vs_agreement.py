"""Ground-truth IoU of the served medoid as a function of medoid agreement, one series per model
(house style: bold Arial, square panel, inward ticks on all sides, plasma x marker cycle, SVG out).

Inputs are consistency JSONs (consistency_rerank.py output: per part the GT IoU of every candidate,
exec flags and the stored pairwise-IoU matrix). For each part the medoid is the executing candidate
with the highest mean IoU to the other executing candidates; that mean is its agreement. Parts are
binned on agreement and each bin plotted at its mean agreement with mean GT IoU +- SEM.
--scatter plots every part as a point instead (one model: opaque Illinois-navy points, grey dashed y = x
reference for perfect correlation, Pearson r^2 annotated).

    .venv/bin/python train_v14/geom/plot_iou_vs_agreement.py \
        --model e24=results/bo8_full_e24_consistency_v2.json \
        --model e55=results/ext/bo8_full_e55-rft-real-u5-gt-dw423_consistency.json \
        --out results/figures/iou_vs_agreement
With no --model the deployed-lineage milestones on the synthetic test pool are plotted.

    .venv/bin/python train_v14/geom/plot_iou_vs_agreement.py --scatter \
        --model e55=results/ext/bo8_full_e55-rft-real-u5-gt-dw423_consistency.json \
        --out results/figures/iou_vs_agreement_e55_scatter
"""
import argparse
import json
import os

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager as fm  # noqa: E402
from matplotlib.ticker import FormatStrFormatter, MultipleLocator  # noqa: E402

DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
DEFAULT = [("e24", f"{DV}/results/bo8_full_e24_consistency_v2.json"),
           ("e40", f"{DV}/results/bo8_full_e40-rft-strict-all-6k_consistency.json"),
           ("e51", f"{DV}/results/bo8_full_e51-rft-real-u3-strict90_consistency.json"),
           ("e55", f"{DV}/results/ext/bo8_full_e55-rft-real-u5-gt-dw423_consistency.json")]
MARKERS = ["o", "s", "d", "^", "v"]
ILLINI_BLUE = "#13294B"

# Arial-metric font on the cluster (no Arial installed); the SVG is relabelled Arial on save
for f in ("NimbusSans-Regular.otf", "NimbusSans-Bold.otf"):
    p = f"/usr/share/fonts/urw-base35/{f}"
    if os.path.exists(p):
        fm.fontManager.addfont(p)
plt.rcParams["font.family"] = "Nimbus Sans"
plt.rcParams["svg.fonttype"] = "none"


def medoid_rows(path):
    """(agreement, GT IoU) of the medoid for every part with >= 2 executing candidates."""
    rows, skipped = [], 0
    for p in json.load(open(path))["parts"]:
        M, ex, iou = p["pair_iou"], p["exec"], p["iou"]
        idx = [i for i in range(len(iou)) if ex[i]]
        if len(idx) < 2 or M is None:
            skipped += 1
            continue
        agree = {i: np.mean([M[i][j] if M[i][j] is not None else 0.0 for j in idx if j != i]) for i in idx}
        m = max(idx, key=lambda i: agree[i])
        rows.append((agree[m], iou[m]))
    return np.array(rows), skipped


def binned(a, edges, min_n):
    out = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        s = a[(a[:, 0] >= lo) & (a[:, 0] < hi)]
        if len(s) >= min_n:
            out.append((s[:, 0].mean(), s[:, 1].mean(), s[:, 1].std(ddof=1) / np.sqrt(len(s)), len(s)))
    return np.array(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", action="append", default=[], help="label=consistency.json (repeat per model)")
    ap.add_argument("--out", default=f"{DV}/results/figures/iou_vs_agreement", help="output path without extension")
    ap.add_argument("--edges", default="0,0.5,0.6,0.7,0.75,0.8,0.85,0.9,0.95,0.98,1.0001",
                    help="agreement bin edges")
    ap.add_argument("--min-n", type=int, default=5, help="drop bins with fewer parts")
    ap.add_argument("--xlim"); ap.add_argument("--ylim")   # defaults: 0.3-1.0 (binned) / 0.1-1.0 (scatter)
    ap.add_argument("--scatter", action="store_true", help="one point per part instead of binned means")
    ap.add_argument("--alpha", type=float, default=0.5, help="scatter point opacity")
    ap.add_argument("--diagonal", action="store_true", help="grey dashed y = x reference")
    a = ap.parse_args()
    models = [tuple(m.split("=", 1)) for m in a.model] or DEFAULT
    edges = [float(x) for x in a.edges.split(",")]
    colors = (plt.cm.plasma(np.linspace(0, 0.75, len(models))) if len(models) > 1
              else [ILLINI_BLUE] if a.scatter else ["black"])

    fig, ax = plt.subplots(figsize=(6, 6))
    if a.diagonal or a.scatter:   # perfect correlation: agreement equals ground-truth IoU
        ax.plot([0, 1], [0, 1], color="gray", linestyle="--", alpha=0.7, linewidth=1.2, zorder=1)
    # scatter: every e55 part has agreement >= 0.25 and IoU >= 0.19; offset origins keep corner labels apart
    a.xlim = a.xlim or ("0.1,1.0" if a.scatter else "0.3,1.0")   # scatter: equal x/y limits so y = x is the true diagonal
    a.ylim = a.ylim or ("0.1,1.0" if a.scatter else "0.3,1.0")
    for i, ((label, path), col) in enumerate(zip(models, colors)):
        rows, skipped = medoid_rows(path)
        b = binned(rows, edges, a.min_n)
        if a.scatter:
            r2 = np.corrcoef(rows[:, 0], rows[:, 1])[0, 1] ** 2
            rmse = np.sqrt(np.mean((rows[:, 1] - rows[:, 0]) ** 2))
            ax.scatter(rows[:, 0], rows[:, 1], s=18, marker=MARKERS[i % len(MARKERS)], color=col, alpha=a.alpha,
                       linewidths=0, zorder=2,
                       label=f"{label} (r² = {r2:.2f})" if len(models) > 1 else None)
            if len(models) == 1:
                ax.text(0.96, 0.05, f"r² = {r2:.2f}\nRMSE = {rmse:.3f}", transform=ax.transAxes, ha="right", va="bottom",
                        fontsize=13, fontweight="bold")
        else:
            ax.errorbar(b[:, 0], b[:, 1], yerr=b[:, 2], fmt=MARKERS[i % len(MARKERS)] + "-", color=col, markersize=7,
                        capsize=3, elinewidth=1, linewidth=1.2, alpha=1.0, label=label)
        rho = np.corrcoef(np.argsort(np.argsort(rows[:, 0])), np.argsort(np.argsort(rows[:, 1])))[0, 1]
        r = np.corrcoef(rows[:, 0], rows[:, 1])[0, 1]
        ss_diag = 1 - ((rows[:, 1] - rows[:, 0]) ** 2).sum() / ((rows[:, 1] - rows[:, 1].mean()) ** 2).sum()
        print(f"{label}: n={len(rows)} (skipped {skipped} with <2 executing)  medoid IoU {rows[:, 1].mean():.3f}  "
              f"pearson r {r:.3f}  r^2 {r * r:.3f}  R^2 about y=x {ss_diag:.3f}  spearman {rho:.3f}  "
              f"RMSE(IoU - agreement) {np.sqrt(np.mean((rows[:, 1] - rows[:, 0]) ** 2)):.4f}  "
              f"mean(IoU - agreement) {np.mean(rows[:, 1] - rows[:, 0]):+.4f}")
        for x, y, e, n in b:
            print(f"    agree {x:.3f}  IoU {y:.3f} +- {e:.3f}  n={int(n)}")

    ax.set_xlabel("Medoid agreement", fontsize=13, fontweight="bold", labelpad=10)
    ax.set_ylabel("Ground-truth IoU", fontsize=13, fontweight="bold", labelpad=10)
    # order: locators -> limits -> formatters -> label styling
    major = 0.2 if a.scatter else 0.1
    ax.xaxis.set_major_locator(MultipleLocator(major)); ax.yaxis.set_major_locator(MultipleLocator(major))
    ax.xaxis.set_minor_locator(MultipleLocator(0.05)); ax.yaxis.set_minor_locator(MultipleLocator(0.05))
    ax.set_xlim(*[float(x) for x in a.xlim.split(",")]); ax.set_ylim(*[float(x) for x in a.ylim.split(",")])
    ax.xaxis.set_major_formatter(FormatStrFormatter("%.1f")); ax.yaxis.set_major_formatter(FormatStrFormatter("%.1f"))
    ax.tick_params(which="both", direction="in", top=True, right=True, bottom=True, left=True)
    ax.tick_params(which="major", labelsize=11)
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_fontweight("bold")
    if len(models) > 1:
        ax.legend(loc="lower right", frameon=False, prop={"weight": "bold", "size": 11})

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    fig.savefig(a.out + ".svg", format="svg", dpi=300, bbox_inches="tight")
    fig.savefig(a.out + ".png", format="png", dpi=300, bbox_inches="tight")
    s = open(a.out + ".svg").read().replace("Nimbus Sans", "Arial"); open(a.out + ".svg", "w").write(s)
    print("wrote", a.out + ".{svg,png}")


if __name__ == "__main__":
    main()
