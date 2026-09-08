"""Agreement-vs-ground-truth scatter (house style: Arial bold, square panel, inward ticks, plasma). Inputs agree_*.json from the consistency JSONs (see RECIPE); run from a dir with fonts/LiberationSans-*.ttf or Arial installed."""
import json, numpy as np, matplotlib
from matplotlib import font_manager as _fm
import glob as _g
for _f in _g.glob("fonts/*.ttf"): _fm.fontManager.addfont(_f)
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
plt.rcParams["font.family"] = "Liberation Sans"   # Arial-metric; renamed to Arial in the SVG below
plt.rcParams["svg.fonttype"] = "none"             # keep text editable
series = [("Synthetic test pool (n=1,019)", "agree_in-dist.json", "o"),
          ("Real parts, held out (n=145)", "agree_real.json", "s")]
cmap = plt.cm.plasma(np.linspace(0, 0.8, len(series)))
fig, ax = plt.subplots(figsize=(6, 6))
for (label, path, mk), col in zip(series, cmap):
    r = [x for x in json.load(open(path)) if x["iou_vote"] is not None]
    x = np.array([v["iou_vote"] for v in r]); y = np.array([v["agree"] for v in r])
    ax.scatter(x, y, marker=mk, s=18, color=col, edgecolors="black", linewidths=0.25, alpha=0.85, label=label)
ax.axhline(0.85, color="gray", linestyle="--", alpha=0.7, linewidth=1.2, label="Agreement gate (0.85)")
ax.set_xlabel("Ground-truth IoU of served candidate", fontsize=13, labelpad=10, fontweight="bold")
ax.set_ylabel("Medoid agreement (mean pairwise IoU)", fontsize=13, labelpad=10, fontweight="bold")
ax.tick_params(top=True, right=True, direction="in", which="both")
ax.tick_params(axis="x", which="minor", direction="in", top=True, bottom=True, labelbottom=False)
ax.tick_params(axis="y", which="minor", direction="in", right=True, left=True, labelleft=False)
ax.xaxis.set_major_locator(MultipleLocator(0.2)); ax.yaxis.set_major_locator(MultipleLocator(0.2))
ax.xaxis.set_minor_locator(MultipleLocator(0.05)); ax.yaxis.set_minor_locator(MultipleLocator(0.05))
ax.set_xlim([0, 1.0]); ax.set_ylim([0, 1.0])
ax.xaxis.set_major_formatter(FormatStrFormatter("%.1f")); ax.yaxis.set_major_formatter(FormatStrFormatter("%.1f"))
ax.tick_params(axis="both", which="major", labelsize=11)
for lab in ax.get_xticklabels() + ax.get_yticklabels(): lab.set_fontweight("bold")
leg = ax.legend(loc="lower right", frameon=False, fontsize=11, prop={"weight": "bold", "size": 11})
fig.savefig("agreement_vs_iou.svg", format="svg", dpi=300, bbox_inches="tight")
fig.savefig("agreement_vs_iou.png", format="png", dpi=300, bbox_inches="tight")
s = open("agreement_vs_iou.svg").read().replace("Liberation Sans", "Arial"); open("agreement_vs_iou.svg", "w").write(s)
# numbers for the caption
for label, path, _ in series:
    r = [x for x in json.load(open(path)) if x["iou_vote"] is not None]
    x = np.array([v["iou_vote"] for v in r]); y = np.array([v["agree"] for v in r])
    print(label, "spearman %.3f" % (np.corrcoef(np.argsort(np.argsort(x)), np.argsort(np.argsort(y)))[0,1]),
          "gate>=0.85: %d/%d (%.0f%%), mean IoU above gate %.3f below %.3f" % ((y>=0.85).sum(), len(y), 100*(y>=0.85).mean(), x[y>=0.85].mean(), x[y<0.85].mean()))
