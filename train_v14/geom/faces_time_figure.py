"""1-column figure: face count vs drawing-to-part time (colour = IoU) with lettered callouts whose drawing ISO view and
SFT + GRPO pick sit in the empty top band. Writes the clean chart on a FIXED layout (no tight bbox) so data points map
to known positions on the image, plus the overlay assets; build_faces_time_figure.js then places every overlay as an
editable PPTX object (circles, letters, images) on top of the chart.
  faces_time_paper/figure/{chart.svg, chart.png, iso_<L>.png, pick_<L>.png, manifest.json}
Renders: render_callouts.py output in faces_time_paper/renders/<key>/{drawing,pick}.png.

    PYTHONPATH=train_v14/geom .venv/bin/python train_v14/geom/faces_time_figure.py --real R.jsonl --synth S.jsonl \
        --keys 47adc310 533abec2 938a49c0 A_00435481
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
from PIL import Image  # noqa: E402
from scipy import ndimage as nd  # noqa: E402

from plot_iou_time_faces import CMAP, F_LIM, LAB, load, log_axis  # noqa: E402
from plot_pipeline_timing import DV, style  # noqa: E402

B = f"{DV}/results/figures/pipeline_timing/faces_time_paper"; O = f"{B}/figure"; os.makedirs(O, exist_ok=True)
FIG = (6.0, 6.0); AX = [0.14, 0.11, 0.64, 0.86]; CB = [0.81, 0.11, 0.035, 0.86]   # figure fractions, fixed


def iso_box(png):
    """Bounding box of the drawing's ISO view: of the separate views on the sheet, the one whose edges run most along the
    isometric +-30 deg directions (orthographic views are nearly all horizontal / vertical), +0.1 if an 'ISO VIEW (NTS)'-
    shaped caption sits just above or below it (round, toothed parts give orthographic views diagonal edges too).
    Right on all 44 bench sheets checked (21 Oct)."""
    gray = np.asarray(Image.open(png).convert("L")).astype(float); ink = gray < 200
    gx, gy = nd.sobel(gray, 1), nd.sobel(gray, 0); ang = np.degrees(np.arctan2(gy, gx)) % 180
    edge = np.hypot(gx, gy) > 200; diag = edge & ((np.abs(ang - 60) < 8) | (np.abs(ang - 120) < 8))
    caps = []   # caption-shaped text blobs at two dilation scales (the caption shrinks with the sheet scale)
    for it in (12, 6):
        for sl in nd.find_objects(nd.label(nd.binary_dilation(ink, iterations=it))[0]):
            w, h = sl[1].stop - sl[1].start, sl[0].stop - sl[0].start
            if (it == 12 and 150 <= w <= 240 and 35 <= h <= 55) or (it == 6 and 15 <= h <= 60 and 3.5 <= w / h <= 6 and w < 240):
                caps.append((sl[1].start, sl[0].start, sl[1].stop, sl[0].stop))
    lab, _ = nd.label(nd.binary_dilation(ink, iterations=8)); best = None
    for n, sl in enumerate(nd.find_objects(lab), 1):
        b = (sl[1].start, sl[0].start, sl[1].stop, sl[0].stop)
        if (b[2] - b[0]) * (b[3] - b[1]) < 20000:
            continue
        m = lab[sl] == n; e = (edge[sl] & m).sum()
        if e < 300:
            continue
        cap = any((0 <= c[1] - b[3] <= 70 or 0 <= b[1] - c[3] <= 70) and b[0] <= (c[0] + c[2]) / 2 <= b[2] for c in caps)
        f = (diag[sl] & m).sum() / e + (0.1 if cap else 0.0)
        if best is None or f > best[0]:
            best = (f, b)
    if best is None:
        return None
    # keep only the view itself inside the box (drops a caption that the dilation merged in)
    x0, y0, x1, y1 = best[1]
    sub = nd.binary_dilation(ink[y0:y1, x0:x1], iterations=4); sl2, _ = nd.label(sub)
    sizes = nd.sum(sub, sl2, range(1, sl2.max() + 1)); keep = nd.find_objects((sl2 == 1 + int(np.argmax(sizes))).astype(int))[0]
    return (x0 + keep[1].start, y0 + keep[0].start, x0 + keep[1].stop, y0 + keep[0].stop)


# synthetic-part marker styles (real parts are filled markers, drawn on top); (marker, size, filled, line width)
SYNTH = {"filled": ("o", 22, True, 0), "hollow": ("o", 26, False, 0.9), "hollow_thick": ("o", 26, False, 1.4),
         "hollow_small": ("o", 14, False, 0.7), "dot": ("o", 7, True, 0), "plus": ("+", 30, False, 0.9), "cross": ("x", 20, False, 0.9),
         "hollow_tri": ("^", 26, False, 0.9)}


def draw(ax, f, t, i, norm, marker, size, filled, lw, alpha=None, zorder=None):
    col = CMAP(norm(i))
    if filled:
        return ax.scatter(f, t, c=col, s=size, marker=marker, alpha=alpha or 0.8, linewidths=0, zorder=zorder)
    if marker in ("+", "x"):
        return ax.scatter(f, t, c=col, s=size, marker=marker, alpha=alpha or 0.85, linewidths=lw)
    return ax.scatter(f, t, facecolors="none", edgecolors=col, s=size, marker=marker, alpha=alpha or 0.9, linewidths=lw, zorder=zorder)


def quartile_means(ax, f, t, filled, edges, sem=True):
    """Mean time per face-count quartile (pooled edges shared by both sets; x = median face count of the set's parts in
    that quartile), SEM whiskers, drawn over the points: real = solid line + filled black circles, synthetic = dashed + open."""
    xs, ys, es = [], [], []
    for q in range(len(edges) - 1):
        m = (f >= edges[q]) & ((f < edges[q + 1]) if q < len(edges) - 2 else (f <= edges[q + 1]))
        xs.append(np.median(f[m])); ys.append(t[m].mean()); es.append(t[m].std(ddof=1) / np.sqrt(m.sum()))
    ax.errorbar(xs, ys, yerr=es if sem else None, fmt="o-" if filled else "o--", color="black", mfc="black" if filled else "white", mec="black",
                mew=1.6, markersize=8, linewidth=1.8, capsize=3, elinewidth=1.2, zorder=6)
    return list(zip(xs, ys, es))


def quartile_guides(ax, edges, ytop, mode):
    """Shared quartile boundaries, kept below the render band (y <= ytop): faint dotted dividers or alternating light
    bands, with Q1-Q4 labels along their top."""
    lo, hi = ax.get_xlim()
    b = [lo] + list(edges[1:-1]) + [hi]
    for q in range(4):
        if mode == "bands" and q % 2 == 1:
            ax.fill_between([b[q], b[q + 1]], 10, ytop, color="#EEF0F3", lw=0, zorder=-1)
        if mode == "lines" and q > 0:
            ax.plot([b[q]] * 2, [10, ytop], color="#9AA0A8", lw=1.0, ls=(0, (2, 2)), zorder=-1)
        ax.text(np.sqrt(b[q] * b[q + 1]), ytop * 0.97, f"Q{q + 1}", ha="center", va="top", fontsize=11, fontweight="bold",
                color="#6B7280", zorder=1)


def transparent(im):
    a = np.asarray(im.convert("RGBA")).copy(); a[a[..., :3].min(-1) > 245, 3] = 0
    im = Image.fromarray(a); return im.crop(im.getbbox())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--real", required=True); ap.add_argument("--synth", required=True); ap.add_argument("--keys", nargs="+", required=True)
    ap.add_argument("--tmax", type=float, default=150); ap.add_argument("--ytop", type=float, default=250)
    ap.add_argument("--renders", default=f"{B}/renders", help="render_callouts.py output dir (use the --iso renders)")
    ap.add_argument("--synth-style", choices=sorted(SYNTH), default="hollow_thick")
    ap.add_argument("--real-marker", default="o", help="real parts: filled marker (o = solid circle, s = square)")
    ap.add_argument("--chart-only", default="", help="write only the chart to this path stem (marker variants)")
    ap.add_argument("--leader", nargs="*", default=[], help="callout letters whose label sits off the point on a leader line")
    ap.add_argument("--alpha", type=float, default=0.6, help="point opacity (the quartile means are drawn opaque on top)")
    ap.add_argument("--no-quartiles", action="store_true")
    ap.add_argument("--qedges", choices=["pooled", "per-set"], default="per-set", help="quartiles of all parts, or of each set (equal n per point)")
    ap.add_argument("--sem", action="store_true", help="SEM whiskers on the quartile means")
    ap.add_argument("--qguide", choices=["lines", "bands", "none"], default="bands", help="how the shared quartile boundaries are marked")
    a = ap.parse_args()
    sets = [load(a.synth, "Synthetic parts", "o"), load(a.real, "Real parts", "s")]
    fig = plt.figure(figsize=FIG); ax = fig.add_axes(AX); cax = fig.add_axes(CB); norm = Normalize(0, 1); pts = {}; shown_xy = []
    for s in sets:
        o = np.argsort(-s["iou"]); f, t, i = s["faces"][o], s["time"][o], s["iou"][o]; keep = t <= a.tmax
        st = SYNTH[a.synth_style] if s["label"].startswith("Synthetic") else (a.real_marker, 22, True, 0)
        draw(ax, f[keep], t[keep], i[keep], norm, *st, alpha=a.alpha); s["style"] = st
        pts.update({k: (float(fx), float(tx), float(ix)) for k, fx, tx, ix in zip(s["keys"], s["faces"], s["time"], s["iou"])})
        shown_xy += list(zip(f[keep], t[keep]))
    qpts = []
    if not a.no_quartiles:
        allf = np.concatenate([s["faces"][s["time"] <= a.tmax] for s in sets]); edges = np.quantile(allf, np.linspace(0, 1, 5))
        print("pooled quartile edges:", np.round(edges, 1))
        for s in sets:
            keep = s["time"] <= a.tmax
            se = edges if a.qedges == "pooled" else np.quantile(s["faces"][keep], np.linspace(0, 1, 5))
            q = quartile_means(ax, s["faces"][keep], s["time"][keep], s["style"][2], se, sem=a.sem); qpts += [(x, y) for x, y, _ in q]
            print(f"{s['label']} quartile means: " + ", ".join(f"{x:.0f} faces {y:.1f}±{e:.1f} s" for x, y, e in q))
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(*F_LIM); ax.set_ylim(10, a.ytop)
    for s in sets:   # called-out points redrawn opaque above the quartile-mean lines, so a leader can end on a visible point
        for k8 in a.keys:
            j = [n for n, k in enumerate(s["keys"]) if k.startswith(k8)]
            if j:
                draw(ax, s["faces"][j], s["time"][j], s["iou"][j], norm, *s["style"], alpha=1.0, zorder=7)
    log_axis(ax.xaxis, *F_LIM, [10, 100]); log_axis(ax.yaxis, 10, a.ytop, [10, 100, 1000])
    if not a.no_quartiles and a.qguide != "none" and a.qedges == "pooled":
        quartile_guides(ax, edges, max(float(s["time"][s["time"] <= a.tmax].max()) for s in sets) * 1.12, a.qguide)
    ax.set_xlabel("Face count", **LAB); ax.set_ylabel("Drawing to part time (s)", **LAB)
    from matplotlib.cm import ScalarMappable
    cb = fig.colorbar(ScalarMappable(norm=norm, cmap=CMAP), cax=cax); cb.set_label("Ground-truth IoU", fontsize=13, fontweight="bold", labelpad=8)
    cb.ax.tick_params(direction="in", labelsize=11)
    for t in cb.ax.get_yticklabels():
        t.set_fontweight("bold")
    h = [Line2D([], [], marker=s["style"][0], ls="", markersize=7 if s["style"][1] > 10 else 4, label=s["label"],
                color="#555555", markerfacecolor="#555555" if s["style"][2] else "none", markeredgewidth=max(s["style"][3], 1))
         for s in sets]
    if not a.no_quartiles:   # one entry per set: its point marker + its quartile-mean line (the caption explains the lines)
        from matplotlib.legend_handler import HandlerTuple
        ln = [Line2D([], [], color="black", ls="-" if s["style"][2] else "--", marker="o", markersize=6, mew=1.4, mec="black",
                     mfc="black" if s["style"][2] else "white") for s in sets]
        ax.legend(handles=[(a_, b_) for a_, b_ in zip(h, ln)], labels=[s["label"] for s in sets], handler_map={tuple: HandlerTuple(ndivide=None, pad=0.6)},
                  handlelength=4.2, loc="lower right", frameon=False, prop={"weight": "bold", "size": 11}); style(ax)
    else:
        ax.legend(handles=h, loc="lower right", frameon=False, prop={"weight": "bold", "size": 11}); style(ax)
    if a.chart_only:
        fig.savefig(a.chart_only + ".png", dpi=200); plt.close(fig); return
    for ext in ("svg", "png"):   # no bbox_inches: the image IS the figure, so the fractions below hold exactly
        fig.savefig(f"{O}/chart.{ext}", format=ext, dpi=300)
    s = open(f"{O}/chart.svg").read().replace("Nimbus Sans", "Arial"); open(f"{O}/chart.svg", "w").write(s)
    W, H = fig.get_size_inches() * fig.dpi
    to_frac = lambda x, y: (lambda p: (p[0] / W, 1 - p[1] / H))(ax.transData.transform((x, y)))
    shown = max(float(s["time"][s["time"] <= a.tmax].max()) for s in sets)
    band = to_frac(F_LIM[0], a.ytop)[1], to_frac(F_LIM[0], shown * 1.12)[1]   # empty band above the highest point (top, bottom)
    man = {"fig_in": list(FIG), "axes": [AX[0], 1 - AX[1] - AX[3], AX[2], AX[3]], "band": list(band), "callouts": []}
    P = np.array([to_frac(x, y) for x, y in shown_xy]) * FIG   # every shown point, inches from the top-left
    if qpts:   # quartile-mean markers and the lines between them count as heavy obstacles (10 copies each)
        Q = np.array([to_frac(x, y) for x, y in qpts]) * FIG
        dense = np.concatenate([np.linspace(Q[j], Q[j + 1], 8) for j in range(len(Q) - 1) if j != len(qpts) // 2 - 1])
        P = np.concatenate([P] + [dense] * 10)
    cpts = [np.array(to_frac(*pts[next(x for x in pts if x.startswith(k8))][:2])) * FIG for k8 in a.keys]
    ax_l, ax_t = AX[0] * FIG[0], (1 - AX[1] - AX[3]) * FIG[1]; ax_r, ax_b = ax_l + AX[2] * FIG[0], ax_t + AX[3] * FIG[1]

    def leader_spot(p0):
        """Emptiest label position 0.45-0.9 in from the point (prefers up-left), below the panel band, clear of the
        legend (lower right) and of the other callouts."""
        best = None
        for r in (0.45, 0.6, 0.75, 0.9, 1.1):
            for deg in range(0, 360, 15):
                q = p0 + r * np.array([np.cos(np.radians(deg)), -np.sin(np.radians(deg))])
                if not (ax_l + 0.2 < q[0] < ax_r - 0.2 and band[1] * FIG[1] + 0.15 < q[1] < ax_b - 0.2) or (q[0] > ax_r - 1.9 and q[1] > ax_b - 0.7):
                    continue
                if min(np.hypot(*(q - c)) for c in cpts) < 0.3:
                    continue
                seg = np.linspace(p0, q, 12)[2:]   # points crowding the line count too, at half weight
                score = (np.hypot(*(P - q).T) < 0.14).sum() + 0.5 * sum((np.hypot(*(P - g).T) < 0.05).sum() for g in seg) + 2 * r
                if best is None or score < best[0]:
                    best = (score, q)
        return best[1] if best is not None else p0 + np.array([-0.5, -0.5])
    for j, k8 in enumerate(a.keys):
        k = next(x for x in pts if x.startswith(k8)); L = chr(65 + j); d = f"{a.renders}/{k}"
        box = iso_box(f"{d}/drawing.png"); dr = Image.open(f"{d}/drawing.png")
        iso = transparent(dr.crop(box) if box else dr); iso.save(f"{O}/iso_{L}.png")
        pk = transparent(Image.open(f"{d}/pick.png")); pk.save(f"{O}/pick_{L}.png")
        fx, fy = to_frac(pts[k][0], pts[k][1])
        man["callouts"].append({"letter": L, "key": k, "faces": pts[k][0], "time": pts[k][1], "iou": pts[k][2], "pt": [fx, fy],
                                "iso": list(iso.size), "pick": list(pk.size), "iso_found": bool(box)})
        if L in a.leader:
            q = leader_spot(np.array([fx, fy]) * FIG); man["callouts"][-1]["label_pt"] = [float(q[0] / FIG[0]), float(q[1] / FIG[1])]
        print(f"{L} {k[:22]}  faces {pts[k][0]:.0f}  {pts[k][1]:.0f} s  IoU {pts[k][2]:.2f}  iso view {'found' if box else 'NOT found (whole sheet)'}")
    json.dump(man, open(f"{O}/manifest.json", "w"), indent=1); plt.close(fig)


if __name__ == "__main__":
    main()
