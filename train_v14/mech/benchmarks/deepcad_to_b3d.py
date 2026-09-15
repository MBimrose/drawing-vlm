#!/usr/bin/env python
"""DeepCAD construction sequence (raw Onshape cad_json) -> build123d script in our dialect.

DeepCAD (Wu et al. 2021) is 178k real Onshape parts as sketch-and-extrude sequences, parsed
from ABC links. Each JSON is {"entities": {id: Sketch | ExtrudeFeature}, "sequence": [...],
"properties": {"bounding_box": {...}}} in METRES (0.0254 = 1 inch is everywhere).

Semantics follow cadlib/visualize.py (DeepCAD's own OpenCASCADE reconstruction):
  * sketch plane = transform {origin, x_axis, y_axis, z_axis}; curve points are sketch-local
    2D (x, y) and map to 3D as origin + x*x_axis + y*y_axis;
  * Line3D(start, end), Circle3D(center, radius), Arc3D via three points where the mid point
    is center + R(mid_angle) @ reference_vector * radius, mid_angle = (start+end)/2 -- the
    exact formula DeepCAD feeds GC_MakeArcOfCircle;
  * a profile is one outer loop plus inner loops as holes;
  * extrude along the plane normal by extent_one; SymmetricFeatureExtentType extrudes
    extent_one BOTH ways; TwoSidesFeatureExtentType adds extent_two the other way;
  * NewBody/Join -> fuse, Cut -> cut, Intersect -> common; several profiles in one extrude
    are extruded then fused before the operation is applied.

Every part is rescaled so its longest bounding-box edge is --target-mm (80, as the real-part
corpora), the script is emitted in millimetres with that scale baked into the numbers, and
the expected bbox (mm) is returned so the executed STEP can be checked against Onshape's own
bounding box (the JSON "properties") -- that check catches plane, unit, direction and
symmetric-extent mistakes.

    python deepcad_to_b3d.py --json <cad_json root> --ids <file of "dddd/dddddddd"> \
        --out <dir>  [--target-mm 80]
writes <out>/code/D_<id>.py, <out>/expect.json {key: {bbox_mm, n_extrudes, ...}} and
<out>/skipped.json {key: reason}.
"""
from __future__ import annotations

import argparse
import json
import math
import os

EPS = 1e-9


def v3(d):
    return (float(d["x"]), float(d["y"]), float(d["z"]))


def v2(d):
    return (float(d["x"]), float(d["y"]))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def norm(a):
    n = math.sqrt(dot(a, a))
    return tuple(x / n for x in a) if n > EPS else a


def fmt(x):
    """Numbers as the model writes them: plain decimals, no float noise."""
    s = f"{x:.4f}".rstrip("0").rstrip(".")
    if s in ("-0", ""):
        s = "0"
    return s


class Skip(Exception):
    pass


def loop_lines(curves, scale, flip_y):
    """BuildLine statements for one loop; returns (lines, is_full_circle)."""
    out = []
    P = (lambda p: (p[0] * scale, -p[1] * scale)) if flip_y else (lambda p: (p[0] * scale, p[1] * scale))
    if len(curves) == 1 and curves[0]["type"] == "Circle3D":
        c = curves[0]
        cx, cy = P(v2(c["center_point"]))
        return [f"Circle({fmt(c['radius'] * scale)}, mode=Mode.PRIVATE)"], (cx, cy, c["radius"] * scale)
    for c in curves:
        t = c["type"]
        if t == "Line3D":
            a, b = P(v2(c["start_point"])), P(v2(c["end_point"]))
            if math.dist(a, b) * 1.0 < 1e-6:
                continue
            out.append(f"Line(({fmt(a[0])}, {fmt(a[1])}), ({fmt(b[0])}, {fmt(b[1])}))")
        elif t == "Arc3D":
            s, e = v2(c["start_point"]), v2(c["end_point"])
            ctr, r = v2(c["center_point"]), float(c["radius"])
            ref = v2(c["reference_vector"])
            mid_ang = (float(c["start_angle"]) + float(c["end_angle"])) / 2.0
            ca, sa = math.cos(mid_ang), math.sin(mid_ang)
            mv = (ca * ref[0] - sa * ref[1], sa * ref[0] + ca * ref[1])
            m = (ctr[0] + mv[0] * r, ctr[1] + mv[1] * r)
            a, mm, b = P(s), P(m), P(e)
            out.append(f"ThreePointArc(({fmt(a[0])}, {fmt(a[1])}), ({fmt(mm[0])}, {fmt(mm[1])}), "
                       f"({fmt(b[0])}, {fmt(b[1])}))")
        elif t == "Circle3D":
            raise Skip("circle mixed into a multi-curve loop")
        else:
            raise Skip(f"curve type {t}")
    if not out:
        raise Skip("empty loop")
    return out, None


