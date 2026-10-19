"""Numbers and gallery assets for build_results_deck.js, and the post-build PNG-fallback fix.

    .venv/bin/python prep_results_deck.py            -> data/summary.json, gallery/*.png
    .venv/bin/python prep_results_deck.py --fix-png  -> replace pptxgenjs's SVG-as-PNG fallbacks with real PNG renders
gallery_picks.txt: one '<key>|<failure-mode label>' per line (labels by inspection of the renders).
"""
import json
import os
import re
import sys
import zipfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
PARTS = f"{DV}/results/figures/complex_parts/parts"
CHARTS = ["repair_loop", "faces_vs_iou", "exectime_vs_iou", "faces_vs_exectime", "iou_hist", "iou_survival"]


def spearman(x, y):
    return float(np.corrcoef(np.argsort(np.argsort(x)), np.argsort(np.argsort(y)))[0, 1])


def summary():
    P = json.load(open(f"{HERE}/data/parts.json")); rc = json.load(open(f"{HERE}/data/repair_curve.json"))
    med = np.array([p["medoid"] for p in P]); fc = np.array([p["faces"] for p in P])
    S = {"aspect": {}}
    for c in CHARTS:   # chart height/width so the deck keeps each SVG's aspect ratio
        if os.path.exists(f"{HERE}/{c}.png"):
            w, h = Image.open(f"{HERE}/{c}.png").size; S["aspect"][c] = h / w
    S["repair"] = {"n": rc["n"], "start": rc["chain1_mean"][0], "chain1_r1": rc["chain1_mean"][1],
                   "chain1_final": rc["chain1_mean"][-1], "ms_final": rc["multistart_mean"][-1], "oracle8": rc["e55_oracle8"],
                   "frac85_start": rc["chain1_frac85"][0], "frac85_final": rc["multistart_frac85"][-1],
                   "fusion": rc["fusion_ms_final"], "abc": rc["abc_ms_final"]}
    q = np.quantile(fc, [1 / 3, 2 / 3]).astype(int)
    bins = [(fc <= q[0], f"≤{q[0]}"), ((fc > q[0]) & (fc <= q[1]), f"{q[0] + 1}–{q[1]}"), (fc > q[1], f">{q[1]}")]
    S["faces"] = {"n": len(P), "rho": spearman(med, fc),
                  "bins": [{"label": l, "n": int(m.sum()), "mean": float(med[m].mean()), "frac85": float((med[m] >= 0.85).mean())} for m, l in bins]}
    T = [(p["medoid"], p["exec_sec"]) for p in P if p.get("exec_sec") is not None]
    S["exec"] = None
    if T and os.path.exists(f"{HERE}/exectime_vs_iou.png"):
        ti, ts = np.array([t[0] for t in T]), np.array([t[1] for t in T])
        S["exec"] = {"n": len(T), "median": float(np.median(ts)), "p95": float(np.percentile(ts, 95)), "max": float(ts.max()),
                     "rho": spearman(ti, ts), "median_ok": float(np.median(ts[ti >= 0.85])), "median_bad": float(np.median(ts[ti < 0.85]))}
    if T:
        fx = np.array([p["faces"] for p in P if p.get("exec_sec") is not None]); fy = np.array([p["exec_sec"] for p in P if p.get("exec_sec") is not None])
        fb = [(0, 20), (21, 32), (33, 60), (61, 10 ** 6)]
        S["faces_exec"] = {"n": len(fx), "rho": spearman(fx, fy), "r2_loglog": float(np.corrcoef(np.log10(fx), np.log10(fy))[0, 1] ** 2),
                           "bins": [{"label": (f"{lo}–{hi}" if hi < 10 ** 6 else f">{lo - 1}") if lo else f"≤{hi}", "n": int(((fx >= lo) & (fx <= hi)).sum()),
                                     "median": float(np.median(fy[(fx >= lo) & (fx <= hi)])), "p95": float(np.percentile(fy[(fx >= lo) & (fx <= hi)], 95))} for lo, hi in fb]}
    S["dist"] = {"n": len(P), "mean": float(med.mean()), "median": float(np.median(med)), "frac85": float((med >= 0.85).mean()),
                 "first85": float(np.mean([p["first"] >= 0.85 for p in P])), "oracle85": float(np.mean([p["oracle"] >= 0.85 for p in P]))}
    os.makedirs(f"{HERE}/gallery", exist_ok=True); G = []
    picks = f"{HERE}/gallery_picks.txt"
    for line in (open(picks) if os.path.exists(picks) else []):
        if not line.strip():
            continue
        k, mode = line.strip().split("|", 1); d = json.load(open(f"{PARTS}/{k}/data.json")); m = d["medoid"]; sid = k[:8]
        dw = Image.open(f"{PARTS}/{k}/drawing.png").convert("RGB"); g = np.asarray(dw.convert("L")) < 235; ys, xs = np.where(g)
        dw = dw.crop((max(0, xs.min() - 12), max(0, ys.min() - 12), min(dw.width, xs.max() + 12), min(dw.height, ys.max() + 12)))
        dw.save(f"{HERE}/gallery/{sid}_drawing.png"); sizes = {"drawing": dw.size}
        for n in ("gt", "gen"):
            im = Image.open(f"{PARTS}/{k}/{n}.png"); im = im.crop(im.getbbox()); im.save(f"{HERE}/gallery/{sid}_{n}.png"); sizes[n] = im.size
        G.append({"id": sid, "mode": mode, "iou": d["iou"][m], "oracle": max(d["iou"]), "n_exec": sum(d["exec"]), "sizes": sizes})
    S["gallery"] = G
    # repair-loop example rows: drawing + every adopted program of the served chain + GT
    RX = f"{DV}/results/figures/repair_example"; os.makedirs(f"{HERE}/repair_ex", exist_ok=True); S["repair_ex"] = []
    for pre, name in (("F_73525", "Handwheel"), ("F_56468", "Hex nut")):
        k = next(x for x in os.listdir(RX) if x.startswith(pre)); m = json.load(open(f"{RX}/{k}/steps.json")); sid = pre
        dw = Image.open(f"{RX}/{k}/drawing.png").convert("RGB"); g = np.asarray(dw.convert("L")) < 235; ys, xs = np.where(g)
        dw = dw.crop((max(0, xs.min() - 12), max(0, ys.min() - 12), min(dw.width, xs.max() + 12), min(dw.height, ys.max() + 12)))
        dw.save(f"{HERE}/repair_ex/{sid}_drawing.png"); row = {"id": sid, "name": name, "chain": m["chain"], "drawing": dw.size, "steps": []}
        for st in m["steps"]:
            im = Image.open(f"{RX}/{k}/step{st['step']}.png"); im = im.crop(im.getbbox()); im.save(f"{HERE}/repair_ex/{sid}_step{st['step']}.png")
            row["steps"].append({"step": st["step"], "round": st["round"], "iou": st["iou"], "size": im.size})
        im = Image.open(f"{RX}/{k}/gt.png"); im = im.crop(im.getbbox()); im.save(f"{HERE}/repair_ex/{sid}_gt.png"); row["gt"] = im.size
        S["repair_ex"].append(row)
    json.dump(S, open(f"{HERE}/data/summary.json", "w"), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in S.items() if k not in ("gallery", "aspect")}, indent=1, ensure_ascii=False))


def fix_png(pptx):
    """pptxgenjs writes the SVG text under a .png name as the fallback blip; put the real PNG render there."""
    svgs = {open(f"{HERE}/{c}.svg", "rb").read(): f"{HERE}/{c}.png" for c in CHARTS if os.path.exists(f"{HERE}/{c}.svg")}
    z = zipfile.ZipFile(pptx); items = {n: z.read(n) for n in z.namelist()}; z.close(); fixed = 0
    for n, b in list(items.items()):
        mm = re.match(r"ppt/media/image-(\d+)-(\d+)\.png$", n)
        if mm and b.lstrip().startswith(b"<?xml"):
            png = svgs.get(b)
            if png is None:
                raise SystemExit(f"unmatched SVG fallback {n}")
            items[n] = open(png, "rb").read(); fixed += 1
    tmp = pptx + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as out:
        for n, b in items.items():
            out.writestr(n, b)
    os.replace(tmp, pptx); print(f"fixed {fixed} PNG fallbacks in {pptx}")


if __name__ == "__main__":
    if "--fix-png" in sys.argv:
        fix_png(f"{HERE}/results_figures.pptx")
    else:
        summary()
