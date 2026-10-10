import json, sys, os
from multiprocessing import Pool
sys.path.insert(0, "train_v14/geom")
from cad_render import render_stl
from PIL import Image, ImageDraw, ImageFont
D = "results/figures/complex_parts"; GT = "step_to_drw/wds_dataset/gt_meshes_v15"
R = json.load(open(f"{D}/rank.json"))
R = sorted([r for r in R if r["aspect"] >= 0.12], key=lambda r: (-r["ops"] - r["bools"], -r["faces"]))
def one(r):
    p = f"{D}/shortlist/{r['key']}.png"
    if not os.path.exists(p):
        render_stl(f"{GT}/{r['key']}.stl", color="#8a8f99", size=420).save(p)
    return p
with Pool(32) as pool: paths = pool.map(one, R)
cols, rows, cw, ch = 14, 10, 260, 270; per = cols * rows
f = ImageFont.load_default(size=15)
for pg in range(0, len(R), per):
    sheet = Image.new("RGB", (cols * cw, rows * ch), "white"); d = ImageDraw.Draw(sheet)
    for i, (r, p) in enumerate(zip(R[pg:pg + per], paths[pg:pg + per])):
        im = Image.open(p); im = im.crop(im.getbbox()); im.thumbnail((cw - 10, ch - 40))
        x, y = (i % cols) * cw, (i // cols) * ch
        sheet.paste(im, (x + (cw - im.width) // 2, y + 5), im)
        d.text((x + 4, y + ch - 32), f"{pg+i} {r['key'][:8]} v{r['vote']:.3f}", fill="black", font=f)
        d.text((x + 4, y + ch - 16), f"op{r['ops']} b{r['bools']} F{r['faces']} h{r['small_cyl']}", fill="black", font=f)
    sheet.save(f"{D}/all_sheet_{pg // per}.jpg", quality=82)
json.dump([r["key"] for r in R], open(f"{D}/all_keys.json", "w"))
print("ok", len(R))
