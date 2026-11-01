"""IoU vs drawing-to-part time vs face count, SFT + GRPO pipeline WITHOUT repair (generate 8 -> execute -> select),
four versions of the same three variables:
  v1  face count vs IoU, colour = time
  v2  time vs IoU, colour = face count
  v3  face count vs time, colour = IoU
  v4  binned by face count: median time (IQR) on top, mean IoU (SEM) below, shared x
Time per part = generate + execute + select from serve_full_timed.py records; IoU = ground-truth IoU of the served pick.
House style: bold Arial, square panels, inward ticks on all four sides, plasma <= 0.75 (no yellow), SVG out.

    .venv/bin/python train_v14/geom/plot_iou_time_faces.py [--real results/figures/pipeline_timing/s05_full_bench_b.jsonl]
"""
import argparse
import json
import os

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import ListedColormap, LogNorm, Normalize  # noqa: E402
from matplotlib.ticker import FixedLocator, FormatStrFormatter, FuncFormatter, MultipleLocator, NullFormatter  # noqa: E402

from plot_pipeline_timing import DV, faces, style  # noqa: E402

D = f"{DV}/results/figures/pipeline_timing"; O = f"{D}/iou_time_faces"; os.makedirs(O, exist_ok=True)
CMAP = ListedColormap(plt.cm.plasma(np.linspace(0, 0.75, 256)))
LAB = dict(fontsize=13, fontweight="bold", labelpad=10)
T_LIM, F_LIM = (10, 500), (5, 500)


def save(fig, name):
    for ext in ("svg", "png"):
        fig.savefig(f"{O}/{name}.{ext}", format=ext, dpi=300, bbox_inches="tight")
    s = open(f"{O}/{name}.svg").read().replace("Nimbus Sans", "Arial"); open(f"{O}/{name}.svg", "w").write(s)
    plt.close(fig); print("wrote", name)


def load(path, label, marker):
    F = faces(); R = [json.loads(l) for l in open(path)]
    R = [r for r in R if r["key"] in F and r.get("iou_start") is not None]
    return {"label": label, "marker": marker, "keys": [r["key"] for r in R], "faces": np.array([F[r["key"]] for r in R], float),
            "time": np.array([r["times"]["generate"] + r["times"]["execute"] + r["times"]["select"] for r in R]),
            "iou": np.array([r["iou_start"] for r in R])}


def log_axis(axis, lo, hi, majors):
    axis.set_major_locator(FixedLocator(majors))
    axis.set_minor_locator(FixedLocator([v * m for m in (1, 10, 100, 1000) for v in range(2, 10) if lo <= v * m <= hi]))
    axis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}")); axis.set_minor_formatter(NullFormatter())


def iou_axis(axis):
    axis.set_major_locator(MultipleLocator(0.2)); axis.set_minor_locator(MultipleLocator(0.05))
    axis.set_major_formatter(FormatStrFormatter("%.1f"))


def colour_scatter(sets, x, y, c, norm, clabel, name, xlog, ylog):
    fig, ax = plt.subplots(figsize=(6, 6))
    for s in sets:   # draw low-IoU / high-time points last so the rare colours sit on top
        o = np.argsort(-s[c] if c == "iou" else s[c]); s = {**s, **{k: s[k][o] for k in ("faces", "time", "iou")}}
        sc = ax.scatter(s[x], s[y], c=s[c], cmap=CMAP, norm=norm, s=22, marker=s["marker"], alpha=0.8, linewidths=0, label=s["label"])
    lims = {"faces": F_LIM, "time": T_LIM, "iou": (0, 1.02)}
    names = {"faces": "Face count", "time": "Drawing to part time (s)", "iou": "Ground-truth IoU"}
    for axis, v, lg in ((ax.xaxis, x, xlog), (ax.yaxis, y, ylog)):
        (ax.set_xscale if axis is ax.xaxis else ax.set_yscale)("log" if lg else "linear")
        (ax.set_xlim if axis is ax.xaxis else ax.set_ylim)(*lims[v])
        if v == "iou":
            iou_axis(axis)
        else:
            log_axis(axis, *lims[v], [10, 100] if v == "faces" else [10, 100])
    ax.set_xlabel(names[x], **LAB); ax.set_ylabel(names[y], **LAB)
    cb = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.03)
    cb.set_label(clabel, fontsize=13, fontweight="bold", labelpad=8); cb.ax.tick_params(direction="in", labelsize=11)
    if norm.vmax == 60:
        cb.ax.yaxis.set_major_locator(MultipleLocator(15)); cb.ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}" + ("+" if v == 60 else "")))
    if isinstance(norm, LogNorm):
        cb.ax.yaxis.set_major_locator(FixedLocator([10, 100])); cb.ax.yaxis.set_minor_locator(FixedLocator([20, 50, 200]))
        cb.ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}")); cb.ax.yaxis.set_minor_formatter(NullFormatter())
    for t in cb.ax.get_yticklabels():
        t.set_fontweight("bold")
    if len(sets) > 1:   # marker shape = test set; grey handles so the legend does not imply a colour
        from matplotlib.lines import Line2D
        h = [Line2D([], [], marker=s["marker"], ls="", color="#555555", markersize=7, label=s["label"]) for s in sets]
        ax.legend(handles=h, loc="upper left" if y == "time" else "lower left", frameon=False, prop={"weight": "bold", "size": 11})
    style(ax); save(fig, name)