def sketch_block(sketch, profile_ids, scale, var):
    """BuildSketch code for the chosen profiles of one sketch entity -> list of lines."""
    tr = sketch["transform"]
    o, x, y, z = v3(tr["origin"]), norm(v3(tr["x_axis"])), norm(v3(tr["y_axis"])), norm(v3(tr["z_axis"]))
    if abs(dot(x, z)) > 1e-3:
        raise Skip("non-orthogonal sketch frame")
    yz = cross(z, x)
    flip_y = dot(yz, y) < 0        # left-handed frame: sketch y runs against z x x
    lines = [f"with BuildSketch(Plane(origin=({fmt(o[0]*scale)}, {fmt(o[1]*scale)}, {fmt(o[2]*scale)}), "
             f"x_dir=({fmt(x[0])}, {fmt(x[1])}, {fmt(x[2])}), z_dir=({fmt(z[0])}, {fmt(z[1])}, {fmt(z[2])}))) as {var}:"]
    n_faces = 0
    for pid in profile_ids:
        prof = sketch["profiles"][pid]
        loops = prof["loops"]
        outer = [lp for lp in loops if lp.get("is_outer", True)]
        inner = [lp for lp in loops if not lp.get("is_outer", True)]
        if not outer:
            raise Skip("profile without outer loop")
        for lp, mode in [(l, "ADD") for l in outer] + [(l, "SUBTRACT") for l in inner]:
            curves = lp["profile_curves"]
            for c in curves:
                for k in ("start_point", "end_point", "center_point"):
                    if k in c and abs(float(c[k].get("z", 0.0))) > 1e-6:
                        raise Skip("sketch point off-plane")
            stmts, circ = loop_lines(curves, scale, flip_y)
            if circ is not None:
                cx, cy, r = circ
                lines.append(f"    with Locations(({fmt(cx)}, {fmt(cy)})):")
                lines.append(f"        Circle({fmt(r)}" + (", mode=Mode.SUBTRACT" if mode == "SUBTRACT" else "") + ")")
            else:
                lines.append("    with BuildLine():")
                for s in stmts:
                    lines.append(f"        {s}")
                lines.append("    make_face(" + ("mode=Mode.SUBTRACT" if mode == "SUBTRACT" else "") + ")")
            n_faces += 1
    return lines, n_faces


