"""Seeds for family synthesis: real training-side parts (corpus 4) that e55 fails (best-of-8 < --max-best).
    python pick_seeds.py --corpus <dir> --bo <bo8 json> --n 120 --out seeds.json"""
import argparse, glob, json, os, random, collections
ap = argparse.ArgumentParser(); ap.add_argument("--corpus"); ap.add_argument("--bo"); ap.add_argument("--n", type=int, default=120)
ap.add_argument("--max-best", type=float, default=0.5); ap.add_argument("--out"); a = ap.parse_args()
man = json.load(open(os.path.join(a.corpus, "manifest.json")))["parts"]
d = json.load(open(a.bo))["candidates"]
best = {p["key"]: max(float(c.get("iou") or 0) for c in p["cands"]) for p in d}
hard = [k for k, b in best.items() if b < a.max_best]
by = collections.defaultdict(list)
for k in hard: by[man.get(k, {}).get("family", k[:1])].append(k)
print("hard parts by family:", {f: len(v) for f, v in by.items()}, "of", len(best))
random.seed(0); per = max(1, a.n // len(by)); seeds = []
for f, ks in sorted(by.items()):
    random.shuffle(ks)
    for k in ks[:per]:
        png = sorted(glob.glob(os.path.join(a.corpus, "render", "png", k + "_v*.png")))
        if png: seeds.append({"key": k, "family": f, "best": best[k], "png": png[0]})
json.dump(seeds, open(a.out, "w"), indent=1); print(len(seeds), "seeds ->", a.out)
