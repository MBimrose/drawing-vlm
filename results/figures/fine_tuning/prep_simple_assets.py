"""Images for the simplified Figure 3/4 slides (Figure 2 style).
Fig 4: handwheel F_73525 (real bench) - start render, final render, target drawing, the start candidate's own drawing
(e55 draw 7 = start of the served repair chain), and an overlay of the two front views (geometry ink only).
Fig 3: the 8 GRPO-style candidates of synthetic part 1fbfa3c8 with their rewards."""
import json, os
import numpy as np
from PIL import Image

DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"; OUT = f"{DV}/results/figures/fine_tuning/simple_assets"
EX = f"{DV}/results/figures/results_deck/repair_ex"
tgt = Image.open(f"{EX}/F_73525_drawing.png").convert("RGB")
cand = Image.open(f"{DV}/results/ext/rc_png_bo8_dw423p_e55/F_73525_7f6b2f67_0_medium__7.png").convert("RGB")


def ink_crop(im, pad=14, thr=235):
    g = np.asarray(im.convert("L")) < thr; ys, xs = np.where(g)
    return im.crop((max(0, xs.min() - pad), max(0, ys.min() - pad), min(im.width, xs.max() + pad), min(im.height, ys.max() + pad)))


# front + iso views only (side views and title block dropped) so the drawings stay legible in a narrow box
ink_crop(tgt.crop((940, 60, 1440, 600))).save(f"{OUT}/hw_target_drawing.png")      # iso views only
ink_crop(cand.crop((1190, 270, 1690, 840))).save(f"{OUT}/hw_candidate_drawing.png")
for n, f in (("hw_start", "F_73525_step0.png"), ("hw_final", "F_73525_step2.png"), ("hw_gt", "F_73525_gt.png")):
    im = Image.open(f"{EX}/{f}"); im.crop(im.getbbox()).save(f"{OUT}/{n}.png")


def geometry_mask(im, box):
    """Black geometry pixels (annotations are blue) inside the front-view box, cropped to their extent."""
    a = np.asarray(im.crop(box)).astype(int); r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = (r + g + b < 380) & (b - r < 40)
    ys, xs = np.where(m); return m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


mt = geometry_mask(tgt, (355, 455, 715, 815)); mc = geometry_mask(cand, (620, 700, 985, 1070))
S = 520
def fit(m):
    return np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize((S, S), Image.LANCZOS)) > 60
from PIL import ImageFilter
thick = lambda m: np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7))) > 0
mt, mc = thick(fit(mt)), thick(fit(mc))
ov = np.zeros((S, S, 4), np.uint8)
ov[mt] = (0x13, 0x29, 0x4B, 255)            # target: Illinois navy
ov[mc & ~mt] = (0xE8, 0x4A, 0x27, 255)      # candidate where it differs: orange
ov[mc & mt] = (0x13, 0x29, 0x4B, 255)
Image.fromarray(ov, "RGBA").save(f"{OUT}/hw_overlay.png")

P = f"{DV}/results/figures/complex_parts/parts"; k = next(d for d in os.listdir(P) if d.startswith("1fbfa3c8"))
d = json.load(open(f"{P}/{k}/data.json")); rows = []
for j in range(8):
    p = f"{P}/{k}/c{j}.png"
    if d["exec"][j] and os.path.exists(p):
        im = Image.open(p); im.crop(im.getbbox()).save(f"{OUT}/grpo_c{j}.png"); rows.append({"j": j, "iou": d["iou"][j], "ok": True})
    else:
        rows.append({"j": j, "iou": 0.0, "ok": False})
json.dump({"cands": rows, "mean": float(np.mean([r["iou"] for r in rows]))}, open(f"{OUT}/grpo_cands.json", "w"), indent=1)
print("ok", [(r["j"], round(r["iou"], 2)) for r in rows])
