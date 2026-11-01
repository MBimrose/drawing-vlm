"""Crops the repair_options_assets.py renders, writes deck/manifest.json for build_options.js and an overview PNG
contact sheet per model (overview_<model>.png): one row per part, drawing | start -> repairs ... | ground truth."""
import json
import os

import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/train_v14/geom")

H = os.path.dirname(os.path.abspath(__file__)); O = f"{H}/deck"; os.makedirs(O, exist_ok=True)
FONT = "/usr/share/fonts/urw-base35/NimbusSans-Bold.otf"


def crop(src, dst, ink=False):
    im = Image.open(src)
    if ink:
        g = np.asarray(im.convert("L")) < 235; ys, xs = np.where(g)
        im = im.convert("RGB").crop((max(0, xs.min() - 12), max(0, ys.min() - 12), min(im.width, xs.max() + 12), min(im.height, ys.max() + 12)))
    else:
        im = im.crop(im.getbbox())
    im.save(dst); return list(im.size)


def iso_crop(src, dst):
    """The drawing's ISO view only (faces_time_figure.iso_box), white made transparent; whole sheet if not found."""
    from faces_time_figure import iso_box, transparent
    im = Image.open(src); b = iso_box(src); im = transparent(im.crop(b) if b else im); im.save(dst); return list(im.size)


def fit(im, w, h):   # transparent renders composited on white
    im = im.convert("RGBA"); im.thumbnail((w, h)); c = Image.new("RGB", (w, h), "white")
    c.paste(im, ((w - im.width) // 2, (h - im.height) // 2), im); return c


M = {}
for model in [m for m in ("sft", "grpo", "sft_iso", "grpo_iso") if os.path.isdir(f"{H}/{m}")]:
    parts = []
    for k in sorted(os.listdir(f"{H}/{model}")):
        d = f"{H}/{model}/{k}"
        if not os.path.exists(f"{d}/steps.json"):
            continue
        s = json.load(open(f"{d}/steps.json")); t = f"{model}_{k[:16]}"
        p = {"key": k, "id": t, "drawing": crop(f"{d}/drawing.png", f"{O}/{t}_drawing.png", ink=True),
             "iso": iso_crop(f"{d}/drawing.png", f"{O}/{t}_iso.png"), "gt": crop(f"{d}/gt.png", f"{O}/{t}_gt.png"),
             "steps": [{"round": st["round"], "iou": st["iou"], "file": f"{t}_step{i}.png", "size": crop(f"{d}/step{i}.png", f"{O}/{t}_step{i}.png")}
                       for i, st in enumerate(s["steps"])]}
        p["gain"] = p["steps"][-1]["iou"] - p["steps"][0]["iou"]; parts.append(p)
    parts.sort(key=lambda p: -p["gain"]); M[model] = parts
    # overview PNG
    cw, rh, lab = 300, 300, 60; ncol = 2 + max(len(p["steps"]) for p in parts)
    sheet = Image.new("RGB", (ncol * cw, len(parts) * (rh + lab)), "white"); dr = ImageDraw.Draw(sheet)
    f1, f2 = ImageFont.truetype(FONT, 22), ImageFont.truetype(FONT, 20)
    for r, p in enumerate(parts):
        y = r * (rh + lab)
        dr.text((8, y + 6), f"{r + 1}. {p['key'][:24]}   gain {p['gain']:+.3f}", fill="black", font=f1)
        cells = [(f"{O}/{p['id']}_drawing.png", "Drawing")] + \
                [(f"{O}/{s['file']}", ("Start" if i == 0 else f"Round {s['round']}") + f"  IoU {s['iou']:.2f}") for i, s in enumerate(p["steps"])] + \
                [(f"{O}/{p['id']}_gt.png", "Ground truth")]
        for i, (f, t) in enumerate(cells):
            sheet.paste(fit(Image.open(f), cw - 20, rh - 40), (i * cw + 10, y + 36))
            dr.text((i * cw + 10, y + rh), t, fill="#13294B", font=f2)
    sheet.save(f"{H}/overview_{model}.png"); print(model, len(parts), "parts ->", f"overview_{model}.png")
json.dump(M, open(f"{O}/manifest.json", "w"), indent=1)
