"""Two label-free diagnostics over a scored best-of-N run, re-executing every stored candidate.

1. Orientation: IoU of each candidate against the ground truth under all 48 signed axis
   permutations (24 rotations + 24 reflections). If the best of the 48 is far above the identity
   score, the candidate has the right shape in the wrong frame -- a convention error (which way
   an extrusion grows, which plane a sketch sits on), not a comprehension error.
2. Dimension audit: the sheet's envelope callouts (m_env_width / m_env_depth / dim_height in the
   renderer's annotation record) against the candidate's sorted bounding-box extents. Every label
   must match some extent within --tol (relative). A candidate that fails the audit contradicts a
   number printed on the drawing, so it can be rejected before any vote.

IoU here is a voxel proxy, not the exact boolean of iou.py: every mesh (ground truth and the
candidates of one part) is centered and rasterised onto one cubic grid (--res per side) with an
orthographic fill, so a signed permutation of the part is a transpose/flip of its occupancy array
and the 48-frame search costs nothing. The exact boolean engines fail on many real-part meshes
and fall back to a 40-180 s Monte-Carlo estimate, which makes 48 frames per candidate impossible.
The stored exact IoU is kept in every row (stored_iou) so the proxy can be checked against it.

Reports, per family (F = Fusion 360, A = ABC): first-execute, agreement vote (medoid by pairwise
voxel IoU) and oracle, each as scored, with the audit, and with orientation fixed.

    python orient_dim_diag.py --bo results/ext/bo8_ext_dw423p_<run>.json \
        --bench train_v14/mech/benchmarks/data/ext_bench_dw423_perm --out results/ext/diag_<run>.json
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from score_partials import execute  # noqa: E402
from iou import load_mesh  # noqa: E402


def signed_perms():
    ops = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((1, -1), repeat=3):
            ops.append((perm, signs))
    return ops  # identity first


OPS = signed_perms()


def apply_op(occ, op):
    perm, signs = op
    a = np.transpose(occ, perm)
    for ax, s in enumerate(signs):
        if s < 0:
            a = np.flip(a, axis=ax)
    return a


def occupancy(mesh, side, res):
    """Centered mesh -> filled boolean res^3 grid on the cube [-side/2, side/2]^3."""
    import trimesh
    from trimesh.remesh import subdivide_to_size
    from trimesh.voxel import morphology
    pitch = side / res
    v = mesh.vertices - 0.5 * (mesh.bounds[0] + mesh.bounds[1])
    try:
        pv, pf = subdivide_to_size(v, mesh.faces, max_edge=pitch * 0.9, max_iter=12)
    except Exception:
        pv = v
    idx = np.floor((pv + side / 2) / pitch).astype(int)
    idx = idx[np.all((idx >= 0) & (idx < res), axis=1)]
    occ = np.zeros((res, res, res), dtype=bool)
    if len(idx):
        occ[idx[:, 0], idx[:, 1], idx[:, 2]] = True
        filled = morphology.fill(occ, method="orthographic")
        occ = np.asarray(getattr(filled, "dense", filled), dtype=bool)
    return occ


def viou(a, b):
    u = np.count_nonzero(a | b)
    return float(np.count_nonzero(a & b) / u) if u else 0.0


def rel_err(extents, labels):
    """max over labels of the closest relative mismatch to any extent."""
    return float(max(min(abs(x - y) / max(y, 1.0) for x in extents) for y in labels))


def part_job(args):
    key, cands, gt_path, env, gt_bbox, workdir, timeout, res = args
    t0 = time.time()
    gt = load_mesh(gt_path)
    meshes = []
    out = []
    for c in cands:
        d = c.get("draw")
        rec = {"draw": d, "stored_iou": float(c.get("iou", 0.0) or 0.0), "stored_exec": bool(c.get("exec", False))}
        code = c.get("code") or ""
        m = None
        if code:
            stl = os.path.join(workdir, f"{key}__{d}.stl")
            if execute(code, stl, workdir, f"{key}__{d}", timeout):
                m = load_mesh(stl)
                try:
                    os.remove(stl)
                except OSError:
                    pass
        rec["exec"] = m is not None
        if m is not None:
            ext = np.sort(m.extents)
            rec["extents"] = ext.tolist()
            if env:
                rec["env_err"] = rel_err(ext, env)
            rec["gt_err"] = rel_err(ext, sorted(gt_bbox))
        meshes.append(m)
        out.append(rec)
    gt_ext = float(np.max(gt.extents)) if gt is not None else float(max(gt_bbox))
    side = 1.02 * max([gt_ext] + [min(float(np.max(m.extents)), 3 * gt_ext) for m in meshes if m is not None])
    occ_gt = occupancy(gt, side, res) if gt is not None else None
    occs = [occupancy(m, side, res) if m is not None else None for m in meshes]
    for rec, o in zip(out, occs):
        if o is None or occ_gt is None:
            continue
        rec["iou0"] = viou(o, occ_gt)
        best, best_op = rec["iou0"], None
        if rec["iou0"] < 0.85:
            for op in OPS[1:]:
                v = viou(apply_op(o, op), occ_gt)
                if v > best:
                    best, best_op = v, op
        rec["iou_rot"] = best
        rec["rot"] = [list(best_op[0]), list(best_op[1])] if best_op else None
    idx = [i for i, o in enumerate(occs) if o is not None]
    pw = {f"{a}, {b}".replace(" ", ""): viou(occs[a], occs[b]) for a, b in itertools.combinations(idx, 2)}
    return {"key": key, "cands": out, "pairwise": pw, "gt_faces": int(len(gt.faces)) if gt is not None else 0,
            "secs": round(time.time() - t0, 1)}


def medoid(pw, allowed):
    if not allowed:
        return None
    if len(allowed) == 1:
        return allowed[0]
    best, best_s = None, -1.0
    for i in allowed:
        s = sum(pw.get(f"{min(i, j)},{max(i, j)}", 0.0) for j in allowed if j != i)
        if s > best_s:
            best, best_s = i, s
    return best


def c_pass(c, tol):
    return c.get("exec") and ("env_err" not in c or c["env_err"] <= tol)


def summarize(rows, fam_of, tol):
    fams = sorted(set(fam_of.values()))
    lines = []
    for fam in ["ALL"] + fams:
        R = [r for r in rows if fam == "ALL" or fam_of.get(r["key"]) == fam]
        if not R:
            continue
        names = ("first", "vote", "oracle", "first_a", "vote_a", "oracle_a", "first_r", "vote_r", "oracle_r")
        stats = {k: [] for k in names + ("audit_pass", "orient_fix", "stored", "proxy")}
        n_exec = n_cand = 0
        for r in R:
            cs = r["cands"]; pw = r["pairwise"]
            ex = [i for i, c in enumerate(cs) if c.get("exec") and "iou0" in c]
            n_cand += len(cs); n_exec += len(ex)
            i0 = [c.get("iou0", 0.0) for c in cs]; ir = [c.get("iou_rot", 0.0) for c in cs]
            for i in ex:
                stats["stored"].append(cs[i]["stored_iou"]); stats["proxy"].append(i0[i])
            aud = [i for i in ex if c_pass(cs[i], tol)]
            stats["audit_pass"].append(len(aud) / len(ex) if ex else 0.0)
            stats["orient_fix"].extend([1.0 if (i0[i] < 0.5 and ir[i] - i0[i] > 0.2) else 0.0 for i in ex])
            f = ex[0] if ex else None; v = medoid(pw, ex)
            stats["first"].append(i0[f] if f is not None else 0.0)
            stats["vote"].append(i0[v] if v is not None else 0.0)
            stats["oracle"].append(max(i0) if cs else 0.0)
            fa = aud[0] if aud else f; va = medoid(pw, aud) if aud else v
            stats["first_a"].append(i0[fa] if fa is not None else 0.0)
            stats["vote_a"].append(i0[va] if va is not None else 0.0)
            stats["oracle_a"].append(max([i0[i] for i in aud]) if aud else (max(i0) if cs else 0.0))
            stats["first_r"].append(ir[f] if f is not None else 0.0)
            stats["vote_r"].append(ir[v] if v is not None else 0.0)
            stats["oracle_r"].append(max(ir) if cs else 0.0)
        m = {k: float(np.mean(v)) if v else 0.0 for k, v in stats.items()}
        g85 = {k: float(np.mean([x >= 0.85 for x in stats[k]])) if stats[k] else 0.0 for k in names}
        corr = float(np.corrcoef(stats["stored"], stats["proxy"])[0, 1]) if len(stats["stored"]) > 2 else 0.0
        lines.append(f"[{fam}] parts {len(R)}  exec {n_exec}/{n_cand}  voxel-vs-exact IoU corr {corr:+.3f} (means {m['proxy']:.3f} vs {m['stored']:.3f})")
        lines.append(f"   audit-pass share of exec'd {m['audit_pass']:.2f}   orientation-fixable share of exec'd {m['orient_fix']:.2f}")
        lines.append(f"   {'':22s} {'first':>7s} {'vote':>7s} {'oracle':>7s}")
        for lab, ks in (("as scored", ("first", "vote", "oracle")), ("dimension audit", ("first_a", "vote_a", "oracle_a")), ("orientation fixed", ("first_r", "vote_r", "oracle_r"))):
            lines.append(f"   {lab:22s} " + " ".join(f"{m[k]:7.3f}" for k in ks) + "   >=.85 " + " ".join(f"{g85[k]:.2f}" for k in ks))
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bo", required=True); ap.add_argument("--bench", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=32); ap.add_argument("--timeout", type=int, default=90)
    ap.add_argument("--tol", type=float, default=0.05); ap.add_argument("--n", type=int, default=0)
    ap.add_argument("--res", type=int, default=96)
    a = ap.parse_args()
    parts = json.load(open(a.bo))["candidates"]
    if a.n:
        parts = parts[: a.n]
    man = json.load(open(os.path.join(a.bench, "manifest.json")))["parts"]
    rend = json.load(open(os.path.join(a.bench, "render", "renderers.json")))
    env_of = {}
    for rk, v in rend.items():
        key = rk.rsplit("_v", 1)[0]
        labels = []
        for ak, ann in v.get("annotations", {}).items():
            if ak.startswith("m_env") or ak == "dim_height":
                try:
                    labels.append(float(ann["label"]))
                except (KeyError, ValueError):
                    pass
        env_of[key] = labels
    fam_of = {k: v.get("family", k[:1]) for k, v in man.items()}
    base = "/dev/shm" if os.path.isdir("/dev/shm") else None
    workdir = tempfile.mkdtemp(prefix="diag_", dir=base)
    jobs = [(p["key"], p["cands"], os.path.join(a.bench, "gt_meshes_v15", p["key"] + ".stl"), env_of.get(p["key"], []),
             man[p["key"]]["bbox_mm"], workdir, a.timeout, a.res) for p in parts if p["key"] in man]
    t0 = time.time(); rows = []
    with ProcessPoolExecutor(a.workers) as ex:
        for i, r in enumerate(ex.map(part_job, jobs), 1):
            rows.append(r)
            if i % 20 == 0 or i <= 4:
                print(f"  {i}/{len(jobs)} parts, {time.time() - t0:.0f} s (last: {r['secs']} s, gt faces {r['gt_faces']})", flush=True)
    summ = summarize(rows, fam_of, a.tol)
    print(summ)
    json.dump({"bo": a.bo, "bench": a.bench, "tol": a.tol, "res": a.res, "summary_text": summ, "rows": rows, "family": fam_of}, open(a.out, "w"))
    print("DIAG DONE", a.out, f"{time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
