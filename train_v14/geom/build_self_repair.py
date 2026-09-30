"""Self-distilled repair pairs from vr_serve.py logs on training parts (true IoU allowed): per part, target = the best
program over all rounds' draws (and the start) if IoU >= --min-best and >= start + --gap; input = the start program
(its sheet is rendered by render_compare). Same output shape as build_c4_repair.py."""
import argparse, json
ap = argparse.ArgumentParser(); ap.add_argument("--logs", nargs="+"); ap.add_argument("--out-bo"); ap.add_argument("--out-targets")
ap.add_argument("--min-best", type=float, default=0.6); ap.add_argument("--gap", type=float, default=0.1)
a = ap.parse_args(); bo = {"candidates": []}; tg = {}
for f in a.logs:
    for l in open(f):
        r = json.loads(l); s = r["hist"][0]
        ds = [d for rd in (r.get("rounds") or []) for d in rd if d.get("exec") and d.get("code")]
        if not ds: continue
        b = max(ds, key=lambda d: d["iou"])
        if b["iou"] < a.min_best or b["iou"] < s["iou"] + a.gap: continue
        bo["candidates"].append({"key": r["key"], "cands": [{"draw": 0, "code": s["code"], "iou": s["iou"], "exec": True}]})
        tg[r["key"]] = {"code": b["code"], "iou": b["iou"]}
json.dump(bo, open(a.out_bo, "w")); json.dump(tg, open(a.out_targets, "w")); print(len(tg), "self-repair pairs")
