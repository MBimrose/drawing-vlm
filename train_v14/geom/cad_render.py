"""Headless CAD-style mesh renderer for figures: numpy z-buffer rasterizer,
orthographic isometric camera, two-light Lambert shading on flat face normals,
and depth-tested crease / silhouette edges (the look of a CAD viewport).

    from cad_render import render_stl
    img = render_stl("part.stl", color="#2f6fd6", size=900)   # PIL RGBA, transparent bg
"""
import numpy as np
import trimesh
from PIL import Image
from matplotlib.colors import to_rgb

ELEV, AZIM = 28.0, -55.0


def view_matrix(elev=ELEV, azim=AZIM):
    e, a = np.radians(elev), np.radians(azim)
    # camera looks from direction d toward the origin, z is up
    d = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    right = np.cross([0, 0, 1], d); right /= np.linalg.norm(right)
    up = np.cross(d, right)
    return np.stack([right, up, d])     # rows: screen x, screen y, depth (toward viewer)


def _raster(P, F, W, H):
    """Z-buffer: returns per-pixel face id (-1 = background) and depth."""
    zbuf = np.full((H, W), -np.inf); fid = np.full((H, W), -1, dtype=np.int64)
    T = P[F]                                              # (n,3,3) screen x,y,depth
    xmin = np.clip(np.floor(T[:, :, 0].min(1)), 0, W - 1).astype(int)
    xmax = np.clip(np.ceil(T[:, :, 0].max(1)), 0, W - 1).astype(int)
    ymin = np.clip(np.floor(T[:, :, 1].min(1)), 0, H - 1).astype(int)
    ymax = np.clip(np.ceil(T[:, :, 1].max(1)), 0, H - 1).astype(int)
    for i in range(len(F)):
        if xmax[i] < xmin[i] or ymax[i] < ymin[i]:
            continue
        (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = T[i]
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(den) < 1e-12:
            continue
        xs = np.arange(xmin[i], xmax[i] + 1) + 0.5; ys = np.arange(ymin[i], ymax[i] + 1) + 0.5
        X, Y = np.meshgrid(xs, ys)
        w0 = ((y1 - y2) * (X - x2) + (x2 - x1) * (Y - y2)) / den
        w1 = ((y2 - y0) * (X - x2) + (x0 - x2) * (Y - y2)) / den
        w2 = 1 - w0 - w1
        m = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        if not m.any():
            continue
        z = w0 * z0 + w1 * z1 + w2 * z2
        sub = zbuf[ymin[i]:ymax[i] + 1, xmin[i]:xmax[i] + 1]
        upd = m & (z > sub)
        sub[upd] = z[upd]
        fid[ymin[i]:ymax[i] + 1, xmin[i]:xmax[i] + 1][upd] = i
    return fid, zbuf


def render_mesh(mesh, color="#2f6fd6", size=900, ss=2, elev=ELEV, azim=AZIM, edge_deg=25.0,
                edge_color=(0.08, 0.08, 0.1), edge_px=1.1, scale=None, center=None, face_colors=None):
    """Render a trimesh to a PIL RGBA image (transparent background).
    `scale`/`center` let several meshes share one camera framing; `face_colors`
    (n_faces x 3, RGB 0-1) overrides the flat `color` (e.g. a deviation map)."""
    V = np.asarray(mesh.vertices, float); F = np.asarray(mesh.faces)
    R = view_matrix(elev, azim)
    c = (V.min(0) + V.max(0)) / 2 if center is None else np.asarray(center, float)
    Q = (V - c) @ R.T
    if scale is None:
        ext = np.abs(Q[:, :2]).max()
        scale = 0.46 / max(ext, 1e-9)
    S = size * ss
    P = np.empty_like(Q)
    P[:, 0] = S / 2 + Q[:, 0] * scale * S
    P[:, 1] = S / 2 - Q[:, 1] * scale * S
    P[:, 2] = Q[:, 2] * scale * S
    fid, zbuf = _raster(P, F, S, S)

    # shading on flat face normals (view space)
    N = mesh.face_normals @ R.T
    keys = [np.array([0.35, 0.55, 0.75]), np.array([-0.6, 0.2, 0.5])]
    keys = [k / np.linalg.norm(k) for k in keys]
    lam = 0.38 + 0.52 * np.clip(N @ keys[0], 0, 1) + 0.18 * np.clip(N @ keys[1], 0, 1)
    spec = 0.10 * np.clip(N[:, 2], 0, 1) ** 12
    base = np.array(to_rgb(color))[None, :] if face_colors is None else np.asarray(face_colors, float)
    fc = np.clip(base * lam[:, None] + spec[:, None], 0, 1)
    img = np.zeros((S, S, 4))
    m = fid >= 0
    img[m, :3] = fc[fid[m]]; img[m, 3] = 1.0

    # crease + silhouette edges, depth-tested against the z-buffer
    adj = mesh.face_adjacency; ang = mesh.face_adjacency_angles
    front = N[:, 2] > 0
    sil = front[adj[:, 0]] != front[adj[:, 1]]
    crease = ang > np.radians(edge_deg)
    sel = (crease | sil) & (front[adj[:, 0]] | front[adj[:, 1]])
    E = mesh.face_adjacency_edges[sel]
    # open boundary edges as well
    try:
        from trimesh.grouping import group_rows
        ue = mesh.edges_sorted
        E = np.vstack([E, ue[group_rows(ue, require_count=1)]])
    except Exception:
        pass
    r = max(1, int(round(edge_px * ss)))
    tol = 0.004 * S
    for a, b in E:
        pa, pb = P[a], P[b]
        n = int(max(abs(pb[0] - pa[0]), abs(pb[1] - pa[1]))) + 2
        t = np.linspace(0, 1, n)[:, None]
        pts = pa[None] * (1 - t) + pb[None] * t
        xi = np.clip(pts[:, 0].astype(int), 0, S - 1); yi = np.clip(pts[:, 1].astype(int), 0, S - 1)
        vis = pts[:, 2] >= zbuf[yi, xi] - tol
        xi, yi = xi[vis], yi[vis]
        for dx in range(-r + 1, r):
            for dy in range(-r + 1, r):
                xx = np.clip(xi + dx, 0, S - 1); yy = np.clip(yi + dy, 0, S - 1)
                img[yy, xx, :3] = edge_color; img[yy, xx, 3] = 1.0
    out = Image.fromarray((img * 255).astype(np.uint8), "RGBA")
    if ss > 1:
        out = out.resize((size, size), Image.LANCZOS)
    return out


def render_stl(path, **kw):
    mesh = trimesh.load(path, force="mesh")
    return render_mesh(mesh, **kw)


def autocrop(img, pad=8):
    bb = img.getbbox()
    if not bb:
        return img
    x0, y0, x1, y1 = bb
    return img.crop((max(0, x0 - pad), max(0, y0 - pad), min(img.width, x1 + pad), min(img.height, y1 + pad)))


def shared_frame(meshes, elev=ELEV, azim=AZIM, fill=0.46):
    """Scale that fits every mesh (each centred on its own bbox, as the IoU metric aligns them)."""
    R = view_matrix(elev, azim); ext = 0.0
    for m in meshes:
        V = np.asarray(m.vertices, float); Q = (V - (V.min(0) + V.max(0)) / 2) @ R.T
        ext = max(ext, np.abs(Q[:, :2]).max())
    return fill / max(ext, 1e-9)
