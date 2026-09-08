#!/usr/bin/env python
"""Convert CADFit (MBimrose/agentic-mesh-to-cad) emitter programs — real ABC parts with a
ground-truth build123d program banked at IoU >= 0.85 vs the source mesh — into OUR dialect at
millimetre scale, verify every conversion geometrically, and lay the result out as a corpus
directory that render_isolated.sh / build_ext_eval_cache.py / run_corpus_gen_generic.sh accept
unchanged (step_mm/, gt_meshes_v15/, manifest.json) plus gt_code/<key>.py and gt_code.jsonl.

Source contract (dataset/README.md of the checkout): <root>/<ver>/<part_id>/{mesh.stl (raw ABC
frame), program.py, model.step} with program + STEP in the normalised frame (bbox-centred, max
extent 2). Programs: `import build123d as b`, inline `_safe_fuse/_safe_cut`, final solid in
`result`, no export. About half draw circles / arcs as 60-130-point `b.Polyline` calls.

Conversion (pure source transform, span edits on the AST so formatting survives):
  1. scale: every LENGTH literal is multiplied by f = 80 / (max extent of model.step) (≈40) and
     rounded to 4 decimals, so the numbers on the rendered sheet ARE the numbers in the code.
     Length slots are whitelisted per build123d call (Plane origin, Polyline/arc points,
     Locations/Location/Vector/Pos, radii, Box/Cylinder/Cone/Wedge/Torus sizes, extrude/offset
     amount, fillet/chamfer radius, Axis origin ...); direction vectors (x_dir/z_dir/direction/
     Axis direction), angles (Rotation, revolution_arc, major_angle, taper ...), counts and
     modes are left alone. Floats in unrecognised contexts are scaled (and counted as warnings);
     ints there are not.
  2. dialect: `import build123d as b` -> `from build123d import *`, `b.X` -> `X`,
     `result` -> `part`, `export_step(part, "output.step")` appended, the `_safe_*` helper
     definitions dropped and their calls rewritten to plain `.fuse()/.cut()` (stage "plain");
     if that fails verification the helpers are kept (stage "helpers").
  3. cleaning (optional, --clean): a closed Polyline whose points all lie on one circle
     (least-squares residual < 1e-3·r, >= 12 points, steps <= 20°) becomes
     `with Locations((cx, cy)): Circle(r[, mode=Mode.SUBTRACT])`; runs of >= 8 such points inside
     a longer Polyline become ThreePointArc(first, middle, last) between Polyline fragments.
     Kept only if verification still passes.

Verification: each stage's program is executed in a fresh subprocess (`--exec-one`, same
semantics as train_v14/geom/exec_harness.py: exec in a temp cwd, output.step -> STL) and its
centred volumetric IoU (train_v14/geom/iou.py::iou_pair) against model.step scaled by the same f
must be >= --min-iou (0.99). The raw mesh (normalised like the banking gate, then scaled) gives
the informational iou_vs_mesh. Stage "orig" executes the untouched program at unit scale
against the unscaled STEP (build123d-version drift check).

  <venv python> convert_cadfit_program.py --root <checkout>/dataset --best cadfit_abc_best.json \
      --heldout heldout_file_ids.txt --out <corpus dir> --iou-py <train_v14/geom> [--clean] \
      [--workers 32] [--only 00003607,...] [--limit N]
  <venv python> convert_cadfit_program.py --exec-one <code.py> <out.stl> [<out.step>]
"""
from __future__ import annotations

import argparse
import ast
import collections
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
import traceback

TARGET_MM = 80.0
ROUND = 4                      # decimals kept after scaling (1e-4 mm)
FAMILY = "A"                   # ABC — analyze_ext.py groups by key.split("_")[0]
KEY_SUFFIX = "code"            # key = A_<part_id>_code (no clash with CADBench keys)

