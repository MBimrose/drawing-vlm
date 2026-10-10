"""Rank the in-distribution test parts the deployed generator (e55) solves by
geometric complexity, for the "most complex successes" figure.

For every part whose consistency (medoid) pick reaches --min-iou, execute the
GT build123d program, load its STEP and record B-rep statistics: face count by
surface type, hole-like cylinders (small-radius full cylinders), distinct face
normal directions, bbox aspect (3D-ness), plus a static count of modelling
operations in the GT code.

    bash train_v14/serv19/cpu_run.sh -c 32 -- .venv/bin/python \
        train_v14/geom/complex_parts_rank.py --out results/figures/complex_parts/rank.json
"""
import argparse
import json
import math
import os
import pickle
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
CONS = f"{DV}/results/ext/bo8_full_e55-rft-real-u5-gt-dw423_consistency.json"
CACHE = f"{DV}/step_to_drw/wds_dataset/eval_cache_v15_dw423.pkl"
GT_DIR = f"{DV}/step_to_drw/wds_dataset/gt_meshes_v15"

OPS = r"\b(Box|Cylinder|Cone|Sphere|Torus|Wedge|extrude|revolve|loft|sweep|fillet|chamfer|offset|mirror|split|" \
      r"Hole|CounterBoreHole|CounterSinkHole|make_face|Polyline|Polygon|Rectangle|RectangleRounded|Circle|" \
      r"SlotOverall|SlotCenterToCenter|Trapezoid|RegularPolygon|Ellipse|Spline|ThreePointArc|JernArc|" \
      r"RadiusArc|TangentArc|Line|thicken|draft|Locations|GridLocations|PolarLocations)\s*\("

WORKER = r'''
import json, math, os, sys, tempfile, traceback
from collections import Counter
from build123d import import_step
s = import_step(sys.argv[1])
bb = s.bounding_box(); dims = sorted([bb.size.X, bb.size.Y, bb.size.Z]); L = dims[2]
faces = s.faces(); types = Counter(); holes = 0; normals = set()
for f in faces:
    t = f.geom_type; t = getattr(t, "name", str(t)); types[t] += 1
    if t == "PLANE":
        n = f.normal_at(); normals.add((round(n.X, 2), round(n.Y, 2), round(n.Z, 2)))
    if t == "CYLINDER":
        try:
            r = f.radius
        except Exception:
            r = None
        if r is not None and r < 0.08 * L:
            holes += 1
print(json.dumps({"faces": len(faces), "edges": len(s.edges()), "types": dict(types),
                  "small_cyl": holes, "plane_normals": len(normals),
                  "dims": dims, "aspect": dims[0] / max(L, 1e-9), "volume": s.volume}))
'''


def ops_count(code):
    return len(re.findall(OPS, code)), code.count(" - ") + code.count("-=") + code.count(" + ") + code.count("+=")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-iou", type=float, default=0.93)
    ap.add_argument("--workers", type=int, default=28)
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", help="file of keys to restrict to")
    a = ap.parse_args()
    cons = json.load(open(CONS)); cache = pickle.load(open(CACHE, "rb"))["samples"]
    keys = [k for k, v in cons["per_part"].items() if v["consistency"] >= a.min_iou]
    if a.only:
        keys = [k for k in keys if k in set(open(a.only).read().split())]
    print(f"[rank] {len(keys)} parts with vote IoU >= {a.min_iou}", flush=True)
    td = tempfile.mkdtemp(prefix="cxrank_")
    wpath = os.path.join(td, "worker.py"); open(wpath, "w").write(WORKER)

    def run(k):
        cp = os.path.join(td, k + ".py"); code = cache[k]["code"]; open(cp, "w").write(code)
        n_ops, n_bool = ops_count(code)
        rec = {"key": k, "ops": n_ops, "bools": n_bool, "loc": len([l for l in code.splitlines() if l.strip()]),
               "vote": cons["per_part"][k]["consistency"], "oracle": cons["per_part"][k]["oracle"],
               "first": cons["per_part"][k]["first_exec"]}
        try:
            p = subprocess.run([sys.executable, wpath, os.path.join(GT_DIR, k + ".step")], capture_output=True, text=True, timeout=180)
            lines = p.stdout.strip().splitlines()
            if not lines:
                raise RuntimeError(p.stderr.strip()[-300:])
            rec.update(json.loads(lines[-1]))
        except Exception as e:
            rec["err"] = repr(e)[:200]
        return rec

    with ThreadPoolExecutor(a.workers) as ex:
        rows = list(ex.map(run, keys))
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(rows, open(a.out, "w"), indent=1)
    print(f"[rank] wrote {len(rows)} rows ({sum('err' in r for r in rows)} errors) -> {a.out}", flush=True)


if __name__ == "__main__":
    main()
