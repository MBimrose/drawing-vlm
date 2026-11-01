"""End-to-end latency of one candidate (drawing -> part) by component, from latency_one_candidate.py output.
House style: bold Arial, square panel, inward ticks on all four sides, single series = points + interquartile
whiskers in Illinois navy (no bars: bar length is not proportional to time on a log axis), SVG out. Log time axis so the sub-second steps stay visible next to token generation.

    .venv/bin/python train_v14/geom/plot_latency.py results/figures/latency/latency_rft2_rl_s60.json
"""
import json
import os
import sys

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager as fm  # noqa: E402
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter  # noqa: E402

ILLINI_BLUE = "#13294B"
for f in ("NimbusSans-Regular.otf", "NimbusSans-Bold.otf"):
    p = f"/usr/share/fonts/urw-base35/{f}"
    if os.path.exists(p):
        fm.fontManager.addfont(p)
plt.rcParams["font.family"] = "Nimbus Sans"; plt.rcParams["svg.fonttype"] = "none"


def main(path):
    d = json.load(open(path)); R = d["rows"]; out = os.path.splitext(path)[0]
    pt0 = int(np.median([r["plan_tokens"] for r in R]) + 0.5); ct0 = int(np.median([r["code_tokens"] for r in R]) + 0.5)
    comp = [("Read drawing", [r["read"] for r in R]),
            (f"Plan ({pt0} tokens)", [r["plan"] for r in R]),
            (f"Write code ({ct0} tokens)", [r["code"] for r in R]),
            ("Run program", [r["run"] for r in R if r["run"] is not None]),
            ("Total", [r["gen_total"] + (r["run"] or 0) for r in R])]
    fig, ax = plt.subplots(figsize=(6, 6))
    y = np.arange(len(comp))[::-1]
    for yi, (label, v) in zip(y, comp):
        v = np.array(v); med, lo, hi = np.median(v), np.percentile(v, 25), np.percentile(v, 75)
        total = label == "Total"
        ax.errorbar(med, yi, xerr=[[med - lo], [hi - med]], fmt="s" if total else "o", markersize=10 if total else 8,
                    color=ILLINI_BLUE, mfc="white" if total else ILLINI_BLUE, mew=2, capsize=3, elinewidth=1, alpha=1.0)
        ax.text(hi * 1.25, yi, f"{med:.2f} s", va="center", fontsize=11, fontweight="bold")
    ax.axhline(0.5, color="gray", linestyle="--", alpha=0.7, linewidth=1)
    ax.set_yticks(y); ax.set_yticklabels([c[0] for c in comp])
    ax.set_xscale("log"); ax.set_xlim(0.01, 30)
    ax.xaxis.set_major_locator(FixedLocator([0.01, 0.1, 1, 10]))
    ax.xaxis.set_minor_locator(FixedLocator([v * m for m in (0.01, 0.1, 1, 10) for v in range(2, 10) if v * m <= 30]))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}")); ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_ylim(-0.6, len(comp) - 0.4)
    ax.set_xlabel("Time per candidate (s)", fontsize=13, fontweight="bold", labelpad=10)
    ax.tick_params(axis="x", which="both", direction="in", top=True, bottom=True)
    ax.tick_params(axis="y", which="both", direction="in", left=True, right=True, length=0)
    ax.tick_params(which="major", labelsize=11)
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_fontweight("bold")
    for ext in ("svg", "png"):
        fig.savefig(f"{out}.{ext}", format=ext, dpi=300, bbox_inches="tight")
    s = open(f"{out}.svg").read().replace("Nimbus Sans", "Arial"); open(f"{out}.svg", "w").write(s)
    pt = np.array([r["plan_tokens"] for r in R]); ct = np.array([r["code_tokens"] for r in R])
    dec = np.array([(r["plan_tokens"] + r["code_tokens"]) / max(r["plan"] + r["code"], 1e-9) for r in R])
    print(f"n={len(R)}  import (one-off) {d['import_sec']:.2f}s  prompt tokens {np.median([r['prompt_tokens'] for r in R]):.0f}")
    for label, v in comp:
        v = np.array(v); print(f"  {label:18s} median {np.median(v):7.3f}s  IQR {np.percentile(v, 25):.3f}-{np.percentile(v, 75):.3f}  mean {v.mean():.3f}")
    print(f"  plan tokens median {np.median(pt):.0f}, code tokens median {np.median(ct):.0f}, decode {np.median(dec):.0f} tok/s; "
          f"executes {np.mean([r['executes'] for r in R]):.0%}")


if __name__ == "__main__":
    main(sys.argv[1])
