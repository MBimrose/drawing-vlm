"""Volumetric IoU between meshes — adapted from agentic-mesh-to-cad
(cadfit_b3d/mesh_utils.py, kept verbatim where possible; see
mesh_utils_reference.py for the original).

IoU = vol(A ∩ B) / vol(A ∪ B) via manifold3d booleans, union by
inclusion-exclusion; trimesh boolean fallback on manifold failure; seeded
Monte-Carlo point-containment fallback when both boolean engines fail (e.g.
a non-watertight STL export, which previously scored a spurious 0.0);
scores > 1+1e-6 are rejected as degenerate. 0.0 only when every path fails.

For drawing→CAD the part's ORIGIN in code is arbitrary but its dimensions
and orientation are dictated by the drawing, so the headline metric centers
both meshes (bbox center → origin) without scaling. The raw (uncentered)
IoU is reported alongside.
"""
from __future__ import annotations

import numpy as np
import trimesh

try:
    import manifold3d
except ImportError:  # pragma: no cover
    manifold3d = None


def center_mesh(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    m = mesh.copy()
    bb_min, bb_max = m.bounds
    m.apply_translation(-0.5 * (bb_min + bb_max))
    return m


def _to_manifold(mesh: trimesh.Trimesh):
    if manifold3d is None or mesh is None or len(mesh.vertices) == 0 or len(mesh.faces) == 0:
        return None
    try:
        mesh = mesh.process(validate=False)
    except Exception:
        pass
    verts = np.asarray(mesh.vertices, dtype=np.float32)
    faces = np.asarray(mesh.faces, dtype=np.uint32)
    m = None
    for _attempt in range(4):  # construction is flappy under load (upstream note)
        try:
            m = manifold3d.Manifold(manifold3d.Mesh(vert_properties=verts, tri_verts=faces))
            break
        except Exception:
            m = None
            import time as _t
            _t.sleep(0.25 * (_attempt + 1))
    if m is None:
        return None
    try:
        if m.volume() == 0.0:
            return None
    except Exception:
        return None
    return m


MC_POINTS = 150_000   # ~±0.003 IoU at 1σ on typical parts (validated 2026-09-01)
MC_SEED = 0           # fixed → deterministic scores
_MC_CHUNK = 10_000    # bounds trimesh ray-containment memory


def _montecarlo_iou(mesh_a: trimesh.Trimesh, mesh_b: trimesh.Trimesh,
                    n: int | None = None, seed: int = MC_SEED) -> float:
    """Last-resort IoU: uniform points in the joint bbox, containment by ray
    parity (trimesh, needs rtree). Independent of both boolean engines, so it
    still scores meshes they cannot build. Deterministic for a fixed seed."""
    import os as _os, sys as _sys, time as _time
    _t0 = _time.time()
    if n is None:   # IOU_MC_POINTS=0 disables the fallback (score 0.0), lower values trade accuracy for speed
        n = int(_os.environ.get("IOU_MC_POINTS", MC_POINTS))
    if n <= 0:
        return 0.0
    try:
        lo = np.minimum(mesh_a.bounds[0], mesh_b.bounds[0])
        hi = np.maximum(mesh_a.bounds[1], mesh_b.bounds[1])
        if not np.all(hi > lo):
            return 0.0
        pts = np.random.default_rng(seed).uniform(lo, hi, size=(n, 3))

        def contains(m):
            return np.concatenate([m.contains(pts[i:i + _MC_CHUNK])
                                   for i in range(0, n, _MC_CHUNK)])
        ia, ib = contains(mesh_a), contains(mesh_b)
        uni = int(np.count_nonzero(ia | ib))
        iou = min(int(np.count_nonzero(ia & ib)) / uni, 1.0) if uni else 0.0
        print(f"[iou] monte-carlo fallback: iou={iou:.3f} ({_time.time() - _t0:.0f}s, "
              f"{len(mesh_a.faces)}+{len(mesh_b.faces)} faces)", file=_sys.stderr, flush=True)
        return iou
    except Exception as e:
        print(f"[iou] monte-carlo fallback FAILED: {e!r}", file=_sys.stderr, flush=True)
        return 0.0


def _trimesh_iou_fallback(mesh_a: trimesh.Trimesh, mesh_b: trimesh.Trimesh) -> float:
    try:
        inter = mesh_a.intersection(mesh_b)
        uni = mesh_a.union(mesh_b)
        if inter is None or uni is None:
            return _montecarlo_iou(mesh_a, mesh_b)
        v_inter = abs(inter.volume)
        v_uni = abs(uni.volume)
        if v_uni <= 0:
            return _montecarlo_iou(mesh_a, mesh_b)
        iou = v_inter / v_uni
        if iou > 1.0 + 1e-6:
            return _montecarlo_iou(mesh_a, mesh_b)
        return min(iou, 1.0)
    except Exception:
        return _montecarlo_iou(mesh_a, mesh_b)


def mesh_iou(mesh_a: trimesh.Trimesh, mesh_b: trimesh.Trimesh) -> float:
    """Exact volumetric IoU (agentic-mesh-to-cad semantics)."""
    if mesh_a is None or mesh_b is None:
        return 0.0
    ma, mb = _to_manifold(mesh_a), _to_manifold(mesh_b)
    if ma is None or mb is None:
        return _trimesh_iou_fallback(mesh_a, mesh_b)
    try:
        inter = manifold3d.Manifold.batch_boolean([ma, mb], manifold3d.OpType.Intersect)
    except Exception:
        return _trimesh_iou_fallback(mesh_a, mesh_b)
    if inter is None:
        return _trimesh_iou_fallback(mesh_a, mesh_b)
    try:
        v_inter = abs(inter.volume())
        va, vb = ma.volume(), mb.volume()
        if va < 0 or vb < 0:
            # Inverted winding (OCC-sew trap): per-term abs() no longer equals
            # |A∪B| — pay the explicit union boolean on this rare path.
            # (serv-08 CADFit_build123d update, 2026-08.)
            uni = manifold3d.Manifold.batch_boolean([ma, mb], manifold3d.OpType.Add)
            if uni is None:
                return _trimesh_iou_fallback(mesh_a, mesh_b)
            v_uni = abs(uni.volume())
        else:
            v_uni = abs(va) + abs(vb) - v_inter
    except Exception:
        return _trimesh_iou_fallback(mesh_a, mesh_b)
    if v_uni <= 0:
        return 0.0
    iou = v_inter / v_uni
    if iou > 1.0 + 1e-6:
        # degenerate boolean output — don't trust either operand
        return _trimesh_iou_fallback(mesh_a, mesh_b)
    return min(iou, 1.0)


def load_mesh(path: str) -> trimesh.Trimesh | None:
    try:
        m = trimesh.load(path, force="mesh")
        if m is None or len(m.faces) == 0:
            return None
        return m
    except Exception:
        return None


def iou_pair(pred_stl: str, gt_stl: str) -> dict:
    """Full comparison record for one (prediction, ground-truth) pair."""
    pred = load_mesh(pred_stl)
    gt = load_mesh(gt_stl)
    if pred is None or gt is None:
        return {"iou_raw": 0.0, "iou_centered": 0.0, "vol_pred": 0.0,
                "vol_gt": float(abs(gt.volume)) if gt is not None else 0.0,
                "mesh_ok": False}
    rec = {
        "mesh_ok": True,
        "vol_pred": float(abs(pred.volume)),
        "vol_gt": float(abs(gt.volume)),
        "iou_raw": mesh_iou(pred, gt),
        "iou_centered": mesh_iou(center_mesh(pred), center_mesh(gt)),
    }
    return rec
