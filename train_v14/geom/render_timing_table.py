"""Paper timing table rendered as an image (SVG + PNG) in the style of the main results table: bold first column, bold
two-line header, navy rule under the header, thin grey rules between rows, no vertical lines, numbers centred.
Same rows as results/figures/pipeline_timing/build_timing_table.js (editable PPTX version).

    .venv/bin/python train_v14/geom/render_timing_table.py   -> results/figures/pipeline_timing/timing_table.{svg,png}
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager as fm  # noqa: E402

D = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/figures/pipeline_timing"
for f in ("NimbusSans-Regular.otf", "NimbusSans-Bold.otf"):
    p = f"/usr/share/fonts/urw-base35/{f}"
    if os.path.exists(p):
        fm.fontManager.addfont(p)
plt.rcParams["font.family"] = "Nimbus Sans"; plt.rcParams["svg.fonttype"] = "none"

HEAD = ["Stage", "Description", "Synthetic Test\nTime (s)", "Real Test\nTime (s)"]
ROWS = [("Generate", "8 candidates (1 greedy + 7 sampled)", "10.7 ± 2.3", "9.9 ± 2.9", False),
        ("Execute", "Run each program (build123d)", "3.2 ± 0.8", "3.2 ± 0.5", False),
        ("Select", "Render each candidate, pick best render-compare", "11.9 ± 21.4", "8.9 ± 4.8", False),
        ("Total", "Drawing to part", "25.9 ± 22.0", "22.0 ± 6.4", True),
        ("Visual Repair", "Optional: 3 chains × 6 rounds", "", "+267.9 ± 142.9", False),
        ("Total with Visual Repair", "Drawing to repaired part", "", "294.3 ± 145.2", False)]
X = [0.01, 0.30, 0.735, 0.895]          # column anchors (fraction of width); last two are centres
W, HH, RH = 12.5, 0.72, 0.5             # inches: width, header height, row height


def main():
    H = HH + RH * len(ROWS); fig = plt.figure(figsize=(W, H)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(H, 0)
    ax.axis("off"); fs = 14
    for j, h in enumerate(HEAD):
        ax.text(X[j], HH / 2, h, ha="left" if j < 2 else "center", va="center", fontsize=fs, fontweight="bold", linespacing=1.15)
    ax.plot([0, 1], [HH, HH], color="#13294B", linewidth=2.2, solid_capstyle="butt")
    for i, (a, b, c, d, bold) in enumerate(ROWS):
        y = HH + RH * (i + 0.5)
        ax.text(X[0], y, a, ha="left", va="center", fontsize=fs, fontweight="bold")
        ax.text(X[1], y, b, ha="left", va="center", fontsize=fs)
        for x, v in ((X[2], c), (X[3], d)):
            ax.text(x, y, v, ha="center", va="center", fontsize=fs, fontweight="bold" if bold else "normal")
        ax.plot([0, 1], [HH + RH * (i + 1)] * 2, color="#D3D6DB", linewidth=0.9)
    for ext in ("svg", "png"):
        fig.savefig(f"{D}/timing_table.{ext}", format=ext, dpi=200)
    s = open(f"{D}/timing_table.svg").read().replace("Nimbus Sans", "Arial"); open(f"{D}/timing_table.svg", "w").write(s)
    print("wrote timing_table.svg/png")


if __name__ == "__main__":
    main()
