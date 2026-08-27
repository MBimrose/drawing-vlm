"""Precompute ground-truth STLs for the frozen eval pool.

Executes each cached eval sample's GT build123d code via exec_harness.py
(parallel subprocesses, timeout-guarded) and stores STLs under
gt_meshes/<key>.stl next to the eval cache. Samples whose GT fails to
execute are recorded in gt_meshes/failed.txt and excluded from IoU eval.

Usage: python build_gt_meshes.py [--n-workers 16] [--pool all] [--limit 96]
"""
from __future__ import annotations

import argparse
import os
import pickle
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from data_v14 import EVAL_CACHE  # noqa: E402

GT_DIR = os.path.join(os.path.dirname(EVAL_CACHE), "gt_meshes_v14")
HARNESS = os.path.join(HERE, "exec_harness.py")
PYTHON = sys.executable


def build_one(key: str, code: str) -> tuple[str, bool, str]:
    out_stl = os.path.join(GT_DIR, f"{key}.stl")
    if os.path.exists(out_stl) and os.path.getsize(out_stl) > 0:
        return key, True, "cached"
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(code)
        code_path = f.name
    try:
        p = subprocess.run(
            [PYTHON, HARNESS, code_path, out_stl],
            capture_output=True, text=True, timeout=120,
        )
        ok = p.returncode == 0
        return key, ok, (p.stderr[-300:] if not ok else "ok")
    except subprocess.TimeoutExpired:
        return key, False, "timeout"
    finally:
        os.unlink(code_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-workers", type=int, default=16)
    ap.add_argument("--pool", default="all")
    ap.add_argument("--limit", type=int, default=96)
    args = ap.parse_args()

    os.makedirs(GT_DIR, exist_ok=True)
    with open(EVAL_CACHE, "rb") as f:
        cache = pickle.load(f)
    keys = cache["pools"][args.pool][: args.limit]
    print(f"[gt-mesh] building {len(keys)} GT meshes -> {GT_DIR}", flush=True)

    ok = 0
    failures = []
    with ProcessPoolExecutor(max_workers=args.n_workers) as ex:
        futs = {ex.submit(build_one, k, cache["samples"][k]["code"]): k for k in keys}
        for fut in as_completed(futs):
            key, success, msg = fut.result()
            if success:
                ok += 1
            else:
                failures.append((key, msg))
                print(f"[gt-mesh] FAIL {key}: {msg}", flush=True)
    with open(os.path.join(GT_DIR, "failed.txt"), "w") as f:
        for key, msg in failures:
            f.write(f"{key}\t{msg}\n")
    print(f"[gt-mesh] done: {ok}/{len(keys)} ok, {len(failures)} failed")


if __name__ == "__main__":
    main()
