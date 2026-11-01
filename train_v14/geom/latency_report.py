"""Latency study report (serv-20 run, latency_run_s20.sh): per-stage time table (mean +- std, median) for one candidate
and for the full served system, and the face-count vs generation-time scatter (synthetic pool), house style.

    .venv/bin/python train_v14/geom/latency_report.py --dir results/figures/latency
Inputs in --dir: s20_single_synth.json, s20_single_benchb.json (latency_one_candidate.py), s20_full_benchb.jsonl
(serve_full_timed.py); face counts from results/figures/results_deck/data/faces_all.json (GT B-rep, synthetic pool).
Writes latency_table.md, latency_table.json, faces_vs_gentime.{svg,png}.
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
ILLINI_BLUE = "#13294B"
for f in ("NimbusSans-Regular.otf", "NimbusSans-Bold.otf"):
    p = f"/usr/share/fonts/urw-base35/{f}"
    if os.path.exists(p):
        fm.fontManager.addfont(p)
plt.rcParams["font.family"] = "Nimbus Sans"; plt.rcParams["svg.fonttype"] = "none"


def stat(v):
    v = np.asarray([x for x in v if x is not None], float)
    return {"mean": float(v.mean()), "std": float(v.std(ddof=1)), "median": float(np.median(v)), "n": int(len(v))}


def spearman(x, y):
    return float(np.corrcoef(np.argsort(np.argsort(x)), np.argsort(np.argsort(y)))[0, 1])


def log_axis(ax, which, lo, hi, majors):
    axis = ax.xaxis if which == "x" else ax.yaxis
    axis.set_major_locator(FixedLocator([m for m in majors if lo <= m <= hi]))
    axis.set_minor_locator(FixedLocator([v * m for m in (0.1, 1, 10, 100) for v in range(2, 10) if lo <= v * m <= hi]))
    axis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}")); axis.set_minor_formatter(NullFormatter())


# outlier key prefix -> inset centre (face count, seconds) in data coordinates
OUTLIERS = {"6cc1618e": (10, 20), "882a0afc": (55, 20), "553502dc": (300, 20),
            "36989f0a": (18, 0.42), "500542c2": (85, 0.42), "7be9bb16": (340, 0.42)}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dir", default=f"{DV}/results/figures/latency"); a = ap.parse_args()
    D = a.dir
    single = json.load(open(f"{D}/s20_single_benchb.json")); S = single["rows"]
    full = [json.loads(l) for l in open(f"{D}/s20_full_benchb.jsonl")]
    rows = [
        ("One candidate (n={})".format(len(S)), None),
        ("Read drawing", stat([r["read"] for r in S])),
        ("Plan (reasoning tokens)", stat([r["plan"] for r in S])),
        ("Write code", stat([r["code"] for r in S])),
        ("Run program", stat([r["run"] for r in S])),
        ("Total, one candidate", stat([r["gen_total"] + (r["run"] or 0) for r in S])),
        ("Full served system (n={})".format(len(full)), None),
        ("Generate 16 candidates", stat([r["times"]["generate"] for r in full])),
        ("Execute 16 candidates", stat([r["times"]["execute"] for r in full])),
        ("Select (render-compare + verifier)", stat([r["times"]["select"] for r in full])),
        ("Repair (3 chains x 6 rounds)", stat([r["times"]["repair"] for r in full])),
        ("Total, full system", stat([r["times"]["total"] for r in full])),
    ]
    md = ["| Stage | Mean ± std (s) | Median (s) |", "|---|---|---|"]
    for name, s in rows:
        md.append(f"| **{name}** | | |" if s is None else f"| {name} | {s['mean']:.2f} ± {s['std']:.2f} | {s['median']:.2f} |")
    tok = {"plan_tokens": stat([r["plan_tokens"] for r in S]), "code_tokens": stat([r["code_tokens"] for r in S]),
           "tok_s": stat([(r["plan_tokens"] + r["code_tokens"]) / max(r["plan"] + r["code"], 1e-9) for r in S]),
           "import": single["import_sec"]}
    acc = {"iou_start": float(np.mean([r["iou_start"] for r in full])), "iou_final": float(np.mean([r["iou_final"] for r in full])),
           "round": stat([t for r in full for ch in r["round_times"] for t in ch])}
    open(f"{D}/latency_table.md", "w").write("\n".join(md) + "\n")
    json.dump({"rows": [[n, s] for n, s in rows], "tokens": tok, "full": acc}, open(f"{D}/latency_table.json", "w"), indent=1)
    print("\n".join(md)); print(json.dumps(tok)); print(json.dumps(acc))

    # face count vs generation time (synthetic pool, one candidate)
    syn = json.load(open(f"{D}/s20_single_synth.json"))["rows"]
    faces = {r["key"]: r["faces"] for r in json.load(open(f"{DV}/results/figures/results_deck/data/faces_all.json"))}
    pts = [(faces[r["key"]], r["gen_total"]) for r in syn if r["key"] in faces]
    x = np.array([p[0] for p in pts]); y = np.array([p[1] for p in pts])
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(x, y, s=18, color=ILLINI_BLUE, alpha=0.5, linewidths=0)
    ax.set_xscale("log"); ax.set_yscale("log")
    ylo, yhi = 0.15, 45   # points fall in ~0.9-10 s; the margins hold the part renders
    ax.set_xlim(5, 500); ax.set_ylim(ylo, yhi)
    log_axis(ax, "x", 5, 500, [10, 100]); log_axis(ax, "y", ylo, yhi, [1, 10])
    ax.set_xlim(5, 700)
    ax.set_xlabel("Face count", fontsize=13, fontweight="bold", labelpad=10)
    ax.set_ylabel("Generation time (s)", fontsize=13, fontweight="bold", labelpad=10)
    ax.tick_params(which="both", direction="in", top=True, right=True, bottom=True, left=True)
    ax.tick_params(which="major", labelsize=11)
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_fontweight("bold")
    # rendered ground-truth parts for outlying points (render_outliers.py -> outlier_renders/<key8>.png)
    from matplotlib.offsetbox import AnnotationBbox, OffsetImage
    from PIL import Image
    gen = {r["key"][:8]: (faces[r["key"]], r["gen_total"]) for r in syn if r["key"] in faces}
    for k8, (ix, iy) in OUTLIERS.items():
        fx, fy = gen[k8]
        ax.scatter([fx], [fy], s=70, facecolors="none", edgecolors=ILLINI_BLUE, linewidths=1.5, zorder=4)
        im = Image.open(f"{D}/outlier_renders/{k8}.png"); im.thumbnail((300, 220))
        canvas = Image.new("RGBA", (300, 220), (255, 255, 255, 0))      # fixed box size for every inset
        canvas.paste(im, ((300 - im.width) // 2, (220 - im.height) // 2), im)
        ab = AnnotationBbox(OffsetImage(np.asarray(canvas), zoom=0.26), (fx, fy), xybox=(ix, iy), xycoords="data", boxcoords="data",
                            frameon=True, bboxprops=dict(edgecolor="#8A8F99", linewidth=0.75, boxstyle="round,pad=0.15"),
                            arrowprops=dict(arrowstyle="-", color="#8A8F99", linewidth=0.9), zorder=5)
        ax.add_artist(ab)
        up = iy > 3   # label outside the box: above the top row, below the bottom row
        ax.annotate(f"{fx} faces · {fy:.1f} s", (ix, iy), xytext=(0, 40 if up else -40), textcoords="offset points",
                    ha="center", va="center", fontsize=9.5, fontweight="bold", color=ILLINI_BLUE, zorder=6)
    for ext in ("svg", "png"):
        fig.savefig(f"{D}/faces_vs_gentime.{ext}", format=ext, dpi=300, bbox_inches="tight")
    s = open(f"{D}/faces_vs_gentime.svg").read().replace("Nimbus Sans", "Arial"); open(f"{D}/faces_vs_gentime.svg", "w").write(s)
    print(f"scatter: n={len(x)} spearman {spearman(x, y):.2f} median gen {np.median(y):.2f}s")


if __name__ == "__main__":
    main()
