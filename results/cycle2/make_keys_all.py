"""Cycle 2: global GT-search priority list over every corpus whose starts exist (search/starts_<c>.json):
parts with start < 0.9, ordered (has round-1 tier program, IoU band [0.5,.75) > [.3,.5) > [.75,.9) > [.1,.3) > <.1, -IoU).
Keys already searched in any --exclude jsonl are dropped.  python make_keys_all.py [--exclude a.jsonl ...]"""
import argparse, json, os
C = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/cycle2"; DV = os.path.dirname(os.path.dirname(C))
ap = argparse.ArgumentParser(); ap.add_argument("--exclude", action="append", default=[]); ap.add_argument("--max-iou", type=float, default=0.9)
a = ap.parse_args()
tier = {json.loads(l)["key"] for l in open(f"{DV}/results/guide/rft1/tier/accepted-000.jsonl")}
ex = set()
for f in a.exclude:
    if os.path.exists(f): ex |= {json.loads(l)["key"] for l in open(f)}
def band(i):
    for r, (lo, hi) in enumerate(((0.5, 0.75), (0.3, 0.5), (0.75, 0.9), (0.1, 0.3), (-1, 0.1))):
        if lo <= i < hi: return r
    return 9
items, per = [], {}
for c in ("c4", "c2", "c1", "rp2"):
    f = f"{C}/search/starts_{c}.json"
    if not os.path.exists(f): continue
    n = 0
    for p in json.load(open(f))["candidates"]:
        i = float(p["cands"][0]["iou"])
        if i < a.max_iou and p["key"] not in ex:
            items.append(((p["key"] in tier, band(i), -i), p["key"])); n += 1
    per[c] = n
items.sort()
open(f"{C}/search/keys_all.txt", "w").write("\n".join(k for _, k in items) + "\n")
print(json.dumps({"keys_all": len(items), "per_corpus": per, "excluded_done": len(ex)}))
