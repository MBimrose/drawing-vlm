"""Build a real-part RFT tier as the union of an existing tier and new generation outputs.

    python build_union_tier.py <out_dir> --base <tier_dir>... --new <gen_out_dir>... [--max-per-key 6] [--min-iou 0.8]

Rows: {key, iou, ok, think, code, sample} from accepted-*.jsonl of every input. Rows whose
think cites privileged-hint quantities (mm^3, octant, centre of mass, fill fraction,
"measured properties") are dropped. Per key the best --max-per-key rows by IoU are kept.
Writes <out>/accepted-000.jsonl, <out>/keys.txt (for the PNG fetch) and <out>/README.md.
"""
import argparse, glob, json, os, re, collections, datetime
ap = argparse.ArgumentParser()
ap.add_argument("out"); ap.add_argument("--base", nargs="*", default=[]); ap.add_argument("--new", nargs="*", default=[])
ap.add_argument("--max-per-key", type=int, default=6); ap.add_argument("--min-iou", type=float, default=0.8)
a = ap.parse_args()
LEAK = re.compile(r"mm\^3|mm³|octant|cent(?:re|er) of mass|fill(?:ed)? fraction|of the bounding box|measured propert|material fraction", re.I)
rows = collections.defaultdict(list); dropped = 0; src = collections.Counter()
for d in a.base + a.new:
    for f in sorted(glob.glob(os.path.join(d, "accepted-*.jsonl"))):
        for l in open(f):
            r = json.loads(l)
            if not r.get("code") or r.get("iou", 0) < a.min_iou:
                continue
            if d in a.new and LEAK.search(r.get("think") or ""):
                dropped += 1; continue
            rows[r["key"]].append({k: r.get(k) for k in ("key", "iou", "ok", "think", "code", "sample")} | {"src": os.path.basename(d.rstrip("/"))})
            src[os.path.basename(d.rstrip("/"))] += 1
os.makedirs(a.out, exist_ok=True); n = 0
with open(os.path.join(a.out, "accepted-000.jsonl"), "w") as f, open(os.path.join(a.out, "keys.txt"), "w") as kf:
    for k in sorted(rows):
        seen = set(); kept = 0
        for r in sorted(rows[k], key=lambda r: -r["iou"]):
            h = hash(r["code"].strip())
            if h in seen: continue
            seen.add(h); f.write(json.dumps(r) + "\n"); kept += 1; n += 1
            if kept >= a.max_per_key: break
        kf.write(k + "\n")
new_keys = {k for k in rows if all(r["src"] not in [os.path.basename(b.rstrip("/")) for b in a.base] for r in rows[k])}
msg = (f"Union tier built {datetime.date.today()}: {len(rows)} keys, {n} rows (max {a.max_per_key}/key, iou>={a.min_iou}); "
       f"{len(new_keys)} keys new vs base; {dropped} hint-leaking rows dropped. Sources: {dict(src)}")
open(os.path.join(a.out, "README.md"), "w").write(msg + "\n"); print(msg)
