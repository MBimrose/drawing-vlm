"""Score oracle b (DeepSeek code from GT description + printed labels, no image) with the orient_dim_diag voxel
proxy (96^3, bbox-centred) and compare per part with e55's first draw / vote / oracle from diag_ext_e55.json."""
import json, os, sys, numpy as np
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iou import load_mesh
from orient_dim_diag import occupancy, viou, medoid
FP, BENCH = sys.argv[1], sys.argv[2]
def one(k):
    g = load_mesh(os.path.join(BENCH, "gt_meshes_v15", k + ".stl")); m = load_mesh(os.path.join(FP, "b_stl", k + ".stl"))
    if g is None or m is None: return k, 0.0
    side = 1.02 * max(float(max(g.extents)), min(float(max(m.extents)), 3 * float(max(g.extents))))
    return k, viou(occupancy(m, side, 96), occupancy(g, side, 96))
rows = [json.loads(l) for l in open(os.path.join(FP, "oracle_b.jsonl"))]
ok = [r["key"] for r in rows if r.get("ok")]
with ProcessPoolExecutor(24) as ex: B = dict(ex.map(one, ok))
diag = {r["key"]: r for r in json.load(open("results/ext/diag_ext_e55.json"))["rows"]}
T = []
for r in rows:
    d = diag.get(r["key"])
    if not d: continue
    cs = d["cands"]; ex_ = [i for i, c in enumerate(cs) if c.get("exec") and "iou0" in c]
    i0 = [c.get("iou0", 0.0) for c in cs]; v = medoid(d["pairwise"], ex_)
    T.append((r["key"][0], B.get(r["key"], 0.0), i0[ex_[0]] if ex_ else 0.0, i0[v] if v is not None else 0.0, max(i0) if i0 else 0.0))
A = np.array([t[1:] for t in T]); fam = np.array([t[0] for t in T])
print(f"oracle b executed {len(ok)}/{len(rows)}")
for F in ("ALL", "A", "F"):
    m = np.ones(len(A), bool) if F == "ALL" else fam == F
    print(f"[{F}] n={m.sum()}  oracle-b (text, perfect description) {A[m,0].mean():.3f} | e55 first {A[m,1].mean():.3f} vote {A[m,2].mean():.3f} best-of-8 {A[m,3].mean():.3f} | b beats e55 vote on {np.mean(A[m,0]>A[m,2]+0.05):.0%} of parts")
