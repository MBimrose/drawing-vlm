"""Real-part repair pairs from the DeepSeek repair search on corpus-4 (2026-09-29). Corpus 4 is training-side, so true
IoU may be used: per part, target = the best program found (start or any executing edit) if its IoU >= --min-best;
inputs = up to --per-part other executing programs from the trajectory whose IoU is <= best - --gap (start first).
Writes a candidates file of the INPUT programs (to render with render_compare --save-png-dir) and a targets map.
    python build_c4_repair.py --log c4_m10.jsonl --out-bo c4_rep_inputs.json --out-targets c4_rep_targets.json"""
import argparse, json, random
ap = argparse.ArgumentParser(); ap.add_argument("--log"); ap.add_argument("--out-bo"); ap.add_argument("--out-targets")
ap.add_argument("--min-best", type=float, default=0.6); ap.add_argument("--gap", type=float, default=0.1); ap.add_argument("--per-part", type=int, default=3)
a = ap.parse_args(); random.seed(0); bo = {"candidates": []}; tg = {}; npairs = 0
for l in open(a.log):
    r = json.loads(l); h = [x for x in r["hist"] if x.get("code") and x.get("exec", True) and "iou" in x]
    if not h: continue
    best = max(h, key=lambda x: x["iou"])
    if best["iou"] < a.min_best: continue
    ins = [x for x in h if x["iou"] <= best["iou"] - a.gap]
    if not ins: continue
    first = [x for x in ins if x["round"] == 0]; rest = [x for x in ins if x["round"] != 0]; random.shuffle(rest)
    ins = (first + rest)[: a.per_part]
    bo["candidates"].append({"key": r["key"], "cands": [{"draw": i, "code": x["code"], "iou": x["iou"], "exec": True} for i, x in enumerate(ins)]})
    tg[r["key"]] = {"code": best["code"], "iou": best["iou"]}; npairs += len(ins)
json.dump(bo, open(a.out_bo, "w")); json.dump(tg, open(a.out_targets, "w"))
print(f"{len(tg)} parts, {npairs} repair pairs")
