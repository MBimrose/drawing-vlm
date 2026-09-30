"""Offline selection study on a vr_serve log (round 1 only, policy-independent): pool = start (e55 vote pick) + the K
repair draws. Every program is executed and voxelised (64^3, bbox-centred, common cube); rules compared:
  start        keep e55's pick
  v3gate       best-v3 repair if v3 > start v3 + 0.1 (current)
  med_pool     medoid of the whole pool by mean voxel IoU to the others (start included)
  med_rep      medoid of the repairs only, adopted if its agreement with the other repairs exceeds the start's agreement with them
  med_v3veto   med_rep, but only if its v3 >= start v3 - 0.02
  oracle       best true IoU in the pool
    python rep_consensus.py <vr_serve jsonl> [--workers 96]"""
import argparse, json, os, subprocess, sys, tempfile
from concurrent.futures import ProcessPoolExecutor
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
PY = sys.executable

def vox(code, res=64):
    import trimesh
    from orient_dim_diag import occupancy
    with tempfile.TemporaryDirectory(prefix="rc_", dir="/dev/shm") as td:
        cp, stl, stp = f"{td}/c.py", f"{td}/c.stl", f"{td}/c.step"; open(cp, "w").write(code)
        try:
            if subprocess.run([PY, os.path.join(HERE, "exec_harness.py"), cp, stl, stp], capture_output=True, timeout=120).returncode or not os.path.exists(stl): return None
            m = trimesh.load(stl); side = float(max(m.extents)) * 1.02
            return occupancy(m, side, res), m.extents
        except Exception: return None

def part(r):
    s = r["hist"][0]; ds = [d for d in (r.get("rounds") or [[]])[0] if d.get("exec") and d.get("code")]
    pool = [dict(s, is_start=True)] + [dict(d, is_start=False) for d in ds]
    occ = [vox(p["code"]) for p in pool]
    keep = [i for i, o in enumerate(occ) if o is not None]
    if 0 not in keep or len(keep) < 2: return None
    # common cube: rescale by extents via re-voxelising in a shared cube of the largest extent
    import trimesh
    n = len(pool); A = np.zeros((n, n))
    # voxel IoU in each pair's own frame (bbox-centred, cube = max extent of the pair) approximated by per-mesh cubes
    for i in keep:
        for j in keep:
            if j <= i: continue
            a, b = occ[i][0], occ[j][0]
            ra = max(occ[i][1]) / max(occ[j][1])
            v = float(np.count_nonzero(a & b) / max(1, np.count_nonzero(a | b))) * min(ra, 1 / ra) ** 3   # size mismatch penalty
            A[i, j] = A[j, i] = v
    rep = [i for i in keep if i != 0]
    agree = {i: np.mean([A[i, j] for j in keep if j != i]) for i in keep}
    med_pool = max(keep, key=lambda i: agree[i])
    ag_rep = {i: np.mean([A[i, j] for j in rep if j != i]) if len(rep) > 1 else 0 for i in rep}
    ag_start = np.mean([A[0, j] for j in rep])
    mr = max(rep, key=lambda i: ag_rep[i])
    med_rep = mr if ag_rep[mr] > ag_start else 0
    med_v3 = med_rep if med_rep and pool[med_rep].get("v3", 0) >= s.get("v3", 0) - 0.02 else 0
    bv = max(rep, key=lambda i: pool[i].get("v3", 0))
    v3g = bv if pool[bv].get("v3", 0) > s.get("v3", 0) + 0.1 else 0
    iou = lambda i: pool[i]["iou"]
    return {"key": r["key"], "start": iou(0), "v3gate": iou(v3g), "med_pool": iou(med_pool), "med_rep": iou(med_rep), "med_v3veto": iou(med_v3), "oracle": max(iou(i) for i in keep)}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("log"); ap.add_argument("--workers", type=int, default=96); a = ap.parse_args()
    R = [json.loads(l) for l in open(a.log)]
    with ProcessPoolExecutor(a.workers) as ex: rows = [x for x in ex.map(part, R) if x]
    json.dump(rows, open(a.log + ".consensus.json", "w"))
    rng = np.random.default_rng(0); F = np.array([x["key"][0] for x in rows])
    for rule in ("start", "v3gate", "med_pool", "med_rep", "med_v3veto", "oracle"):
        v = np.array([x[rule] for x in rows]); st = np.array([x["start"] for x in rows]); d = v - st
        bs = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(3000)]
        print(f"{rule:11s} n={len(v)} ALL {v.mean():.3f} ({d.mean():+.3f} [{np.percentile(bs,2.5):+.3f},{np.percentile(bs,97.5):+.3f}])  A {v[F=='A'].mean():.3f}  F {v[F=='F'].mean():.3f}")
