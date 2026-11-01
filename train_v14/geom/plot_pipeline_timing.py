"""Full-pipeline timing figures from serve_full_timed.py records (lean 8x H200 run on serv-05):
  stage table   mean +- std / median per stage, per test set (+ throughput, IoU before / after repair)
  C             time-to-scale stage bars for three parts (fast / typical / slow)
  E             face count vs end-to-end time, both test sets; 2-3 parts called out by letter, their renders kept as
                separate images (pipeline_fig_assets.py) so they can be placed by hand
House style: bold Arial, square panel, inward ticks on all four sides, plasma + marker cycle, SVG out.

    .venv/bin/python train_v14/geom/plot_pipeline_timing.py --callouts KEY8 KEY8 KEY8 --bars KEY8 KEY8 KEY8
"""
import argparse
import json
import os

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager as fm  # noqa: E402
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter  # noqa: E402

DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
D = f"{DV}/results/figures/pipeline_timing"
SETS = [("bench_b", "Real parts (bench B)", "s"), ("fullpool_dw423", "Synthetic parts", "o")]
STAGES = [("generate", "Generate 8 candidates"), ("execute", "Execute candidates"),
          ("select", "Select starts (verifier + render-compare)"), ("repair", "Repair (3 chains × 6 rounds)"),
          ("total", "Total, drawing to part")]
ILLINI_BLUE = "#13294B"
for f in ("NimbusSans-Regular.otf", "NimbusSans-Bold.otf"):
    p = f"/usr/share/fonts/urw-base35/{f}"
    if os.path.exists(p):
        fm.fontManager.addfont(p)
plt.rcParams["font.family"] = "Nimbus Sans"; plt.rcParams["svg.fonttype"] = "none"


def load(name):
    p = f"{D}/s05_full_{name}.jsonl"
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def faces():
    f = json.load(open(f"{D}/faces_bench_b.json"))
    f.update({r["key"]: r["faces"] for r in json.load(open(f"{DV}/results/figures/results_deck/data/faces_all.json"))})
    return f


def style(ax):
    ax.tick_params(which="both", direction="in", top=True, right=True, bottom=True, left=True)
    ax.tick_params(which="major", labelsize=11)
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_fontweight("bold")


def save(fig, name):
    for ext in ("svg", "png"):
        fig.savefig(f"{D}/{name}.{ext}", format=ext, dpi=300, bbox_inches="tight")
    s = open(f"{D}/{name}.svg").read().replace("Nimbus Sans", "Arial"); open(f"{D}/{name}.svg", "w").write(s)
    plt.close(fig); print("wrote", name)


def table():
    have = [(n, lab) for n, lab, _ in SETS if load(n)]
    out = {}; md = ["| Stage | " + " | ".join(lab for _, lab in have) + " |", "|---|" + "---|" * len(have)]
    rows = {k: [] for k, _ in STAGES}
    for name, lab, _ in SETS:
        R = load(name)
        if not R:
            continue
        o = {}
        for k, _ in STAGES:
            v = np.array([r["times"][k] for r in R]); o[k] = {"mean": float(v.mean()), "std": float(v.std(ddof=1)), "median": float(np.median(v))}
            rows[k].append(f"{v.mean():.1f} ± {v.std(ddof=1):.1f}")
        t0 = min(r["t_start"] for r in R); t1 = max(r["t_end"] for r in R)
        o.update(n=len(R), parts_per_hour=len(R) / (t1 - t0) * 3600, iou_start=float(np.mean([r["iou_start"] for r in R])),
                 iou_final=float(np.mean([r["iou_final"] for r in R])))
        out[name] = o
    md += [f"| {lab} (s) | " + " | ".join(rows[k]) + " |" for k, lab in STAGES]
    md += ["| Parts | " + " | ".join(str(out[n]["n"]) for n, _, _ in SETS if n in out) + " |",
           "| Throughput (parts/hour) | " + " | ".join(f"{out[n]['parts_per_hour']:.0f}" for n, _, _ in SETS if n in out) + " |",
           "| Mean IoU, start → after repair | " + " | ".join(f"{out[n]['iou_start']:.3f} → {out[n]['iou_final']:.3f}" for n, _, _ in SETS if n in out) + " |"]
    open(f"{D}/stage_table.md", "w").write("\n".join(md) + "\n"); json.dump(out, open(f"{D}/stage_table.json", "w"), indent=1)
    print("\n".join(md))


