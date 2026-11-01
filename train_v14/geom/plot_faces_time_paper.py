"""Paper figure (1 column): face count vs drawing-to-part time, colour = ground-truth IoU, SFT + GRPO without repair.
Extra headroom at the top of the panel (y to --ytop) so part renders can be placed inside the axes by hand.
  faces_time_clean        the plot alone
  faces_time_annotated    same, with every callout OPTION circled and numbered (pick a few, then place their renders)
  options.json            the options: number, key, set, faces, time, IoU, why it was picked
Options span the plot: most complex parts that still come out right, the slowest parts, complex parts that are fast,
complex real parts that come out right, and complex parts that fail, and typical parts at the median time. Parts slower than --tmax (render-compare
timeouts) are left out of the plot and the options.
House style: bold Arial, square panel, inward ticks on all four sides, plasma <= 0.75 (no yellow), SVG out.

    PYTHONPATH=train_v14/geom .venv/bin/python train_v14/geom/plot_faces_time_paper.py --real R.jsonl --synth S.jsonl
"""
import argparse
import json
import os

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import Normalize  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

from plot_iou_time_faces import CMAP, F_LIM, LAB, log_axis, load  # noqa: E402
from plot_pipeline_timing import DV, style  # noqa: E402
from faces_time_figure import SYNTH, draw  # noqa: E402

O = f"{DV}/results/figures/pipeline_timing/faces_time_paper"; os.makedirs(O, exist_ok=True)


def save(fig, name):
    for ext in ("svg", "png"):
        fig.savefig(f"{O}/{name}.{ext}", format=ext, dpi=300, bbox_inches="tight")
    s = open(f"{O}/{name}.svg").read().replace("Nimbus Sans", "Arial"); open(f"{O}/{name}.svg", "w").write(s)
    plt.close(fig); print("wrote", name)


CATS = [12, 16, 8, 8, 8, 8]   # options per category, in the order below


def options(sets, tmax, cats=CATS):
    rows = [dict(key=k, set=s["label"], faces=float(f), time=float(t), iou=float(i))
            for s in sets for k, f, t, i in zip(s["keys"], s["faces"], s["time"], s["iou"]) if t <= tmax]
    picks, seen = [], set()

    def add(cands, why, n):
        for r in cands:
            if n == 0:
                break
            if r["key"] not in seen:
                seen.add(r["key"]); picks.append({**r, "why": why}); n -= 1
    add(sorted([r for r in rows if r["iou"] >= 0.85], key=lambda r: -r["faces"]), "most complex, comes out right", cats[0])
    add(sorted([r for r in rows if r["set"] == "Real parts" and r["iou"] >= 0.8], key=lambda r: -r["faces"]), "complex real part, comes out right", cats[1])
    add(sorted([r for r in rows if r["iou"] >= 0.8], key=lambda r: -r["time"]), "slow, comes out right", cats[2])
    add(sorted([r for r in rows if r["faces"] >= 60 and r["iou"] >= 0.85], key=lambda r: r["time"]), "complex but fast", cats[3])
    add(sorted([r for r in rows if r["faces"] >= 40 and r["iou"] < 0.4], key=lambda r: -r["faces"]), "complex, fails", cats[4])
    med = np.median([r["time"] for r in rows])
    typ = sorted([r for r in rows if 30 <= r["faces"] <= 60 and r["iou"] >= 0.9], key=lambda r: abs(r["time"] - med))
    add([r for r in typ if r["set"] == "Real parts"], "typical part, typical time", cats[5] // 2)
    add(typ, "typical part, typical time", cats[5] - cats[5] // 2)
    for n, p in enumerate(picks, 1):
        p["n"] = n
    return picks


def plot(sets, tmax, ytop, opts=None, name="faces_time_clean"):
    fig, ax = plt.subplots(figsize=(6, 6)); norm = Normalize(0, 1)
    for s in sets:
        o = np.argsort(-s["iou"]); f, t, i = s["faces"][o], s["time"][o], s["iou"][o]; keep = t <= tmax
        st = SYNTH["hollow_thick"] if s["label"].startswith("Synthetic") else ("o", 22, True, 0); s["style"] = st
        draw(ax, f[keep], t[keep], i[keep], norm, *st)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(*F_LIM); ax.set_ylim(10, ytop)
    log_axis(ax.xaxis, *F_LIM, [10, 100]); log_axis(ax.yaxis, 10, ytop, [10, 100, 1000])
    if opts:   # numbers spread along the empty top band (order kept in x), thin leader line down to each part
        so = sorted(opts, key=lambda p: p["faces"]); lx = np.geomspace(F_LIM[0] * 1.6, F_LIM[1] / 1.4, len(so))
        for j, (p, x) in enumerate(zip(so, lx)):
            y = ytop / (1.5, 2.8, 5.2)[j % 3]
            ax.plot([x, p["faces"]], [y / 1.08, p["time"]], color="#8A8F99", linewidth=0.6, zorder=3)
            ax.scatter([p["faces"]], [p["time"]], s=60, facecolors="none", edgecolors="black", linewidths=1.1, zorder=4)
            ax.text(x, y, str(p["n"]), ha="center", va="bottom", fontsize=10, fontweight="bold", zorder=5)
    ax.set_xlabel("Face count", **LAB); ax.set_ylabel("Drawing to part time (s)", **LAB)
    from matplotlib.cm import ScalarMappable
    cb = fig.colorbar(ScalarMappable(norm=norm, cmap=CMAP), ax=ax, fraction=0.046, pad=0.03)
    cb.set_label("Ground-truth IoU", fontsize=13, fontweight="bold", labelpad=8); cb.ax.tick_params(direction="in", labelsize=11)
    for t in cb.ax.get_yticklabels():
        t.set_fontweight("bold")
    h = [Line2D([], [], marker="o", ls="", markersize=7, label=s["label"], color="#555555",
                markerfacecolor="#555555" if s["style"][2] else "none", markeredgewidth=1.4) for s in sets]
    ax.legend(handles=h, loc="upper left", frameon=False, prop={"weight": "bold", "size": 11})
    style(ax); save(fig, name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--real", required=True); ap.add_argument("--synth", required=True)
    ap.add_argument("--tmax", type=float, default=150); ap.add_argument("--ytop", type=float, default=250)
    ap.add_argument("--out", default="", help="output dir (default faces_time_paper/)")
    a = ap.parse_args()
    global O
    if a.out:
        O = a.out; os.makedirs(O, exist_ok=True)
    sets = [load(a.synth, "Synthetic parts", "o"), load(a.real, "Real parts", "s")]
    opts = options(sets, a.tmax)
    plot(sets, a.tmax, a.ytop)   # key: taller axis so three rows of option numbers fit above the data
    plot(sets, a.tmax, max(a.ytop, 2000), opts, "faces_time_annotated")
    json.dump(opts, open(f"{O}/options.json", "w"), indent=1)
    for p in opts:
        print(f"{p['n']:2d} {p['key'][:20]:20s} {p['set'][:9]:9s} faces {p['faces']:4.0f}  {p['time']:5.1f} s  IoU {p['iou']:.2f}  {p['why']}")


if __name__ == "__main__":
    main()
