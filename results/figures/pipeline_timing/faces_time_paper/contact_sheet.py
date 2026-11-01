"""Contact sheet of the callout options for the face count / time figure (numbers match faces_time_annotated):
  contact_sheet.png        one tile per option: number + why, drawing | SFT + GRPO pick | ground truth, faces / time / IoU
  cutouts/<n>_pick.png     the pick render cropped, white made transparent (drop straight onto the plot)
  cutouts/<n>_gt.png       same for the ground truth
Renders come from render_callouts.py (<renders>/<key>/{drawing,pick,gt}.png). With --iso-crop the drawing column shows only
the sheet's ISO view (faces_time_figure.iso_box), matching renders made with render_callouts.py --iso.

    python3 results/figures/pipeline_timing/faces_time_paper/contact_sheet.py [--dir options_bf16 --renders renders_bf16_iso --iso-crop]
"""
import argparse
import sys
import json
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument("--dir", default=""); ap.add_argument("--renders", default="renders")
ap.add_argument("--iso-crop", action="store_true"); a = ap.parse_args()
H = os.path.join(HERE, a.dir) if a.dir else HERE; RD = os.path.join(HERE, a.renders); CO = f"{H}/cutouts"; os.makedirs(CO, exist_ok=True)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "train_v14", "geom"))
FB, FR = "/usr/share/fonts/urw-base35/NimbusSans-Bold.otf", "/usr/share/fonts/urw-base35/NimbusSans-Regular.otf"


def cutout(src, dst):
    im = Image.open(src).convert("RGBA"); a = np.asarray(im).copy()
    white = (a[..., :3].min(-1) > 245); a[white, 3] = 0
    im = Image.fromarray(a); im = im.crop(im.getbbox()); im.save(dst); return im


def ink(src):
    im = Image.open(src).convert("RGB"); g = np.asarray(im.convert("L")) < 235; ys, xs = np.where(g)
    return im.crop((max(0, xs.min() - 10), max(0, ys.min() - 10), min(im.width, xs.max() + 10), min(im.height, ys.max() + 10)))


def fit(im, w, h):
    im = im.copy(); im.thumbnail((w, h)); c = Image.new("RGB", (w, h), "white")
    c.paste(im, ((w - im.width) // 2, (h - im.height) // 2), im if im.mode == "RGBA" else None); return c


opts = json.load(open(f"{H}/options.json")); cols = 3; tw, th = 900, 380
sheet = Image.new("RGB", (cols * tw, -(-len(opts) // cols) * th), "white"); dr = ImageDraw.Draw(sheet)
f1, f2 = ImageFont.truetype(FB, 26), ImageFont.truetype(FR, 22)
for j, p in enumerate(opts):
    d = f"{RD}/{p['key']}"
    if not os.path.exists(f"{d}/pick.png"):
        print("missing", p["n"], p["key"]); continue
    pk = cutout(f"{d}/pick.png", f"{CO}/{p['n']:02d}_pick.png"); gt = cutout(f"{d}/gt.png", f"{CO}/{p['n']:02d}_gt.png")
    x, y = (j % cols) * tw, (j // cols) * th
    dr.rectangle([x + 4, y + 4, x + tw - 4, y + th - 4], outline="#D3DEE0", width=2)
    dr.text((x + 16, y + 12), f"{p['n']}. {p['why']}", fill="#13294B", font=f1)
    if a.iso_crop:
        from faces_time_figure import iso_box, transparent
        b = iso_box(f"{d}/drawing.png"); dr_im = transparent(Image.open(f"{d}/drawing.png").crop(b)) if b else ink(f"{d}/drawing.png")
        dr_im.save(f"{CO}/{p['n']:02d}_iso.png")
    else:
        dr_im = ink(f"{d}/drawing.png")
    for i, im in enumerate((dr_im, pk, gt)):
        sheet.paste(fit(im, 280, 270), (x + 14 + i * 292, y + 50))
    dr.text((x + 16, y + th - 42), f"{p['set']}  ·  {p['faces']:.0f} faces  ·  {p['time']:.0f} s  ·  IoU {p['iou']:.2f}  ·  {p['key'][:18]}",
            fill="#5A5F69", font=f2)
sheet.save(f"{H}/contact_sheet.png"); print("wrote contact_sheet.png,", len(opts), "options; cutouts in", CO)
