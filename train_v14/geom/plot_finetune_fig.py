"""Figure 3 (fine tuning) chart: real-part IoU after each fine-tuning stage on held-out bench B (280 parts, frozen
2026-10-09, never used for checkpoint selection). House style (bold Arial, square panel, inward ticks on all four
sides, plasma + marker cycle, SVG out).

Numbers = GRPO_HANDOFF.md "Bench B + baselines" table (eval_table.py over results/bench_b/eval/*_consistency.json):
  stage        checkpoint          vote   best-of-8  draw-0
  Base         Qwen3.8-27B, no FT  0.082  0.092      0.017
  SFT          e55ctl              0.509  0.595      0.402
  GRPO         ent_t10 s120        0.640  0.696      0.625
  Round 1      rft1_rl2 s120       0.651  0.708      0.628
  Round 2      rft2_rl s60         0.665  0.732      0.625
    .venv/bin/python train_v14/geom/plot_finetune_fig.py
"""
import os

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager as fm  # noqa: E402
from matplotlib.ticker import FixedLocator, FormatStrFormatter, MultipleLocator, NullFormatter  # noqa: E402

OUT = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/figures/fine_tuning"
for f in ("NimbusSans-Regular.otf", "NimbusSans-Bold.otf"):
    p = f"/usr/share/fonts/urw-base35/{f}"
    if os.path.exists(p):
        fm.fontManager.addfont(p)
plt.rcParams["font.family"] = "Nimbus Sans"; plt.rcParams["svg.fonttype"] = "none"

STAGES = ["SFT", "GRPO", "Round 1", "Round 2"]
SERIES = [("Best of 8", [0.595, 0.696, 0.708, 0.732]),
          ("Medoid vote", [0.509, 0.640, 0.651, 0.665]),
          ("Single draw", [0.402, 0.625, 0.628, 0.625])]
MARKERS = ["o", "s", "d"]


def main():
    os.makedirs(OUT, exist_ok=True)
    fig, ax = plt.subplots(figsize=(5, 5))
    x = np.arange(len(STAGES)); c = plt.cm.plasma(np.linspace(0, 0.75, len(SERIES)))
    for i, (label, y) in enumerate(SERIES):
        ax.plot(x, y, marker=MARKERS[i], color=c[i], linewidth=2, markersize=8, label=label)
    ax.set_xlabel("Training stage", fontsize=13, fontweight="bold", labelpad=10)
    ax.set_ylabel("Mean IoU, held-out real parts", fontsize=13, fontweight="bold", labelpad=10)
    ax.xaxis.set_major_locator(FixedLocator(list(x))); ax.yaxis.set_major_locator(MultipleLocator(0.1))
    ax.yaxis.set_minor_locator(MultipleLocator(0.05)); ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_xlim(-0.35, len(STAGES) - 0.65); ax.set_ylim(0.35, 0.8)
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.1f"))
    ax.set_xticklabels(STAGES)
    ax.tick_params(which="both", direction="in", top=True, right=True, bottom=True, left=True)
    ax.tick_params(which="major", labelsize=11)
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_fontweight("bold")
    ax.legend(loc="lower right", frameon=False, prop={"weight": "bold", "size": 11})
    for ext in ("svg", "png"):
        fig.savefig(f"{OUT}/finetune_progress.{ext}", format=ext, dpi=300, bbox_inches="tight")
    s = open(f"{OUT}/finetune_progress.svg").read().replace("Nimbus Sans", "Arial")
    open(f"{OUT}/finetune_progress.svg", "w").write(s)
    print("wrote", f"{OUT}/finetune_progress.svg")


if __name__ == "__main__":
    main()
