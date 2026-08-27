# Reference: wpk-serv-08:/srv/scratch/bimrose2/CADFit_build123d/cadfit_b3d/mesh_utils.py (canonical, per user 2026-08-20)
"""Mesh utilities: normalization, IoU via manifold3d, residual computation.

IoU is computed as volume(A ∩ B) / volume(A ∪ B) using manifold3d's boolean
engine. Inputs are converted to guaranteed-watertight manifolds via trimesh
repair + manifold3d's vertex-merging; if that fails the mesh is skipped.
"""
from __future__ import annotations

import os
import numpy as np
import trimesh
import manifold3d


def normalize_mesh(mesh: trimesh.Trimesh, target_min: float = -1.0,
                   target_max: float = 1.0) -> trimesh.Trimesh:
    """Center and uniformly scale mesh so its largest extent fits [target_min, target_max]."""
    bb_min = mesh.bounds[0]
    bb_max = mesh.bounds[1]
    center = 0.5 * (bb_min + bb_max)
    max_dim = float((bb_max - bb_min).max())
    if max_dim > 0:
        scale = (target_max - target_min) / max_dim
        mesh.apply_translation(-center)
        mesh.apply_scale(scale)
    return mesh


def load_mesh(path: str, normalize: bool = False) -> trimesh.Trimesh:
    """Load a mesh from disk, optionally normalizing to [-1, 1]."""
    mesh = trimesh.load(path, force='mesh')
    if normalize:
        mesh = normalize_mesh(mesh)
    return mesh


def mesh_volume(mesh: trimesh.Trimesh) -> float:
    """Absolute volume of a mesh. Returns 0 for empty/degenerate input."""
    try:
        return abs(mesh.volume)
    except Exception:
        return 0.0


def _to_manifold(mesh: trimesh.Trimesh):
    """Build a manifold3d.Manifold from a trimesh mesh.

    Returns None if the mesh is empty or manifold3d can't build a non-zero-volume
    solid from it. Tries a basic trimesh fill_holes + dedupe first.
    """
    if mesh is None or len(mesh.vertices) == 0 or len(mesh.faces) == 0:
        return None
    try:
        mesh = mesh.process(validate=False)
    except Exception:
        pass
    verts = np.asarray(mesh.vertices, dtype=np.float32)
    faces = np.asarray(mesh.faces, dtype=np.uint32)
    m = None
    for _attempt in range(4):  # construction is flappy under load
        try:
            m = manifold3d.Manifold(manifold3d.Mesh(vert_properties=verts, tri_verts=faces))
            break
        except Exception:
            m = None
            # Back-to-back retries land in the same contention spike;
            # a short sleep rides it out.
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


_MANIFOLD_CACHE: dict = {}
_CACHE_MAX = 256  # a part's pass builds dozens of trial manifolds; at 32 the
# FIFO evicted the TARGET's manifold before refinement needed it, so
# residual_meshes rebuilt under load and flapped (hex_bolt 0.82).


def _cached_manifold(mesh: trimesh.Trimesh, key: tuple):
    if key in _MANIFOLD_CACHE:
        return _MANIFOLD_CACHE[key]
    if len(_MANIFOLD_CACHE) >= _CACHE_MAX:
        _MANIFOLD_CACHE.pop(next(iter(_MANIFOLD_CACHE)))
    m = _to_manifold(mesh)
    if m is not None:  # don't cache failures — construction can be flappy
        _MANIFOLD_CACHE[key] = m
    return m


def _mesh_key(mesh: trimesh.Trimesh):
    """Cheap content key for manifold caching (counts + full bounds + volume).

    Uses the FULL bounds tuple, not bounds.sum(): a mesh and its mirror share
    vertex/face counts, |volume|, AND a symmetric bounds sum (equal when the
    bbox is centered), so a sum-based key collides them -> the cache returns
    the wrong manifold and scores the wrong IoU. The min/max bounds tuple
    discriminates the mirror. Key changes only affect cache hit/miss, never a
    computed value (a miss recomputes the identical manifold), so this is a
    pure bug-fix for wrong-cache-hit collisions.
    """
    try:
        b = mesh.bounds
        return (len(mesh.vertices), len(mesh.faces),
                round(float(b[0][0]), 9), round(float(b[0][1]), 9),
                round(float(b[0][2]), 9), round(float(b[1][0]), 9),
                round(float(b[1][1]), 9), round(float(b[1][2]), 9),
                round(float(abs(mesh.volume)), 9))
    except Exception:
        return None


