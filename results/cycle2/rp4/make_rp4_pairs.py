"""rp4c2 repair pairs (2026-10-09, expert iteration round 2, step 6): repairs of the NEW generator's failures on
TRAINING parts. Per part:
  target = best known program: the tier-2 row (>= 0.75; results/cycle2/tier2) else the best GT-search / DeepSeek
           program if >= --min-best (0.6, = build_c4_repair.py, the rp3 data rule);
  inputs (<= 2, executing, IoU <= target - --gap (0.1), >= 0.05, distinct code):
    (a) the GT-search start (= the best policy draw / earlier program the search repaired),
    (b) the highest-IoU K=16 policy draw below the gap (a near miss of the new generator).
realpool2 (DeepCAD) pairs are subsampled to at most the CADBench pair count (idiom balance, as in the tier-2 mix).
Hard error on any held-out file_id. Writes per corpus <out>/<c>_inputs.json (bo format, to render) and <c>_targets.json.
    python make_rp4_pairs.py --out results/cycle2/rp4"""
import argparse, json, os, random
DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"; C = f"{DV}/results/cycle2"; BD = f"{DV}/train_v14/mech/benchmarks/data"
ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--min-best", type=float, default=0.6)
ap.add_argument("--gap", type=float, default=0.1); a = ap.parse_args(); random.seed(0)
def file_id(k): return k.split("_", 1)[1].rsplit("_", 1)[0]
held = set(l.strip() for l in open(f"{BD}/heldout_file_ids.txt") if l.strip())
for hb in ("ext_bench_dw423_perm", "ext_bench_dw423", "ext_bench"):
    p = f"{BD}/{hb}/manifest.json"
    if os.path.exists(p): held |= {file_id(k) for k in json.load(open(p))["parts"]}
CORP = {"rft_corpus4": "c4", "rft_corpus2_dw423": "c2", "rft_corpus_dw423": "c1", "rft_realpool_v2": "rp2"}
SETS = {"c4": ["A_c4", "C_c4"], "c2": ["A_c2", "C_c2"], "c1": ["A_c1", "C_c1"], "rp2": ["B_rp2"]}
target, corpus_of = {}, {}
for l in open(f"{C}/tier2/accepted-000.jsonl"):
    r = json.loads(l); target[r["key"]] = (float(r["iou"]), r["code"]); corpus_of[r["key"]] = CORP[r["bench"]]
starts = {}   # key -> (iou, code) of the search start
for c in ("c4", "c2", "c1", "rp2"):
    for p in json.load(open(f"{C}/search/starts_{c}.json"))["candidates"]:
        starts[p["key"]] = (float(p["cands"][0]["iou"]), p["cands"][0]["code"]); corpus_of.setdefault(p["key"], c)
for f in ("gts_c4_p1", "gts_all", "gts_rp2", "gts_rp2b"):
    for l in open(f"{C}/search/{f}.jsonl"):
        r = json.loads(l)
        if r.get("code") and r["best_iou"] >= a.min_best and r["key"] not in target:
            target[r["key"]] = (float(r["best_iou"]), r["code"])
for f in os.listdir(f"{C}/teacher"):
    if not f.startswith("ds_"): continue
    for l in open(f"{C}/teacher/{f}"):
        r = json.loads(l); h = [x for x in r["hist"][1:] if x.get("exec") and x.get("code")]
        b = max(h, key=lambda x: x["iou"], default=None)
        if b and b["iou"] >= a.min_best and (r["key"] not in target or b["iou"] > target[r["key"]][0]):
            target[r["key"]] = (float(b["iou"]), b["code"])
near = {}     # key -> (iou, code) highest K=16 draw with iou <= target - gap
for c, sets in SETS.items():
    for s in sets:
        for p in json.load(open(f"{C}/gen/{s}_c2pol.json"))["candidates"]:
            k = p["key"]
            if k not in target: continue
            lim = target[k][0] - a.gap
            ok = [(float(x["iou"]), x["code"]) for x in p["cands"] if x.get("exec") and x.get("code") and 0.05 <= float(x["iou"]) <= lim]
            if ok: near[k] = max(ok)
out = {c: {"bo": [], "tg": {}, "n_search": 0, "n_near": 0} for c in SETS}
for k, (ti, tc) in target.items():
    if file_id(k) in held: raise SystemExit(f"FATAL held-out {k}")
    c = corpus_of.get(k)
    if c is None: continue
    ins = []
    if k in starts and 0.05 <= starts[k][0] <= ti - a.gap and starts[k][1] != tc:
        ins.append(("search", starts[k])); out[c]["n_search"] += 1
    if k in near and near[k][1] != tc and all(near[k][1] != x[1][1] for x in ins):
        ins.append(("near", near[k])); out[c]["n_near"] += 1
    if not ins: continue
    out[c]["bo"].append({"key": k, "cands": [{"draw": i, "code": x[1][1], "iou": x[1][0], "exec": True, "src": x[0]} for i, x in enumerate(ins)]})
    out[c]["tg"][k] = {"code": tc, "iou": ti}
ncad = sum(sum(len(p["cands"]) for p in out[c]["bo"]) for c in ("c4", "c2", "c1"))
random.shuffle(out["rp2"]["bo"]); kept, n = [], 0
for p in out["rp2"]["bo"]:
    if n + len(p["cands"]) > ncad: continue
    kept.append(p); n += len(p["cands"])
out["rp2"]["bo"] = kept; out["rp2"]["tg"] = {p["key"]: out["rp2"]["tg"][p["key"]] for p in kept}
os.makedirs(a.out, exist_ok=True); st = {}
for c, d in out.items():
    json.dump({"candidates": d["bo"]}, open(f"{a.out}/{c}_inputs.json", "w")); json.dump(d["tg"], open(f"{a.out}/{c}_targets.json", "w"))
    st[c] = {"parts": len(d["bo"]), "pairs": sum(len(p["cands"]) for p in d["bo"]), "search_pairs_before_cap": d["n_search"], "near_pairs_before_cap": d["n_near"],
             "mean_input_iou": round(sum(x["iou"] for p in d["bo"] for x in p["cands"]) / max(1, sum(len(p["cands"]) for p in d["bo"])), 3),
             "mean_target_iou": round(sum(v["iou"] for v in d["tg"].values()) / max(1, len(d["tg"])), 3)}
json.dump(st, open(f"{a.out}/pairs_stats.json", "w"), indent=1); print(json.dumps(st, indent=1))