def scatter(callouts):
    F = faces(); fig, ax = plt.subplots(figsize=(6, 6)); c = plt.cm.plasma(np.linspace(0, 0.75, 2)); allpts = {}
    for i, (name, lab, mk) in enumerate(SETS):
        R = [r for r in load(name) if r["key"] in F]
        if not R:
            continue
        x = np.array([F[r["key"]] for r in R]); y = np.array([r["times"]["total"] for r in R])
        ax.scatter(x, y, s=18, marker=mk, color=c[i], alpha=0.55, linewidths=0, label=lab)
        allpts.update({r["key"][:8]: (F[r["key"]], r["times"]["total"]) for r in R})
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(5, 500); ax.set_ylim(50, 2000)
    ax.xaxis.set_major_locator(FixedLocator([10, 100])); ax.yaxis.set_major_locator(FixedLocator([100, 1000]))
    ax.xaxis.set_minor_locator(FixedLocator([v * m for m in (1, 10, 100) for v in range(2, 10) if 5 <= v * m <= 500]))
    ax.yaxis.set_minor_locator(FixedLocator([v * m for m in (10, 100, 1000) for v in range(2, 10) if 50 <= v * m <= 2000]))
    for axis in (ax.xaxis, ax.yaxis):
        axis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}")); axis.set_minor_formatter(NullFormatter())
    for j, k8 in enumerate(callouts):
        fx, fy = allpts[k8]
        ax.scatter([fx], [fy], s=90, facecolors="none", edgecolors=ILLINI_BLUE, linewidths=1.6, zorder=4)
        ax.annotate(chr(65 + j), (fx, fy), xytext=(9, 9), textcoords="offset points", fontsize=13, fontweight="bold", color=ILLINI_BLUE)
    ax.set_xlabel("Face count", fontsize=13, fontweight="bold", labelpad=10)
    ax.set_ylabel("Drawing to part time (s)", fontsize=13, fontweight="bold", labelpad=10)
    ax.legend(loc="lower right", frameon=False, prop={"weight": "bold", "size": 11}); style(ax)
    save(fig, "faces_vs_pipeline_time")


def bars(keys):
    R = {r["key"][:8]: r for n, _, _ in SETS for r in load(n)}
    seg = [("generate", "Generate"), ("execute", "Execute"), ("select", "Select"), ("repair", "Repair")]
    col = plt.cm.plasma(np.linspace(0, 0.75, len(seg)))
    fig, ax = plt.subplots(figsize=(6, 6)); y = np.arange(len(keys))[::-1]
    for yi, k in zip(y, keys):
        left = 0.0
        for (s, lab), cc in zip(seg, col):
            w = R[k]["times"][s]
            ax.barh(yi, w, left=left, height=0.5, color=cc, edgecolor="white", linewidth=0.8, label=lab if yi == y[0] else None)
            left += w
        ax.text(left + 8, yi, f"{R[k]['times']['total']:.0f} s", va="center", fontsize=11, fontweight="bold")
    ax.set_yticks(y); ax.set_yticklabels([chr(65 + i) for i in range(len(keys))])
    xmax = max(R[k]["times"]["total"] for k in keys) * 1.2
    ax.set_xlim(0, xmax); ax.set_ylim(-0.6, len(keys) - 0.4)
    from matplotlib.ticker import MultipleLocator
    ax.xaxis.set_major_locator(MultipleLocator(200)); ax.xaxis.set_minor_locator(MultipleLocator(50))
    ax.set_xlabel("Time (s)", fontsize=13, fontweight="bold", labelpad=10)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.12), ncol=4, frameon=False, prop={"weight": "bold", "size": 11})
    style(ax); save(fig, "stage_bars")


