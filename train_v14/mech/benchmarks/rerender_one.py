#!/usr/bin/env python3
"""Render ONE STEP file into a v14 sheet (worker_v11._process_one_part, VLM_MODE=1)
with the sheet variant either forced or seed-chosen.

    <renderer python> rerender_one.py --step <part.step> --out-png <file.png> \
        --out-meta <file.json> --uuid <hex uuid> --seed <int> [--variant N]

--variant N (1-based, the "_vN" of a tars_v14 member name) forces that variant so a
training member can be reproduced under the same name; --variant 0 (default) picks
the variant from the seed exactly as worker_v11 / render_ext.py do. Everything else
(SCRIPT_DIR, VLM_MODE, 1920x1280, precompute) is render_ext.py's per-part path;
the per-view HLR and per-sheet drawing alarms default to 60 s / 150 s
(RR_HLR_TIMEOUT / RR_DRAWING_TIMEOUT) instead of worker_v11's 25 s / 60 s because a
timed-out draftwright attempt silently falls back to the legacy renderer, and on a
fully loaded box that happened to several percent of the parts. The dispatcher's
"draftwright renderer failed ... falling back to legacy" warning is captured into the
meta as "fallback". Run under the interpreter whose draftwright you want (dw_venv =
0.4.23+patch).
There is no legacy fallback (removed 2026-09-08 at the user's request): a draftwright failure
exits 5 with the full error on stderr and in --out-meta (renderer="failed", render_error).
Exit codes: 0 ok, 5 no sheet produced, 6 wrong variant produced, 1 other error.
"""
import argparse
import json
import logging
import os
import random
import sys
import time

ROOT = os.environ.get("SCRIPT_DIR", "/srv/scratch/bimrose2/mech_benchmarks/step_to_drw")
os.environ["SCRIPT_DIR"] = ROOT
os.environ["VLM_MODE"] = "1"
for k, v in (("OMP_NUM_THREADS", "1"), ("TBB_NUM_THREADS", "1"), ("MKL_NUM_THREADS", "1"),
             ("OPENBLAS_NUM_THREADS", "1")):
    os.environ.setdefault(k, v)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", required=True)
    ap.add_argument("--out-png", required=True)
    ap.add_argument("--out-meta", required=True)
    ap.add_argument("--uuid", required=True, help="hex uuid handed to the renderer (title block)")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--variant", type=int, default=0, help="1-based forced variant; 0 = seed choice")
    a = ap.parse_args()
    step_bytes = open(a.step, "rb").read()

    sys.path.insert(0, ROOT)
    os.chdir(ROOT)
    try:  # worker_v11 imports sqlite3; the dw_venv python has no _sqlite3
        import sqlite3  # noqa: F401
    except ImportError:
        import types
        sys.modules["sqlite3"] = types.ModuleType("sqlite3")
    _uniform = random.uniform
    random.uniform = lambda lo, hi: 0.0  # worker_v11 sleeps uniform(0, 2) s at import
    try:
        import worker_v11 as w  # noqa: E402
    finally:
        random.uniform = _uniform

    if a.variant:
        forced = a.variant - 1
        if not 0 <= forced < len(w._variant_specs):
            print(f"variant {a.variant} out of range", file=sys.stderr)
            return 1

        class _Forced:  # replaces _random.Random(seed).randrange(n) inside _process_one_part
            def __init__(self, seed):
                pass

            def randrange(self, n):
                return forced

        import types
        w._random = types.SimpleNamespace(Random=_Forced, uniform=random.uniform)

    hlr_timeout = int(os.environ.get("RR_HLR_TIMEOUT", "60"))
    drawing_timeout = int(os.environ.get("RR_DRAWING_TIMEOUT", "150"))
    warnings: list[str] = []

    class _Capture(logging.Handler):  # draw_generator logs the fallback reason as a warning
        def emit(self, rec):
            try:
                msg = rec.getMessage()
            except Exception:
                return
            warnings.append(msg[:300])

    logging.getLogger().addHandler(_Capture())
    logging.getLogger().setLevel(logging.WARNING)
    args = (step_bytes, None, a.uuid, w._variant_specs, a.seed, w.PNG_WIDTH, w.PNG_HEIGHT,
            w._PRECOMPUTE_VIEWS, hlr_timeout, drawing_timeout, ROOT)
    t0 = time.time()
    r = w._process_one_part(args)
    if not r.get("examples"):
        # No legacy fallback: the failure meta (renderer="failed", render_error=...) recorded by
        # draw_generator / worker_v11 goes to --out-meta, and the error is the last stderr line
        # (the driver stores it as the failure reason).
        fm = {}
        for vi, m in (r.get("render_meta") or {}).items():
            fm = dict(m, variant=int(vi) + 1)
        fm.setdefault("renderer", "failed")
        fm.setdefault("render_error", "no sheet produced (STEP import / HLR / drawing timeout)")
        if warnings:
            fm["warnings"] = warnings[-5:]
        fm["wall_s"] = round(time.time() - t0, 3)
        with open(a.out_meta, "w") as fh:
            json.dump(fm, fh)
        print(fm["render_error"], file=sys.stderr)
        return 5
    (_, png, _, vi) = r["examples"][0]
    if a.variant and vi + 1 != a.variant:
        print(f"produced variant {vi + 1}, wanted {a.variant}", file=sys.stderr)
        return 6
    meta = dict((r.get("render_meta") or {}).get(vi, {}))
    meta["variant"] = vi + 1
    meta["wall_s"] = round(time.time() - t0, 3)
    rep = [w for w in warnings if "retrying with front/plan/side" in w or "pre-export lint skipped" in w]
    if rep:  # the ViewNotPlanned repair (planner mismatch) was used for this sheet
        meta["repair"] = rep[-1]
    if warnings:
        meta["warnings"] = warnings[-5:]
    with open(a.out_png, "wb") as fh:
        fh.write(png)
    with open(a.out_meta, "w") as fh:
        json.dump(meta, fh)
    return 0


if __name__ == "__main__":
    sys.exit(main())
