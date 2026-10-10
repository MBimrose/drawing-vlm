"""Cycle 2: collect GT-search (rp3, gt_search/gt_search2 rows) and DeepSeek-teacher (vis_repair_gt rows) results into
per-corpus rationalization targets {key: {code, iou, start_iou, src}} = programs that beat the part's best known start
(K=16 / round-1 tier / bank) by > 0.01 and reach >= --min-iou; plus search statistics by corpus x start band.
    python collect_search.py [--min-iou 0.75]   (inputs under results/cycle2/search, teacher; outputs search/targets_<c>.json,
    search/search_stats.json)"""
import argparse, glob, json, os
from collections import defaultdict
C = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/cycle2"
ap = argparse.ArgumentParser(); ap.add_argument("--min-iou", type=float, default=0.75); a = ap.parse_args()
start = {}
for c in ("c4", "c2", "c1", "rp2"):
    f = f"{C}/search/starts_{c}.json"
    if os.path.exists(f):
        for p in json.load(open(f))["candidates"]:
            start[p["key"]] = (c, float(p["cands"][0]["iou"]))
def band(i):
    for n, (lo, hi) in zip(("0.5-0.75", "0.3-0.5", "0.75-0.9", "0.1-0.3", "<0.1"), ((0.5, 0.75), (0.3, 0.5), (0.75, 0.9), (0.1, 0.3), (-1, 0.1))):
        if lo <= i < hi: return n
    return ">=0.9"
best = {}   # key -> dict(code, iou, start_iou, src)
st = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0.0]))   # src -> corpus|band -> [n, improved, crossed, gain]
def offer(k, code, iou, s0, src):
    c = start.get(k, ("?",))[0]
    for key in (f"{c}|{band(s0)}", f"{c}|all", "all|all"):
        r = st[src][key]; r[0] += 1; r[1] += iou > s0 + 0.01; r[2] += iou >= a.min_iou > s0; r[3] += max(0.0, iou - s0)
    if code and iou > s0 + 0.01 and iou >= a.min_iou and (k not in best or iou > best[k]["iou"]):
        best[k] = {"code": code, "iou": iou, "start_iou": s0, "src": src, "corpus": c}
seen = set()
for f in [f"{C}/search/gts_c4_p1.jsonl", f"{C}/search/gts_all.jsonl", f"{C}/search/gts_rp2.jsonl", f"{C}/search/gts_rp2b.jsonl"]:
    if not os.path.exists(f): print("missing", f); continue
    for l in open(f):
        r = json.loads(l)
        if ("rp3", r["key"]) in seen: continue
        seen.add(("rp3", r["key"]))
        offer(r["key"], r.get("code"), float(r["best_iou"]), float(r["start_iou"]), "rp3")
for f in sorted(glob.glob(f"{C}/teacher/ds_*.jsonl")):
    for l in open(f):
        r = json.loads(l); h = r["hist"]
        if not h or ("ds", r["key"]) in seen: continue
        seen.add(("ds", r["key"]))
        s0 = float(h[0].get("iou") or 0)
        cands = [x for x in h[1:] if x.get("exec") and x.get("code")]
        b = max(cands, key=lambda x: float(x["iou"]), default=None)
        offer(r["key"], b["code"] if b else None, float(b["iou"]) if b else s0, s0, "deepseek")
by_c = defaultdict(dict)
for k, v in best.items():
    by_c[v["corpus"]][k] = v
for c, d in by_c.items():
    json.dump(d, open(f"{C}/search/targets_{c}.json", "w"))
out = {src: {k: {"n": v[0], "improved": v[1], f"crossed_{a.min_iou}": v[2], "mean_gain": round(v[3] / max(1, v[0]), 4)}
             for k, v in sorted(d.items())} for src, d in st.items()}
out["targets_per_corpus"] = {c: len(d) for c, d in by_c.items()}
out["targets_by_src"] = {s: sum(v["src"] == s for v in best.values()) for s in ("rp3", "deepseek")}
json.dump(out, open(f"{C}/search/search_stats.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ("targets_per_corpus", "targets_by_src")}))
for src in st:
    print(src, json.dumps({k: v for k, v in out[src].items() if k.endswith("|all")}))