def convert(d, target_mm):
    bb = d["properties"]["bounding_box"]
    lo, hi = v3(bb["min_point"]), v3(bb["max_point"])
    ext = [hi[i] - lo[i] for i in range(3)]
    mx = max(ext)
    if mx < 1e-6:
        raise Skip("degenerate bbox")
    scale = target_mm / (mx * 1000.0) * 1000.0    # metres -> mm, longest edge -> target_mm
    ents = d["entities"]
    seq = [s for s in d["sequence"] if s["type"] == "ExtrudeFeature"]
    if not seq:
        raise Skip("no extrude")
    if len(seq) > 40:
        raise Skip("sequence too long")
    body_lines = ["from build123d import *", "", f"# DeepCAD part, rescaled so the longest edge is {fmt(target_mm)} mm", ""]
    body_var = None
    n_ext = 0
    for si, step in enumerate(seq):
        ex = ents[step["entity"]]
        for k in ("extent_one", "extent_two"):
            ta = ex.get(k, {}).get("taper_angle", {}).get("value", 0.0) or 0.0
            if abs(float(ta)) > 1e-6:
                raise Skip("taper angle")
        e1 = float(ex["extent_one"]["distance"]["value"]) * scale
        et = ex["extent_type"]
        e2 = float(ex.get("extent_two", {}).get("distance", {}).get("value", 0.0) or 0.0) * scale \
            if et == "TwoSidesFeatureExtentType" else 0.0
        if abs(e1) < 1e-6 and abs(e2) < 1e-6:
            raise Skip("zero extent")
        # group this extrude's profiles by sketch (almost always one sketch)
        if not ex.get("profiles"):
            raise Skip("extrude without profiles")
        by_sketch = {}
        for pr in ex["profiles"]:
            by_sketch.setdefault(pr["sketch"], []).append(pr["profile"])
        solid_vars = []
        for sk_i, (sk_id, pids) in enumerate(by_sketch.items()):
            var = f"sk{si}" + (f"_{sk_i}" if sk_i else "")
            lines, _ = sketch_block(ents[sk_id], pids, scale, var)
            body_lines += lines
            sv = f"s{si}" + (f"_{sk_i}" if sk_i else "")
            if et == "SymmetricFeatureExtentType":
                body_lines.append(f"{sv} = extrude({var}.sketch, amount={fmt(e1)}, both=True)")
            elif et == "TwoSidesFeatureExtentType":
                body_lines.append(f"{sv} = extrude({var}.sketch, amount={fmt(e1)}) + extrude({var}.sketch, amount={fmt(-e2)})")
            else:
                body_lines.append(f"{sv} = extrude({var}.sketch, amount={fmt(e1)})")
            solid_vars.append(sv)
        combined = " + ".join(solid_vars)
        op = ex["operation"]
        if body_var is None:
            if op in ("CutFeatureOperation", "IntersectFeatureOperation"):
                raise Skip(f"first operation is {op}")
            body_lines.append(f"part = {combined}")
            body_var = "part"
        else:
            sym = {"NewBodyFeatureOperation": "+", "JoinFeatureOperation": "+",
                   "CutFeatureOperation": "-", "IntersectFeatureOperation": "&"}[op]
            body_lines.append(f"part = part {sym} ({combined})")
        body_lines.append("")
        n_ext += 1
    body_lines.append('export_step(part, "output.step")')
    expect = {"bbox_mm": [e * scale for e in ext], "scale_m_to_mm": scale, "n_extrudes": n_ext,
              "n_sketches": sum(1 for e in ents.values() if e["type"] == "Sketch")}
    return "\n".join(body_lines) + "\n", expect


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True, help="cad_json root")
    ap.add_argument("--ids", required=True, help="file of ids like 0067/00675619, one per line")
    ap.add_argument("--out", required=True)
    ap.add_argument("--target-mm", type=float, default=80.0)
    args = ap.parse_args()
    os.makedirs(os.path.join(args.out, "code"), exist_ok=True)
    expect, skipped = {}, {}
    ids = [l.strip() for l in open(args.ids) if l.strip()]
    for i, pid in enumerate(ids):
        key = "D_" + pid.split("/")[-1]
        try:
            d = json.load(open(os.path.join(args.json, pid + ".json")))
            code, ex = convert(d, args.target_mm)
        except Skip as e:
            skipped[key] = str(e)
            continue
        except Exception as e:
            skipped[key] = f"{type(e).__name__}: {e}"
            continue
        with open(os.path.join(args.out, "code", key + ".py"), "w") as f:
            f.write(code)
        expect[key] = ex
        if (i + 1) % 500 == 0:
            print(f"[deepcad] {i+1}/{len(ids)} converted={len(expect)} skipped={len(skipped)}", flush=True)
    json.dump(expect, open(os.path.join(args.out, "expect.json"), "w"))
    json.dump(skipped, open(os.path.join(args.out, "skipped.json"), "w"), indent=1)
    import collections
    print(f"[deepcad] DONE converted={len(expect)} skipped={len(skipped)} "
          f"{dict(collections.Counter(skipped.values()).most_common(8))}")


if __name__ == "__main__":
    main()