def mesh_iou(mesh_a: trimesh.Trimesh, mesh_b: trimesh.Trimesh,
             verbose: bool = False) -> float:
    """Volumetric IoU between two meshes via manifold3d booleans.

    Returns 0.0 on any failure (degenerate inputs, boolean errors, zero union).
    Falls back to trimesh-based boolean ops if manifold3d construction fails
    (common with non-watertight loft STL exports).
    """
    if mesh_a is None or mesh_b is None:
        return 0.0
    # CADFIT_XCACHE: (v_inter, v_uni) is a pure function of the two
    # meshes' exact content; concurrent arms score largely identical
    # (candidate, target) and (assembly, target) pairs. Only the
    # manifold3d-success path publishes (the trimesh fallback is the
    # flap-prone path); the hit replays the exact final float math.
    from . import xcache
    _xk = None
    if xcache.enabled():
        _da, _db = xcache.mesh_digest(mesh_a), xcache.mesh_digest(mesh_b)
        if _da is not None and _db is not None:
            _xk = xcache.compose_key(b"meshiou-v1", _da, _db)
            _hit = xcache.lookup("meshiou", _xk)
            if _hit is not None:
                _vi, _vu = _hit
                if _vu <= 0:
                    return 0.0
                return min(_vi / _vu, 1.0)
    # The target mesh recurs across hundreds of IoU calls per part; cache
    # its manifold construction by content key.
    ka, kb = _mesh_key(mesh_a), _mesh_key(mesh_b)
    ma = _cached_manifold(mesh_a, ka) if ka is not None else _to_manifold(mesh_a)
    mb = _cached_manifold(mesh_b, kb) if kb is not None else _to_manifold(mesh_b)
    if ma is None or mb is None:
        if verbose:
            print(f"[IoU] manifold construction failed (ma={ma is not None}, mb={mb is not None}), trying trimesh fallback")
        return _trimesh_iou_fallback(mesh_a, mesh_b, verbose=verbose)

    try:
        inter = manifold3d.Manifold.batch_boolean([ma, mb], manifold3d.OpType.Intersect)
    except Exception as e:
        if verbose:
            print(f"[IoU] boolean failed: {e}, trying trimesh fallback")
        return _trimesh_iou_fallback(mesh_a, mesh_b, verbose=verbose)

    if inter is None:
        return _trimesh_iou_fallback(mesh_a, mesh_b, verbose=verbose)

    try:
        # Inclusion-exclusion: vol(A∪B) = vol(A) + vol(B) − vol(A∩B) holds
        # exactly for the valid manifolds manifold3d guarantees, so the
        # union boolean (half the boolean cost of every IoU call) is
        # replaced by two cheap volume property reads.
        va, vb = ma.volume(), mb.volume()
        v_inter = abs(inter.volume())
        if va < 0 or vb < 0:
            # Inverted winding: per-term abs() no longer equals |A∪B|
            # (the OCC-sew/winding trap class). Pay the explicit union
            # boolean on this rare path — exact parity with the
            # pre-inclusion-exclusion scorer.
            uni = manifold3d.Manifold.batch_boolean(
                [ma, mb], manifold3d.OpType.Add)
            if uni is None:
                return _trimesh_iou_fallback(mesh_a, mesh_b, verbose=verbose)
            v_uni = abs(uni.volume())
        else:
            v_uni = abs(va) + abs(vb) - v_inter
    except Exception:
        return _trimesh_iou_fallback(mesh_a, mesh_b, verbose=verbose)

    if v_uni <= 0:
        return 0.0
    iou = v_inter / v_uni
    if iou > 1.0 + 1e-6:
        # Impossible by definition: a degenerate manifold (self-intersecting
        # boolean output) produced a bogus volume (E8 v3's 00010020 recorded
        # 1.18 in-process; the honest re-executed score was 0.9985). Don't
        # trust either operand — fall back to the trimesh path.
        return _trimesh_iou_fallback(mesh_a, mesh_b, verbose=verbose)
    if verbose:
        print(f"[IoU] inter={v_inter:.6f} uni={v_uni:.6f} iou={iou:.6f}")
    if _xk is not None:
        xcache.publish("meshiou", _xk, (float(v_inter), float(v_uni)))
    return min(iou, 1.0)


