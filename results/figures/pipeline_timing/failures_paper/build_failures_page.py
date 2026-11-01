"""(failures variant) Builds failures_page.html; based on faces_time_paper/options_bf16/build_options_page.py. Builds options_page.html: an interactive map of the 40 callout options for the face count / time figure. Every bench
part is a point (same encoding as the paper figure: synthetic = hollow circle, real = solid circle, colour = IoU); the
options are numbered on the plot and listed as cards (ISO view | SFT + GRPO part | ground truth). Hover or click either
to find the other. Images are embedded (WebP data URIs), so the page is one self-contained file.

    PYTHONPATH=train_v14/geom .venv/bin/python results/figures/pipeline_timing/faces_time_paper/options_bf16/build_options_page.py
"""
import base64
import io
import json
import os
import sys

import numpy as np
from PIL import Image

H = os.path.dirname(os.path.abspath(__file__)); PT = os.path.abspath(f"{H}/..")
sys.path.insert(0, os.path.abspath(f"{H}/../../../../train_v14/geom"))
from faces_time_figure import CMAP  # noqa: E402
from plot_iou_time_faces import load  # noqa: E402

TMAX = 150


def uri(path, px=260):
    im = Image.open(path).convert("RGBA"); im.thumbnail((px, px)); b = io.BytesIO(); im.save(b, "WEBP", quality=82)
    return "data:image/webp;base64," + base64.b64encode(b.getvalue()).decode()


def hexc(v):
    r, g, b, _ = CMAP(float(np.clip(v, 0, 1))); return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


sets = [load(f"{PT}/throughput/bf16v3_plotpass_fullpool_dw423.jsonl", "Synthetic parts", "o"),
        load(f"{PT}/throughput/bf16v3_plotpass_bench_b.jsonl", "Real parts", "s")]
pts = [{"f": float(f), "t": round(float(t), 2), "i": round(float(i), 3), "r": int(s["label"].startswith("Real")), "c": hexc(i)}
       for s in sets for f, t, i in zip(s["faces"], s["time"], s["iou"]) if t <= TMAX]
fig = {}
opts = []
for o in json.load(open(f"{H}/options.json")):
    n = o["n"]; co = f"{H}/cutouts"
    opts.append({"n": n, "key": o["key"], "set": "Real" if o["set"].startswith("Real") else "Synthetic", "why": o["why"], "group": o["group"],
                 "faces": int(o["faces"]), "time": round(o["time"], 1), "iou": round(o["iou"], 2), "c": hexc(o["iou"]),
                 "fig": fig.get(o["key"], ""), "iso": uri(f"{co}/{n:02d}_iso.png"), "pick": uri(f"{co}/{n:02d}_pick.png"),
                 "gt": uri(f"{co}/{n:02d}_gt.png")})
cbar = [hexc(v) for v in np.linspace(0, 1, 11)]
data = json.dumps({"pts": pts, "opts": opts, "cbar": cbar}, separators=(",", ":"))
html = open(f"{H}/failures_page_template.html").read().replace("/*__DATA__*/null", data)
open(f"{H}/failures_page.html", "w").write(html)
print(f"wrote failures_page.html ({len(html) / 1e6:.1f} MB): {len(pts)} points, {len(opts)} options; in current figure: {fig}")