# ---------------------------------------------------------------- length-slot whitelist
ALL = "all"
# name -> (positional slots that are lengths | ALL, keyword names that are lengths)
LEN_CALLS: dict[str, tuple] = {
    "Plane": ({0}, {"origin"}),
    "Polyline": (ALL, set()), "Line": (ALL, set()), "ThreePointArc": (ALL, set()),
    "Spline": (ALL, set()), "TangentArc": (ALL, set()), "Bezier": (ALL, set()),
    "RadiusArc": (ALL, {"radius"}), "SagittaArc": (ALL, {"sagitta"}),
    "CenterArc": ({0, 1}, {"center", "radius"}),
    "EllipticalCenterArc": ({0, 1, 2}, {"center", "x_radius", "y_radius"}),
    "Circle": ({0}, {"radius"}), "Ellipse": ({0, 1}, {"x_radius", "y_radius"}),
    "Rectangle": ({0, 1}, {"width", "height"}), "RectangleRounded": ({0, 1, 2}, {"width", "height", "radius"}),
    "RegularPolygon": ({0}, {"radius"}), "Polygon": (ALL, set()),
    "SlotCenterToCenter": ({0, 1}, {"center_separation", "height"}),
    "SlotOverall": ({0, 1}, {"width", "height"}), "SlotArc": ({0, 1}, {"arc", "height"}),
    "SlotCenterPoint": ({0, 1, 2}, {"center", "point", "height"}),
    "Trapezoid": ({0, 1}, {"width", "height"}), "Triangle": ({0, 1, 2}, {"a", "b", "c"}),
    "Text": ({1}, {"font_size"}),
    "Locations": (ALL, set()), "Location": ({0}, {"point", "position"}), "Vector": (ALL, set()),
    "Pos": (ALL, set()), "GridLocations": ({0, 1}, {"x_spacing", "y_spacing"}),
    "PolarLocations": ({0}, {"radius"}), "HexLocations": ({0}, {"radius"}),
    "Box": ({0, 1, 2}, {"length", "width", "height"}),
    "Cylinder": ({0, 1}, {"radius", "height"}),
    "Cone": ({0, 1, 2}, {"bottom_radius", "top_radius", "height"}),
    "Sphere": ({0}, {"radius"}),
    "Torus": ({0, 1}, {"major_radius", "minor_radius"}),
    "Wedge": ({0, 1, 2, 3, 4, 5, 6}, {"xsize", "ysize", "zsize", "xmin", "zmin", "xmax", "zmax"}),
    "Hole": ({0, 1}, {"radius", "depth"}),
    "CounterBoreHole": ({0, 1, 2, 3}, {"radius", "counter_bore_radius", "counter_bore_depth", "depth"}),
    "CounterSinkHole": ({0, 1, 3}, {"radius", "counter_sink_radius", "depth"}),
    "extrude": ({1}, {"amount"}), "offset": ({1}, {"amount"}), "thicken": ({1}, {"amount"}),
    "fillet": ({1}, {"radius"}), "chamfer": ({1, 2}, {"length", "length2"}),
    "Axis": ({0}, {"origin"}),
    # angle / count / direction-only calls: nothing inside is a length
    "Rotation": (set(), set()), "Rot": (set(), set()), "revolve": (set(), set()),
    "loft": (set(), set()), "sweep": (set(), set()), "make_face": (set(), set()),
    "add": (set(), set()), "mirror": (set(), set()), "split": (set(), set()),
    "BuildSketch": (set(), set()), "BuildPart": (set(), set()), "BuildLine": (set(), set()),
    "isinstance": (set(), set()), "range": (set(), set()), "len": (set(), set()),
    "sort_by": (set(), set()), "filter_by": (set(), set()), "group_by": (set(), set()),
    "Align": (set(), set()), "Mode": (set(), set()),
}
KEEP_KW = {"angle", "rotation", "revolution_arc", "major_angle", "minor_start_angle", "minor_end_angle",
           "taper", "start_angle", "end_angle", "arc_size", "x_dir", "z_dir", "direction", "normal",
           "mode", "align", "count", "tolerance", "angular_tolerance", "both", "clean", "centered",
           "rotation_angle", "counter_sink_angle", "font_size"}
HELPERS = {"_safe_fuse": "fuse", "_safe_cut": "cut", "_safe_intersect": "intersect"}


def _call_name(node: ast.Call) -> str:
    f = node.func
    if isinstance(f, ast.Attribute):
        return f.attr
    if isinstance(f, ast.Name):
        return f.id
    return ""


class _Offsets:
    """Byte offsets of AST positions (col_offset is a UTF-8 byte offset)."""

    def __init__(self, src: bytes):
        self.starts = [0]
        for i, ch in enumerate(src):
            if ch == 0x0A:
                self.starts.append(i + 1)

    def span(self, node) -> tuple[int, int]:
        return (self.starts[node.lineno - 1] + node.col_offset,
                self.starts[node.end_lineno - 1] + node.end_col_offset)


def _apply(src: bytes, edits: list[tuple[int, int, bytes]]) -> bytes:
    """Apply non-overlapping (start, end, replacement) edits; inner edits of a replaced span are dropped."""
    edits = sorted(edits, key=lambda e: (e[0], -e[1]))
    out, pos, kept = [], 0, []
    last_end = -1
    for s, e, rep in edits:
        if s < last_end:          # nested inside an earlier (outer) edit -> drop
            continue
        kept.append((s, e, rep)); last_end = e
    for s, e, rep in kept:
        out.append(src[pos:s]); out.append(rep); pos = e
    out.append(src[pos:])
    return b"".join(out)


def _fmt(x: float) -> str:
    r = round(x, ROUND)
    if r == int(r) and abs(r) < 1e15:
        return f"{int(r)}.0"
    return repr(r)


