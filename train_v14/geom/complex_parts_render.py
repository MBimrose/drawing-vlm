"""Render the mesh images for the complex-parts figures (run on a compute node;
the rasterizer is CPU-heavy). Inputs come from complex_parts_assets.py.

    bash train_v14/serv19/cpu_run.sh -c 16 -- .venv/bin/python train_v14/geom/complex_parts_render.py \
        --sheet <keys...> --hero 475993e4-... --agree 475993e4-... 232ebd96-...

PARTS_DIR overrides the part-asset root. Per part dir writes: gt.png, gen.png (served program if present, else medoid), and for --hero: gt_back.png, gen_back.png, dev.png (+dev.json);
for --agree: c{j}.png thumbnails of every executing candidate. All renders of one part share a camera
scale fitted to GT + medoid, each mesh centred on its own bbox (the alignment the IoU metric uses).
"""
import argparse
import json
import os
import sys
from multiprocessing import Pool

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from cad_render import render_mesh, shared_frame  # noqa: E402

D = os.environ.get("PARTS_DIR", "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/figures/complex_parts/parts")
GT_C, GEN_C, FIRST_C = "#8a8f99", "#2f6fd6", "#9fb3d6"
BACK = dict(elev=28.0, azim=125.0)
DEV_CLIP = 2.0   # mm, colour-scale limit of the deviation map


def centred(m):
    m = m.copy(); m.apply_translation(-(m.bounds[0] + m.bounds[1]) / 2); return m


def job(a):
    kind, k, j = a
    d = os.path.join(D, k); data = json.load(open(os.path.join(d, "data.json")))
    gt = centred(trimesh.load(os.path.join(d, "gt.stl"), force="mesh"))
    # the shown generation: the served program when the part has one (real bench), else the medoid
    gen = os.path.join(d, "served.stl") if data.get("served_ok") else os.path.join(d, f"cand{data['medoid']}.stl")
    md = centred(trimesh.load(gen, force="mesh"))
    sc = shared_frame([gt, md])
    if kind == "gt":
        render_mesh(gt, color=GT_C, size=900, scale=sc, center=0 * gt.centroid).save(os.path.join(d, "gt.png"))
    elif kind == "gen":
        render_mesh(md, color=GEN_C, size=900, scale=sc, center=0 * md.centroid).save(os.path.join(d, "gen.png"))
    elif kind == "gt_back":
        scb = shared_frame([gt, md], **BACK)
        render_mesh(gt, color=GT_C, size=900, scale=scb, center=0 * gt.centroid, **BACK).save(os.path.join(d, "gt_back.png"))
    elif kind == "gen_back":
        scb = shared_frame([gt, md], **BACK)
        render_mesh(md, color=GEN_C, size=900, scale=scb, center=0 * md.centroid, **BACK).save(os.path.join(d, "gen_back.png"))
    elif kind == "dev":
        L = (md.bounds[1] - md.bounds[0]).max()
        V, F = trimesh.remesh.subdivide_to_size(md.vertices, md.faces, max_edge=L / 70, max_iter=12)
        fine = trimesh.Trimesh(V, F, process=False)
        # positive = generated surface lies inside GT (material missing), negative = outside (excess)
        sd = trimesh.proximity.signed_distance(gt, fine.triangles_center)
        import matplotlib
        cmap = matplotlib.colormaps["RdBu"]
        fc = cmap(np.clip(0.5 + 0.5 * sd / DEV_CLIP, 0, 1))[:, :3]
        render_mesh(fine, size=900, scale=sc, center=np.zeros(3), face_colors=fc).save(os.path.join(d, "dev.png"))
        a = np.abs(sd); w = fine.area_faces / fine.area_faces.sum()
        json.dump({"clip_mm": DEV_CLIP, "within_0p5mm": float(w[a <= 0.5].sum()), "within_1mm": float(w[a <= 1.0].sum()),
                   "mean_abs_mm": float((w * a).sum()), "p95_mm": float(np.quantile(a, 0.95)), "bbox_mm": float(L)},
                  open(os.path.join(d, "dev.json"), "w"), indent=1)
    elif kind == "first":   # first executing draw: what a single-shot model would have served
        j0 = next(i for i, ok in enumerate(data["stl_ok"]) if ok)
        c = centred(trimesh.load(os.path.join(d, f"cand{j0}.stl"), force="mesh"))
        render_mesh(c, color=FIRST_C, size=900, scale=sc, center=np.zeros(3)).save(os.path.join(d, "first.png"))
    elif kind == "cand":
        c = centred(trimesh.load(os.path.join(d, f"cand{j}.stl"), force="mesh"))
        render_mesh(c, color=GEN_C, size=500, scale=sc, center=np.zeros(3), edge_px=0.9).save(os.path.join(d, f"c{j}.png"))
    return kind, k[:8], j


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", nargs="*", default=[])
    ap.add_argument("--hero", nargs="*", default=[])
    ap.add_argument("--agree", nargs="*", default=[])
    a = ap.parse_args()
    jobs = [(t, k, None) for k in set(a.sheet + a.hero + a.agree) for t in ("gt", "gen")]
    jobs += [(t, k, None) for k in a.hero for t in ("gt_back", "gen_back", "dev", "first")]
    for k in a.agree:
        ok = json.load(open(os.path.join(D, k, "data.json")))["stl_ok"]
        jobs += [("cand", k, j) for j in range(len(ok)) if ok[j]]
    with Pool(min(32, len(jobs))) as p:
        for r in p.imap_unordered(job, jobs):
            print("[render]", *r, flush=True)


if __name__ == "__main__":
    main()
