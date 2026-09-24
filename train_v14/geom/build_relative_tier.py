"""Relative (group-advantage) RFT tier: for each part whose best-of-K draw is in [lo, hi) and beats the part's
median draw by >= margin, keep that best draw (the model's own think + code). The positive half of a GRPO-style
group-relative update, learned from the partial-credit parts that the IoU >= 0.8 RFT cutoff discards.
    python build_relative_tier.py --bo <scored bo json> --png-dir <render/png> --out <tier dir> [--lo 0.4 --hi 0.8 --margin 0.15]"""
import argparse, glob, json, os, shutil, numpy as np
ap = argparse.ArgumentParser(); ap.add_argument("--bo"); ap.add_argument("--png-dir"); ap.add_argument("--out")
ap.add_argument("--lo", type=float, default=0.4); ap.add_argument("--hi", type=float, default=0.8); ap.add_argument("--margin", type=float, default=0.15)
a = ap.parse_args()
os.makedirs(os.path.join(a.out, "png"), exist_ok=True)
d = json.load(open(a.bo))["candidates"]; n = 0; nopng = 0
with open(os.path.join(a.out, "accepted-000.jsonl"), "w") as f:
    for p in d:
        cs = [c for c in p["cands"] if c.get("code")]
        if not cs: continue
        i = [float(c.get("iou") or 0) for c in cs]; b = max(i); m = float(np.median(i))
        if not (a.lo <= b < a.hi and b - m >= a.margin): continue
        c = cs[int(np.argmax(i))]
        if not c.get("exec") or not (c.get("think") or "").strip(): continue
        png = sorted(glob.glob(os.path.join(a.png_dir, p["key"] + "_v*.png")))
        if not png: nopng += 1; continue
        shutil.copy(png[0], os.path.join(a.out, "png", p["key"] + ".png"))
        f.write(json.dumps({"key": p["key"], "iou": b, "think": c["think"], "code": c["code"], "median": m}) + "\n"); n += 1
print(f"relative tier: {n} rows ({nopng} without png) -> {a.out}")
