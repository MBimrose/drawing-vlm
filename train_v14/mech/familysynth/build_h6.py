"""H6 overfit test data: seed-disjoint split of rendered family parts into TRAIN (GT code rows, empty think ->
trained as no-think) and HELD (unseen seeds/families). Writes:
  <out>/train_tier/accepted-000.jsonl + png/ (for pack_rft_shards_dir)
  <out>/bench_train, <out>/bench_held : eval corpora (eval_cache_v15.pkl with pools.certified, gt_meshes_v15 links)
    python build_h6.py --corpus <family corpus> --out <dir> --n 50"""
import argparse, json, os, pickle, random, shutil, glob
ap = argparse.ArgumentParser(); ap.add_argument("--corpus"); ap.add_argument("--out"); ap.add_argument("--n", type=int, default=50); a = ap.parse_args()
C = a.corpus; man = json.load(open(os.path.join(C, "manifest.json")))["parts"]
cache = pickle.load(open(os.path.join(C, "eval_cache_v15.pkl"), "rb"))
keys = [k for k in cache["samples"] if os.path.exists(os.path.join(C, "code", k + ".py"))]
by_seed = {}
for k in keys: by_seed.setdefault(man[k]["seed"], []).append(k)
seeds = sorted(by_seed); random.seed(0); random.shuffle(seeds)
train, held = [], []
for s in seeds:
    tgt = train if len(train) <= len(held) else held
    if len(tgt) < a.n: tgt.extend(by_seed[s])
train, held = train[: a.n], held[: a.n]
assert not ({man[k]["seed"] for k in train} & {man[k]["seed"] for k in held})
os.makedirs(os.path.join(a.out, "train_tier", "png"), exist_ok=True)
with open(os.path.join(a.out, "train_tier", "accepted-000.jsonl"), "w") as f:
    for k in train:
        f.write(json.dumps({"key": k, "iou": 1.0, "think": "", "code": open(os.path.join(C, "code", k + ".py")).read()}) + "\n")
        open(os.path.join(a.out, "train_tier", "png", k + ".png"), "wb").write(cache["samples"][k]["png"])
for name, ks in (("bench_train", train), ("bench_held", held)):
    d = os.path.join(a.out, name); os.makedirs(os.path.join(d, "gt_meshes_v15"), exist_ok=True)
    sub = {"samples": {k: cache["samples"][k] for k in ks}, "pools": {"certified": sorted(ks)}, "source": cache.get("source"), "render_meta": {}}
    pickle.dump(sub, open(os.path.join(d, "eval_cache_v15.pkl"), "wb"))
    for k in ks: shutil.copy(os.path.join(C, "gt_meshes_v15", k + ".stl"), os.path.join(d, "gt_meshes_v15", k + ".stl"))
    json.dump({"parts": {k: man[k] for k in ks}}, open(os.path.join(d, "manifest.json"), "w"))
print(f"train {len(train)} parts / {len({man[k]['seed'] for k in train})} seeds; held {len(held)} parts / {len({man[k]['seed'] for k in held})} seeds")
