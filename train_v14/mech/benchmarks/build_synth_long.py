"""Long-program synthetic corpus (2026-09-22): training sheets whose GT build123d program has >= --min-ops
construction ops -- the tail where e55 writes ~8 ops for a 12-16-op program (first draw 0.59, best-of-8
0.92 on the certified pool). Output is a solve_corpus_split.sh corpus: render/png/<key>.png,
eval_cache_v15.pkl {samples:{key:{png,code,trace}}}, manifest.json, gt_meshes_v15/<key>.stl (GT code executed).
Excludes eval (uuid residue 0 mod 50), the legacy holdout (7) and exec_bad_keys.
    python build_synth_long.py --tars <tars_v14_dw423> --out <corpus dir> [--min-ops 12 --n 12000 --workers 60]
"""
import argparse, glob, io, json, os, pickle, random, re, sys, tarfile, tempfile, time
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "geom"))
OPS = re.compile(r"\b(Box|Cylinder|Sphere|Cone|Torus|Wedge|extrude|revolve|loft|sweep|fillet|chamfer|offset|Hole|CounterBoreHole|CounterSinkHole|mirror|split|Rectangle|Circle|Polyline|Polygon|Line|make_face|RegularPolygon|SlotOverall|SlotCenterToCenter|GridLocations|PolarLocations|Locations)\b")

def scan(tp):
    out = []
    try:
        with tarfile.open(tp) as t:
            for m in t:
                if m.name.endswith(".py"):
                    key = m.name[:-3]; u = key.split("_v")[0]
                    if int(u[:8], 16) % 50 in (0, 7): continue
                    code = t.extractfile(m).read().decode("utf8", "ignore")
                    out.append((key, len(OPS.findall(code)), tp))
    except Exception as e:
        print("scan fail", tp, e, flush=True)
    return out

def fetch(args):
    tp, keys, outdir, wd = args
    from score_partials import execute
    res = []
    want = set(keys); got = {}
    with tarfile.open(tp) as t:
        for m in t:
            k, ext = os.path.splitext(m.name)
            if k in want and ext in (".png", ".py"):
                got.setdefault(k, {})[ext] = t.extractfile(m).read()
    for k, d in got.items():
        if ".png" not in d or ".py" not in d: continue
        code = d[".py"].decode("utf8", "ignore")
        stl = os.path.join(outdir, "gt_meshes_v15", k + ".stl")
        ok = os.path.exists(stl) or execute(code, stl, wd, k, 90)
        if ok:
            open(os.path.join(outdir, "render", "png", k + ".png"), "wb").write(d[".png"])
            res.append((k, code))
    return res

ap = argparse.ArgumentParser()
ap.add_argument("--tars", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--min-ops", type=int, default=12); ap.add_argument("--n", type=int, default=12000)
ap.add_argument("--workers", type=int, default=60); ap.add_argument("--bad", default="")
a = ap.parse_args()
os.makedirs(os.path.join(a.out, "render", "png"), exist_ok=True); os.makedirs(os.path.join(a.out, "gt_meshes_v15"), exist_ok=True)
bad = set(open(a.bad).read().split()) if a.bad else set()
t0 = time.time(); tars = sorted(glob.glob(os.path.join(a.tars, "*.tar")))
allrows = []
with ProcessPoolExecutor(a.workers) as ex:
    for i, r in enumerate(ex.map(scan, tars, chunksize=8)):
        allrows += r
        if i % 500 == 0: print(f"scan {i}/{len(tars)} rows {len(allrows)} {time.time()-t0:.0f}s", flush=True)
allrows = [r for r in allrows if r[0] not in bad and r[0].split("_v")[0] not in bad]
import collections
hist = collections.Counter(min(r[1], 20) for r in allrows)
print("ops histogram (train, exec-good):", dict(sorted(hist.items())), flush=True)
long_ = [r for r in allrows if r[1] >= a.min_ops]
print(f"{len(long_)} of {len(allrows)} train sheets have >= {a.min_ops} ops ({len(long_)/max(1,len(allrows)):.1%})", flush=True)
random.seed(0); random.shuffle(long_); pick = long_[: int(a.n * 1.15)]   # headroom for GT exec failures
by_tar = collections.defaultdict(list)
for k, n, tp in pick: by_tar[tp].append(k)
wd = tempfile.mkdtemp(prefix="synthlong_", dir="/dev/shm")
samples = {}; ops_of = {k: n for k, n, _ in pick}
with ProcessPoolExecutor(a.workers) as ex:
    for i, r in enumerate(ex.map(fetch, [(tp, ks, a.out, wd) for tp, ks in by_tar.items()])):
        for k, code in r:
            if len(samples) < a.n: samples[k] = code
        if i % 200 == 0: print(f"fetch {i}/{len(by_tar)} kept {len(samples)} {time.time()-t0:.0f}s", flush=True)
cache = {"samples": {}, "pools": {"certified": sorted(samples)}, "source": "synth_long", "render_meta": {}}
for k, code in samples.items():
    cache["samples"][k] = {"png": open(os.path.join(a.out, "render", "png", k + ".png"), "rb").read(), "code": code, "trace": ""}
pickle.dump(cache, open(os.path.join(a.out, "eval_cache_v15.pkl"), "wb"))
json.dump({"parts": {k: {"family": "S", "gt_ops": ops_of[k]} for k in samples}, "source": "tars_v14_dw423 GT ops >= %d" % a.min_ops},
          open(os.path.join(a.out, "manifest.json"), "w"))
print(f"SYNTH LONG DONE {len(samples)} parts -> {a.out} {time.time()-t0:.0f}s")
