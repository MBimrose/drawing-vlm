import json, sys, os
from multiprocessing import Pool
sys.path.insert(0, "train_v14/geom")
from cad_render import render_stl
from PIL import Image, ImageDraw, ImageFont
D = "results/figures/real_parts"; GT = "train_v14/mech/benchmarks/data/ext_bench_dw423_perm/gt_meshes_v15"
R = sorted(json.load(open(f"{D}/served.json")), key=lambda r: -r["served_iou"])
def one(r):
    p = f"{D}/shortlist/{r['key']}.png"
    if not os.path.exists(p):
        render_stl(f"{GT}/{r['key']}.stl", color="#8a8f99", size=420).save(p)
    return p
with Pool(32) as pool: paths = pool.map(one, R)
cols, cw, ch = 12, 300, 300
sheet = Image.new("RGB", (cols * cw, ((len(R) + cols - 1) // cols) * ch), "white"); d = ImageDraw.Draw(sheet)
f = ImageFont.load_default(size=16)
for i, (r, p) in enumerate(zip(R, paths)):
    im = Image.open(p); im = im.crop(im.getbbox()); im.thumbnail((cw - 10, ch - 50))
    x, y = (i % cols) * cw, (i // cols) * ch
    sheet.paste(im, (x + (cw - im.width) // 2, y + 5), im)
    d.text((x + 5, y + ch - 44), f"{i} {r['key'][:10]}", fill="black", font=f)
    d.text((x + 5, y + ch - 24), f"srv {r['served_iou']:.3f} vote {(r['vote_iou'] or 0):.2f}", fill="black", font=f)
sheet.save(f"{D}/shortlist_sheet.jpg", quality=85); print("ok", len(R))
