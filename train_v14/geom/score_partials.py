"""Execute and score the candidates in a best-of-N run's .partial.json checkpoints.

`bestofn_verifier_eval.py` checkpoints after every DRAW (code + think per candidate) but its
execute-and-score phase is one un-checkpointed block: a job that hits its walltime there loses
hours of generation even though every candidate is already on disk. This re-runs just that
phase from the checkpoints, resumably, and writes a candidates file in the same shape as the
job would have (`{"metrics", "candidates": [{"key", "cands":[{draw, code, think, exec, iou}]}]}`),
so `merge_bo_shards.py` / `write_rft_real.py` / `consistency_rerank.py` accept it unchanged.

Resume: results are appended to <out>.scored.jsonl ({key, draw, exec, iou}) and re-read on a
second run, so it can be interrupted freely.

    python score_partials.py --partials '<dir>/bo32_*.shard?.json.partial.json' \
        --gt-dir <bench>/gt_meshes_v15 --out <dir>/bo32_<corpus>_<run>.json [--workers 16]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

HARNESS = os.path.join(HERE, "exec_harness.py")
IOU_ONCE = os.path.join(HERE, "iou_once.py")
PYTHON = sys.executable


def scored_iou(stl, gt, timeout):
    """Centered IoU in a subprocess, killed after `timeout` s.

    Returns (iou, timed_out). A pair whose overlap cannot be computed inside the budget
    is recorded as 0.0: its mesh is pathological enough that the boolean engines failed
    AND the Monte-Carlo fallback could not finish, which is not a candidate worth
    training on. Bulk tier building needs the accept/reject decision, not a number for
    every reject.
    """
    import subprocess
    try:
        p = subprocess.run([PYTHON, IOU_ONCE, stl, gt], capture_output=True, text=True,
                           timeout=timeout)
        return float(json.loads(p.stdout)["iou_centered"]), False
    except subprocess.TimeoutExpired:
        return 0.0, True
    except Exception:
        return 0.0, False


def execute(code, stl_path, workdir, key, timeout):
    """rft_generate.exec_to_stl with a caller-chosen timeout (it hardcodes 120 s)."""
    import subprocess
    cp = os.path.join(workdir, key + ".py")
    with open(cp, "w") as f:
        f.write(code)
    try:
        p = subprocess.run([PYTHON, HARNESS, cp, stl_path], capture_output=True,
                           text=True, timeout=timeout)
        return p.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False


def volume_bound(stl_a, stl_b):
    """Upper bound on IoU from volumes alone: |A&B|/|A|B| <= min(vA,vB)/max(vA,vB).

    Loading a mesh and summing signed tetrahedra is milliseconds; the manifold3d
    boolean behind the real IoU is seconds to minutes on real-part geometry. When
    the bound already falls below the acceptance threshold the boolean cannot
    change the decision, so it is skipped. Returns None when either volume is
    unusable (non-watertight export, degenerate mesh) and the real IoU must run.
    """
    import trimesh
    try:
        ma = trimesh.load(stl_a, process=False)
        mb = trimesh.load(stl_b, process=False)
        # volume is only meaningful for a closed surface; a leaky export would give a
        # confident wrong number and could reject a good candidate
        if not (ma.is_watertight and mb.is_watertight):
            return None
        va = abs(float(ma.volume))
        vb = abs(float(mb.volume))
    except Exception:
        return None
    if not (va > 0 and vb > 0) or not all(map(np.isfinite, (va, vb))):
        return None
    return min(va, vb) / max(va, vb)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--partials", required=True, help="glob of .partial.json checkpoints")
    ap.add_argument("--gt-dir", required=True, help="dir of <key>.stl ground-truth meshes")
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--exec-timeout", type=int, default=60,
                    help="per-candidate build timeout (rft_generate uses 120)")
    ap.add_argument("--iou-timeout", type=int, default=90,
                    help="wall-clock budget for one overlap; a pair that exceeds it scores 0")
    ap.add_argument("--accept", type=float, default=0.8,
                    help="tier acceptance threshold; the volume bound skips the boolean "
                         "only when it already rules this out (0 disables the shortcut)")
    args = ap.parse_args()

    files = sorted(glob.glob(args.partials))
    assert files, f"no checkpoints match {args.partials}"
    parts = []          # (key, [cand dicts in draw order])
    for f in files:
        d = json.load(open(f))
        for key, cs in zip(d["keys"], d["cands"]):
            cs = sorted(cs, key=lambda c: c.get("draw", 0))
            parts.append((key, cs))
    print(f"[score] {len(files)} checkpoints, {len(parts)} parts, "
          f"{sum(len(c) for _, c in parts)} candidates", flush=True)

    done = {}
    jl = args.out + ".scored.jsonl"
    if os.path.exists(jl):
        for line in open(jl):
            try:
                r = json.loads(line)
            except Exception:
                continue
            done[(r["key"], r["draw"])] = r
        print(f"[score] resuming: {len(done)} candidates already scored", flush=True)

    todo = [(key, c) for key, cs in parts for c in cs
            if c.get("code") and (key, c.get("draw")) not in done]
    print(f"[score] {len(todo)} to execute", flush=True)
    t0 = time.time()
    n_done = [0]
    out_f = open(jl, "a")

    with tempfile.TemporaryDirectory(prefix="score_") as td:
        def run_one(item):
            key, c = item
            stl = os.path.join(td, f"{key}_{c['draw']}.stl")
            gt = os.path.join(args.gt_dir, f"{key}.stl")
            ok = iou = None
            bound = timed_out = False
            try:
                ok = execute(c["code"], stl, td, f"{key}_{c['draw']}", args.exec_timeout)
                if ok:
                    vb = volume_bound(stl, gt) if args.accept > 0 else None
                    if vb is not None and vb < args.accept:
                        iou, bound = vb, True      # true IoU <= vb < accept: decision settled
                    else:
                        iou, timed_out = scored_iou(stl, gt, args.iou_timeout)
            except Exception as e:
                print(f"[score] {key} draw {c['draw']}: {type(e).__name__}", flush=True)
                ok = False
            rec = {"key": key, "draw": c["draw"], "exec": bool(ok), "iou": float(iou or 0.0)}
            if bound:
                rec["iou_bound"] = True
            if timed_out:
                rec["iou_timeout"] = True
            out_f.write(json.dumps(rec) + "\n")
            n_done[0] += 1
            if n_done[0] % 500 == 0:
                out_f.flush()
                rate = n_done[0] / max(1e-9, time.time() - t0)
                left = (len(todo) - n_done[0]) / max(1e-9, rate)
                print(f"[score] {n_done[0]}/{len(todo)}  {rate:.2f}/s  eta {left/3600:.1f} h", flush=True)
            return rec
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            for rec in ex.map(run_one, todo):
                done[(rec["key"], rec["draw"])] = rec
    out_f.close()

    n_bound = sum(1 for r in done.values() if r.get("iou_bound"))
    n_to = sum(1 for r in done.values() if r.get("iou_timeout"))
    print(f"[score] volume bound settled {n_bound} of {len(done)} without a boolean; "
          f"{n_to} overlaps timed out (scored 0)", flush=True)
    n_exec = 0
    for key, cs in parts:
        for c in cs:
            r = done.get((key, c.get("draw")))
            c["exec"] = bool(r and r["exec"])
            c["iou"] = float(r["iou"]) if r else 0.0
            c.pop("pred", None)
            n_exec += c["exec"]
    metrics = {"n": len(parts), "k": max(len(cs) for _, cs in parts), "n_exec": n_exec,
               "source": "score_partials.py"}
    with open(args.out, "w") as f:
        json.dump({"metrics": metrics, "candidates": [{"key": k, "cands": cs} for k, cs in parts]}, f)
    print(f"[score] executed {n_exec}/{sum(len(c) for _, c in parts)} -> {args.out}", flush=True)


if __name__ == "__main__":
    main()
