#!/usr/bin/env python
"""Execute converted DeepCAD scripts and keep only the ones whose solid matches Onshape's bbox.

For every <gate>/code/D_<id>.py: run it through exec_harness.py (build123d, temp cwd) to a
STEP, load the STEP, and accept when
  * one or more solids with positive volume, and
  * the axis-aligned bounding-box extents match expect.json's bbox_mm within --tol of the
    longest edge (Onshape computed that box on the real part, independently of our rebuild --
    it catches a wrong plane, a flipped extent, a metre/mm slip, or a symmetric extrude
    applied once instead of twice).
Accepted STEPs are copied to <corpus>/src/000/<key>.step for prep_external_parts.py; the code
stays next to them as the tier's ground truth. Resumable: results append to verify.jsonl.

    python deepcad_verify.py --gate <dir> --corpus <dir> [--workers 32] [--tol 0.02]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.environ.get("EXEC_HARNESS", os.path.join(HERE, "..", "..", "geom", "exec_harness.py"))
PYTHON = sys.executable


def bbox_of_step(path):
    from build123d import import_step
    shape = import_step(path)
    solids = shape.solids()
    if not solids:
        return None, 0.0
    vol = sum(s.volume for s in solids)
    bb = shape.bounding_box()
    return [bb.size.X, bb.size.Y, bb.size.Z], vol


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--tol", type=float, default=0.02)
    ap.add_argument("--timeout", type=int, default=90)
    args = ap.parse_args()
    expect = json.load(open(os.path.join(args.gate, "expect.json")))
    src = os.path.join(args.corpus, "src", "000")
    os.makedirs(src, exist_ok=True)
    log = os.path.join(args.gate, "verify.jsonl")
    done = {}
    if os.path.exists(log):
        for line in open(log):
            try:
                r = json.loads(line); done[r["key"]] = r
            except Exception:
                pass
    todo = [k for k in expect if k not in done]
    print(f"[verify] {len(expect)} scripts, {len(done)} done, {len(todo)} to run", flush=True)
    out = open(log, "a")
    t0 = time.time(); n = [0]

    def one(key):
        code = os.path.join(args.gate, "code", key + ".py")
        rec = {"key": key, "ok": False}
        with tempfile.TemporaryDirectory(prefix="dcv_") as td:
            stl, step = os.path.join(td, "o.stl"), os.path.join(td, "o.step")
            try:
                p = subprocess.run([PYTHON, HARNESS, code, stl, step], capture_output=True, text=True,
                                   timeout=args.timeout)
            except subprocess.TimeoutExpired:
                rec["why"] = "timeout"; return rec
            if p.returncode != 0 or not os.path.exists(step):
                tail = (p.stderr or "").strip().splitlines()
                rec["why"] = f"exec rc={p.returncode}: {tail[-1][:160] if tail else ''}"; return rec
            try:
                got, vol = bbox_of_step(step)
            except Exception as e:
                rec["why"] = f"load: {type(e).__name__}"; return rec
            if got is None or vol <= 0:
                rec["why"] = "no solid"; return rec
            want = expect[key]["bbox_mm"]
            mx = max(want)
            err = max(abs(g - w) for g, w in zip(sorted(got), sorted(want))) / mx
            rec.update({"bbox_got": [round(x, 3) for x in got], "bbox_want": [round(x, 3) for x in want],
                        "bbox_err": round(err, 4), "volume": round(vol, 3)})
            if err > args.tol:
                rec["why"] = "bbox mismatch"; return rec
            shutil.copyfile(step, os.path.join(src, key + ".step"))
            rec["ok"] = True
            return rec

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for rec in ex.map(one, todo):
            out.write(json.dumps(rec) + "\n"); n[0] += 1
            if n[0] % 200 == 0:
                out.flush()
                print(f"[verify] {n[0]}/{len(todo)}  {n[0]/(time.time()-t0):.1f}/s", flush=True)
    out.close()
    import collections
    rows = [json.loads(l) for l in open(log)]
    ok = sum(r["ok"] for r in rows)
    why = collections.Counter((r.get("why") or "").split(":")[0] for r in rows if not r["ok"])
    print(f"[verify] DONE accepted {ok}/{len(rows)} ({ok/max(1,len(rows)):.0%}); rejected: {dict(why.most_common(8))}")


if __name__ == "__main__":
    main()
