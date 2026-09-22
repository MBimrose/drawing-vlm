"""Shape-level diagnostic: is a low volume IoU a wrong shape, or a right shape the metric punishes?

Volume IoU is unforgiving on thin parts: a plate 2 mm thick drawn 3 mm thick scores 0.67 though
every surface is within 1 mm. This re-executes every stored candidate of a scored best-of-N run
and, against the ground truth (both centered on their bbox centres, as the headline IoU is),
measures a thickness-insensitive surface score:
  * F@tau: harmonic mean of precision/recall of 20k surface samples within tau x GT bbox
    diagonal (tau = 1%, 2%, 5%);
  * chamfer: mean two-way nearest-surface distance / GT diagonal;
  * GT relative thickness 2V/A / max extent (V from the voxel fill when the mesh leaks).
The agreement-vote pick is the medoid of the voxel pairwise matrix in --diag (orient_dim_diag.py).

    python shape_diag.py --bo results/ext/bo8_ext_dw423p_<run>.json --diag results/ext/diag_ext_<run>.json \
        --bench <bench> --out results/ext/shape_<run>.json
"""
from __future__ import annotations

import argparse, json, os, sys, tempfile, time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from score_partials import execute  # noqa: E402
from iou import load_mesh  # noqa: E402

TAUS = (0.01, 0.02, 0.05)
NS = 20000


def centered_samples(m, n=NS, seed=0):
    import trimesh
    c = 0.5 * (m.bounds[0] + m.bounds[1])
    pts, _ = trimesh.sample.sample_surface(m, n, seed=seed)
    return pts - c


def surf_scores(p, g, diag):
    from scipy.spatial import cKDTree
    dp = cKDTree(g).query(p)[0]   # pred -> gt (precision)
    dg = cKDTree(p).query(g)[0]   # gt -> pred (recall)
    out = {"chamfer": float((dp.mean() + dg.mean()) / 2 / diag)}
    for t in TAUS:
        pr = float(np.mean(dp < t * diag)); rc = float(np.mean(dg < t * diag))
        out[f"f{int(t * 100)}"] = 2 * pr * rc / (pr + rc) if pr + rc else 0.0
        out[f"p{int(t * 100)}"] = pr; out[f"r{int(t * 100)}"] = rc
    return out


def thickness(m):
    try:
        V = float(abs(m.volume)) if m.is_watertight else None
    except Exception:
        V = None
    if V is None:
        try:
            V = float(m.voxelized(max(m.extents) / 96).fill().volume)
        except Exception:
            V = 0.0
    A = float(m.area)
    return (2 * V / A if A else 0.0), V, A


def part_job(args):
    key, cands, gt_path, workdir, timeout = args
    t0 = time.time()
    gt = load_mesh(gt_path)
    if gt is None:
        return {"key": key, "err": "no gt"}
    diag = float(np.linalg.norm(gt.extents))
    t, V, A = thickness(gt)
    g = centered_samples(gt, seed=1)
    out = []
    for c in cands:
        d = c.get("draw"); rec = {"draw": d, "iou": float(c.get("iou", 0.0) or 0.0)}
        code = c.get("code") or ""
        if code:
            stl = os.path.join(workdir, f"{key}__{d}.stl")
            if execute(code, stl, workdir, f"{key}__{d}", timeout):
                m = load_mesh(stl)
                try:
                    os.remove(stl)
                except OSError:
                    pass
                if m is not None and len(m.faces):
                    try:
                        rec.update(surf_scores(centered_samples(m), g, diag))
                        rec["ext_ratio"] = (np.sort(m.extents) / np.maximum(np.sort(gt.extents), 1e-6)).tolist()
                    except Exception as e:
                        rec["err"] = f"{type(e).__name__}: {e}"
        out.append(rec)
    return {"key": key, "cands": out, "gt_diag": diag, "gt_thick": t, "gt_rel_thick": t / float(max(gt.extents)),
            "gt_vol": V, "gt_area": A, "gt_faces": int(len(gt.faces)), "secs": round(time.time() - t0, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bo", required=True); ap.add_argument("--diag", required=True)
    ap.add_argument("--bench", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=32); ap.add_argument("--timeout", type=int, default=90)
    a = ap.parse_args()
    parts = json.load(open(a.bo))["candidates"]
    base = "/dev/shm" if os.path.isdir("/dev/shm") else None
    wd = tempfile.mkdtemp(prefix="shape_", dir=base)
    jobs = [(p["key"], p["cands"], os.path.join(a.bench, "gt_meshes_v15", p["key"] + ".stl"), wd, a.timeout) for p in parts]
    rows = []; t0 = time.time()
    with ProcessPoolExecutor(a.workers) as ex:
        for i, r in enumerate(ex.map(part_job, jobs), 1):
            rows.append(r)
            if i % 20 == 0:
                print(f"  {i}/{len(jobs)} {time.time() - t0:.0f} s", flush=True)
    diag = {r["key"]: r for r in json.load(open(a.diag))["rows"]}
    for r in rows:
        dr = diag.get(r["key"])
        if not dr or "cands" not in r:
            continue
        ex_ = [i for i, c in enumerate(dr["cands"]) if c.get("exec") and "iou0" in c]
        best, bs = None, -1
        for i in ex_:
            s = sum(dr["pairwise"].get(f"{min(i, j)},{max(i, j)}", 0.0) for j in ex_ if j != i)
            if s > bs:
                best, bs = i, s
        r["vote_idx"] = best
    json.dump({"bo": a.bo, "rows": rows}, open(a.out, "w"))
    print("SHAPE DONE", a.out, f"{time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
