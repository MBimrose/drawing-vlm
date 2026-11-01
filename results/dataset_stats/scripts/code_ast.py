"""Static (AST) descriptors of one build123d program. Pure python, no build123d import.

Every call site is counted once by callee name (ast.Call; name = Name.id or Attribute.attr), so
a Cylinder inside a 4-iteration loop counts 1 here (the executed count is in exec_worker.py).
Categories (CAT below) cover the build123d API names the corpora use; `b3d_calls` = calls whose
name is any build123d export (list frozen in B3D_NAMES, from build123d 0.11.1 __all__), so plain
python (range, int, math.sin, list.append) is excluded.

Static "feature ops" = call sites in FEATURE_CATS (solid primitives, extrude/revolve/loft/sweep,
holes, fillet/chamfer, shell/offset, mirror, split/thicken/draft) + explicit boolean call sites
(fuse/cut/intersect method calls, `mode=Mode.SUBTRACT|INTERSECT` keywords and shape-algebra
binary operators). A shape-algebra operator is a BinOp/AugAssign with + - & whose left or right
operand is (i) a call to a solid/sketch constructor or a feature op, (ii) a `Pos(...)*X` /
`Rot(...)*X` / `Location*X` product, or (iii) a name that was assigned from (i)/(ii) or from a
feature op / `.part` / `.sketch` anywhere in the program (a cheap type inference; numeric
arithmetic on parameters is never matched).
"""
from __future__ import annotations

import ast
import re

CAT = {
    "solid_prim": ["Box", "Cylinder", "Cone", "Sphere", "Torus", "Wedge"],
    "hole": ["Hole", "CounterBoreHole", "CounterSinkHole"],
    "extrude": ["extrude", "extrude_until"],
    "revolve": ["revolve"],
    "loft": ["loft"],
    "sweep": ["sweep"],
    "fillet": ["fillet", "full_round"],
    "chamfer": ["chamfer"],
    "shell_offset": ["offset", "thicken", "shell"],
    "mirror": ["mirror"],
    "split_section": ["split", "section", "draft", "make_brake_formed", "project_workplane"],
    "bool_method": ["fuse", "cut", "intersect"],
    "sketch_prim": ["Rectangle", "RectangleRounded", "Circle", "Ellipse", "Polygon",
                    "RegularPolygon", "SlotCenterToCenter", "SlotOverall", "SlotCenterPoint",
                    "SlotArc", "Trapezoid", "Triangle", "Text", "Arrow", "ArrowHead",
                    "DimensionLine", "ExtensionLine"],
    "curve_prim": ["Line", "Polyline", "CenterArc", "ThreePointArc", "RadiusArc", "TangentArc",
                   "SagittaArc", "JernArc", "Spline", "Bezier", "Helix", "FilletPolyline",
                   "EllipticalCenterArc", "EllipticalStartArc", "PolarLine", "IntersectingLine",
                   "DoubleTangentArc", "ParabolicCenterArc", "HyperbolicCenterArc", "ArcArcTangentLine",
                   "ArcArcTangentArc", "PointArcTangentLine", "PointArcTangentArc", "BlendCurve"],
    "face_from_wire": ["make_face", "make_hull", "trace", "Face", "Wire", "Solid", "Shell"],
    "pattern": ["GridLocations", "PolarLocations", "HexLocations", "Locations"],
    "transform": ["Pos", "Rot", "Location", "Rotation", "Plane", "moved", "move", "located",
                  "locate", "rotate", "translate", "scale", "mirror_plane"],
    "builder": ["BuildPart", "BuildSketch", "BuildLine"],
    "selector": ["faces", "edges", "vertices", "wires", "solids", "filter_by", "sort_by",
                 "group_by", "filter_by_position"],
    "export": ["export_step", "export_stl"],
    "add_op": ["add"],
}
FEATURE_CATS = ["solid_prim", "hole", "extrude", "revolve", "loft", "sweep", "fillet", "chamfer",
                "shell_offset", "mirror", "split_section"]
NAME2CAT = {n: c for c, ns in CAT.items() for n in ns}
SHAPE_CTORS = set(CAT["solid_prim"] + CAT["hole"] + CAT["sketch_prim"] + CAT["extrude"]
                  + CAT["revolve"] + CAT["loft"] + CAT["sweep"] + CAT["fillet"] + CAT["chamfer"]
                  + CAT["shell_offset"] + CAT["mirror"] + CAT["split_section"]
                  + CAT["bool_method"] + ["make_face", "make_hull", "Solid", "Face", "Part",
                                          "Sketch", "Compound"])
TRANSFORM_NAMES = {"Pos", "Rot", "Location", "Rotation", "Plane"}


def _cname(node):
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


def _is_shape_expr(e, shape_names):
    if isinstance(e, ast.Call):
        n = _cname(e)
        if n in SHAPE_CTORS:
            return True
        # Pos(...)(...) style? rare
        return False
    if isinstance(e, ast.BinOp) and isinstance(e.op, ast.Mult):
        l = e.left
        if isinstance(l, ast.Call) and _cname(l) in TRANSFORM_NAMES:
            return True
        if isinstance(l, ast.Name) and l.id in shape_names:
            return True
        return _is_shape_expr(e.right, shape_names)
    if isinstance(e, ast.BinOp) and isinstance(e.op, (ast.Add, ast.Sub, ast.BitAnd)):
        return _is_shape_expr(e.left, shape_names) or _is_shape_expr(e.right, shape_names)
    if isinstance(e, ast.Name):
        return e.id in shape_names
    if isinstance(e, ast.Attribute):
        return e.attr in ("part", "sketch") or (isinstance(e.value, ast.Name) and e.value.id in shape_names and e.attr in ("part", "sketch"))
    if isinstance(e, ast.Subscript):
        return _is_shape_expr(e.value, shape_names)
    return False


