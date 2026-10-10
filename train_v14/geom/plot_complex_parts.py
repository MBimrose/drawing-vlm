"""Slide figures for the most complex in-distribution test parts the deployed
generator (e55, best-of-8 + medoid vote) solves:

  contact_sheet   6 parts: input drawing, GT solid, served (medoid) generation
  hero_<key>      drawing | GT | generation | signed deviation map
  agreement_<key> 8-candidate pairwise-IoU heatmap, GT IoU on the diagonal, medoid boxed

Assets: complex_parts_assets.py -> complex_parts_render.py (compute node) -> this (cheap).
    .venv/bin/python train_v14/geom/plot_complex_parts.py
"""
import json
import os

import matplotlib
import numpy as np
from PIL import Image

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager as fm  # noqa: E402
from matplotlib.colors import Normalize  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

for f in ("NimbusSans-Regular.otf", "NimbusSans-Bold.otf"):
    p = f"/usr/share/fonts/urw-base35/{f}"
    if os.path.exists(p):
        fm.fontManager.addfont(p)
plt.rcParams["font.family"] = "Nimbus Sans"; plt.rcParams["svg.fonttype"] = "none"

OUT = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/figures/complex_parts"
P = f"{OUT}/parts"
NAVY, GREY = "#13294B", "#5a5f69"
NAMES = {  # short labels for the contact sheets, from the GT solids
    "6989952c": "Double-flanged spool",
    "1fbfa3c8": "Flanged hub",
    "9ca41004": "Slotted shaft on mounting plate",
    "390dc972": "Flanged bushing",
    "40a1be28": "Flared pedestal mount",
    "2a127616": "Splined hub on shaft",
    "475993e4": "Lofted hopper with rib and boss",
    "232ebd96": "L-arm with bored boss",
    "a2f71172": "Bolted hub housing",
    "0264f04e": "Stepped tower with flange",
    "8f00d7de": "Cone-tipped spike on plate",
    "27676dd6": "Grooved spool sleeve",
    "27b61d00": "Slotted cage sleeve",
    "14378534": "Finger collet tube",
    "a32fd1f6": "Cone boss on plate",
    "87e6177a": "Flanged cylinder",
    "07832ef6": "Disc head on pin",
    "525053d2": "Flange disc with keyed bore",
    "6f62d896": "Perforated disc",
    "500542c2": "Toothed ring",
    "769781ca": "Stepped cylinder cap",
    "1b648c80": "Stepped shaft",
}
SHEET6 = ["6989952c", "1fbfa3c8", "9ca41004", "390dc972", "40a1be28", "2a127616"]
SHEET12 = SHEET6 + ["475993e4", "232ebd96", "a2f71172", "0264f04e", "8f00d7de", "27676dd6"]


def key(prefix):
    return next(d for d in os.listdir(P) if d.startswith(prefix))


def load(k):
    return json.load(open(f"{P}/{k}/data.json"))