# R-8 cross-engine visibility: count of trimesh-fallback fires in this
# process. mesh_level_trim (silhouette_trim.py) samples it around each accept
# decision so a flap-prone cross-engine score is LOGGED at the decision site
# (the unconditional stderr line below is off the parsed stdout). Receipts
# only — never read by any decision path; incrementing it changes no output.
TRIMESH_FALLBACK_FIRES = 0


def _trimesh_iou_fallback(mesh_a: trimesh.Trimesh, mesh_b: trimesh.Trimesh,
                           verbose: bool = False) -> float:
    """Fallback IoU using trimesh boolean ops. Less accurate but works on
    non-watertight meshes."""
    global TRIMESH_FALLBACK_FIRES
    TRIMESH_FALLBACK_FIRES += 1
    # Cross-engine visibility: this trimesh path can score differently than the
    # manifold3d path, so a single run can mix engines. Announce unconditionally
    # (to stderr, off the parsed stdout) so cross-engine scores are traceable.
    import sys as _sys
    print("[IoU] trimesh boolean fallback fired (cross-engine score possible)",
          file=_sys.stderr, flush=True)
    try:
        inter = mesh_a.intersection(mesh_b)
        uni = mesh_a.union(mesh_b)
        if inter is None or uni is None:
            return 0.0
        v_inter = abs(inter.volume)
        v_uni = abs(uni.volume)
        if v_uni <= 0:
            return 0.0
        iou = v_inter / v_uni
        if iou > 1.0 + 1e-6:
            if verbose:
                print(f"[IoU-trimesh] impossible iou {iou:.4f}, treating as failure")
            return 0.0
        if verbose:
            print(f"[IoU-trimesh] inter={v_inter:.6f} uni={v_uni:.6f} iou={iou:.6f}")
        return min(iou, 1.0)
    except Exception as e:
        if verbose:
            print(f"[IoU-trimesh] fallback also failed: {e}")
        return 0.0


def mesh_iou_path(path_a: str, path_b: str, normalize_a: bool = False,
                  verbose: bool = False) -> float:
    """IoU between two meshes on disk, with LRU caching on the ground-truth side."""
    key = (path_a, os.path.getmtime(path_a) if os.path.exists(path_a) else None, normalize_a)
    ma = _cached_manifold(load_mesh(path_a, normalize=normalize_a) if normalize_a else load_mesh(path_a), key)
    mb_mesh = load_mesh(path_b)
    mb = _to_manifold(mb_mesh)
    if ma is None or mb is None:
        if verbose:
            print(f"[IoU] manifold construction failed (ma={ma is not None}, mb={mb is not None})")
        return 0.0
    try:
        inter = manifold3d.Manifold.batch_boolean([ma, mb], manifold3d.OpType.Intersect)
    except Exception as e:
        if verbose:
            print(f"[IoU] boolean failed: {e}")
        return 0.0
    if inter is None:
        return 0.0
    try:
        # Same inclusion-exclusion shortcut as mesh_iou, with the same
        # inverted-winding guard (explicit union on negative volumes).
        va, vb = ma.volume(), mb.volume()
        v_inter = abs(inter.volume())
        if va < 0 or vb < 0:
            uni = manifold3d.Manifold.batch_boolean(
                [ma, mb], manifold3d.OpType.Add)
            if uni is None:
                return 0.0
            v_uni = abs(uni.volume())
        else:
            v_uni = abs(va) + abs(vb) - v_inter
    except Exception:
        return 0.0
    if v_uni <= 0:
        return 0.0
    iou = v_inter / v_uni
    if iou > 1.0 + 1e-6:
        # Impossible by definition (a degenerate self-intersecting boolean
        # output produced a bogus volume). mesh_iou falls back to trimesh
        # here; this ABC-scoring path has no fallback, so reject the
        # untrustworthy score rather than report an impossible >1.0 IoU.
        if verbose:
            print(f"[IoU] impossible iou {iou:.4f}, treating as failure")
        return 0.0
    if verbose:
        print(f"[IoU] inter={v_inter:.6f} uni={v_uni:.6f} iou={iou:.6f}")
    return min(iou, 1.0)


