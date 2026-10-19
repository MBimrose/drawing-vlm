"""pptxgenjs stores the SVG text under a .png name as the fallback picture; replace it with the real PNG render."""
import os, re, sys, zipfile
deck, svg, png = sys.argv[1:4]
z = zipfile.ZipFile(deck); items = {n: z.read(n) for n in z.namelist()}; z.close(); target = open(svg, "rb").read(); n_fix = 0
for n, b in items.items():
    if re.match(r"ppt/media/image-\d+-\d+\.png$", n) and b.lstrip().startswith(b"<?xml"):
        if b != target:
            raise SystemExit(f"unmatched SVG fallback {n}")
        items[n] = open(png, "rb").read(); n_fix += 1
with zipfile.ZipFile(deck + ".tmp", "w", zipfile.ZIP_DEFLATED) as out:
    for n, b in items.items():
        out.writestr(n, b)
os.replace(deck + ".tmp", deck); print(f"fixed {n_fix} PNG fallback(s)")
