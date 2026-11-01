"""Crops renders and writes deck/manifest.json for build_deck.js (pipeline timing + bench-B repair slides)."""
import json
import os

import numpy as np
from PIL import Image

H = os.path.dirname(os.path.abspath(__file__)); P = f"{H}/parts"; O = f"{H}/deck"; os.makedirs(O, exist_ok=True)


def crop(src, dst, ink=False):
    im = Image.open(src)
    if ink:   # drawing sheet: crop to the ink
        g = np.asarray(im.convert("L")) < 235; ys, xs = np.where(g)
        im = im.convert("RGB").crop((max(0, xs.min() - 12), max(0, ys.min() - 12), min(im.width, xs.max() + 12), min(im.height, ys.max() + 12)))
    else:
        im = im.crop(im.getbbox())
    im.save(dst); return list(im.size)


def part(prefix):
    k = next(d for d in os.listdir(P) if d.startswith(prefix)); a = json.load(open(f"{P}/{k}/assets.json")); s = prefix
    out = {"key": k, "id": s, "times": a["times"], "iou_start": a["iou_start"], "iou_final": a["iou"].get("final", a["iou_final"]),
           "drawing": crop(f"{P}/{k}/drawing.png", f"{O}/{s}_drawing.png", ink=True), "gt": crop(f"{P}/{k}/gt.png", f"{O}/{s}_gt.png"),
           "final": crop(f"{P}/{k}/final.png", f"{O}/{s}_final.png") if os.path.exists(f"{P}/{k}/final.png") else None}
    out["cands"] = []
    for j in range(8):
        f = f"{P}/{k}/cand{j}.png"
        out["cands"].append({"j": j, "img": crop(f, f"{O}/{s}_cand{j}.png") if os.path.exists(f) else None,
                             "iou": a["iou"].get(f"cand{j}", 0.0), "chosen": a["chosen"].index(j) if j in a["chosen"] else None})
    bc = a["best_chain"]; start = a["chosen"][bc]
    steps = [{"label": "Start", "img": f"cand{start}", "iou": a["iou"].get(f"cand{start}", 0.0)}]
    for h in a["chains"][bc][1:]:
        steps.append({"label": f"Round {h['round']}", "img": f"c{bc}_r{h['round']}", "iou": a["iou"].get(f"c{bc}_r{h['round']}", 0.0)})
    for st in steps:
        st["size"] = crop(f"{P}/{k}/{st['img']}.png", f"{O}/{s}_{st['img']}.png"); st["file"] = f"{s}_{st['img']}.png"
    out["steps"] = steps; out["best_chain"] = bc
    return out


M = {"repair_examples": [part(p) for p in ("A_00426242", "F_36088")], "filmstrip": part("A_00429445"),
     "abc": [part(p) for p in ("F_33610", "A_00436918", "A_00434010")],
     "table": json.load(open(f"{H}/stage_table.json")), "curve": json.load(open(f"{H}/repair_curve_bench_b.json")),
     "curve_sft": json.load(open(f"{H}/repair_curve_bench_b_e55.json"))}
REP = [("F_24559", "75th percentile", "Repair helps"), ("A_00423888", "Median", "No change"),
       ("A_00432894", "10th percentile", "Repair hurts")]   # per-part repair gain on bench B (SFT + GRPO, 3 chains x 6 rounds)
M["repair_rep"] = []
for pre, pct, what in REP:
    e = part(pre); k = e["key"]; a = json.load(open(f"{P}/{k}/assets.json")); c = a["chosen"][0]
    e.update(pct=pct, what=what, pick=f"{pre}_cand{c}.png", pick_size=e["cands"][c]["img"], gain=e["iou_final"] - e["iou_start"])
    M["repair_rep"].append(e)
# no-repair rows: paper config (bf16, render-compare pick, 8 drawings in flight on 8x H200) when that pass exists;
# optional repair rows: the 20 Oct full run with repair (verifier + render-compare starts, 6 drawings in flight)
def st(v): v = np.asarray(v, float); return {"mean": float(v.mean()), "std": float(v.std(ddof=1))}
RR = [json.loads(l) for l in open(f"{H}/s05_full_bench_b.jsonl")]
PB = f"{H}/throughput/bf16v3_plotpass_bench_b.jsonl"
R = [json.loads(l) for l in open(PB)] if os.path.exists(PB) else RR
pre = [r["times"]["generate"] + r["times"]["execute"] + r["times"]["select"] for r in R]
M["grpo_times"] = {"generate": st([r["times"]["generate"] for r in R]), "execute": st([r["times"]["execute"] for r in R]),
                   "select": st([r["times"]["select"] for r in R]), "total": st(pre), "n": len(R), "paper_config": R is not RR,
                   "iou": float(np.mean([r["iou_start"] for r in R])),
                   "repair": st([r["times"]["repair"] for r in RR]), "total_repair": st([r["times"]["total"] for r in RR]),
                   "iou_repair": float(np.mean([r["iou_final"] for r in RR])), "iou_repair_start": float(np.mean([r["iou_start"] for r in RR]))}
BEST = [("A_00433390", "Shelving unit"), ("A_00435801", "Cross pipe fitting"), ("A_00439477", "Plate with four posts"),
        ("F_21164", "Bored cylinder, hole ring"), ("F_132350", "Shaft with square boss"), ("F_50782", "Four-way hub"),
        ("F_57444", "Flanged pulley"), ("F_69488", "Slotted block")]
M["best"] = []
for pre, name in BEST:
    k = next(d for d in os.listdir(f"{H}/best") if d.startswith(pre)); b = f"{H}/best/{k}"; m = json.load(open(f"{b}/meta.json"))
    M["best"].append({"id": pre, "name": name, "iou": m["iou"], "drawing": crop(f"{b}/drawing.png", f"{O}/best_{pre}_drawing.png", ink=True),
                      "gt": crop(f"{b}/gt.png", f"{O}/best_{pre}_gt.png"), "pick": crop(f"{b}/pick.png", f"{O}/best_{pre}_pick.png")})
IT = f"{H}/iou_time_faces"; M["v3"] = []
for c in json.load(open(f"{IT}/callouts.json")):
    b = f"{IT}/callouts/{c['key']}"; L = c["letter"]
    c.update(drawing=crop(f"{b}/drawing.png", f"{O}/v3_{L}_drawing.png", ink=True), gt=crop(f"{b}/gt.png", f"{O}/v3_{L}_gt.png"),
             pick=crop(f"{b}/pick.png", f"{O}/v3_{L}_pick.png")); M["v3"].append(c)
M.setdefault("aspect", {})["v3"] = (lambda im: im.height / im.width)(Image.open(f"{IT}/v3_faces_time_by_iou_callouts.png"))
for c in ("repair_loop", "stage_bars", "faces_vs_pipeline_time", "repair_sft_vs_grpo", "grpo_stage_times"):
    M.setdefault("aspect", {})[c] = (lambda im: im.height / im.width)(Image.open(f"{H}/{c}.png"))
json.dump(M, open(f"{O}/manifest.json", "w"), indent=1)
print("ok", [s["label"] for s in M["filmstrip"]["steps"]], [[s["label"] for s in e["steps"]] for e in M["repair_examples"]])