# ---------------------------------------------------------------- pass A: scale lengths
def scale_lengths(src: bytes, factor: float) -> tuple[bytes, dict]:
    tree = ast.parse(src)
    off = _Offsets(src)
    edits, stats = [], collections.Counter()

    def visit(node, ctx):
        # ctx: "len" (scale ints and floats), "keep" (nothing), "unknown" (scale floats, warn)
        if isinstance(node, ast.FunctionDef):
            return                                     # helper bodies untouched
        if isinstance(node, ast.Constant):
            v = node.value
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                return
            if ctx == "len" or (ctx == "unknown" and isinstance(v, float)):
                s, e = off.span(node)
                edits.append((s, e, _fmt(v * factor).encode()))
                stats["scaled"] += 1
                if ctx == "unknown":
                    stats["scaled_unknown_ctx"] += 1
            return
        if isinstance(node, ast.Call):
            name = _call_name(node)
            spec = LEN_CALLS.get(name)
            if name == "Polyline":
                pts = _points_of(node)
                if pts is not None and len(pts) >= 2:
                    # whole-list rewrite: scale, round, drop consecutive points that coincide after
                    # rounding (zero-length edges make Edge.make_line raise), keep the closure
                    sp = [(round(x * factor, ROUND), round(y * factor, ROUND)) for x, y in pts]
                    closed = sp[0] == sp[-1]
                    dd = _dedupe(sp)
                    if closed and dd[-1] != dd[0]:
                        dd.append(dd[0])
                    stats["scaled"] += 2 * len(pts); stats["polyline_pts_dropped"] += len(sp) - len(dd)
                    s, e = off.span(node.args[0])
                    edits.append((s, e, b"[" + b", ".join(_pt(q).encode() for q in dd) + b"]"))
                    return
            visit(node.func, "keep")
            for i, a in enumerate(node.args):
                if spec is None:
                    visit(a, ctx if ctx != "len" else "unknown")
                else:
                    visit(a, "len" if (spec[0] == ALL or i in spec[0]) else "keep")
            for kw in node.keywords:
                if kw.arg in KEEP_KW:
                    visit(kw.value, "keep")
                elif spec is None:
                    visit(kw.value, ctx if ctx != "len" else "unknown")
                else:
                    visit(kw.value, "len" if kw.arg in spec[1] else "keep")
            return
        if isinstance(node, ast.Subscript):           # indices are never lengths
            visit(node.value, ctx); visit(node.slice, "keep"); return
        if isinstance(node, ast.Compare):
            visit(node.left, ctx)
            for c in node.comparators:
                visit(c, ctx)
            return
        for child in ast.iter_child_nodes(node):
            visit(child, ctx)

    visit(tree, "unknown")
    return _apply(src, edits), dict(stats)


# ---------------------------------------------------------------- pass B/C: dialect
def to_dialect(src: bytes, drop_helpers: bool) -> tuple[bytes, dict]:
    stats = collections.Counter()
    # pass B: helper calls -> methods, helper defs dropped, result -> part
    tree = ast.parse(src)
    off = _Offsets(src)
    edits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in HELPERS and drop_helpers:
            s, e = off.span(node)
            # swallow trailing blank lines
            while e < len(src) and src[e:e + 1] in (b"\n", b"\r"):
                e += 1
            edits.append((s, e, b""))
            stats["helper_defs_dropped"] += 1
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in HELPERS \
                and drop_helpers and len(node.args) == 2 and not node.keywords:
            s, e = off.span(node)
            a0, a1 = off.span(node.args[0]), off.span(node.args[1])
            rep = src[a0[0]:a0[1]] + b"." + HELPERS[node.func.id].encode() + b"(" + src[a1[0]:a1[1]] + b")"
            edits.append((s, e, rep))
            stats["helper_calls_rewritten"] += 1
        elif isinstance(node, ast.Name) and node.id == "result":
            s, e = off.span(node)
            edits.append((s, e, b"part"))
            stats["result_renamed"] += 1
    src = _apply(src, edits)
    # pass C: `b.` prefix + import line (re-parse: pass B may have left nested `b.` inside helper args)
    tree = ast.parse(src)
    off = _Offsets(src)
    edits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "b":
            s, e = off.span(node)
            edits.append((s, e, node.attr.encode()))
            stats["b_prefix_removed"] += 1
        elif isinstance(node, ast.Import) and any(a.name == "build123d" and a.asname == "b" for a in node.names):
            s, e = off.span(node)
            edits.append((s, e, b"from build123d import *"))
            stats["import_rewritten"] += 1
    src = _apply(src, edits)
    text = src.decode().rstrip("\n") + "\n"
    if "from build123d import *" not in text:
        text = "from build123d import *\n" + text
    text += '\nexport_step(part, "output.step")\n'
    return text.encode(), dict(stats)


