"""Crop drawing / GT / generation images for the editable contact-sheet deck and write manifest.json."""
import json, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, "train_v14/geom")
from plot_complex_parts import NAMES, SHEET12, key, load, P
OUT = "results/figures/complex_parts/pptx/assets"; os.makedirs(OUT, exist_ok=True)
rows = []
for p in SHEET12:
    k = key(p); d = load(k); m = d["medoid"]
    dw = Image.open(f"{P}/{k}/drawing.png").convert("RGB")
    g = np.asarray(dw.convert("L")) < 235; ys, xs = np.where(g); pad = 12
    dw = dw.crop((max(0, xs.min() - pad), max(0, ys.min() - pad), min(dw.width, xs.max() + pad), min(dw.height, ys.max() + pad)))
    dw.save(f"{OUT}/{p}_drawing.png")
    sizes = {"drawing": dw.size}
    for n in ("gt", "gen"):
        im = Image.open(f"{P}/{k}/{n}.png"); im = im.crop(im.getbbox()); im.save(f"{OUT}/{p}_{n}.png"); sizes[n] = im.size
    rows.append({"id": p, "name": NAMES[p], "iou": round(d["iou"][m], 3), "agree": round(d["agree"][m], 2),
                 "n_exec": sum(d["exec"]), "sizes": sizes})
json.dump(rows, open("results/figures/complex_parts/pptx/manifest.json", "w"), indent=1)
print(len(rows), "parts")