def residual_meshes(target: trimesh.Trimesh, current: trimesh.Trimesh):
    """Compute (under, over) residual meshes: target - current, current - target.

    Returns (None, None) if either input is None or the boolean fails.
    Components with near-zero volume are filtered out.
    """
    if target is None or current is None:
        return None, None
    # Primary path: manifold3d Subtract on the same construction that
    # mesh_iou uses — trimesh's .difference() wrapper was observed failing
    # on mesh pairs whose IoU boolean had just succeeded (the gear/pulley
    # iters=0 flap). Fall back to trimesh per side.
    under = over = None
    # Order matters: trimesh's difference produces tessellation whose
    # downstream sketch profiles execute reliably in OCCT (gear's over-cut
    # exec-fails when built from raw manifold output), so try it FIRST;
    # the manifold-direct path is the rescue when the trimesh wrapper
    # flaps (its historical failure mode).
    try:
        under = target.difference(current)
    except Exception:
        under = None
    try:
        over = current.difference(target)
    except Exception:
        over = None
    if under is None or over is None:
        kt, kc = _mesh_key(target), _mesh_key(current)
        ma = _cached_manifold(target, kt) if kt is not None else _to_manifold(target)
        mb = _cached_manifold(current, kc) if kc is not None else _to_manifold(current)
    else:
        ma = mb = None

    def _sub_to_trimesh(x, y):
        try:
            m = manifold3d.Manifold.batch_boolean([x, y], manifold3d.OpType.Subtract)
            if m is None or abs(m.volume()) < 1e-9:
                return None
            mm = m.to_mesh()
            tm = trimesh.Trimesh(
                vertices=np.asarray(mm.vert_properties)[:, :3],
                faces=np.asarray(mm.tri_verts), process=False)
            # Clean the raw manifold output: unmerged vertices/slivers
            # yield sketch profiles whose downstream OCCT booleans fail
            # (gear's over-cut exec-failed deterministically).
            try:
                tm.merge_vertices()
                tm.update_faces(tm.nondegenerate_faces())
                tm = tm.process(validate=False)
            except Exception:
                pass
            return tm
        except Exception:
            return None
    if ma is not None and mb is not None:
        if under is None:
            under = _sub_to_trimesh(ma, mb)
        if over is None:
            over = _sub_to_trimesh(mb, ma)

    def _clean(m):
        if m is None or not hasattr(m, 'volume'):
            return None
        try:
            if abs(m.volume) < 1e-6:
                return None
        except Exception:
            return None
        try:
            if hasattr(m, 'split'):
                components = m.split()
                if len(components) > 1:
                    big = [c for c in components if abs(c.volume) > 1e-6]
                    if big:
                        return trimesh.util.concatenate(big) if len(big) > 1 else big[0]
        except Exception:
            pass
        return m

    return _clean(under), _clean(over)


def robust_mesh_boolean(a: trimesh.Trimesh, b: trimesh.Trimesh, op: str):
    """Boolean a op b ("difference" = a - b, "union") with the residual_meshes
    reliability pattern: trimesh wrapper first (its tessellation executes
    reliably downstream), manifold3d batch_boolean as the rescue when the
    wrapper flaps (its historical failure mode). Returns None on failure.
    """
    if a is None or b is None:
        return None
    result = None
    try:
        result = a.difference(b) if op == "difference" else a.union(b)
    except Exception:
        result = None
    if result is not None and len(result.faces) > 0:
        return result
    ka, kb = _mesh_key(a), _mesh_key(b)
    ma = _cached_manifold(a, ka) if ka is not None else _to_manifold(a)
    mb = _cached_manifold(b, kb) if kb is not None else _to_manifold(b)
    if ma is None or mb is None:
        return None
    try:
        mtype = (manifold3d.OpType.Subtract if op == "difference"
                 else manifold3d.OpType.Add)
        m = manifold3d.Manifold.batch_boolean([ma, mb], mtype)
        if m is None or abs(m.volume()) < 1e-9:
            return None
        mm = m.to_mesh()
        tm = trimesh.Trimesh(
            vertices=np.asarray(mm.vert_properties)[:, :3],
            faces=np.asarray(mm.tri_verts), process=False)
        # Clean the raw manifold output (unmerged vertices/slivers), same as
        # residual_meshes' rescue path.
        try:
            tm.merge_vertices()
            tm.update_faces(tm.nondegenerate_faces())
            tm = tm.process(validate=False)
        except Exception:
            pass
        return tm
    except Exception:
        return None


# --- Cached trimesh-exact booleans -----------------------------------------
# assemble_program's forward rounds re-run current.union(cand)/difference(cand)
# for every candidate every round; trimesh's boolean_manifold rebuilds the
# manifold3d.Manifold of BOTH operands on every call. The conversion below is
# byte-identical to trimesh's (fp32 vertices, uint32 faces, no processing,
# result Trimesh(process=False)) but caches operand Manifolds keyed by object
# id — safe because the cache holds a strong reference (id can't be recycled)
# and assembly never mutates operand meshes in place.

