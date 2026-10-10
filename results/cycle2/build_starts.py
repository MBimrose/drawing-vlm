"""Cycle 2 (2026-10-09): GT-search starts = best KNOWN program per training part, over
  - the round-2 K=16 policy samples (results/cycle2/gen/<set>_<tag>.json, executing draws),
  - the round-1 tier row (results/guide/rft1/tier/accepted-000.jsonl),
  - round-1 bank entries (results/guide/bankv2_c4.json, bankv2_c2.json, bank_c1.json).
Writes results/cycle2/search/starts_<corpus>.json (bo-K format, one cand per part, field src) and
search/keys_<corpus>.txt = parts with start < --max-iou, ordered by priority: no round-1 tier program first, then
start IoU band [0.5,0.75) > [0.3,0.5) > [0.75,0.9) > [0.1,0.3) > <0.1 (closest-to-threshold first).
    python build_starts.py --tag <tag> [--max-iou 0.9]"""
import argparse, json, os
DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"; C = f"{DV}/results/cycle2"
ap = argparse.ArgumentParser(); ap.add_argument("--tag", required=True); ap.add_argument("--max-iou", type=float, default=0.9); ap.add_argument("--corpora", default="c4,c2,c1,rp2")
a = ap.parse_args()
os.makedirs(f"{C}/search", exist_ok=True)
tier = {}
for l in open(f"{DV}/results/guide/rft1/tier/accepted-000.jsonl"):
    r = json.loads(l); tier[r["key"]] = (float(r["iou"]), r["code"], "tier1")
banks = {"c4": ["bankv2_c4.json"], "c2": ["bankv2_c2.json"], "c1": ["bank_c1.json"], "rp2": []}
SETS = {"c4": ["A_c4", "C_c4"], "c2": ["A_c2", "C_c2"], "c1": ["A_c1", "C_c1"], "rp2": ["B_rp2"]}
def band(i):
    for r, (lo, hi) in enumerate(((0.5, 0.75), (0.3, 0.5), (0.75, 0.9), (0.1, 0.3), (-1, 0.1))):
        if lo <= i < hi: return r
    return 9
stats = {}
for c, sets in SETS.items():
    if c not in a.corpora.split(","): continue
    best, keys = {}, []
    for s in sets:
        f = f"{C}/gen/{s}_{a.tag}.json"
        if not os.path.exists(f): print(f"[starts] missing {f}"); continue
        for p in json.load(open(f))["candidates"]:
            keys.append(p["key"])
            for d in p["cands"]:
                if d.get("code") and d.get("exec"):
                    i = float(d.get("iou") or 0)
                    if p["key"] not in best or i > best[p["key"]][0]: best[p["key"]] = (i, d["code"], "k16")
    ks = set(keys)
    for k in ks:
        if k in tier and (k not in best or tier[k][0] > best[k][0]): best[k] = tier[k]
    for b in banks[c]:
        for k, v in json.load(open(f"{DV}/results/guide/{b}")).items():
            if k in ks and v.get("code") and (k not in best or float(v["iou"]) > best[k][0]): best[k] = (float(v["iou"]), v["code"], "bank1")
    json.dump({"candidates": [{"key": k, "cands": [{"draw": 0, "code": v[1], "exec": True, "iou": v[0], "src": v[2]}]}
                              for k, v in sorted(best.items())]}, open(f"{C}/search/starts_{c}.json.tmp", "w"))
    os.replace(f"{C}/search/starts_{c}.json.tmp", f"{C}/search/starts_{c}.json")  # atomic: gt_search2 polls for it
    todo = sorted((k for k in best if best[k][0] < a.max_iou), key=lambda k: (k in tier, band(best[k][0]), -best[k][0]))
    open(f"{C}/search/keys_{c}.txt", "w").write("\n".join(todo) + "\n")
    stats[c] = {"parts": len(ks), "with_start": len(best), "no_start": len(ks - set(best)), "to_search": len(todo),
                "start_src": {s: sum(v[2] == s for v in best.values()) for s in ("k16", "tier1", "bank1")},
                "bands": {n: sum(band(best[k][0]) == r for k in todo) for r, n in enumerate(("0.5-0.75", "0.3-0.5", "0.75-0.9", "0.1-0.3", "<0.1"))}}
    print(c, json.dumps(stats[c]), flush=True)
json.dump(stats, open(f"{C}/search/starts_stats_{a.corpora.replace(',', '_')}.json", "w"), indent=1)