def time_vs_iou(name="bench_b", lines=True, out="time_vs_iou"):
    """Per part: generator only (generate + execute + select, IoU of the label-free pick) and with repair (total time,
    IoU of the served program), joined by a faint line; big markers = means with SEM whiskers."""
    R = load(name); c = plt.cm.plasma(np.linspace(0, 0.75, 2))
    t0 = np.array([r["times"]["generate"] + r["times"]["execute"] + r["times"]["select"] for r in R]); i0 = np.array([r["iou_start"] for r in R])
    t1 = np.array([r["times"]["total"] for r in R]); i1 = np.array([r["iou_final"] for r in R])
    fig, ax = plt.subplots(figsize=(6, 6))
    if lines:
        for a, b, y0, y1 in zip(t0, t1, i0, i1):
            ax.plot([a, b], [y0, y1], color="#8A8F99", alpha=0.18, linewidth=0.6, zorder=1)
    ax.scatter(t0, i0, s=16, marker="o", color=c[0], alpha=0.55, linewidths=0, zorder=2, label="SFT + GRPO")
    ax.scatter(t1, i1, s=16, marker="s", color=c[1], alpha=0.55, linewidths=0, zorder=2, label="With repair")
    for (t, i), cc, mk in (((t0, i0), c[0], "o"), ((t1, i1), c[1], "s")):
        sem = i.std(ddof=1) / np.sqrt(len(i))
        ax.errorbar(np.mean(t), i.mean(), yerr=sem, fmt=mk, color=cc, markersize=11, mec="black", mew=1.2, capsize=3,
                    elinewidth=1, zorder=4)
        ax.annotate(f"{i.mean():.3f}", (np.mean(t), i.mean()), xytext=(10, 10), textcoords="offset points",
                    fontsize=11, fontweight="bold", color="black", zorder=5)
    ax.set_xscale("log"); ax.set_xlim(8, 2000); ax.set_ylim(0, 1.0)
    ax.xaxis.set_major_locator(FixedLocator([10, 100, 1000]))
    ax.xaxis.set_minor_locator(FixedLocator([v * m for m in (1, 10, 100, 1000) for v in range(2, 10) if 8 <= v * m <= 2000]))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}")); ax.xaxis.set_minor_formatter(NullFormatter())
    from matplotlib.ticker import MultipleLocator, FormatStrFormatter
    ax.yaxis.set_major_locator(MultipleLocator(0.2)); ax.yaxis.set_minor_locator(MultipleLocator(0.05))
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.1f"))
    ax.set_xlabel("Drawing to part time (s)", fontsize=13, fontweight="bold", labelpad=10)
    ax.set_ylabel("Ground-truth IoU", fontsize=13, fontweight="bold", labelpad=10)
    leg = ax.legend(loc="lower right", frameon=False, prop={"weight": "bold", "size": 11}, markerscale=2.2)
    for h in leg.legend_handles:
        h.set_alpha(1)
    style(ax)
    save(fig, out)
    print(f"generator only: {np.mean(t0):.1f} +- {np.std(t0, ddof=1):.1f} s, IoU {i0.mean():.3f}; with repair: {np.mean(t1):.1f} +- "
          f"{np.std(t1, ddof=1):.1f} s, IoU {i1.mean():.3f}")


def save_text_overlay(fig, name):
    """Chart with its text removed (<name>_notext.svg/png) plus <name>_text.json: each visible text's string, box (inches
    from the top-left of the saved image), size (pt), weight, alignment and rotation, so a PPTX can set every label as
    native Arial text (no reliance on the viewer rendering the SVG's font). Same crop as save()'s bbox_inches="tight"."""
    from matplotlib.colors import to_hex
    from matplotlib.text import Text
    fig.canvas.draw(); r = fig.canvas.get_renderer(); inch = fig.dpi_scale_trans.inverted()
    bb = fig.get_tightbbox(r).padded(0.1); items = []
    for t in fig.findobj(Text):
        if not t.get_visible() or not t.get_text().strip():
            continue
        e = t.get_window_extent(r).transformed(inch); w = t.get_fontweight()
        if e.x1 < bb.x0 or e.x0 > bb.x1 or e.y1 < bb.y0 or e.y0 > bb.y1:   # tick labels beyond the axis limits are never drawn
            continue
        w = w if isinstance(w, (int, float)) else {"bold": 700, "heavy": 800, "black": 900, "semibold": 600}.get(w, 400)
        items.append({"text": t.get_text(), "x": e.x0 - bb.x0, "y": bb.y1 - e.y1, "w": e.width, "h": e.height,
                      "size": t.get_fontsize(), "bold": w >= 600, "rot": t.get_rotation(), "ha": t.get_ha(),
                      "color": to_hex(t.get_color())[1:].upper()})
        t.set_visible(False)
    for ext in ("svg", "png"):
        fig.savefig(f"{D}/{name}_notext.{ext}", format=ext, dpi=300, bbox_inches=bb)
    json.dump({"size": [bb.width, bb.height], "texts": items}, open(f"{D}/{name}_text.json", "w"), indent=1)
    print("wrote", name + "_notext", len(items), "texts")


