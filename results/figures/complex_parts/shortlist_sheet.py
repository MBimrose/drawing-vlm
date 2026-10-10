import json, sys, os
from multiprocessing import Pool
sys.path.insert(0, "train_v14/geom")
from cad_render import render_stl, autocrop
from PIL import Image, ImageDraw, ImageFont
D = "results/figures/complex_parts"; GT = "step_to_drw/wds_dataset/gt_meshes_v15"
R = json.load(open(f"{D}/rank.json"))
for r in R:
    r["score"] = r["faces"] - r["small_cyl"] + 2 * r["plane_normals"] + 3 * len(r["types"]) + r["ops"]
C = sorted([r for r in R if r["aspect"] >= 0.12], key=lambda r: -r["score"])[:96]
def one(r):
    p = f"{D}/shortlist/{r['key']}.png"
    if not os.path.exists(p):
        autocrop(render_stl(f"{GT}/{r['key']}.stl", color="#8a8f99", size=420)).save(p)
    return p
with Pool(32) as pool: paths = pool.map(one, C)
cols, cw, ch = 12, 300, 300
sheet = Image.new("RGB", (cols * cw, ((len(C) + cols - 1) // cols) * ch), "white"); d = ImageDraw.Draw(sheet)
f = ImageFont.load_default(size=16)
for i, (r, p) in enumerate(zip(C, paths)):
    im = Image.open(p); im.thumbnail((cw - 10, ch - 50))
    x, y = (i % cols) * cw, (i // cols) * ch
    sheet.paste(im, (x + (cw - im.width) // 2, y + 5), im)
    d.text((x + 5, y + ch - 44), f"{i} {r['key'][:8]} s{r['score']:.0f} op{r['ops']}", fill="black", font=f)
    d.text((x + 5, y + ch - 24), f"F{r['faces']} h{r['small_cyl']} a{r['aspect']:.2f} v{r['vote']:.3f}", fill="black", font=f)
sheet.save(f"{D}/shortlist_sheet.jpg", quality=85)
json.dump([r["key"] for r in C], open(f"{D}/shortlist_keys.json", "w"))
print("ok", len(C))
