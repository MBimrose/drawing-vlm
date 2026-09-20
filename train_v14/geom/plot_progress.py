"""House-style figure: out-of-distribution (real-part) IoU across the fine-tune series.

Every point is the same held-out bench — 146 real engineering drawings (Fusion 360 + ABC parts,
never synthetic) scored by exact centered volumetric IoU at K=8 — so the runs are directly
comparable. Numbers are parsed from `results/ext/bo8_ext_<run>_summary.txt`, the analyze_ext
output of each run's best-of-8 pass.

Style: King Lab publication guide — Arial (Nimbus Sans where Arial is absent), 13pt bold axis
labels with labelpad=10, 11pt bold ticks, inward ticks on all four sides with minor ticks
unlabeled, plasma(0 -> 0.8) crossed with the o/s/d/^ marker cycle, frameless bold legend, limits
cropped to the performance band, SVG out.

    python plot_progress.py [--out results/figures/ood_progress.svg]
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
from matplotlib.ticker import FormatStrFormatter, MultipleLocator

BENCH_GLOB = "results/ext/bo8_ext_e*_summary.txt"
# Serving-policy variants re-evaluate an existing checkpoint rather than adding a trained model.
VARIANTS = {"e55v4", "e55vb55"}


def load_runs(root: str) -> list[dict]:
    rows = []
    for f in sorted(glob.glob(os.path.join(root, BENCH_GLOB))):
        m = re.match(r"bo8_ext_(e(\d+)[a-z0-9-]*)_summary\.txt", os.path.basename(f))
        if not m or m.group(1) in VARIANTS:
            continue
        txt = open(f).read()
        if "usage: analyze_ext" in txt:          # a couple of early runs never got a clean summary
            continue
        hdr = re.search(r"^slice.*$", txt, re.M)
        ext = re.search(r"^ALL external\s+(\d+) \|(.*)$", txt, re.M)
        if not hdr or not ext:
            continue
        cols = [c.strip() for c in hdr.group(0).split("|")[1:] if c.strip()]
        vals = [float(v) for v, _ in re.findall(r"([\d.]+) /\s*(\d+)%", ext.group(2))]
        d = dict(zip(cols, vals))
        rows.append({"run": m.group(1), "e": int(m.group(2)), "n": int(ext.group(1)), **d})
    return sorted(rows, key=lambda r: r["e"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm")
    ap.add_argument("--out", default="results/figures/ood_progress.svg")
    ap.add_argument("--noise", type=float, default=0.02, help="documented single-run noise (+-)")
    a = ap.parse_args()

    rows = load_runs(a.root)
    if not rows:
        raise SystemExit("no run summaries found")
    x = np.array([r["e"] for r in rows], float)

    # Arial per the house style; Nimbus Sans is the metric-compatible stand-in on this host.
    installed = {f.name for f in matplotlib.font_manager.fontManager.ttflist}
    family = next((f for f in ("Arial", "Helvetica", "Nimbus Sans", "DejaVu Sans") if f in installed), "sans-serif")
    plt.rcParams.update({"font.family": family, "font.weight": "bold", "svg.fonttype": "none",
                         "axes.unicode_minus": False})

    series = [("first_exec", "Greedy first draw"),
              ("consistency", "Best-of-8, agreement vote"),
              ("gated", "Served policy (vote + verifier gate)"),
              ("oracle", "Best-of-8 ceiling (oracle)")]
    colors = plt.cm.plasma(np.linspace(0, 0.8, len(series)))
    markers = ["o", "s", "d", "^"]

    fig, ax = plt.subplots(figsize=(6, 6))
    for (key, label), c, mk in zip(series, colors, markers):
        y = np.array([r.get(key, np.nan) for r in rows], float)
        ok = ~np.isnan(y)
        ax.errorbar(x[ok], y[ok], yerr=a.noise, fmt=mk + "-", color=c, markersize=6,
                    linewidth=1.6, capsize=3, elinewidth=1, alpha=1.0,
                    markeredgecolor="black", markeredgewidth=0.4, label=label)

    ax.set_xlabel("Fine-tune experiment", fontsize=13, fontweight="bold", labelpad=10)
    ax.set_ylabel("Mean volumetric IoU, 146 held-out real parts", fontsize=13,
                  fontweight="bold", labelpad=10)

    # locators -> limits -> formatters -> label styling (the order the notebooks rely on)
    ax.xaxis.set_major_locator(MultipleLocator(2)); ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(0.05)); ax.yaxis.set_minor_locator(MultipleLocator(0.01))
    ax.set_xlim(x.min() - 0.6, x.max() + 0.6)
    ax.set_ylim(0.40, 0.63)
    ax.xaxis.set_major_formatter(FormatStrFormatter("%.0f"))
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
    ax.tick_params(which="both", direction="in", top=True, right=True, labelsize=11)
    ax.tick_params(which="major", length=6, width=1.1)
    ax.tick_params(which="minor", length=3, width=0.8)
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_fontweight("bold")
    for s in ax.spines.values():
        s.set_linewidth(1.1)

    ax.legend(fontsize=11, frameon=False, loc="upper left", handlelength=2.2,
              prop={"weight": "bold", "size": 11})

    out = os.path.join(a.root, a.out) if not os.path.isabs(a.out) else a.out
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, format="svg", dpi=300, bbox_inches="tight")
    fig.savefig(out.replace(".svg", ".png"), format="png", dpi=200, bbox_inches="tight")
    print(f"[plot] font={family}  runs={len(rows)} ({rows[0]['run']} -> {rows[-1]['run']})")
    for r in rows:
        print(f"   {r['run']:30s} first {r.get('first_exec', float('nan')):.3f}  "
              f"vote {r.get('consistency', float('nan')):.3f}  "
              f"gated {r.get('gated', float('nan')):.3f}  oracle {r.get('oracle', float('nan')):.3f}")
    print(f"[plot] wrote {out}")


if __name__ == "__main__":
    main()