_RAW_MANIFOLD_CACHE: dict = {}
# 2026-08-04 incident: at 64 entries this cache PINNED dozens of
# multi-million-face forward-selection intermediates (mesh + Manifold,
# strong refs) — one selection worker ballooned to 311 GiB and the load
# spike took the node's production services down. The cache's win is the
# REPEATING `current` operand within a forward round; 4 entries capture
# that (current + candidate + 2 spare) and bound the pin to a few GB.
_RAW_CACHE_MAX = int(os.environ.get("CADFIT_RAW_MANIFOLD_CACHE", "4"))


def _mesh_sentinel(mesh: trimesh.Trimesh):
    """Near-free staleness sentinel for the id()-keyed cache: catches
    gross in-place mutation (vertex count / first-vertex change) without
    hashing the whole mesh. Discipline still forbids in-place edits."""
    n = len(mesh.vertices)
    return (n, len(mesh.faces),
            float(mesh.vertices[0, 0]) if n else 0.0)


def _raw_manifold(mesh: trimesh.Trimesh):
    key = id(mesh)
    sent = _mesh_sentinel(mesh)
    hit = _RAW_MANIFOLD_CACHE.get(key)
    if hit is not None and hit[0] is mesh and hit[2] == sent:
        return hit[1]
    m = manifold3d.Manifold(
        mesh=manifold3d.Mesh(
            vert_properties=np.array(mesh.vertices, dtype=np.float32),
            tri_verts=np.array(mesh.faces, dtype=np.uint32)))
    if len(_RAW_MANIFOLD_CACHE) >= _RAW_CACHE_MAX:
        _RAW_MANIFOLD_CACHE.pop(next(iter(_RAW_MANIFOLD_CACHE)))
    _RAW_MANIFOLD_CACHE[key] = (mesh, m, sent)
    return m


def cached_boolean(a: trimesh.Trimesh, b: trimesh.Trimesh, operation: str
                   ) -> trimesh.Trimesh:
    """Drop-in for trimesh's a.union(b) / a.difference(b) (manifold engine),
    producing the identical result mesh, with operand-conversion caching.
    Raises like trimesh on non-volume inputs."""
    if not (a.is_volume and b.is_volume):
        raise ValueError("Not all meshes are volumes!")
    ma, mb = _raw_manifold(a), _raw_manifold(b)
    rm = (ma - mb) if operation == "difference" else (ma + mb)
    out = rm.to_mesh()
    return trimesh.Trimesh(vertices=out.vert_properties, faces=out.tri_verts,
                           process=False)


def sample_surface_points(mesh: trimesh.Trimesh, n: int = 10000):
    """Uniformly sample points + face normals from the mesh surface."""
    points, face_indices = mesh.sample(n, return_index=True)
    return points, face_indices, mesh.face_normals[face_indices]


# --- R1: Hausdorff / max-residual honesty diagnostic (rails, ΔIoU=0) ---------
# Report Sec 3.3 signature: LOW Chamfer/high-IoU + HIGH one-sided Hausdorff =
# a localized hallucinated fill (the filled-blind-hole failure mode mean-IoU
# forgives). This is a DIAGNOSTIC only — it never gates or banks a score.

def _one_sided_nn(src_pts, dst_pts):
    """Nearest-neighbour distance from each src point to the dst point set."""
    from scipy.spatial import cKDTree
    d, _ = cKDTree(dst_pts).query(src_pts)
    return d