def repair_compare(out="repair_sft_vs_grpo"):
    """Mean IoU after each repair round (3 chains, served pick) on bench B: SFT model + repair vs GRPO model + repair."""
    from matplotlib.ticker import MultipleLocator, FormatStrFormatter
    series = [("SFT", json.load(open(f"{D}/repair_curve_bench_b_e55.json")), "o"),
              ("SFT + GRPO", json.load(open(f"{D}/repair_curve_bench_b.json")), "s")]
    # SFT = dark plasma (0.0); SFT + GRPO = black (user choice); circles vs squares keep them apart
    c = [plt.cm.plasma(0.0), "black"]; fig, ax = plt.subplots(figsize=(6, 6))
    for (lab, rc, mk), cc in zip(series, c):   # solid = 3 parallel chains (served pick), dashed = one chain
        r = np.array(rc["rounds"])
        ax.errorbar(r, rc["multistart_mean"], yerr=rc["multistart_sem"], fmt=mk + "-", color=cc, markersize=8, capsize=3,
                    elinewidth=1, linewidth=2, alpha=1.0, label=f"{lab} + repair, 3 chains")
        ax.errorbar(r, rc["chain1_mean"], yerr=rc["chain1_sem"], fmt=mk + "--", color=cc, mfc="white", mew=1.5, markersize=7,
                    capsize=3, elinewidth=1, linewidth=1.5, alpha=1.0, label=f"{lab} + repair, 1 chain")
    ax.set_xlabel("Repair round", fontsize=13, fontweight="bold", labelpad=10)
    ax.set_ylabel("Mean IoU", fontsize=13, fontweight="bold", labelpad=10)
    ax.xaxis.set_major_locator(FixedLocator(list(range(7)))); ax.yaxis.set_major_locator(MultipleLocator(0.05))
    ax.yaxis.set_minor_locator(MultipleLocator(0.01)); ax.set_xlim(-0.4, 6.4); ax.set_ylim(0.45, 0.75)
    ax.xaxis.set_major_formatter(FormatStrFormatter("%.0f")); ax.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
    ax.legend(loc="lower right", frameon=False, prop={"weight": "bold", "size": 11}); style(ax)
    for ext in ("svg", "png"):
        fig.savefig(f"{D}/{out}.{ext}", format=ext, dpi=300, bbox_inches="tight")
    s = open(f"{D}/{out}.svg").read().replace("Nimbus Sans", "Arial"); open(f"{D}/{out}.svg", "w").write(s)
    save_text_overlay(fig, out); plt.close(fig)


def gen_stages(name="bench_b", out="grpo_stage_times", path=""):
    """GRPO pipeline without repair, per stage: median with interquartile whiskers (single series, Illinois navy).
    path = a serve_full_timed.py records file to use instead of the s05 run (e.g. the bf16 render-compare-only pass)."""
    from matplotlib.ticker import MultipleLocator, FormatStrFormatter
    R = [json.loads(l) for l in open(path)] if path else load(name)
    comp = [("Generate 8 candidates", [r["times"]["generate"] for r in R]), ("Execute candidates", [r["times"]["execute"] for r in R]),
            ("Select best candidate", [r["times"]["select"] for r in R]),
            ("Total", [r["times"]["generate"] + r["times"]["execute"] + r["times"]["select"] for r in R])]
    fig, ax = plt.subplots(figsize=(6, 6)); y = np.arange(len(comp))[::-1]
    for yi, (lab, v) in zip(y, comp):
        v = np.array(v); m, lo, hi = np.median(v), np.percentile(v, 25), np.percentile(v, 75); tot = lab == "Total"
        ax.errorbar(m, yi, xerr=[[m - lo], [hi - m]], fmt="s" if tot else "o", markersize=10 if tot else 8, color=ILLINI_BLUE,
                    mfc="white" if tot else ILLINI_BLUE, mew=2, capsize=3, elinewidth=1)
        ax.text(hi + 1.0, yi, f"{m:.1f} s", va="center", fontsize=11, fontweight="bold")
    ax.axhline(0.5, color="gray", linestyle="--", alpha=0.7, linewidth=1)
    ax.set_yticks(y); ax.set_yticklabels([c[0] for c in comp]); ax.set_ylim(-0.6, len(comp) - 0.4)
    ax.xaxis.set_major_locator(MultipleLocator(10)); ax.xaxis.set_minor_locator(MultipleLocator(2)); ax.set_xlim(0, 45)
    ax.xaxis.set_major_formatter(FormatStrFormatter("%.0f"))
    ax.set_xlabel("Time per drawing (s)", fontsize=13, fontweight="bold", labelpad=10)
    style(ax); ax.tick_params(axis="y", which="both", length=0)
    save(fig, out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--callouts", nargs="*", default=[]); ap.add_argument("--bars", nargs="*", default=[])
    ap.add_argument("--stages-records", default="", help="records for the no-repair stage chart (default: s05 run)")
    ap.add_argument("--only", default="", help="run just this chart function (e.g. repair_compare)")
    a = ap.parse_args()
    if a.only:
        globals()[a.only](); raise SystemExit
    table()
    scatter(a.callouts)
    if a.bars:
        bars(a.bars)
    repair_compare(); gen_stages(path=a.stages_records)
    time_vs_iou(lines=True, out="time_vs_iou")
    time_vs_iou(lines=False, out="time_vs_iou_nolines")
