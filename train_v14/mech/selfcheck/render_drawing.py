"""Render a STEP file back into a dimensioned multi-view drawing PNG.

FALLBACK renderer (the upstream draftwright renderer in MBimrose/step_to_drw is
not present in this checkout and the cluster has no GitHub access). It mimics
the dataset's sheet: third-angle top / front / right views with hidden lines
dashed, an isometric view ("ISO VIEW (NTS)"), navy dimension lines for the
overall extents of every view, hole callouts (`N× ⌀d`) with centre-position
dimensions in the top view, and a title block. Line work comes from OCCT HLR
via build123d's `project_to_viewport`; the raster is drawn with matplotlib
(no cairosvg in the venv). Output is 1920x1280 like the training drawings.

    python render_drawing.py <part.step> <out.png> [--label TEXT]
"""
from __future__ import annotations

import argparse
import math
import sys
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch  # noqa: E402

EDGE_COL = "#6b4a25"     # brownish visible edges (dataset style)
HID_COL = "#9a7b52"
DIM_COL = "#1c2a80"      # navy dimensions
FONT = {"family": "DejaVu Sans Mono", "size": 13, "color": DIM_COL}

VIEWS = {
    # name: (viewport_origin_dir, up)
    "top": ((0, 0, 1), (0, 1, 0)),
    "front": ((0, -1, 0), (0, 0, 1)),
    "right": ((1, 0, 0), (0, 0, 1)),
    "iso": ((1, -1, 1), (0, 0, 1)),
}


def fmt(v: float) -> str:
    """Dataset-style significant figures: >=10 integer, <10 one decimal."""
    if abs(v) >= 10:
        return str(int(round(v)))
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def _edge_polyline(e, n=24):
    if e.geom_type.name == "LINE":
        pts = [e.position_at(0), e.position_at(1)]
    else:
        pts = [e.position_at(i / n) for i in range(n + 1)]
    return [(p.X, p.Y) for p in pts]


def project_views(shape, diag):
    """Return {view: {"vis": [polylines], "hid": [...], "circles": [(cx,cy,r)]}}
    in each viewport's own 2D coordinates."""
    out = {}
    c = shape.center()
    for name, (d, up) in VIEWS.items():
        origin = (c.X + d[0] * diag * 3, c.Y + d[1] * diag * 3, c.Z + d[2] * diag * 3)
        vis, hid = shape.project_to_viewport(origin, up, look_at=c)
        rec = {"vis": [_edge_polyline(e) for e in vis],
               "hid": [_edge_polyline(e) for e in hid], "circles": []}
        if name != "iso":
            for e in vis:
                if e.geom_type.name == "CIRCLE" and e.is_closed:
                    cc = e.arc_center
                    rec["circles"].append((cc.X, cc.Y, float(e.radius)))
        out[name] = rec
    return out


def _bbox(polys):
    xs = [x for pl in polys for x, _ in pl]
    ys = [y for pl in polys for _, y in pl]
    if not xs:
        return (0, 0, 0, 0)
    return (min(xs), min(ys), max(xs), max(ys))