# ---------------------------------------------------------------- pass D: polyline cleaning
MIN_CIRCLE_PTS = 12
MIN_ARC_PTS = 8
MAX_STEP_DEG = 20.0
REL_RESID = 1e-3


def _fit_circle(pts):
    """Algebraic (Kasa) least-squares circle; returns (cx, cy, r, max_rel_residual)."""
    n = len(pts)
    sx = sum(p[0] for p in pts) / n; sy = sum(p[1] for p in pts) / n
    u = [p[0] - sx for p in pts]; v = [p[1] - sy for p in pts]
    suu = sum(a * a for a in u); svv = sum(a * a for a in v); suv = sum(a * b for a, b in zip(u, v))
    suuu = sum(a ** 3 for a in u); svvv = sum(a ** 3 for a in v)
    suvv = sum(a * b * b for a, b in zip(u, v)); svuu = sum(b * a * a for a, b in zip(u, v))
    det = suu * svv - suv * suv
    if abs(det) < 1e-18:
        return None
    r1 = 0.5 * (suuu + suvv); r2 = 0.5 * (svvv + svuu)
    uc = (r1 * svv - r2 * suv) / det; vc = (suu * r2 - suv * r1) / det
    cx, cy = uc + sx, vc + sy
    r = math.sqrt(uc * uc + vc * vc + (suu + svv) / n)
    if r <= 0:
        return None
    resid = max(abs(math.hypot(p[0] - cx, p[1] - cy) - r) for p in pts) / r
    return cx, cy, r, resid


def _run_ok(pts):
    fit = _fit_circle(pts)
    if fit is None or fit[3] > REL_RESID:
        return None
    cx, cy, r, _ = fit
    ang = [math.atan2(p[1] - cy, p[0] - cx) for p in pts]
    steps = []
    for a0, a1 in zip(ang, ang[1:]):
        d = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        steps.append(d)
    if any(abs(d) > math.radians(MAX_STEP_DEG) or abs(d) < 1e-9 for d in steps):
        return None
    if not (all(d > 0 for d in steps) or all(d < 0 for d in steps)):   # one turning sense
        return None
    return fit


def _points_of(call: ast.Call):
    """Literal points of a Polyline call: list, or list + list; None when not literal."""
    if call.keywords or len(call.args) != 1:
        return None

    def ev(n):
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
            a, b = ev(n.left), ev(n.right)
            return None if a is None or b is None else a + b
        try:
            v = ast.literal_eval(n)
        except Exception:
            return None
        if not isinstance(v, list) or not all(isinstance(p, tuple) and len(p) == 2 and
                                               all(isinstance(c, (int, float)) for c in p) for p in v):
            return None
        return [tuple(float(c) for c in p) for p in v]
    return ev(call.args[0])


def _dedupe(pts):
    out = [pts[0]]
    for p in pts[1:]:
        if math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > 1e-9:
            out.append(p)
    return out


def _find_runs(pts):
    """Greedy maximal circle-fitting runs [(i, j, fit)] over an open point sequence."""
    runs, i, n = [], 0, len(pts)
    while i + MIN_ARC_PTS - 1 < n:
        j, best = i + 2, None
        while j < n:
            fit = _run_ok(pts[i:j + 1])
            if fit is None:
                break
            best = fit; j += 1
        j -= 1
        if best is not None and j - i + 1 >= MIN_ARC_PTS:
            runs.append((i, j, best)); i = j
        else:
            i += 1
    return runs


def _pt(p):
    return f"({_fmt(p[0])}, {_fmt(p[1])})"