def img(path, pad=10, aspect=None):
    im = Image.open(path)
    if im.mode == "RGBA":
        bb = im.getbbox()
    else:  # drawing sheet: crop to the ink
        g = np.asarray(im.convert("L")) < 235
        ys, xs = np.where(g); bb = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    x0, y0, x1, y1 = bb
    im = im.convert("RGBA").crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))
    if aspect:  # letterbox to a fixed width/height so every panel's axes box is identical
        w, h = im.size; W, H = max(w, int(round(h * aspect))), max(h, int(round(w / aspect)))
        bg = Image.new("RGBA", (W, H), (255, 255, 255, 0)); bg.paste(im, ((W - w) // 2, (H - h) // 2)); im = bg
    return np.asarray(im)


def blank(aspect=1.0):
    return np.zeros((100, int(100 * aspect), 4), np.uint8)


def show(ax, a):
    ax.imshow(a, interpolation="lanczos"); ax.set_axis_off()


def save(fig, name):
    fig.savefig(f"{OUT}/{name}.png", dpi=250, bbox_inches="tight", facecolor="white")
    fig.savefig(f"{OUT}/{name}.svg", bbox_inches="tight", facecolor="white")
    s = open(f"{OUT}/{name}.svg").read().replace("Nimbus Sans", "Arial"); open(f"{OUT}/{name}.svg", "w").write(s)
    plt.close(fig); print("wrote", name)


def contact_sheet(keys, name="contact_sheet", cols=3):
    rows = (len(keys) + cols - 1) // cols
    fig = plt.figure(figsize=(16 * cols / 3, 4.8 * rows))
    outer = fig.add_gridspec(rows, cols, wspace=0.10, hspace=0.22)
    for t, k in enumerate(keys):
        d = load(k); m = d["medoid"]
        g = outer[t // cols, t % cols].subgridspec(2, 2, height_ratios=[1.0, 1.05], hspace=0.04, wspace=0.02)
        ax = fig.add_subplot(g[0, :]); show(ax, img(f"{P}/{k}/drawing.png", aspect=2.1))
        ax.set_title(NAMES[k[:8]], fontsize=14, fontweight="bold", color=NAVY, pad=6)
        a1 = fig.add_subplot(g[1, 0]); show(a1, img(f"{P}/{k}/gt.png", aspect=1.0))
        a2 = fig.add_subplot(g[1, 1]); show(a2, img(f"{P}/{k}/gen.png", aspect=1.0))
        a1.text(0.5, -0.04, "Ground truth", transform=a1.transAxes, ha="center", va="top", fontsize=11, color=GREY)
        a2.text(0.5, -0.04, f"Generation  IoU {d['iou'][m]:.3f}", transform=a2.transAxes, ha="center", va="top",
                fontsize=11, fontweight="bold", color=NAVY)
        a2.text(0.5, -0.17, f"agreement {d['agree'][m]:.2f} · {sum(d['exec'])}/8 executed", transform=a2.transAxes,
                ha="center", va="top", fontsize=9.5, color=GREY)
    save(fig, name)


def hero(k, first=False):
    d = load(k); m = d["medoid"]; dev = json.load(open(f"{P}/{k}/dev.json"))
    fig = plt.figure(figsize=(16, 4.6))
    g = fig.add_gridspec(1, 4, width_ratios=[1.55, 1.4, 1.4, 1.4], wspace=0.04)
    ax = fig.add_subplot(g[0]); show(ax, img(f"{P}/{k}/drawing.png", aspect=1.55))
    ax.set_title("Input drawing", fontsize=15, fontweight="bold", color=NAVY)
    # a perfect medoid has a blank deviation map: show the first draw against the medoid instead
    show_first = (first or dev["within_0p5mm"] > 0.999) and os.path.exists(f"{P}/{k}/first.png")
    panels = [("gt.png", "Ground truth")]
    if show_first:
        panels += [("first.png", f"First draw  IoU {d['per_part']['first_exec']:.3f}"), ("gen.png", f"Medoid  IoU {d['iou'][m]:.3f}")]
    else:
        panels += [("gen.png", f"Generation  IoU {d['iou'][m]:.3f}"), ("dev.png", "Deviation from ground truth")]
    for i, (f, t) in enumerate(panels):
        a = fig.add_subplot(g[i + 1]); show(a, img(f"{P}/{k}/{f}", aspect=1.4))
        a.set_title(t, fontsize=15, fontweight="bold", color=NAVY)
    if show_first:
        a.text(0.5, -0.02, f"agreement {d['agree'][m]:.2f}  ·  {sum(d['exec'])}/8 executed", transform=a.transAxes,
               ha="center", va="top", fontsize=11, color=GREY)
        save(fig, f"hero_{k[:8]}")
        return
    a.text(0.5, -0.02, f"{dev['within_0p5mm']:.0%} of surface within 0.5 mm  ·  mean |d| {dev['mean_abs_mm']:.2f} mm",
           transform=a.transAxes, ha="center", va="top", fontsize=11, color=GREY)
    cax = a.inset_axes([0.15, -0.20, 0.70, 0.045])
    sm = plt.cm.ScalarMappable(norm=Normalize(-dev["clip_mm"], dev["clip_mm"]), cmap="RdBu")
    cb = fig.colorbar(sm, cax=cax, orientation="horizontal")
    cb.set_ticks([-dev["clip_mm"], 0, dev["clip_mm"]])
    cb.set_ticklabels([f"{dev['clip_mm']:.0f} mm excess", "0", f"{dev['clip_mm']:.0f} mm missing"], fontsize=10)
    cb.outline.set_linewidth(0.5)
    save(fig, f"hero_{k[:8]}")


def agreement(k):
    d = load(k); n = len(d["iou"]); gt = np.array(d["iou"]); ex = d["exec"]; med = d["medoid"]
    M = np.array([[np.nan if v is None else v for v in r] for r in d["pair_iou"]], float)
    fig = plt.figure(figsize=(8, 10.2))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.35, 7.0], hspace=0.0)
    top = gs[0].subgridspec(1, n, wspace=0.05)
    for j in range(n):
        ax = fig.add_subplot(top[0, j])
        p = f"{P}/{k}/c{j}.png"
        if ex[j] and os.path.exists(p):
            show(ax, img(p, pad=4, aspect=1.0))
        else:
            show(ax, blank())
            ax.text(0.5, 0.45, "no solid", ha="center", va="center", fontsize=9, fontweight="bold", color=GREY, transform=ax.transAxes)
        ax.set_title(f"c{j}", fontsize=11, fontweight="bold", color=NAVY if j == med else "black", pad=2)
    ax = fig.add_subplot(gs[1])
    eye = np.eye(n, dtype=bool)
    ax.imshow(np.ma.masked_where(eye | np.isnan(M), np.nan_to_num(M)), cmap="Blues", vmin=0.0, vmax=1.0, aspect="equal")
    ax.imshow(np.ma.masked_where(~eye, np.tile(gt, (n, 1))), cmap="Greys", vmin=0.55, vmax=1.15, aspect="equal")
    ax.imshow(np.ma.masked_where(~(np.isnan(M) & ~eye), np.ones_like(M)), cmap="Greys", vmin=0, vmax=40, aspect="equal")
    for i in range(n):
        for j in range(n):
            if i == j:
                txt = f"GT\n{gt[i]:.2f}" if ex[i] else "GT\nfail"; col = "white" if ex[i] and gt[i] >= 0.9 else "black"
            elif np.isnan(M[i, j]):
                txt, col = "–", "#888888"
            else:
                txt = f"{M[i, j]:.2f}"; col = "white" if M[i, j] > 0.6 else "black"
            ax.text(j, i, txt, ha="center", va="center", fontsize=10, fontweight="bold", color=col)
    ax.set_xticks(range(n)); ax.set_yticks(range(n))
    lab = [f"c{j}" for j in range(n)]
    ax.set_xticklabels(lab, fontsize=11, fontweight="bold"); ax.set_yticklabels(lab, fontsize=11, fontweight="bold")
    for t in (ax.get_xticklabels()[med], ax.get_yticklabels()[med]):
        t.set_color(NAVY)
    ax.set_xticks(np.arange(-0.5, n, 1), minor=True); ax.set_yticks(np.arange(-0.5, n, 1), minor=True)
    ax.grid(which="minor", color="black", linewidth=0.5); ax.tick_params(which="both", length=0)
    ax.add_patch(Rectangle((-0.5, med - 0.5), n, 1, fill=False, edgecolor=NAVY, linewidth=3.2, zorder=5))
    ax.set_xlabel("Candidate", fontsize=13, fontweight="bold", labelpad=10); ax.set_ylabel("Candidate", fontsize=13, fontweight="bold", labelpad=10)
    ag = d["agree"]
    ax2 = ax.secondary_yaxis("right"); ax2.set_yticks(range(n))
    ax2.set_yticklabels([("medoid " if i == med else "agree ") + f"{a:.2f}" if a is not None else "fail" for i, a in enumerate(ag)],
                        fontsize=10, fontweight="bold")
    ax2.get_yticklabels()[med].set_color(NAVY); ax2.tick_params(length=0)
    save(fig, f"agreement_{k[:8]}")
    print(f"  {k[:8]}: medoid c{med} GT {gt[med]:.3f} agree {ag[med]:.3f} | first-exec {d['per_part']['first_exec']:.3f} "
          f"oracle c{d['oracle']} {gt[d['oracle']]:.3f}")


def gallery(keys, name="agreement_gallery", cols=3):
    """All agreement figures on one page, titled with part name and medoid vs first-draw IoU, for picking."""
    rows = (len(keys) + cols - 1) // cols
    fig, axs = plt.subplots(rows, cols, figsize=(6.2 * cols, 7.4 * rows))
    for ax, k in zip(axs.flat, keys):
        d = load(k); m = d["medoid"]
        show(ax, img(f"{OUT}/agreement_{k[:8]}.png", pad=4))
        ag = sorted({round(a, 2) for a in d["agree"] if a is not None})
        ax.set_title(f"{NAMES.get(k[:8], '')}  ({k[:8]})\nmedoid c{m} IoU {d['iou'][m]:.3f} · first draw {d['per_part']['first_exec']:.3f}"
                     f" · {sum(d['exec'])}/8 ran · {len(ag)} distinct agreements", fontsize=12, color=NAVY, fontweight="bold")
    for ax in list(axs.flat)[len(keys):]:
        ax.set_axis_off()
    fig.tight_layout()
    save(fig, name)


if __name__ == "__main__":
    contact_sheet([key(p) for p in SHEET6], "contact_sheet")
    contact_sheet([key(p) for p in SHEET12], "contact_sheet_12", cols=4)
    hero(key("1fbfa3c8"))
    hero(key("024cdfc2"), first=True)   # medoid-agreement hero: every candidate scores a distinct agreement
    for p in ("024cdfc2", "1fbfa3c8", "475993e4", "232ebd96"):
        agreement(key(p))
    gal = [l.strip() for l in open(f"{OUT}/picks_gallery.txt") if l.strip()]
    for k in gal:
        agreement(k)
    gallery(gal)