class Sheet:
    def __init__(self, ax):
        self.ax = ax

    def lines(self, polys, dx, dy, color, ls="-", lw=1.4):
        for pl in polys:
            xs = [x + dx for x, _ in pl]
            ys = [y + dy for _, y in pl]
            self.ax.plot(xs, ys, color=color, ls=ls, lw=lw, solid_capstyle="round")

    def dim_h(self, x0, x1, y, text, ext_from=None, gap=1.5):
        """Horizontal dimension between x0..x1 drawn at height y."""
        ax = self.ax
        if ext_from is not None:
            for x in (x0, x1):
                ax.plot([x, x], [ext_from + math.copysign(gap, y - ext_from), y + math.copysign(gap, y - ext_from)],
                        color=DIM_COL, lw=0.8)
        ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle="<|-|>", mutation_scale=12,
                                     color=DIM_COL, lw=1.0, shrinkA=0, shrinkB=0))
        ax.text((x0 + x1) / 2, y, text, ha="center", va="center",
                bbox=dict(facecolor="white", edgecolor="none", pad=1.5), **FONT)

    def dim_v(self, y0, y1, x, text, ext_from=None, gap=1.5):
        ax = self.ax
        if ext_from is not None:
            for y in (y0, y1):
                ax.plot([ext_from + math.copysign(gap, x - ext_from), x + math.copysign(gap, x - ext_from)], [y, y],
                        color=DIM_COL, lw=0.8)
        ax.add_patch(FancyArrowPatch((x, y0), (x, y1), arrowstyle="<|-|>", mutation_scale=12,
                                     color=DIM_COL, lw=1.0, shrinkA=0, shrinkB=0))
        ax.text(x, (y0 + y1) / 2, text, ha="center", va="center", rotation=90,
                bbox=dict(facecolor="white", edgecolor="none", pad=1.5), **FONT)

    def leader(self, x, y, tx, ty, text):
        self.ax.add_patch(FancyArrowPatch((tx, ty), (x, y), arrowstyle="-|>", mutation_scale=12,
                                         color=DIM_COL, lw=1.0, shrinkA=0, shrinkB=0))
        self.ax.text(tx + 0.5, ty, text, ha="left", va="center",
                     bbox=dict(facecolor="white", edgecolor="none", pad=1.5), **FONT)


