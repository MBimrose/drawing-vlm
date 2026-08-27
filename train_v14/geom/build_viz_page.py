"""Assemble the reconstruction-gallery HTML from a viz_* asset directory."""
import base64
import json
import os
import sys

VIZ = sys.argv[1] if len(sys.argv) > 1 else \
    "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/viz_e15"
OUT = sys.argv[2] if len(sys.argv) > 2 else \
    "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/viz_e15/report.html"

meta = json.load(open(os.path.join(VIZ, "results.json")))
results = sorted(meta["results"], key=lambda r: -r["iou"])
n = len(results)
ex = [r for r in results if r["exec_ok"]]
mean_iou = sum(r["iou"] for r in results) / n
mean_exec = sum(r["iou"] for r in ex) / len(ex)
n85 = sum(r["iou"] >= 0.85 for r in results)


def b64(path, mime):
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


def chip(iou, ok):
    if not ok:
        return '<span class="chip fail">did not execute</span>'
    cls = "pass" if iou >= 0.85 else ("mid" if iou >= 0.5 else "low")
    return f'<span class="chip {cls}">IoU {iou:.3f}</span>'


cards = []
for r in results:
    k = r["key"]
    drawing = b64(os.path.join(VIZ, f"{k}_drawing.jpg"), "image/jpeg")
    gt = b64(os.path.join(VIZ, f"{k}_gt.png"), "image/png")
    pred_path = os.path.join(VIZ, f"{k}_pred.png")
    if os.path.exists(pred_path):
        pred_img = f'<img src="{b64(pred_path, "image/png")}" alt="predicted part">'
    else:
        pred_img = '<div class="nopred">execution failed<br>after 1 repair round</div>'
    rep = ' <span class="repnote">repaired</span>' if r.get("repaired") else ""
    cards.append(f"""
<section class="card">
  <header class="cardhead">
    <span class="uuid">{k}</span>
    {chip(r["iou"], r["exec_ok"])}{rep}
  </header>
  <div class="panes">
    <figure class="pane wide"><img src="{drawing}" alt="input drawing">
      <figcaption>input drawing</figcaption></figure>
    <figure class="pane">{pred_img}
      <figcaption>model output</figcaption></figure>
    <figure class="pane"><img src="{gt}" alt="ground truth">
      <figcaption>ground truth</figcaption></figure>
  </div>
</section>""")

