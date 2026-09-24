"""Oracle-free repair test: snap near-miss numeric literals in a candidate program to the sheet's printed values.
For each literal x with a printed value t in {v, v/2, 2v} where 0 < |x-t|/t <= --tol (and no exact match already),
replace x by t. Re-execute original and snapped programs, voxel IoU (96^3, bbox-centred, as orient_dim_diag) vs GT.
Label-free: uses only the sheet's own annotations, so it is also a candidate serving-time repair.
    python fp_snap.py --bo <bo json> --bench <bench dir> --out <json> [--tol 0.08]"""
import argparse, json, os, re, sys, tempfile, numpy as np
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from score_partials import execute
from iou import load_mesh
from orient_dim_diag import occupancy, viou
from fp_h2_dimrecall import sheet_vals
LIT = re.compile(r"(?<![\w.])(\d+\.\d+|\d+)(?![\w.])")
def snap(code, vals, tol):
    targets = sorted({t for v in vals for t in (v, v / 2, 2 * v) if t > 0})
    n = 0
    def rep(m):
        nonlocal n
        x = float(m.group(1))
        if x == 0 or any(abs(x - t) <= 1e-9 for t in targets): return m.group(1)
        best = min(targets, key=lambda t: abs(x - t) / t) if targets else None
        if best is not None and abs(x - best) / best <= tol and x >= 1.0:
            n += 1; return repr(round(best, 4))
        return m.group(1)
    # only touch assignment lines and call arguments, not ranges/counts: skip small integers used as counts
    out = []
    for line in code.splitlines():
        if re.match(r"\s*(for |range|import|from )", line) or "range(" in line: out.append(line); continue
        out.append(LIT.sub(rep, line))
    return "\n".join(out) + "\n", n
def job(a):
    key, cands, gt, vals, wd, tol = a
    g = load_mesh(gt)
    if g is None: return None
    res = []
    for c in cands:
        if not c.get("exec") or not c.get("code"): continue
        sc, n = snap(c["code"], vals, tol)
        if n == 0: res.append({"draw": c["draw"], "n": 0, "iou": c["iou"]}); continue
        ms = []
        for tag, code in (("o", c["code"]), ("s", sc)):
            stl = os.path.join(wd, f"{key}_{c['draw']}_{tag}.stl")
            ms.append(load_mesh(stl) if execute(code, stl, wd, f"{key}_{c['draw']}_{tag}", 90) else None)
        if ms[0] is None: continue
        side = 1.02 * max([float(max(g.extents))] + [min(float(max(m.extents)), 3 * float(max(g.extents))) for m in ms if m is not None])
        og = occupancy(g, side, 96)
        vo = viou(occupancy(ms[0], side, 96), og); vs = viou(occupancy(ms[1], side, 96), og) if ms[1] is not None else 0.0
        res.append({"draw": c["draw"], "n": n, "iou": c["iou"], "v_orig": vo, "v_snap": vs, "snap_exec": ms[1] is not None})
    return {"key": key, "cands": res}
ap = argparse.ArgumentParser(); ap.add_argument("--bo"); ap.add_argument("--bench"); ap.add_argument("--out"); ap.add_argument("--tol", type=float, default=0.08); ap.add_argument("--workers", type=int, default=32)
a = ap.parse_args()
bo = json.load(open(a.bo))["candidates"]; rend = json.load(open(os.path.join(a.bench, "render", "renderers.json")))
side = {k.rsplit("_v", 1)[0]: v for k, v in rend.items() if v}
wd = tempfile.mkdtemp(dir="/dev/shm")
jobs = [(p["key"], p["cands"], os.path.join(a.bench, "gt_meshes_v15", p["key"] + ".stl"), sheet_vals(side[p["key"]].get("annotations") or {}), wd, a.tol) for p in bo if p["key"] in side]
rows = [r for r in ProcessPoolExecutor(a.workers).map(job, jobs) if r]
json.dump(rows, open(a.out, "w"))
C = [c for r in rows for c in r["cands"] if c.get("n")]
d = np.array([c["v_snap"] - c["v_orig"] for c in C])
print(f"candidates snapped {len(C)} (mean {np.mean([c['n'] for c in C]):.1f} literals); snapped still execute {np.mean([c['snap_exec'] for c in C]):.1%}")
print(f"voxel IoU orig {np.mean([c['v_orig'] for c in C]):.3f} -> snapped {np.mean([c['v_snap'] for c in C]):.3f}; better by >0.05: {np.mean(d>0.05):.1%}, worse by >0.05: {np.mean(d<-0.05):.1%}")
for F in "AF":
    Cf = [c for r in rows if r["key"][0] == F for c in r["cands"] if c.get("n")]
    if Cf: print(f"  {F}: n={len(Cf)} orig {np.mean([c['v_orig'] for c in Cf]):.3f} -> snapped {np.mean([c['v_snap'] for c in Cf]):.3f}")
