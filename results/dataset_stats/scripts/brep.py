"""B-rep topology / geometry descriptors of one shape (OCP). Used for GT STEP files and for
executed programs (which are exported to STEP and re-imported, so both go through import_step).

Definitions
- solids / shells / faces / edges / vertices / wires: unique sub-shapes (TopTools_IndexedMapOfShape).
- face types: BRepAdaptor_Surface.GetType() per unique face.
- edge types: BRepAdaptor_Curve.GetType() per unique edge.
- genus: Euler-Poincare  V - E + F - (L - F) = 2 (S - G)  with L = wires summed over faces and
  S = shells  ->  G = S - (V - E + 2F - L) / 2. For a single closed solid G = number of handles
  (through-holes / loops). Checked: box 0, cylinder 0, box with one through hole 1.
- concave_cyl_faces: cylindrical faces whose outward normal points toward the cylinder axis
  (bores / holes / internal fillets), sampled at the face's mid (u, v).
- bbox: axis-aligned, sorted dims (mm); fill = volume / bbox volume; aspect = max / min dim.
"""
from __future__ import annotations

import math

from OCP.BRep import BRep_Tool  # noqa: F401
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepGProp import BRepGProp
from OCP.Bnd import Bnd_Box
from OCP.GeomAbs import (GeomAbs_BezierSurface, GeomAbs_BSplineSurface, GeomAbs_Cone,
                         GeomAbs_Cylinder, GeomAbs_OffsetSurface, GeomAbs_OtherSurface,
                         GeomAbs_Plane, GeomAbs_Sphere, GeomAbs_SurfaceOfExtrusion,
                         GeomAbs_SurfaceOfRevolution, GeomAbs_Torus,
                         GeomAbs_Line, GeomAbs_Circle, GeomAbs_Ellipse, GeomAbs_Hyperbola,
                         GeomAbs_Parabola, GeomAbs_BezierCurve, GeomAbs_BSplineCurve,
                         GeomAbs_OffsetCurve, GeomAbs_OtherCurve)
from OCP.GProp import GProp_GProps
from OCP.gp import gp_Pnt, gp_Vec
from OCP.TopAbs import (TopAbs_EDGE, TopAbs_FACE, TopAbs_REVERSED, TopAbs_SHELL, TopAbs_SOLID,
                        TopAbs_VERTEX, TopAbs_WIRE)
from OCP.TopExp import TopExp, TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.TopTools import TopTools_IndexedMapOfShape

SURF = {GeomAbs_Plane: "plane", GeomAbs_Cylinder: "cylinder", GeomAbs_Cone: "cone",
        GeomAbs_Sphere: "sphere", GeomAbs_Torus: "torus", GeomAbs_BezierSurface: "bezier",
        GeomAbs_BSplineSurface: "bspline", GeomAbs_SurfaceOfRevolution: "revolution",
        GeomAbs_SurfaceOfExtrusion: "extrusion", GeomAbs_OffsetSurface: "offset",
        GeomAbs_OtherSurface: "other"}
CURV = {GeomAbs_Line: "line", GeomAbs_Circle: "circle", GeomAbs_Ellipse: "ellipse",
        GeomAbs_Hyperbola: "hyperbola", GeomAbs_Parabola: "parabola",
        GeomAbs_BezierCurve: "bezier", GeomAbs_BSplineCurve: "bspline",
        GeomAbs_OffsetCurve: "offset", GeomAbs_OtherCurve: "other"}


def _map(shape, kind):
    m = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, kind, m)
    return m


def _concave_cyl(face, ad):
    try:
        u = 0.5 * (ad.FirstUParameter() + ad.LastUParameter())
        v = 0.5 * (ad.FirstVParameter() + ad.LastVParameter())
        p, du, dv = gp_Pnt(), gp_Vec(), gp_Vec()
        ad.D1(u, v, p, du, dv)
        n = du.Crossed(dv)
        if face.Orientation() == TopAbs_REVERSED:
            n.Reverse()
        ax = ad.Cylinder().Axis()
        o, d = ax.Location(), ax.Direction()
        w = gp_Vec(o, p)
        t = w.Dot(gp_Vec(d))
        radial = w - gp_Vec(d).Multiplied(t)
        return n.Dot(radial) < 0
    except Exception:
        return None


def brep_stats(shape) -> dict:
    """shape: a TopoDS_Shape (build123d: obj.wrapped)."""
    faces = _map(shape, TopAbs_FACE)
    edges = _map(shape, TopAbs_EDGE)
    verts = _map(shape, TopAbs_VERTEX)
    solids = _map(shape, TopAbs_SOLID)
    shells = _map(shape, TopAbs_SHELL)
    ftypes: dict[str, int] = {}
    concave = 0
    loops = 0
    for i in range(1, faces.Extent() + 1):
        f = TopoDS.Face_s(faces.FindKey(i))
        ad = BRepAdaptor_Surface(f)
        t = SURF.get(ad.GetType(), "other")
        ftypes[t] = ftypes.get(t, 0) + 1
        if t == "cylinder" and _concave_cyl(f, ad):
            concave += 1
        ex = TopExp_Explorer(f, TopAbs_WIRE)
        while ex.More():
            loops += 1
            ex.Next()
    etypes: dict[str, int] = {}
    for i in range(1, edges.Extent() + 1):
        e = TopoDS.Edge_s(edges.FindKey(i))
        try:
            t = CURV.get(BRepAdaptor_Curve(e).GetType(), "other")
        except Exception:
            t = "degenerate"
        etypes[t] = etypes.get(t, 0) + 1
    F, E, V, S, L = faces.Extent(), edges.Extent(), verts.Extent(), shells.Extent(), loops
    genus = S - (V - E + 2 * F - L) / 2 if S else None
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    vol = abs(props.Mass())
    sprops = GProp_GProps()
    BRepGProp.SurfaceProperties_s(shape, sprops)
    area = sprops.Mass()
    bb = Bnd_Box()
    BRepBndLib.AddOptimal_s(shape, bb, False, False)
    x0, y0, z0, x1, y1, z1 = bb.Get()
    dims = sorted([x1 - x0, y1 - y0, z1 - z0])
    bvol = dims[0] * dims[1] * dims[2]
    return {
        "solids": solids.Extent(), "shells": S, "faces": F, "edges": E, "vertices": V,
        "loops": L, "inner_loops": L - F, "genus": genus,
        "face_types": ftypes, "edge_types": etypes, "concave_cyl_faces": concave,
        "volume": vol, "area": area, "bbox": dims,
        "fill": vol / bvol if bvol > 1e-12 else None,
        "aspect": dims[2] / dims[0] if dims[0] > 1e-9 else None,
        "max_dim": dims[2],
    }


def step_stats(path: str) -> dict:
    from build123d import import_step
    shp = import_step(path)
    return brep_stats(shp.wrapped)