def render(step_path: str, out_png: str, label: str = "GENERATED PART") -> dict:
    from build123d import import_step
    shape = import_step(step_path)
    bb = shape.bounding_box()
    W, D, H = bb.size.X, bb.size.Y, bb.size.Z
    diag = max(bb.size.length, 1.0)
    views = project_views(shape, diag)
    try:
        vol = float(abs(shape.volume))
    except Exception:
        vol = float("nan")

    # ---- layout in "sheet mm" (scaled to fit) ----
    boxes = {k: _bbox(v["vis"] + v["hid"]) for k, v in views.items()}
    dim_margin = max(0.16 * max(W, D, H), 6.0)   # room for dimension lines
    gap = dim_margin * 1.6
    # place views: front at origin, top above, right to the right, iso far right
    pos = {}
    fb = boxes["front"]; pos["front"] = (-fb[0], -fb[1])
    tb = boxes["top"]; pos["top"] = (-tb[0], -tb[1] + (fb[3] - fb[1]) + gap)
    rb = boxes["right"]; pos["right"] = (-rb[0] + (fb[2] - fb[0]) + gap, -rb[1])
    ib = boxes["iso"]
    iso_x = max(fb[2] - fb[0] + gap + rb[2] - rb[0], tb[2] - tb[0]) + gap * 1.2
    iso_y = (fb[3] - fb[1]) + gap + (tb[3] - tb[1]) - (ib[3] - ib[1])
    pos["iso"] = (-ib[0] + iso_x, -ib[1] + iso_y)

    fig = plt.figure(figsize=(19.2, 12.8), dpi=100)
    ax = fig.add_axes([0.03, 0.10, 0.94, 0.86])
    ax.set_aspect("equal"); ax.axis("off")
    sh = Sheet(ax)
    for name, v in views.items():
        dx, dy = pos[name]
        if name != "iso":
            sh.lines(v["hid"], dx, dy, HID_COL, ls=(0, (4, 3)), lw=0.9)
        sh.lines(v["vis"], dx, dy, EDGE_COL, lw=1.5 if name != "iso" else 1.2)

    def placed_box(name):
        b = boxes[name]; dx, dy = pos[name]
        return (b[0] + dx, b[1] + dy, b[2] + dx, b[3] + dy)

    # ---- overall dimensions (extents of each view) ----
    dims_txt = []
    for name, (htxt, vtxt) in {"top": (W, D), "front": (W, H), "right": (D, H)}.items():
        x0, y0, x1, y1 = placed_box(name)
        off = dim_margin * 0.6
        if name == "top":
            sh.dim_h(x0, x1, y1 + off, fmt(htxt), ext_from=y1)
            sh.dim_v(y0, y1, x0 - off, fmt(vtxt), ext_from=x0)
        else:
            sh.dim_h(x0, x1, y0 - off, fmt(htxt), ext_from=y0)
            sh.dim_v(y0, y1, x1 + off, fmt(vtxt), ext_from=x1)
    dims_txt.append(f"OVERALL {fmt(W)} x {fmt(D)} x {fmt(H)}")

    # ---- hole callouts + positions in the top view (then front/right if none) ----
    callouts = []
    for name in ("top", "front", "right"):
        circ = views[name]["circles"]
        if not circ:
            continue
        dx, dy = pos[name]
        x0, y0, x1, y1 = placed_box(name)
        groups = defaultdict(list)
        for cx, cy, r in circ:
            groups[round(2 * r, 1)].append((cx + dx, cy + dy))
        k = 0
        for dia, cs in sorted(groups.items(), key=lambda kv: -len(kv[1]))[:3]:
            cs = sorted(cs)
            cx, cy = cs[0]
            tx = x1 + dim_margin * (1.3 + 0.9 * k)
            ty = cy + dim_margin * (0.35 * (k + 1))
            txt = (f"{len(cs)}x " if len(cs) > 1 else "") + f"⌀{fmt(dia)}"
            sh.leader(cx + dia / 2 * 0.7, cy + dia / 2 * 0.7, tx, ty, txt)
            callouts.append(f"{name}: {txt}")
            if name == "top":
                # position of the first hole from the view's left / bottom edges
                lvl = y1 + dim_margin * (1.25 + 0.55 * k)
                sh.dim_h(x0, cx, lvl, fmt(cx - x0), ext_from=None)
                ax.plot([cx, cx], [cy, lvl + 1.5], color=DIM_COL, lw=0.8)
                if len(cs) > 1:
                    cx2, cy2 = cs[-1]
                    if abs(cx2 - cx) > 0.5:
                        lvl2 = lvl + dim_margin * 0.5
                        sh.dim_h(cx, cx2, lvl2, fmt(cx2 - cx))
                        ax.plot([cx2, cx2], [cy2, lvl2 + 1.5], color=DIM_COL, lw=0.8)
                    if abs(cy2 - cy) > 0.5:
                        lx = x0 - dim_margin * (1.25 + 0.55 * k)
                        sh.dim_v(cy, cy2, lx, fmt(abs(cy2 - cy)))
                        ax.plot([cx, lx - 1.5], [cy, cy], color=DIM_COL, lw=0.8)
                        ax.plot([cx2, lx - 1.5], [cy2, cy2], color=DIM_COL, lw=0.8)
                lvl0 = x0 - dim_margin * (1.25 + 0.55 * k)
                sh.dim_v(y0, cy, lvl0 - dim_margin * 0.5 * (len(cs) > 1 and abs(cs[-1][1] - cy) > 0.5), fmt(cy - y0))
            k += 1
        if name == "top":
            break   # holes found in the top view: don't clutter the others
        break

    # ---- iso label, title block ----
    ix0, iy0, ix1, iy1 = placed_box("iso")
    ax.text((ix0 + ix1) / 2, iy0 - dim_margin * 0.8, "ISO VIEW (NTS)", ha="center", va="top", **FONT)
    ax.autoscale_view()
    ax.margins(0.06)
    fig.text(0.62, 0.05, f"{label}    {dims_txt[0]} mm    VOLUME {vol:,.0f} mm³",
             fontsize=13, family="DejaVu Sans Mono", color="#222",
             bbox=dict(facecolor="white", edgecolor="#222", pad=8))
    fig.text(0.62, 0.02, "SELF-CHECK RENDER    ISO 2768-m    draftwright-lite (fallback)",
             fontsize=11, family="DejaVu Sans Mono", color="#222")
    fig.savefig(out_png, dpi=100, facecolor="white")
    plt.close(fig)
    return {"W": W, "D": D, "H": H, "volume": vol, "callouts": callouts,
            "n_edges": {k: len(v["vis"]) + len(v["hid"]) for k, v in views.items()}}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step"); ap.add_argument("out")
    ap.add_argument("--label", default="GENERATED PART")
    a = ap.parse_args()
    info = render(a.step, a.out, a.label)
    print(info)
    sys.exit(0)
