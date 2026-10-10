import json
from PIL import Image, ImageDraw, ImageFont
D = "results/figures/complex_parts/parts"; keys = open("results/figures/complex_parts/picks12_v2.txt").read().split()
W, H = 1800, 400; f = ImageFont.load_default(size=22)
for half in (0, 1):
    ks = keys[half * 6:(half + 1) * 6]
    sheet = Image.new("RGB", (W, H * len(ks)), "white"); dr = ImageDraw.Draw(sheet)
    for i, k in enumerate(ks):
        d = json.load(open(f"{D}/{k}/data.json")); m = d["medoid"]; y = i * H
        dw = Image.open(f"{D}/{k}/drawing.png").convert("RGB"); dw.thumbnail((760, H - 20)); sheet.paste(dw, (10, y + 10))
        for x, fn in ((800, "gt.png"), (1220, "gen.png")):
            im = Image.open(f"{D}/{k}/{fn}"); im = im.crop(im.getbbox()); im.thumbnail((380, 330)); sheet.paste(im, (x, y + 60), im)
        dr.text((800, y + 5), f"{half*6+i} {k[:8]} GT", fill="black", font=f)
        dr.text((1220, y + 5), f"medoid c{m} IoU {d['iou'][m]:.3f} agree {d['agree'][m]:.2f}", fill="black", font=f)
        dr.text((1220, y + 30), f"first {d['per_part']['first_exec']:.3f} oracle {d['per_part']['oracle']:.3f} exec {sum(d['exec'])}/8", fill="black", font=f)
        dr.line((0, y + H - 1, W, y + H - 1), fill="#ccc")
    sheet.save(f"/tmp/claude-1147665/-projects-illinois-eng-ece-wpk-bimrose2-drawing-vlm/4815eb44-cd53-4180-880d-a364eef74cae/scratchpad/rv2_{half}.jpg", quality=85)
