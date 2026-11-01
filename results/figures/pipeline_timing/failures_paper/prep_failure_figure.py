"""Crops for build_failure_figure.js: drawing sheet (ink crop), ground truth and generation (transparent) per option.
    python3 prep_failure_figure.py N [N ...]   -> fig_assets/<n>_{drawing,gt,pick}.png + manifest.json"""
import json, os, sys
import numpy as np
from PIL import Image
H = os.path.dirname(os.path.abspath(__file__)); A = f"{H}/fig_assets"; os.makedirs(A, exist_ok=True)
O = {o["n"]: o for o in json.load(open(f"{H}/options.json"))}
man = json.load(open(f"{A}/manifest.json")) if os.path.exists(f"{A}/manifest.json") else {}
for n in map(int, sys.argv[1:]):
    d = f"{H}/renders/{O[n]['key']}"; m = {}
    im = Image.open(f"{d}/drawing.png").convert("RGB"); g = np.asarray(im.convert("L")) < 235; ys, xs = np.where(g)
    im = im.crop((max(0, xs.min() - 12), max(0, ys.min() - 12), min(im.width, xs.max() + 12), min(im.height, ys.max() + 12)))
    im.save(f"{A}/{n}_drawing.png"); m["drawing"] = list(im.size)
    for k in ("gt", "pick"):
        a = np.asarray(Image.open(f"{d}/{k}.png").convert("RGBA")).copy(); a[a[..., :3].min(-1) > 245, 3] = 0
        im = Image.fromarray(a); im = im.crop(im.getbbox()); im.save(f"{A}/{n}_{k}.png"); m[k] = list(im.size)
    man[str(n)] = m
json.dump(man, open(f"{A}/manifest.json", "w"), indent=1); print("ok", sorted(man))