def clean_polylines(src: bytes) -> tuple[bytes, dict]:
    tree = ast.parse(src)
    off = _Offsets(src)
    stats = collections.Counter()
    edits = []
    lines = src.split(b"\n")

    def indent_of(node):
        return lines[node.lineno - 1][:node.col_offset]

    def stmt_end(node):
        return off.span(node)[1]

    for parent in ast.walk(tree):
        body = getattr(parent, "body", None)
        if not isinstance(body, list):
            continue
        for idx, st in enumerate(body):
            # ---- whole-circle case: `with BuildLine() as x: Polyline(...)` followed by make_face(...)
            if isinstance(st, ast.With) and len(st.items) == 1 and isinstance(st.items[0].context_expr, ast.Call) \
                    and _call_name(st.items[0].context_expr) == "BuildLine" and len(st.body) == 1 \
                    and isinstance(st.body[0], ast.Expr) and isinstance(st.body[0].value, ast.Call) \
                    and _call_name(st.body[0].value) == "Polyline" and idx + 1 < len(body) \
                    and isinstance(body[idx + 1], ast.Expr) and isinstance(body[idx + 1].value, ast.Call) \
                    and _call_name(body[idx + 1].value) == "make_face":
                pts = _points_of(st.body[0].value)
                mf = body[idx + 1].value
                if pts is not None and len(pts) >= MIN_CIRCLE_PTS + 1 and not mf.args and all(k.arg == "mode" for k in mf.keywords):
                    p = _dedupe(pts)
                    closed = math.hypot(p[0][0] - p[-1][0], p[0][1] - p[-1][1]) < 1e-9
                    if closed:
                        p = p[:-1]
                    fit = _run_ok(p + [p[0]]) if (closed and len(p) >= MIN_CIRCLE_PTS) else None
                    if fit is not None:
                        cx, cy, r, _ = fit
                        ind = indent_of(st)
                        mode = b""
                        if mf.keywords:
                            ks, ke = off.span(mf.keywords[0].value)
                            mode = b", mode=" + src[ks:ke]
                        rep = (b"with Locations(" + _pt((cx, cy)).encode() + b"):\n" + ind + b"    Circle(" +
                               _fmt(r).encode() + mode + b")")
                        edits.append((off.span(st)[0], stmt_end(body[idx + 1]), rep))
                        stats["circles"] += 1
                        continue
            # ---- partial arcs inside any Polyline statement in a BuildLine body
            if isinstance(parent, ast.With) and isinstance(st, ast.Expr) and isinstance(st.value, ast.Call) \
                    and _call_name(st.value) == "Polyline" and _call_name(parent.items[0].context_expr) == "BuildLine":
                pts = _points_of(st.value)
                if pts is None or len(pts) < MIN_ARC_PTS:
                    continue
                p = _dedupe(pts)
                runs = _find_runs(p)
                if not runs:
                    continue
                ind = indent_of(st)
                pieces, cur = [], 0
                for i, j, _fit in runs:
                    if i > cur:
                        pieces.append(b"Polyline([" + b", ".join(_pt(q).encode() for q in p[cur:i + 1]) + b"])")
                    m = (i + j) // 2
                    pieces.append(b"ThreePointArc(" + b", ".join(_pt(q).encode() for q in (p[i], p[m], p[j])) + b")")
                    cur = j
                if cur < len(p) - 1:
                    pieces.append(b"Polyline([" + b", ".join(_pt(q).encode() for q in p[cur:]) + b"])")
                edits.append((off.span(st)[0], stmt_end(st), (b"\n" + ind).join(pieces)))
                stats["arcs"] += len(runs); stats["polylines_split"] += 1
    return _apply(src, edits), dict(stats)


# ---------------------------------------------------------------- execution / verification
def exec_one(code_path: str, out_stl: str, out_step: str | None) -> int:
    """Same semantics as train_v14/geom/exec_harness.py (exec in a temp cwd, output.step -> STL)."""
    code = open(code_path, encoding="utf-8", errors="replace").read()
    with tempfile.TemporaryDirectory(prefix="cadfitexec_") as td:
        os.chdir(td)
        g = {"__name__": "__main__", "OUTPUT_PATH": "output.step"}
        try:
            exec(compile(code, "<converted>", "exec"), g)  # noqa: S102
        except SystemExit:
            pass
        except Exception:
            traceback.print_exc()
            return 2
        step = os.path.join(td, "output.step")
        if not os.path.exists(step) or os.path.getsize(step) == 0:
            print("no output.step produced", file=sys.stderr)
            return 3
        if out_step:
            shutil.copyfile(step, out_step)
        try:
            from build123d import export_stl, import_step
            shape = import_step(step)
            export_stl(shape, out_stl, tolerance=0.01, angular_tolerance=0.1)
        except Exception:
            traceback.print_exc()
            return 4
        if not os.path.exists(out_stl) or os.path.getsize(out_stl) == 0:
            return 4
    return 0


def run_program(code: bytes, workdir: str, tag: str, timeout: int, want_step: bool = False) -> tuple[int, str, str, str]:
    cp = os.path.join(workdir, f"{tag}.py"); stl = os.path.join(workdir, f"{tag}.stl"); stp = os.path.join(workdir, f"{tag}.step")
    open(cp, "wb").write(code)
    cmd = [sys.executable, os.path.abspath(__file__), "--exec-one", cp, stl] + ([stp] if want_step else [])
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, stl, stp, (p.stderr or "")[-400:]
    except subprocess.TimeoutExpired:
        return 9, stl, stp, "timeout"


def _analyse(shape) -> dict:
    faces = shape.faces()
    kinds = collections.Counter(f.geom_type.name for f in faces)
    bb = shape.bounding_box().size
    vol = float(abs(shape.volume)); bbv = bb.X * bb.Y * bb.Z
    an = {"PLANE", "CYLINDER", "CONE", "TORUS", "SPHERE"}
    return dict(solids=len(shape.solids()), faces=len(faces), kinds=dict(kinds), analytic=all(k in an for k in kinds),
                bbox=[bb.X, bb.Y, bb.Z], fill=(vol / bbv) if bbv > 0 else 0.0, volume=vol)