def residual_distances(recon: trimesh.Trimesh, gt: trimesh.Trimesh,
                       n_samples: int = 30000, seed: int = 0,
                       normalize_gt: bool = True,
                       normalize_recon: bool = False):
    """Deterministic one-sided residual (Hausdorff-class) distances between a
    reconstruction and its ground truth, in the SHIPPED scoring frame.

    The harness scores ``mesh_iou(recon, normalize_mesh(GT))`` — recon arrives
    already in the normalized [-1, 1] input frame and GT is normalized to it —
    so by default GT is normalized and recon is used AS-IS. Re-normalizing recon
    would rescale it to its own bbox and HIDE the exact over-build this diagnostic
    exists to catch (measured: it moved 00033724 IoU 0.6824 -> 0.6644).

    Point-cloud estimator: seeded ``sample_surface(seed=seed)`` on both surfaces
    + KD-tree nearest-neighbour. Two directions:

      recon_to_gt_* : recon surface -> nearest GT surface (over-build /
                      hallucinated protrusion or fill worst case)
      gt_to_recon_* : GT surface -> nearest recon surface (missing feature /
                      FILLED-BLIND-HOLE worst case — the v_block mode mean-IoU
                      forgives, report Sec 3.3)

    Each direction reports max (true worst case, sampling-noisy) + p99/p95
    (robust worst case) + mean. ``hausdorff`` is the symmetric max and
    ``hausdorff_p99`` its robust form. Distances are in normalized units (the
    shared [-1, 1] frame, comparable across parts); ``bbox_diag`` (of normalized
    GT) is reported so a fractional threshold (e.g. R3's ~0.05·bbox-diag support
    check) is directly computable. Deterministic for a fixed seed.

    Point-cloud (not exact point-to-surface) is deliberate: it is seconds per row
    (0.1-0.2s vs 30-50s on 100k-500k-face parts) with an ~inter-sample-spacing
    floor (~0.005 in the normalized frame) that sits far below the honesty
    threshold (filled holes read 0.05-0.2). Returns None on degenerate input.
    """
    if recon is None or gt is None:
        return None
    recon = recon.copy()
    gt = gt.copy()
    if normalize_gt:
        gt = normalize_mesh(gt)
    if normalize_recon:
        recon = normalize_mesh(recon)
    try:
        rp, _ = trimesh.sample.sample_surface(recon, n_samples, seed=seed)
        gp, _ = trimesh.sample.sample_surface(gt, n_samples, seed=seed)
    except Exception:
        return None
    rp = np.asarray(rp)
    gp = np.asarray(gp)
    if len(rp) == 0 or len(gp) == 0:
        return None
    r2g = _one_sided_nn(rp, gp)   # recon point -> nearest gt point
    g2r = _one_sided_nn(gp, rp)   # gt point    -> nearest recon point

    def _stats(prefix, d):
        return {
            f"{prefix}_max": float(d.max()),
            f"{prefix}_p99": float(np.percentile(d, 99)),
            f"{prefix}_p95": float(np.percentile(d, 95)),
            f"{prefix}_mean": float(d.mean()),
        }

    out = {}
    out.update(_stats("recon_to_gt", r2g))
    out.update(_stats("gt_to_recon", g2r))
    out["hausdorff"] = max(out["recon_to_gt_max"], out["gt_to_recon_max"])
    out["hausdorff_p99"] = max(out["recon_to_gt_p99"], out["gt_to_recon_p99"])
    out["bbox_diag"] = float(np.linalg.norm(gt.bounds[1] - gt.bounds[0]))
    out["n_samples"] = int(n_samples)
    out["seed"] = int(seed)
    return out


def residual_report(recon: trimesh.Trimesh, gt: trimesh.Trimesh,
                    iou: float | None = None,
                    flag_iou: float = 0.85, flag_frac: float = 0.05,
                    n_samples: int = 30000, seed: int = 0):
    """Full honesty row for one (recon, GT) pair: residual distances + IoU +
    the localized-hallucinated-fill ``honesty_flag``.

    ``honesty_flag`` fires when a row LOOKS clean by IoU (>= ``flag_iou``) yet a
    robust one-sided residual (p99) exceeds ``flag_frac`` * bbox_diag — the
    high-IoU + high-one-sided-Hausdorff signature the report names. ``flag_side``
    records which direction dominates ('over' = recon_to_gt / hallucinated fill,
    'under' = gt_to_recon / missing feature). ``iou`` is computed via the shipped
    ``mesh_iou`` (recon as-is vs normalized GT) if not supplied.
    """
    res = residual_distances(recon, gt, n_samples=n_samples, seed=seed)
    if res is None:
        return None
    if iou is None:
        gtn = normalize_mesh(gt.copy())
        iou = mesh_iou(recon.copy(), gtn)
    res["iou"] = float(iou)
    thresh = flag_frac * res["bbox_diag"]
    res["flag_thresh"] = float(thresh)
    over_p99, under_p99 = res["recon_to_gt_p99"], res["gt_to_recon_p99"]
    res["honesty_flag"] = bool(iou >= flag_iou and max(over_p99, under_p99) >= thresh)
    res["flag_side"] = "over" if over_p99 >= under_p99 else "under"
    return res
