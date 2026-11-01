"""Persistent worker: reads JSON tasks on stdin, writes one JSON result per line on the original
stdout (user prints are sent to /dev/null). Driven by run_exec.py, which kills and respawns a
worker that exceeds the per-task timeout.

Task  {"id": str, "code": str}  -> execute (as exec_harness.py: fresh globals, OUTPUT_PATH,
                                    temp cwd), re-import output.step, B-rep stats + executed op counts
      {"id": str, "step": path} -> B-rep stats of the STEP file

Executed op counts ("dyn"): build123d functions/classes are wrapped before the program's
`from build123d import *`; a call is counted only when it is not nested inside another counted
call (user-level calls only; e.g. the Cylinder a CounterBoreHole builds internally is not
counted, a Cylinder inside a 4-iteration python loop counts 4). Booleans:
  - shape algebra  a + b / a - b / a & b  and .fuse/.cut/.intersect at user level, split into
    3D (result has a solid) and 2D (sketch) ones;
  - builder-mode implicit booleans: a solid added to a BuildPart that already holds a part with
    mode ADD (= fuse), or any mode SUBTRACT / INTERSECT (counted in Builder._add_to_context when
    called directly by a user-level op), one per solid passed (a Hole placed at 4 Locations = 4).
"""
from __future__ import annotations

import functools
import json
import os
import sys
import tempfile
import time
import traceback

_out = os.fdopen(os.dup(1), "w", buffering=1)
_devnull = open(os.devnull, "w")
os.dup2(_devnull.fileno(), 1)
sys.stdout = _devnull

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build123d as b3d  # noqa: E402
from build123d import build_common  # noqa: E402
from brep import brep_stats  # noqa: E402
from code_ast import CAT  # noqa: E402

COUNTS: dict[str, int] = {}
DEPTH = [0]


def _inc(k, n=1):
    COUNTS[k] = COUNTS.get(k, 0) + n


def _wrap(name, fn):
    @functools.wraps(fn)
    def w(*a, **k):
        if DEPTH[0] == 0:
            _inc(name)
        DEPTH[0] += 1
        try:
            return fn(*a, **k)
        finally:
            DEPTH[0] -= 1
    return w


def _wrap_cls(name, fn):
    """Constructor wrapper: counts the call (name) and its placed instances (inst_<name> = number
    of active Locations when used inside a builder, else 1)."""
    @functools.wraps(fn)
    def w(*a, **k):
        if DEPTH[0] == 0:
            _inc(name)
            n = 1
            try:
                ctx = build_common.LocationList._get_context()
                if ctx is not None and build_common.Builder._get_context() is not None:
                    n = max(1, len(ctx.local_locations))
            except Exception:
                pass
            _inc("inst_" + name, n)
        DEPTH[0] += 1
        try:
            return fn(*a, **k)
        finally:
            DEPTH[0] -= 1
    return w


def _has_solid(r):
    try:
        return len(r.solids()) > 0
    except Exception:
        return False


def _wrap_bool(kind, fn):
    @functools.wraps(fn)
    def w(self, *a, **k):
        top = DEPTH[0] == 0
        DEPTH[0] += 1
        try:
            r = fn(self, *a, **k)
        finally:
            DEPTH[0] -= 1
        if top:
            _inc(f"bool3d_{kind}" if _has_solid(r) else f"bool2d_{kind}")
        return r
    return w


FUNCS = (CAT["extrude"] + CAT["revolve"] + CAT["loft"] + CAT["sweep"] + CAT["fillet"]
         + CAT["chamfer"] + CAT["shell_offset"] + CAT["mirror"] + CAT["split_section"]
         + ["make_face", "make_hull", "trace", "add", "project", "scale"])
CLASSES = (CAT["solid_prim"] + CAT["hole"] + CAT["sketch_prim"] + CAT["curve_prim"]
           + CAT["pattern"])


def instrument():
    for n in FUNCS:
        f = getattr(b3d, n, None)
        if callable(f) and not isinstance(f, type):
            setattr(b3d, n, _wrap(n, f))
    for n in CLASSES:
        c = getattr(b3d, n, None)
        if isinstance(c, type):
            c.__init__ = (_wrap(n, c.__init__) if n in CAT["pattern"] else _wrap_cls(n, c.__init__))
    # every Shape subclass that defines its own boolean dunder / method (Shape, Compound, ...)
    seen, stack = set(), [b3d.Shape]
    while stack:
        cls = stack.pop()
        if cls in seen:
            continue
        seen.add(cls)
        stack.extend(cls.__subclasses__())
        for meth, kind in (("__add__", "add"), ("__sub__", "subtract"), ("__and__", "intersect"),
                           ("fuse", "add"), ("cut", "subtract"), ("intersect", "intersect")):
            if meth in cls.__dict__:
                setattr(cls, meth, _wrap_bool(kind, cls.__dict__[meth]))
    orig = build_common.Builder._add_to_context

    @functools.wraps(orig)
    def atc(self, *objects, **kw):
        if DEPTH[0] == 1 and isinstance(self, b3d.BuildPart):
            mode = kw.get("mode", b3d.Mode.ADD)
            ns = 0
            for o in objects:
                try:
                    ns += len(o.solids())
                except Exception:
                    pass
            if ns:
                cur = getattr(self, "_obj", None)
                has = cur is not None and _has_solid(cur)
                if mode == b3d.Mode.ADD:
                    if ns - (0 if has else 1) > 0:
                        _inc("builder_add", ns - (0 if has else 1))
                elif mode == b3d.Mode.SUBTRACT:
                    _inc("builder_subtract", ns)
                elif mode == b3d.Mode.INTERSECT:
                    _inc("builder_intersect", ns)
        return orig(self, *objects, **kw)
    build_common.Builder._add_to_context = atc


instrument()


def run_code(code):
    COUNTS.clear()
    DEPTH[0] = 0
    with tempfile.TemporaryDirectory(prefix="dsexec_") as td:
        cwd = os.getcwd()
        os.chdir(td)
        try:
            g = {"__name__": "__main__", "OUTPUT_PATH": "output.step"}
            t0 = time.time()
            try:
                exec(compile(code, "<generated>", "exec"), g)  # noqa: S102
            except SystemExit:
                pass
            except BaseException as e:  # noqa: BLE001
                return {"ok": False, "stage": "exec", "err": f"{type(e).__name__}: {str(e)[:200]}",
                        "dyn": dict(COUNTS)}
            t_exec = time.time() - t0
            dyn = dict(COUNTS)
            step = os.path.join(td, "output.step")
            if not os.path.exists(step) or os.path.getsize(step) == 0:
                return {"ok": False, "stage": "nostep", "dyn": dyn}
            try:
                shp = b3d.import_step(step)
                st = brep_stats(shp.wrapped)
            except BaseException as e:  # noqa: BLE001
                return {"ok": False, "stage": "brep", "err": str(e)[:200], "dyn": dyn}
            return {"ok": True, "dyn": dyn, "brep": st, "t_exec": t_exec}
        finally:
            os.chdir(cwd)


def run_step(path):
    shp = b3d.import_step(path)
    return {"ok": True, "brep": brep_stats(shp.wrapped)}


def main():
    _out.write(json.dumps({"ready": True}) + "\n")
    for line in sys.stdin:
        task = json.loads(line)
        try:
            r = run_code(task["code"]) if "code" in task else run_step(task["step"])
        except BaseException as e:  # noqa: BLE001
            r = {"ok": False, "stage": "worker", "err": traceback.format_exc()[-300:]}
        r["id"] = task["id"]
        _out.write(json.dumps(r) + "\n")


if __name__ == "__main__":
    main()
