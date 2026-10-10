import json, sys, os
sys.path.insert(0, "train_v14/geom")
import trimesh
from multiprocessing import Pool
from cad_render import render_mesh, shared_frame, autocrop
from PIL import Image, ImageDraw, ImageFont
D = "results/figures/complex_parts/parts"; keys = open("results/figures/complex_parts/picks12.txt").read().split()
def one(k):
    d = json.load(open(f"{D}/{k}/data.json")); m = d["medoid"]
    gt = trimesh.load(f"{D}/{k}/gt.stl", force="mesh"); md = trimesh.load(f"{D}/{k}/cand{m}.stl", force="mesh")
    sc = shared_frame([gt, md])
    return render_mesh(gt, color="#8a8f99", size=500, scale=sc), render_mesh(md, color="#2f6fd6", size=500, scale=sc), d
with Pool(12) as p: R = p.map(one, keys)
W = 1800; H = 420; sheet = Image.new("RGB", (W, H * len(keys)), "white"); dr = ImageDraw.Draw(sheet); f = ImageFont.load_default(size=22)
for i, (k, (g, m, d)) in enumerate(zip(keys, R)):
    y = i * H
    dw = Image.open(f"{D}/{k}/drawing.png").convert("RGB"); dw.thumbnail((760, H - 20)); sheet.paste(dw, (10, y + 10))
    g.thumbnail((400, 400)); m.thumbnail((400, 400))
    sheet.paste(g, (800, y + 10), g); sheet.paste(m, (1220, y + 10), m)
    med = d["medoid"]
    dr.text((800, y + 5), f"{i} {k[:8]} GT", fill="black", font=f)
    dr.text((1220, y + 5), f"medoid c{med} IoU {d['iou'][med]:.3f} agree {d['agree'][med]:.2f}", fill="black", font=f)
    dr.text((1220, y + 35), f"first {d['per_part']['first_exec']:.3f} oracle {d['per_part']['oracle']:.3f} exec {sum(d['exec'])}/8", fill="black", font=f)
    dr.line((0, y + H - 1, W, y + H - 1), fill="#ccc")
sheet.save("results/figures/complex_parts/review_sheet.jpg", quality=85); print("ok")
