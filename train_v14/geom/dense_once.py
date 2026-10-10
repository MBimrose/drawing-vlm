"""Dense geometric similarity for RL reward shaping (2026-10-07), as a subprocess like iou_once.py.

IoU is coarse on near-misses (a slightly wrong wall thickness or hole can cost most of the IoU), so GRPO gets
little signal there. Two denser, cheap terms, both centered on the bbox center as iou.center_mesh does:
  chamfer: symmetric mean nearest-neighbour surface distance (N sampled points each) minus the sampling-noise floor
           (same distance between two independent samples of the GT), normalised by the GT bbox
           diagonal, mapped to (0, 1] by exp(-d / TAU)  (TAU = 0.02 -> d = 1% of the diagonal scores 0.61)
  dims:    agreement of the sorted bbox extents, mean_i min(e_pred_i, e_gt_i) / max(e_pred_i, e_gt_i)
           (reading the drawing's overall dimensions right earns credit even when internals are off)

    python dense_once.py <pred.stl> <gt.stl>  ->  {"chamfer": 0.71, "dims": 0.93}
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

N = int(os.environ.get("DENSE_POINTS", "20000"))
TAU = float(os.environ.get("DENSE_TAU", "0.02"))


def main(pred, gt):
    import trimesh
    from scipy.spatial import cKDTree
    from iou import center_mesh, load_mesh
    a, b = load_mesh(pred), load_mesh(gt)
    if a is None or b is None or len(a.faces) == 0 or len(b.faces) == 0:
        return {"chamfer": 0.0, "dims": 0.0}
    a, b = center_mesh(a), center_mesh(b)
    ea, eb = np.sort(a.extents), np.sort(b.extents)
    dims = float(np.mean(np.minimum(ea, eb) / np.maximum(np.maximum(ea, eb), 1e-9)))
    rng = np.random.default_rng(0)
    pa = trimesh.sample.sample_surface(a, N, seed=int(rng.integers(1 << 30)))[0]
    pb = trimesh.sample.sample_surface(b, N, seed=int(rng.integers(1 << 30)))[0]
    pb2 = trimesh.sample.sample_surface(b, N, seed=int(rng.integers(1 << 30)))[0]
    d = 0.5 * (cKDTree(pb).query(pa)[0].mean() + cKDTree(pa).query(pb)[0].mean())
    floor = 0.5 * (cKDTree(pb).query(pb2)[0].mean() + cKDTree(pb2).query(pb)[0].mean())   # sampling-noise floor
    diag = float(np.linalg.norm(b.extents)) or 1.0
    return {"chamfer": float(np.exp(-(max(0.0, d - floor) / diag) / TAU)), "dims": dims}


if __name__ == "__main__":
    try:
        print(json.dumps(main(sys.argv[1], sys.argv[2])))
    except Exception as e:
        print(json.dumps({"chamfer": 0.0, "dims": 0.0, "error": f"{type(e).__name__}: {e}"}))