def convert_part(job: dict) -> dict:
    """One part end to end. Runs in a pool worker; every heavy import is local."""
    t0 = time.time()
    part_id, ver, pdir, out, factor_target, min_iou, do_clean, timeout, iou_dir = (
        job["part_id"], job["ver"], job["dir"], job["out"], job["target_mm"], job["min_iou"], job["clean"],
        job["timeout"], job["iou_py"])
    global ROUND
    ROUND = job.get("round", ROUND)
    key = f"{FAMILY}_{part_id}_{KEY_SUFFIX}"
    rec = {"key": key, "part_id": part_id, "source_version": ver, "stages": {}, "ok": False, "round": ROUND}
    sys.path.insert(0, iou_dir)
    try:
        from iou import iou_pair
        from build123d import export_stl, import_step
        import trimesh
    except Exception as e:  # noqa: BLE001
        rec["error"] = f"import: {e}"; return rec
    work = os.path.join(out, "work", key); os.makedirs(work, exist_ok=True)
    try:
        src = open(os.path.join(pdir, "program.py"), "rb").read()
        # --- references
        shp = import_step(os.path.join(pdir, "model.step"))
        ext = max(shp.bounding_box().size.X, shp.bounding_box().size.Y, shp.bounding_box().size.Z)
        factor = factor_target / ext
        rec["max_extent_norm"] = ext; rec["factor"] = factor
        ref_unit = os.path.join(work, "ref_unit.stl"); ref_mm = os.path.join(work, "ref_mm.stl"); ref_mesh = os.path.join(work, "ref_mesh_mm.stl")
        export_stl(shp, ref_unit, tolerance=0.001, angular_tolerance=0.1)
        sol = shp.solids()
        shp_mm = (sol[0] if len(sol) == 1 else shp).scale(factor)
        export_stl(shp_mm, ref_mm, tolerance=0.01, angular_tolerance=0.1)
        m = trimesh.load(os.path.join(pdir, "mesh.stl"), force="mesh")
        bmin, bmax = m.bounds; m.apply_translation(-0.5 * (bmin + bmax)); m.apply_scale(2.0 / float((bmax - bmin).max()) * factor)
        m.export(ref_mesh)
        # --- stage orig: untouched program at unit scale (build123d version drift)
        orig = src.rstrip(b"\n") + b'\nfrom build123d import export_step\nexport_step(result, "output.step")\n'
        rc, stl, _, err = run_program(orig, work, "orig", timeout)
        rec["stages"]["orig"] = {"rc": rc, "iou": iou_pair(stl, ref_unit)["iou_centered"] if rc == 0 else 0.0, "err": err if rc else ""}
        # --- scaled + dialect
        scaled, st_scale = scale_lengths(src, factor)
        rec["scale_stats"] = st_scale
        cands = []
        plain, st_plain = to_dialect(scaled, drop_helpers=True)
        cands.append(("plain", plain, st_plain))
        helpers, st_help = to_dialect(scaled, drop_helpers=False)
        cands.append(("helpers", helpers, st_help))
        chosen = None
        for name, code, st in cands:
            rc, stl, _, err = run_program(code, work, name, timeout)
            iou = iou_pair(stl, ref_mm)["iou_centered"] if rc == 0 else 0.0
            rec["stages"][name] = {"rc": rc, "iou": iou, "err": err if rc else ""}
            if rc == 0 and iou >= min_iou:
                chosen = (name, code); break
        if chosen is None:
            # diagnostics: the best executing stage against the raw mesh (is the mm version closer to
            # the real part than the unit-scale STEP it disagrees with?)
            best = max(((n, s) for n, s in rec["stages"].items() if n != "orig" and s["rc"] == 0), key=lambda x: x[1]["iou"], default=None)
            if best is not None:
                rec["best_stage"] = best[0]
                rec["best_stage_iou_vs_mesh"] = iou_pair(os.path.join(work, f"{best[0]}.stl"), ref_mesh)["iou_centered"]
            rec["error"] = "no stage verified"; return rec
        rec["cleaned"] = False; rec["clean_stats"] = {}
        if do_clean:
            cleaned, st_clean = clean_polylines(chosen[1])
            rec["clean_stats"] = st_clean
            if st_clean:
                rc, stl, _, err = run_program(cleaned, work, "clean", timeout)
                iou = iou_pair(stl, ref_mm)["iou_centered"] if rc == 0 else 0.0
                rec["stages"]["clean"] = {"rc": rc, "iou": iou, "err": err if rc else ""}
                if rc == 0 and iou >= min_iou:
                    chosen = (chosen[0] + "+clean", cleaned); rec["cleaned"] = True
        # --- final artefacts: re-run the chosen program once more, keeping STEP + STL
        rc, stl, stp, err = run_program(chosen[1], work, "final", timeout, want_step=True)
        if rc != 0:
            rec["error"] = f"final rerun rc={rc}"; return rec
        r_step = iou_pair(stl, ref_mm); r_mesh = iou_pair(stl, ref_mesh)
        rec.update(stage=chosen[0], iou_vs_step=r_step["iou_centered"], iou_vs_mesh=r_mesh["iou_centered"],
                   vol_mm3=r_step["vol_pred"], code=chosen[1].decode())
        final_shape = import_step(stp)
        st = _analyse(final_shape); st["bbox_mm"] = [round(x, 3) for x in st["bbox"]]; st["scale"] = factor
        rec["stats"] = st
        os.makedirs(os.path.join(out, "step_mm"), exist_ok=True); os.makedirs(os.path.join(out, "gt_meshes_v15"), exist_ok=True)
        os.makedirs(os.path.join(out, "gt_code"), exist_ok=True)
        shutil.copyfile(stp, os.path.join(out, "step_mm", f"{key}.step"))
        shutil.copyfile(stl, os.path.join(out, "gt_meshes_v15", f"{key}.stl"))
        open(os.path.join(out, "gt_code", f"{key}.py"), "w").write(rec["code"])
        rec["ok"] = True
    except Exception as e:  # noqa: BLE001
        rec["error"] = f"{type(e).__name__}: {str(e)[:200]}"
    finally:
        rec["seconds"] = round(time.time() - t0, 1)
        shutil.rmtree(work, ignore_errors=True)
    return rec


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--exec-one":
        sys.exit(exec_one(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None))
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="", help="<checkout>/dataset")
    ap.add_argument("--best", default="", help="cadfit_abc_best.json: part_id -> {src: version, iou, ...}")
    ap.add_argument("--heldout", default="", help="heldout_file_ids.txt (8-digit id = prefix before '_')")
    ap.add_argument("--out", default="", help="corpus dir")
    ap.add_argument("--iou-py", default="", help="dir containing train_v14/geom/iou.py")
    ap.add_argument("--target-mm", type=float, default=TARGET_MM)
    ap.add_argument("--min-iou", type=float, default=0.99)
    ap.add_argument("--clean", action="store_true")
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--only", default="", help="comma list of part ids, or a file with one id per line")
    ap.add_argument("--round", type=int, default=ROUND, help="decimals kept after scaling (4 = 1e-4 mm; 6 rescues parts with sub-1e-4 features)")
    ap.add_argument("--merge", action="store_true", help="keep earlier records of parts not re-run (retry pass)")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--transform-only", default="", help="print the converted source of one program.py and exit (factor 40)")
    a = ap.parse_args()
    if a.transform_only:
        src = open(a.transform_only, "rb").read()
        s, st = scale_lengths(src, 40.0); print("# scale", st, file=sys.stderr)
        d, st2 = to_dialect(s, True); print("# dialect", st2, file=sys.stderr)
        if a.clean:
            d, st3 = clean_polylines(d); print("# clean", st3, file=sys.stderr)
        sys.stdout.write(d.decode()); return
    if not (a.root and a.best and a.out and a.iou_py):
        ap.error("--root, --best, --out and --iou-py are required for a conversion run")
    best = json.load(open(a.best))
    held = {l.strip().split("_")[0] for l in open(a.heldout) if l.strip()} if a.heldout else set()
    only = None
    if a.only:
        only = {l.strip() for l in open(a.only) if l.strip()} if os.path.exists(a.only) else set(a.only.split(","))
    jobs, skipped = [], collections.Counter()
    for pid, info in sorted(best.items()):
        if only and pid not in only:
            continue
        if pid in held:
            skipped["heldout"] += 1; continue
        pdir = os.path.join(a.root, info["src"], pid)
        if not all(os.path.exists(os.path.join(pdir, f)) for f in ("program.py", "model.step", "mesh.stl")):
            skipped["missing_files"] += 1; continue
        jobs.append(dict(part_id=pid, ver=info["src"], dir=pdir, out=a.out, target_mm=a.target_mm, min_iou=a.min_iou,
                         clean=a.clean, timeout=a.timeout, iou_py=a.iou_py, bank_iou=info.get("iou"), round=a.round))
    if a.limit:
        jobs = jobs[: a.limit]
    a.out = os.path.abspath(a.out)
    for j in jobs:
        j["out"] = a.out; j["iou_py"] = os.path.abspath(a.iou_py)
    os.makedirs(a.out, exist_ok=True)
    print(f"[convert] {len(jobs)} parts, skipped {dict(skipped)}, workers={a.workers}", flush=True)
    import multiprocessing as mp
    recs, t0 = [], time.time()
    with mp.get_context("spawn").Pool(a.workers, maxtasksperchild=8) as pool:
        for i, r in enumerate(pool.imap_unordered(convert_part, jobs)):
            recs.append(r)
            if (i + 1) % 20 == 0 or i + 1 == len(jobs):
                ok = sum(x["ok"] for x in recs)
                print(f"[convert] {i+1}/{len(jobs)} ok={ok} {time.time()-t0:.0f}s", flush=True)
    bank = {j["part_id"]: j["bank_iou"] for j in jobs}
    if a.merge and os.path.exists(os.path.join(a.out, "conversion_log.json")):
        done = {r["key"] for r in recs}
        for r in json.load(open(os.path.join(a.out, "conversion_log.json"))):
            if r["key"] in done:
                continue
            if r["ok"]:
                r["code"] = open(os.path.join(a.out, "gt_code", f"{r['key']}.py")).read()
            recs.append(r); bank.setdefault(r["part_id"], best.get(r["part_id"], {}).get("iou"))
    recs.sort(key=lambda r: r["key"])
    # ---- outputs
    with open(os.path.join(a.out, "gt_code.jsonl"), "w") as f:
        for r in recs:
            if r["ok"]:
                f.write(json.dumps({"key": r["key"], "part_id": r["part_id"], "code": r["code"], "iou_vs_step": r["iou_vs_step"],
                                    "iou_vs_mesh": r["iou_vs_mesh"], "source_version": r["source_version"], "cleaned": r["cleaned"],
                                    "stage": r["stage"], "factor": r["factor"], "bank_iou": bank.get(r["part_id"])}) + "\n")
    parts = {}
    for r in recs:
        if r["ok"]:
            st = dict(r["stats"]); st.update(family=FAMILY, part_id=r["part_id"], source_version=r["source_version"],
                                              src=os.path.join(a.out, "gt_code", f"{r['key']}.py"), bank_iou=bank.get(r["part_id"]),
                                              iou_vs_step=r["iou_vs_step"], iou_vs_mesh=r["iou_vs_mesh"], stage=r["stage"], label="code")
            parts[r["key"]] = st
    # ---- stats
    c = collections.Counter()
    for r in recs:
        for name, s in r["stages"].items():
            c[f"{name}_exec"] += s["rc"] == 0; c[f"{name}_pass"] += (s["rc"] == 0 and s["iou"] >= a.min_iou)
        c["ok"] += r["ok"]; c["cleaned"] += bool(r.get("cleaned")); c["scaled_unknown_ctx_parts"] += bool((r.get("scale_stats") or {}).get("scaled_unknown_ctx"))
        c["circles"] += (r.get("clean_stats") or {}).get("circles", 0) if r.get("cleaned") else 0
        c["arcs"] += (r.get("clean_stats") or {}).get("arcs", 0) if r.get("cleaned") else 0
        if r["ok"]:
            c[f"final_{r['stage']}"] += 1
        else:
            c["fail_" + (r.get("error") or "?")[:40]] += 1
    stats = {"n_parts": len(recs), "skipped": dict(skipped), "min_iou": a.min_iou, "target_mm": a.target_mm, "counts": dict(c),
             "mean_iou_vs_step": sum(r["iou_vs_step"] for r in recs if r["ok"]) / max(1, c["ok"]),
             "mean_iou_vs_mesh": sum(r["iou_vs_mesh"] for r in recs if r["ok"]) / max(1, c["ok"]),
             "per_version": {v: sum(1 for r in recs if r["ok"] and r["source_version"] == v) for v in sorted({r["source_version"] for r in recs})},
             "per_version_total": {v: sum(1 for r in recs if r["source_version"] == v) for v in sorted({r["source_version"] for r in recs})}}
    json.dump(stats, open(os.path.join(a.out, "conversion_stats.json"), "w"), indent=1)
    json.dump([{k: v for k, v in r.items() if k != "code"} for r in recs], open(os.path.join(a.out, "conversion_log.json"), "w"), indent=1)
    man_path = os.path.join(a.out, "manifest.json")
    man = json.load(open(man_path)) if os.path.exists(man_path) else {}
    man.update({"target_mm": a.target_mm, "max_faces": None, "parts": parts, "source": "MBimrose/agentic-mesh-to-cad dataset (CADFit), ABC parts with banked build123d programs",
                "conversion": {"script": "train_v14/mech/benchmarks/convert_cadfit_program.py", "min_iou": a.min_iou, "clean": a.clean, "counts": dict(c)}})
    json.dump(man, open(man_path, "w"), indent=1)
    shutil.rmtree(os.path.join(a.out, "work"), ignore_errors=True)
    stats["rounds"] = dict(collections.Counter(r.get("round", ROUND) for r in recs if r["ok"]))
    json.dump(stats, open(os.path.join(a.out, "conversion_stats.json"), "w"), indent=1)
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