def analyze(code: str) -> dict:
    lines = code.splitlines()
    nonblank = [l for l in lines if l.strip()]
    sloc = [l for l in nonblank if not l.strip().startswith("#")]
    out = {"chars": len(code), "lines": len(lines), "sloc": len(sloc)}
    try:
        tree = ast.parse(code)
    except SyntaxError:
        out["parse_ok"] = False
        return out
    out["parse_ok"] = True
    calls: dict[str, int] = {}
    cats: dict[str, int] = {c: 0 for c in CAT}
    n_for = n_comp = n_def = n_while = n_if = 0
    mode_sub = mode_int = 0
    num_params = 0
    with_builders = {"BuildPart": 0, "BuildSketch": 0, "BuildLine": 0}
    # pass 1: shape-valued names
    shape_names: set[str] = set()
    for _ in range(2):
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                val = node.value
                tg = node.targets if isinstance(node, ast.Assign) else [node.target]
                if val is not None and _is_shape_expr(val, shape_names):
                    for t in tg:
                        if isinstance(t, ast.Name):
                            shape_names.add(t.id)
            elif isinstance(node, ast.withitem) and node.optional_vars is not None:
                if isinstance(node.context_expr, ast.Call) and _cname(node.context_expr) in ("BuildPart", "BuildSketch"):
                    if isinstance(node.optional_vars, ast.Name):
                        shape_names.add(node.optional_vars.id)
    bool_ops = {"add": 0, "subtract": 0, "intersect": 0}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            n = _cname(node)
            if n:
                calls[n] = calls.get(n, 0) + 1
                c = NAME2CAT.get(n)
                if c:
                    cats[c] += 1
                for kw in node.keywords:
                    if kw.arg == "mode":
                        s = ast.unparse(kw.value)
                        if "SUBTRACT" in s:
                            mode_sub += 1
                        elif "INTERSECT" in s:
                            mode_int += 1
        elif isinstance(node, ast.For):
            n_for += 1
        elif isinstance(node, ast.While):
            n_while += 1
        elif isinstance(node, ast.If):
            n_if += 1
        elif isinstance(node, (ast.ListComp, ast.GeneratorExp, ast.SetComp, ast.DictComp)):
            n_comp += 1
        elif isinstance(node, (ast.FunctionDef, ast.Lambda)):
            n_def += 1
        elif isinstance(node, ast.With):
            for it in node.items:
                if isinstance(it.context_expr, ast.Call):
                    cn = _cname(it.context_expr)
                    if cn in with_builders:
                        with_builders[cn] += 1
        elif isinstance(node, (ast.BinOp, ast.AugAssign)):
            op = node.op
            if isinstance(op, (ast.Add, ast.Sub, ast.BitAnd)):
                if isinstance(node, ast.BinOp):
                    hit = _is_shape_expr(node.left, shape_names) or _is_shape_expr(node.right, shape_names)
                else:
                    hit = (isinstance(node.target, ast.Name) and node.target.id in shape_names) or _is_shape_expr(node.value, shape_names)
                if hit:
                    k = {ast.Add: "add", ast.Sub: "subtract", ast.BitAnd: "intersect"}[type(op)]
                    bool_ops[k] += 1
    # numeric top-level parameters: NAME = <number or simple numeric expr of constants>
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            v = node.value
            if isinstance(v, ast.Constant) and isinstance(v.value, (int, float)) and not isinstance(v.value, bool):
                num_params += 1
            elif isinstance(v, ast.UnaryOp) and isinstance(v.operand, ast.Constant) and isinstance(v.operand.value, (int, float)):
                num_params += 1
    num_literals = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Constant)
                       and isinstance(n.value, (int, float)) and not isinstance(n.value, bool))
    bool_ops["subtract"] += mode_sub
    bool_ops["intersect"] += mode_int
    bool_method = cats["bool_method"]
    feature_static = sum(cats[c] for c in FEATURE_CATS) + sum(bool_ops.values()) + bool_method
    out.update({
        "calls": calls, "cats": cats, "n_calls": sum(calls.values()),
        "b3d_calls": sum(v for k, v in calls.items() if k in NAME2CAT),
        "bool_static": bool_ops, "mode_subtract_kw": mode_sub,
        "feature_ops_static": feature_static,
        "n_for": n_for, "n_while": n_while, "n_if": n_if, "n_comp": n_comp, "n_def": n_def,
        "with_builders": with_builders,
        "style": (("hybrid" if (bool_ops["add"] + bool_ops["subtract"] - mode_sub + bool_ops["intersect"] - mode_int + bool_method) else "builder")
                  if with_builders["BuildPart"] else "algebra"),
        "num_params": num_params, "num_literals": num_literals,
        "op_types_static": sorted({c for c in FEATURE_CATS if cats[c]}
                                  | ({"boolean"} if sum(bool_ops.values()) + bool_method else set())),
    })
    return out


THINK_STEP = re.compile(r"^\s*\d+[.)]\s", re.M)


def trace_stats(t: str) -> dict:
    return {"chars": len(t), "lines": len([l for l in t.splitlines() if l.strip()]),
            "steps": len(THINK_STEP.findall(t))}