def v3_callouts(sets, callouts, name, tmax=150):
    """Version 3 for the paper: face count vs time (log-log), colour = IoU; parts slower than tmax are left out (render
    timeouts; printed, and listed in the slide notes), called-out parts circled and lettered (renders: render_callouts.py)."""
    fig, ax = plt.subplots(figsize=(6, 6)); norm = Normalize(0, 1); pos = {}
    for s in sets:
        o = np.argsort(-s["iou"]); f, t, i = s["faces"][o], s["time"][o], s["iou"][o]; k = [s["keys"][j] for j in o]; keep = t <= tmax
        sc = ax.scatter(f[keep], t[keep], c=i[keep], cmap=CMAP, norm=norm, s=22, marker=s["marker"], alpha=0.8, linewidths=0)
        pos.update({kk: (fx, tx) for kk, fx, tx, kp in zip(k, f, t, keep) if kp})
        if (~keep).any():
            print(f"  {s['label']}: left out {(~keep).sum()} parts above {tmax:g} s: {np.round(t[~keep]).tolist()}")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(*F_LIM); ax.set_ylim(10, tmax)
    log_axis(ax.xaxis, *F_LIM, [10, 100]); log_axis(ax.yaxis, 10, tmax, [10, 100])
    for j, k8 in enumerate(callouts):
        fx, fy = pos[next(kk for kk in pos if kk.startswith(k8))]
        ax.scatter([fx], [fy], s=110, facecolors="none", edgecolors="black", linewidths=1.6, zorder=4, clip_on=False)
        ax.annotate(chr(65 + j), (fx, fy), xytext=(-22, -5) if fy > tmax / 1.3 else (-16, 4), textcoords="offset points", fontsize=13, fontweight="bold", zorder=5)
    ax.set_xlabel("Face count", **LAB); ax.set_ylabel("Drawing to part time (s)", **LAB)
    cb = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.03)
    cb.set_label("Ground-truth IoU", fontsize=13, fontweight="bold", labelpad=8); cb.ax.tick_params(direction="in", labelsize=11)
    for t in cb.ax.get_yticklabels():
        t.set_fontweight("bold")
    if len(sets) > 1:
        from matplotlib.lines import Line2D
        h = [Line2D([], [], marker=s["marker"], ls="", color="#555555", markersize=7, label=s["label"]) for s in sets]
        ax.legend(handles=h, loc="lower right", frameon=False, prop={"weight": "bold", "size": 11})
    style(ax); save(fig, name)
    F = {k: (fx, t, i) for s in sets for k, fx, t, i in zip(s["keys"], s["faces"], s["time"], s["iou"])}
    json.dump([{"letter": chr(65 + j), "key": k, "faces": int(F[k][0]), "time": float(F[k][1]), "iou": float(F[k][2])}
               for j, c8 in enumerate(callouts) for k in [next(x for x in F if x.startswith(c8))]], open(f"{O}/callouts.json", "w"), indent=1)


