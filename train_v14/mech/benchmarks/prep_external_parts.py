#!/usr/bin/env python
"""Prepare EXTERNAL (real / independently designed) STEP parts for the
"real geometry, our drawings" benchmark.

Pipeline:  <step dir>  --filter-->  single-body machined parts
           --scale-->  mm-sized copies  (STEP for the renderer, STL for IoU GT)
           --manifest-->  manifest.json  (key -> stats, scale, source)

Nothing here touches train_v14/; run with the repo venv:

  cd /projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
  OPENBLAS_NUM_THREADS=2 .venv/bin/python train_v14/mech/benchmarks/prep_external_parts.py \
      --src <dir of *.step> --out <bench dir> [--target-mm 80] [--max-faces 80]

Outputs:  <out>/step_mm/<key>.step   (scaled STEP, feed to the draftwright renderer)
          <out>/gt_meshes_v15/<key>.stl  (GT for train_v14/geom/iou.py::iou_pair)
          <out>/manifest.json

Filter ("single-body machined part", see RESULTS.md for the pass rates):
  exactly 1 solid; all faces analytic (plane/cylinder/cone/torus/sphere —
  no B-spline/free-form); 6 <= faces <= max_faces; bbox aspect <= 15
  (no wire/sheet stock); volume/bbox-volume >= 0.05 (no lattice/thin shells).

Scale: CADBench parts are normalised to a 20-unit bbox and Fusion 360 Gallery
parts are in cm, so every part is rescaled so its LONGEST edge = --target-mm
(default 80 mm, the median of our synthetic pool's envelope dims), then
snapped to the renderer's 0.5 mm grid via rounding the scale factor so the
sheet's dimensions stay integer-friendly. The IoU metric is centred but NOT
scale-invariant, so the same scaled STL is the GT.
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import signal
import sys

ANALYTIC = {"PLANE", "CYLINDER", "CONE", "TORUS", "SPHERE"}


class _Timeout(Exception):
    pass


def _alarm(*_):
    raise _Timeout()


def analyse(path: str):
    from build123d import import_step
    shp = import_step(path)
    faces = shp.faces()
    kinds = collections.Counter(f.geom_type.name for f in faces)
    bb = shp.bounding_box().size
    dims = sorted([bb.X, bb.Y, bb.Z])
    vol = float(shp.volume)
    bbv = bb.X * bb.Y * bb.Z
    return shp, dict(
        solids=len(shp.solids()), faces=len(faces), kinds=dict(kinds),
        analytic=all(k in ANALYTIC for k in kinds),
        bbox=[bb.X, bb.Y, bb.Z], aspect=dims[2] / max(dims[0], 1e-9),
        fill=(vol / bbv) if bbv > 0 else 0.0, volume=vol,
    )


def passes(st: dict, max_faces: int, min_faces: int = 6, max_aspect: float = 15.0) -> bool:
    # Defaults are the CADBench-corpus filters (rounds 1-5). DeepCAD sequences are simpler and
    # thinner (plain extruded plates and rods are real Onshape parts): pass --min-faces 3
    # --max-aspect 40 for that corpus. Multi-body parts stay out -- one sheet, one solid.
    return (st["solids"] == 1 and st["analytic"] and min_faces <= st["faces"] <= max_faces
            and st["aspect"] <= max_aspect and st["fill"] >= 0.05)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--target-mm", type=float, default=80.0)
    ap.add_argument("--max-faces", type=int, default=80)
    ap.add_argument("--min-faces", type=int, default=6)
    ap.add_argument("--max-aspect", type=float, default=15.0)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--timeout", type=int, default=30, help="per-part seconds")
    ap.add_argument("--stl-tol", type=float, default=0.01)
    args = ap.parse_args()

    from build123d import export_step, export_stl
    step_dir = os.path.join(args.out, "step_mm")
    gt_dir = os.path.join(args.out, "gt_meshes_v15")
    os.makedirs(step_dir, exist_ok=True)
    os.makedirs(gt_dir, exist_ok=True)
    signal.signal(signal.SIGALRM, _alarm)

    files = sorted(glob.glob(os.path.join(args.src, "*.step")) + glob.glob(os.path.join(args.src, "*.stp")))
    if args.limit:
        files = files[: args.limit]
    manifest, rejected = {}, collections.Counter()
    for i, f in enumerate(files):
        key = os.path.splitext(os.path.basename(f))[0]
        signal.alarm(args.timeout)
        try:
            shp, st = analyse(f)
            if not passes(st, args.max_faces, args.min_faces, args.max_aspect):
                why = ("multi_body" if st["solids"] != 1 else "freeform" if not st["analytic"]
                       else "faces" if not (6 <= st["faces"] <= args.max_faces)
                       else "aspect" if st["aspect"] > 15 else "fill")
                rejected[why] += 1
                continue
            scale = args.target_mm / max(st["bbox"])
            scale = round(scale, 3)
            # export_step fails on the Solid that import_step returns; the extracted child works.
            shp = shp.solids()[0].scale(scale)
            export_step(shp, os.path.join(step_dir, f"{key}.step"))
            export_stl(shp, os.path.join(gt_dir, f"{key}.stl"), tolerance=args.stl_tol, angular_tolerance=0.1)
            st["scale"] = scale
            st["bbox_mm"] = [round(x * scale, 3) for x in st["bbox"]]
            st["src"] = os.path.abspath(f)
            manifest[key] = st
        except _Timeout:
            rejected["timeout"] += 1
        except Exception as e:  # noqa: BLE001
            rejected["error"] += 1
            print(f"[prep] {key}: {str(e)[:80]}", file=sys.stderr)
        finally:
            signal.alarm(0)
        if (i + 1) % 50 == 0:
            print(f"[prep] {i+1}/{len(files)} kept={len(manifest)}", flush=True)
    with open(os.path.join(args.out, "manifest.json"), "w") as fh:
        json.dump({"target_mm": args.target_mm, "max_faces": args.max_faces,
                   "parts": manifest, "rejected": dict(rejected)}, fh, indent=1)
    print(f"[prep] kept {len(manifest)}/{len(files)}  rejected={dict(rejected)}  -> {args.out}")


if __name__ == "__main__":
    main()
