"""H6b learning curve data: pool all rendered family parts (pilot + scale-up corpora), split by SEED into train
and held-out (the pilot bench_held seeds are always held out, plus --held-frac of the other seeds). Writes GT-code
tiers (empty think) for N in --ns (nested subsets) and an eval corpus of the held-out parts.
    python build_h6b.py --corpora <c1> <c2> --pilot-held <bench_held dir> --out <dir> --ns 500 0   (0 = all)"""
import argparse, json, os, pickle, random, shutil
ap = argparse.ArgumentParser(); ap.add_argument("--corpora", nargs="+"); ap.add_argument("--pilot-held"); ap.add_argument("--out")
ap.add_argument("--ns", nargs="+", type=int, default=[500, 0]); ap.add_argument("--held-frac", type=float, default=0.2); ap.add_argument("--max-held", type=int, default=200)
a = ap.parse_args()
parts = {}
for C in a.corpora:
    man = json.load(open(os.path.join(C, "manifest.json")))["parts"]; cache = pickle.load(open(os.path.join(C, "eval_cache_v15.pkl"), "rb"))
    for k, s in cache["samples"].items():
        code = os.path.join(C, "code", k + ".py")
        if os.path.exists(code): parts[f"{os.path.basename(C)}:{k}"] = {"C": C, "k": k, "seed": man[k]["seed"], "png": s["png"], "code": open(code).read(), "man": man[k]}
pilot_held_seeds = {v["seed"] for v in json.load(open(os.path.join(a.pilot_held, "manifest.json")))["parts"].values()}
seeds = sorted({p["seed"] for p in parts.values()} - pilot_held_seeds); random.seed(1); random.shuffle(seeds)
held_seeds = pilot_held_seeds | set(seeds[: int(len(seeds) * a.held_frac)])
train = [u for u, p in parts.items() if p["seed"] not in held_seeds]; held = [u for u, p in parts.items() if p["seed"] in held_seeds]
random.shuffle(train); random.shuffle(held); held = sorted(held[: a.max_held])
uid = lambda u: u.replace(":", "__")
for n in a.ns:
    sel = train if n == 0 else train[:n]; d = os.path.join(a.out, f"tier_n{len(sel)}"); os.makedirs(os.path.join(d, "png"), exist_ok=True)
    with open(os.path.join(d, "accepted-000.jsonl"), "w") as f:
        for u in sel:
            f.write(json.dumps({"key": uid(u), "iou": 1.0, "think": "", "code": parts[u]["code"]}) + "\n")
            open(os.path.join(d, "png", uid(u) + ".png"), "wb").write(parts[u]["png"])
    print("tier", d, len(sel), "parts,", len({parts[u]["seed"] for u in sel}), "seeds")
d = os.path.join(a.out, "bench_held2"); os.makedirs(os.path.join(d, "gt_meshes_v15"), exist_ok=True)
pickle.dump({"samples": {uid(u): {"png": parts[u]["png"], "code": parts[u]["code"], "trace": ""} for u in held}, "pools": {"certified": [uid(u) for u in held]},
             "source": "h6b held-out", "render_meta": {}}, open(os.path.join(d, "eval_cache_v15.pkl"), "wb"))
for u in held: shutil.copy(os.path.join(parts[u]["C"], "gt_meshes_v15", parts[u]["k"] + ".stl"), os.path.join(d, "gt_meshes_v15", uid(u) + ".stl"))
json.dump({"parts": {uid(u): parts[u]["man"] for u in held}}, open(os.path.join(d, "manifest.json"), "w"))
print("held-out", len(held), "parts,", len({parts[u]["seed"] for u in held}), "seeds; train pool", len(train))