def binned(sets, name, nb=5):
    """Shared face-count bins (quantiles of the pooled face counts) so both sets sit on the same x positions."""
    allf = np.concatenate([s["faces"] for s in sets]); edges = np.unique(np.quantile(allf, np.linspace(0, 1, nb + 1)))
    edges[-1] += 1; cols = [plt.cm.plasma(0.0), plt.cm.plasma(0.6)]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6, 9), sharex=True, gridspec_kw={"hspace": 0.06})
    for s, cc in zip(sets, cols):
        xs, tm, tlo, thi, im, ise = [], [], [], [], [], []
        for lo, hi in zip(edges[:-1], edges[1:]):
            m = (s["faces"] >= lo) & (s["faces"] < hi)
            if m.sum() < 5:
                continue
            xs.append(np.sqrt(lo * (hi - 1))); t = s["time"][m]; i = s["iou"][m]
            tm.append(np.median(t)); tlo.append(np.percentile(t, 25)); thi.append(np.percentile(t, 75))
            im.append(i.mean()); ise.append(i.std(ddof=1) / np.sqrt(m.sum()))
        xs, tm, tlo, thi = map(np.array, (xs, tm, tlo, thi))
        a1.errorbar(xs, tm, yerr=[tm - tlo, thi - tm], fmt=s["marker"] + "-", color=cc, markersize=8, capsize=3, linewidth=2,
                    elinewidth=1, label=s["label"])
        a2.errorbar(xs, im, yerr=ise, fmt=s["marker"] + "-", color=cc, markersize=8, capsize=3, linewidth=2, elinewidth=1)
    for e in edges[1:-1]:
        for a in (a1, a2):
            a.axvline(e, color="gray", linestyle="--", alpha=0.35, linewidth=0.8)
    a2.set_xscale("log"); a2.set_xlim(*F_LIM); log_axis(a2.xaxis, *F_LIM, [10, 100])
    a1.set_ylim(0, 60); a1.yaxis.set_major_locator(MultipleLocator(20)); a1.yaxis.set_minor_locator(MultipleLocator(5))
    a1.yaxis.set_major_formatter(FormatStrFormatter("%.0f"))
    a2.set_ylim(0, 1.0); iou_axis(a2.yaxis)
    a1.set_ylabel("Drawing to part time (s)", **LAB); a2.set_ylabel("Mean IoU", **LAB); a2.set_xlabel("Face count", **LAB)
    a1.legend(loc="upper left", frameon=False, prop={"weight": "bold", "size": 11})
    style(a1); style(a2); save(fig, name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--real", default=f"{D}/s05_full_bench_b.jsonl"); ap.add_argument("--synth", default=f"{D}/s05_full_fullpool_dw423.jsonl")
    ap.add_argument("--callouts", nargs="*", default=[]); ap.add_argument("--tmax", type=float, default=150)
    a = ap.parse_args()
    real = load(a.real, "Real parts", "s"); syn = load(a.synth, "Synthetic parts", "o"); both = [syn, real]
    for s in both:
        print(f"{s['label']}: n={len(s['iou'])}  time {np.median(s['time']):.1f} s median [{s['time'].min():.1f}, {s['time'].max():.1f}]"
              f"  faces [{s['faces'].min():.0f}, {s['faces'].max():.0f}]  IoU {s['iou'].mean():.3f}")
    tn = Normalize(15, 60); fn = LogNorm(*F_LIM); inorm = Normalize(0, 1)
    for tag, sets in (("", both), ("_real", [real])):
        colour_scatter(sets, "faces", "iou", "time", tn, "Drawing to part time (s)", f"v1_faces_iou_by_time{tag}", True, False)
        colour_scatter(sets, "time", "iou", "faces", fn, "Face count", f"v2_time_iou_by_faces{tag}", True, False)
        colour_scatter(sets, "faces", "time", "iou", inorm, "Ground-truth IoU", f"v3_faces_time_by_iou{tag}", True, True)
    v3_callouts(both, a.callouts, "v3_faces_time_by_iou_callouts", a.tmax)
    binned(both, "v4_binned_by_faces")
    binned([real], "v4_binned_by_faces_real")


if __name__ == "__main__":
    main()