html = f"""<title>Drawing-to-Part Gallery</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo+Narrow:wght@500;600;700&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root {{
  --paper:#FAFAF7; --ink:#23282D; --ink-2:#5A6169; --line:#C9CCC6;
  --accent:#2B5F8A; --panel:#FFFFFF; --panel-edge:#D8DAD4;
  --pass:#2E7D4F; --mid:#B07C1F; --low:#A94436;
  --pass-bg:#E4F0E8; --mid-bg:#F5EBD7; --low-bg:#F3E0DC;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --paper:#14181C; --ink:#E8E6E1; --ink-2:#9AA1A8; --line:#3A4148;
    --accent:#7FAFD4; --panel:#1C2127; --panel-edge:#2E353C;
    --pass:#7FC79A; --mid:#D9B36A; --low:#DE8E7F;
    --pass-bg:#1E3227; --mid-bg:#332B1A; --low-bg:#39231F;
  }}
}}
:root[data-theme="dark"] {{
  --paper:#14181C; --ink:#E8E6E1; --ink-2:#9AA1A8; --line:#3A4148;
  --accent:#7FAFD4; --panel:#1C2127; --panel-edge:#2E353C;
  --pass:#7FC79A; --mid:#D9B36A; --low:#DE8E7F;
  --pass-bg:#1E3227; --mid-bg:#332B1A; --low-bg:#39231F;
}}
* {{ box-sizing:border-box; }}
body {{ background:var(--paper); color:var(--ink);
  font-family:"Source Sans 3",system-ui,sans-serif; font-size:16px;
  line-height:1.5; margin:0; padding:2rem 1.25rem 4rem; }}
main {{ max-width:1080px; margin:0 auto; }}
.titleblock {{ border:2px solid var(--ink); display:grid;
  grid-template-columns:1fr auto auto auto; }}
.titleblock > div {{ padding:.55rem .9rem; border-left:1px solid var(--line); }}
.titleblock > div:first-child {{ border-left:none; }}
.tb-label {{ font-family:"IBM Plex Mono",monospace; font-size:.62rem;
  letter-spacing:.12em; text-transform:uppercase; color:var(--ink-2); }}
.tb-val {{ font-family:"Archivo Narrow",sans-serif; font-weight:600;
  font-size:1.05rem; white-space:nowrap; }}
h1 {{ font-family:"Archivo Narrow",sans-serif; font-weight:700;
  font-size:1.7rem; margin:0; letter-spacing:.01em; text-wrap:balance; }}
.sub {{ color:var(--ink-2); margin:.15rem 0 0; font-size:.92rem; }}
.stats {{ display:flex; gap:1px; background:var(--ink); border:2px solid var(--ink);
  border-top:none; }}
.stat {{ flex:1; background:var(--panel); padding:.6rem .9rem; }}
.stat b {{ font-family:"Archivo Narrow",sans-serif; font-size:1.35rem;
  font-variant-numeric:tabular-nums; display:block; color:var(--accent); }}
.stat span {{ font-size:.72rem; letter-spacing:.06em; text-transform:uppercase;
  color:var(--ink-2); }}
.note {{ margin:1.1rem 0 2rem; color:var(--ink-2); font-size:.9rem;
  max-width:68ch; }}
.card {{ background:var(--panel); border:1px solid var(--panel-edge);
  margin-bottom:1.4rem; }}
.cardhead {{ display:flex; align-items:center; gap:.8rem;
  padding:.5rem .9rem; border-bottom:1px solid var(--panel-edge); }}
.uuid {{ font-family:"IBM Plex Mono",monospace; font-size:.72rem;
  color:var(--ink-2); overflow-wrap:anywhere; }}
.chip {{ font-family:"IBM Plex Mono",monospace; font-size:.78rem;
  font-weight:500; padding:.14rem .55rem; border-radius:2px;
  margin-left:auto; white-space:nowrap; font-variant-numeric:tabular-nums; }}
.chip.pass {{ color:var(--pass); background:var(--pass-bg); }}
.chip.mid  {{ color:var(--mid);  background:var(--mid-bg); }}
.chip.low, .chip.fail {{ color:var(--low); background:var(--low-bg); }}
.repnote {{ font-size:.7rem; color:var(--accent);
  font-family:"IBM Plex Mono",monospace; }}
.panes {{ display:grid; grid-template-columns:1.55fr 1fr 1fr; gap:1px;
  background:var(--panel-edge); }}
.pane {{ margin:0; background:var(--panel); padding:.6rem;
  display:flex; flex-direction:column; }}
.pane img {{ width:100%; height:auto; display:block; background:#fff;
  border-radius:2px; }}
.pane figcaption {{ font-family:"IBM Plex Mono",monospace; font-size:.66rem;
  letter-spacing:.1em; text-transform:uppercase; color:var(--ink-2);
  margin-top:.45rem; }}
.nopred {{ flex:1; display:flex; align-items:center; justify-content:center;
  text-align:center; color:var(--low); font-size:.85rem; min-height:9rem;
  border:1px dashed var(--low); border-radius:2px; }}
@media (max-width:760px) {{ .panes {{ grid-template-columns:1fr; }}
  .titleblock {{ grid-template-columns:1fr 1fr; }} }}
</style>
<main>
<div class="titleblock">
  <div><h1>Drawing-to-Part Gallery</h1>
    <p class="sub">Qwen 3.8-27B fine-tune · single-shot + 1 repair round</p></div>
  <div><span class="tb-label">Model</span><div class="tb-val">{meta["run"]}</div></div>
  <div><span class="tb-label">Eval date</span><div class="tb-val">2026-08-26</div></div>
  <div><span class="tb-label">Samples</span><div class="tb-val">{n} · certified eval split</div></div>
</div>
<div class="stats">
  <div class="stat"><b>{mean_iou:.3f}</b><span>mean IoU (all)</span></div>
  <div class="stat"><b>{mean_exec:.3f}</b><span>mean IoU (executed)</span></div>
  <div class="stat"><b>{len(ex)}/{n}</b><span>programs executed</span></div>
  <div class="stat"><b>{n85}/{n}</b><span>parts ≥ 0.85 IoU</span></div>
</div>
<p class="note">Each row: the engineering drawing the model saw, the part its
generated build123d program produced (clay), and the ground-truth part
(steel blue). IoU is exact volumetric intersection-over-union after
bounding-box centering, the same scoring as the agentic-mesh-to-cad pipeline.
Rows are sorted best-first: clean reconstructions at the top, the failure
modes at the tail.</p>
{''.join(cards)}
</main>
"""
with open(OUT, "w") as f:
    f.write(html)
print(f"wrote {OUT} ({os.path.getsize(OUT)/1e6:.1f} MB)")
