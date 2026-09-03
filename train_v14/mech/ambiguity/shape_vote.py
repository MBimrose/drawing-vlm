"""Selectors that ignore the (unknown) underdetermined extent when computing
agreement.  Uses the STL cache written by exec_cands.py; no GT in selection.

  plain      : medoid on raw pairwise IoU (deployed; recomputed here as a check)
  shape_all  : every candidate anisotropically scaled to a unit box before the
               pairwise IoU -> pure shape agreement; medoid by that
  shape_axis : only the axis on which the candidates disagree most (largest
               coefficient of variation of extents) is normalised
  hybrid     : shape_axis agreement, but ties broken toward the modal extent
               (candidates whose extent on the normalised axis sits in the
               largest 3%-cluster get a bonus)
  scaled     : plain medoid, then its mesh is rescaled on the max-CV axis to
               the modal candidate extent (upper bound for "fix the extent
               after the vote"; produces a mesh, not code)

    python shape_vote.py --geom out/cand_geom_e24.jsonl --workers 8
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations

import numpy as np
import trimesh

DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
sys.path.insert(0, os.path.join(DV, "train_v14", "geom"))
os.environ.setdefault("IOU_MC_POINTS", "20000")
from iou import center_mesh, mesh_iou  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
GT_DIR = os.path.join(DV, "step_to_drw/wds_dataset/gt_meshes_v15")
TOL = 0.03


MAX_FACES = 60000   # bigger (non-manifold) meshes fall to a 4-min Monte-Carlo path per pair; treat as non-voters


def load(p):
    m = trimesh.load(p, force="mesh")
    if m is None or len(m.faces) == 0 or len(m.faces) > MAX_FACES:
        return None
    return m


def scaled(m, factors):
    n = m.copy()
    n.apply_scale(factors)
    return center_mesh(n)


def rel_err(a, b):
    return abs(a - b) / max(b, 1e-6)


def modal_value(vals):
    vs = sorted(vals); clusters = [[vs[0]]]
    for v in vs[1:]:
        if rel_err(v, clusters[-1][0]) <= TOL:
            clusters[-1].append(v)
        else:
            clusters.append([v])
    clusters.sort(key=len, reverse=True)
    return float(np.median(clusters[0])), len(clusters[0])


def part_worker(rec):
    key = rec["key"]
    cands = [c for c in rec["cands"] if c.get("stl")]
    out = {"key": key, "n": len(cands)}
    if not cands:
        out.update({k: 0.0 for k in ("plain", "shape_all", "shape_axis", "hybrid", "scaled", "oracle", "first")})
        return out
    meshes = [load(c["stl"]) for c in cands]
    keep = [i for i, m in enumerate(meshes) if m is not None]
    cands = [cands[i] for i in keep]; meshes = [meshes[i] for i in keep]
    ious = np.array([c["iou"] for c in cands])
    out["oracle"] = float(ious.max()); out["first"] = float(ious[0])
    n = len(cands)
    if n == 1:
        out.update({k: float(ious[0]) for k in ("plain", "shape_all", "shape_axis", "hybrid", "scaled")})
        return out
    ext = np.array([c["ext"] for c in cands])
    cv = ext.std(0) / np.maximum(ext.mean(0), 1e-6)
    ax = int(np.argmax(cv))
    out["max_cv_axis"] = ax; out["cv"] = cv.tolist()
    centered = [center_mesh(m) for m in meshes]
    # normalise to a 100 mm box (not unit) so manifold's epsilons do not eat small features
    unit = [scaled(m, 100.0 / np.maximum(np.array(c["ext"]), 1e-6)) for m, c in zip(meshes, cands)]
    f_axis = []
    for m, c in zip(meshes, cands):
        f = np.ones(3); f[ax] = 100.0 / max(c["ext"][ax], 1e-6)
        f_axis.append(scaled(m, f))

    def agree(ms):
        A = np.zeros((n, n))
        for a, b in combinations(range(n), 2):
            try:
                v = mesh_iou(ms[a], ms[b])
            except Exception:
                v = 0.0
            A[a, b] = A[b, a] = v
        return A.sum(1) / (n - 1)

    g_plain = agree(centered); g_all = agree(unit); g_axis = agree(f_axis)
    out["plain"] = float(ious[int(np.argmax(g_plain))])
    out["shape_all"] = float(ious[int(np.argmax(g_all))])
    out["shape_axis"] = float(ious[int(np.argmax(g_axis))])
    modal, share = modal_value(ext[:, ax].tolist())
    bonus = np.array([0.05 if rel_err(e, modal) <= TOL else 0.0 for e in ext[:, ax]])
    out["hybrid"] = float(ious[int(np.argmax(g_axis + bonus))])
    out["modal_share"] = share / n
    # 'scaled': rescale the plain medoid's mesh on the max-CV axis to the modal extent, rescore vs GT
    j = int(np.argmax(g_plain))
    f = np.ones(3); f[ax] = modal / max(cands[j]["ext"][ax], 1e-6)
    gt = load(os.path.join(GT_DIR, f"{key}.stl"))
    try:
        out["scaled"] = float(mesh_iou(scaled(meshes[j], f), center_mesh(gt))) if gt is not None else out["plain"]
    except Exception:
        out["scaled"] = out["plain"]
    out["plain_agree"] = float(g_plain.max()); out["axis_agree"] = float(g_axis.max())
    print(f"[shape_vote] {key[:8]} n={n} ax={ax} plain={out['plain']:.3f} shape_axis={out['shape_axis']:.3f} oracle={out['oracle']:.3f}", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geom", default=os.path.join(HERE, "out/cand_geom_e24.jsonl"))
    ap.add_argument("--keys", default="", help="restrict to these uuids")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", default=os.path.join(HERE, "out/shape_vote_e24.json"))
    args = ap.parse_args()
    recs = [json.loads(l) for l in open(args.geom)]
    if args.keys:
        ks = set(l.strip() for l in open(args.keys) if l.strip())
        recs = [r for r in recs if r["key"] in ks]
    print(f"[shape_vote] {len(recs)} parts", flush=True)
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        rows = list(ex.map(part_worker, recs, chunksize=2))
    json.dump(rows, open(args.out, "w"), indent=1)
    underdet = set(l.strip() for l in open(os.path.join(HERE, "keys_underdet.txt")) if l.strip())
    for label, sel in (("underdetermined", lambda r: r["key"] in underdet),
                       ("determinate ctrl", lambda r: r["key"] not in underdet)):
        rs = [r for r in rows if sel(r)]
        if not rs:
            continue
        print(f"--- {label} (n={len(rs)})")
        for k in ("first", "plain", "shape_all", "shape_axis", "hybrid", "scaled", "oracle"):
            v = np.array([r.get(k, 0.0) for r in rs])
            print(f"  {k:10s} mean={v.mean():.4f}  iou85={np.mean(v >= 0.85):.3f}  median={np.median(v):.3f}")


if __name__ == "__main__":
    main()
