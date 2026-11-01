"""Full-pipeline latency on the 8x H200 deployment (serv-05, run_full_s05.sh): per-stage time table (mean +- std,
median) per test set, throughput, and the face count vs end-to-end time scatter over the whole test sets, with 2-3
called-out parts marked A/B/C in the plot and their renders written as separate images (for the slide).

    .venv/bin/python train_v14/geom/latency_full_report.py --dir results/figures/latency_s05 --callouts KEY8 KEY8 KEY8
Inputs in --dir: s05_full_bench_b.jsonl, s05_full_fullpool_dw423.jsonl (serve_full_timed.py), faces_bench_b.json
(count_faces_dir.py); synthetic face counts from results/figures/results_deck/data/faces_all.json.
"""
import argparse
import json
import os
import string

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager as fm  # noqa: E402
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter  # noqa: E402

DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
for f in ("NimbusSans-Regular.otf", "NimbusSans-Bold.otf"):
    p = f"/usr/share/fonts/urw-base35/{f}"
    if os.path.exists(p):
        fm.fontManager.addfont(p)
plt.rcParams["font.family"] = "Nimbus Sans"; plt.rcParams["svg.fonttype"] = "none"
STAGES = [("generate", "Generate 8 candidates"), ("execute", "Execute candidates"),
          ("select", "Select (render-compare + verifier)"), ("repair", "Repair (3 chains x 6 rounds)"), ("total", "Total")]
SETS = [("fullpool_dw423", "Synthetic test set"), ("bench_b", "Real held-out (bench B)")]


def load(D):
    faces = {r["key"]: r["faces"] for r in json.load(open(f"{DV}/results/figures/results_deck/data/faces_all.json"))}
    faces.update(json.load(open(f"{D}/faces_bench_b.json")))
    data = {}
    for s, _ in SETS:
        f = f"{D}/s05_full_{s}.jsonl"
        if os.path.exists(f):
            data[s] = [json.loads(l) for l in open(f)]
    return data, faces


def table(data):
    md = ["| Stage | " + " | ".join(f"{lab} (n={len(data[s])})" for s, lab in SETS if s in data) + " |",
          "|---|" + "---|" * len([s for s, _ in SETS if s in data])]
    out = {}
    for st, lab in STAGES:
        cells = []
        for s, _ in SETS:
            if s not in data:
                continue
            v = np.array([r["times"][st] for r in data[s]]); out.setdefault(s, {})[st] = (float(v.mean()), float(v.std(ddof=1)), float(np.median(v)))
            cells.append(f"{v.mean():.1f} ± {v.std(ddof=1):.1f} (median {np.median(v):.1f})")
        md.append(f"| {'**' + lab + '**' if st == 'total' else lab} | " + " | ".join(cells) + " |")
    for s, lab in SETS:
        if s in data:
            R = data[s]; span = (max(r["t_end"] for r in R) - min(r["t_start"] for r in R)) / 3600
            out[s]["throughput_parts_per_h"] = len(R) / span if span > 0 else None
            out[s]["iou_start"] = float(np.mean([r["iou_start"] for r in R])); out[s]["iou_final"] = float(np.mean([r["iou_final"] for r in R]))
    return "\n".join(md), out


def scatter(data, faces, D, callouts):
    fig, ax = plt.subplots(figsize=(6, 6)); col = plt.cm.plasma(np.linspace(0, 0.75, 2)); mk = ["o", "s"]
    allpts = {}
    for i, (s, lab) in enumerate(SETS):
        if s not in data:
            continue
        pts = [(faces[r["key"]], r["times"]["total"], r["key"]) for r in data[s] if faces.get(r["key"])]
        for p in pts:
            allpts[p[2][:8]] = p
        ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=18, marker=mk[i], color=col[i], alpha=0.5, linewidths=0, label=lab)
    t = [p[1] for p in allpts.values()]
    ylo, yhi = 10 ** np.floor(np.log10(min(t))), 10 ** np.ceil(np.log10(max(t)))
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(5, 500); ax.set_ylim(ylo, yhi)
    for axis, lo, hi, maj in ((ax.xaxis, 5, 500, [10, 100]), (ax.yaxis, ylo, yhi, [1, 10, 100, 1000])):
        axis.set_major_locator(FixedLocator([m for m in maj if lo <= m <= hi]))
        axis.set_minor_locator(FixedLocator([v * m for m in (1, 10, 100) for v in range(2, 10) if lo <= v * m <= hi]))
        axis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}")); axis.set_minor_formatter(NullFormatter())
    for letter, k8 in zip(string.ascii_uppercase, callouts):
        fx, fy, _ = allpts[k8]
        ax.scatter([fx], [fy], s=90, facecolors="none", edgecolors="black", linewidths=1.6, zorder=4)
        ax.annotate(letter, (fx, fy), xytext=(9, 7), textcoords="offset points", fontsize=13, fontweight="bold", zorder=5)
    ax.set_xlabel("Face count", fontsize=13, fontweight="bold", labelpad=10)
    ax.set_ylabel("End-to-end time per part (s)", fontsize=13, fontweight="bold", labelpad=10)
    ax.tick_params(which="both", direction="in", top=True, right=True, bottom=True, left=True)
    ax.tick_params(which="major", labelsize=11)
    for tl in ax.get_xticklabels() + ax.get_yticklabels():
        tl.set_fontweight("bold")
    ax.legend(loc="lower right", frameon=False, prop={"weight": "bold", "size": 11})
    for ext in ("svg", "png"):
        fig.savefig(f"{D}/faces_vs_e2e.{ext}", format=ext, dpi=300, bbox_inches="tight")
    s = open(f"{D}/faces_vs_e2e.svg").read().replace("Nimbus Sans", "Arial"); open(f"{D}/faces_vs_e2e.svg", "w").write(s)
    return {letter: allpts[k8] for letter, k8 in zip(string.ascii_uppercase, callouts)}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dir", required=True); ap.add_argument("--callouts", nargs="*", default=[])
    a = ap.parse_args()
    data, faces = load(a.dir)
    md, stats = table(data)
    open(f"{a.dir}/timing_table.md", "w").write(md + "\n"); json.dump(stats, open(f"{a.dir}/timing_stats.json", "w"), indent=1)
    print(md); print(json.dumps({s: {k: v for k, v in d.items() if not isinstance(v, tuple)} for s, d in stats.items()}))
    co = scatter(data, faces, a.dir, a.callouts)
    json.dump({k: {"faces": v[0], "seconds": v[1], "key": v[2]} for k, v in co.items()}, open(f"{a.dir}/callouts.json", "w"), indent=1)
    print("callouts", {k: (v[0], round(v[1], 1)) for k, v in co.items()})


if __name__ == "__main__":
    main()
