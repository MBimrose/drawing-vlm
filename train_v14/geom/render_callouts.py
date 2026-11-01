"""Render drawing / ground truth / SFT + GRPO pick (no repair) for called-out parts of a scatter, from serve_full_timed.py
records. Pick = the top verifier [+ render-compare] candidate (chosen[0]); GT and pick share one camera frame.
-> <out>/<key>/{drawing,gt,pick}.png + meta.json (iou, time, stage times)

    .venv/bin/python train_v14/geom/render_callouts.py --records R.jsonl --bench BENCH_DIR --out DIR PREFIX [PREFIX ...]
BENCH_DIR holds eval_cache_v15.pkl (drawing PNGs) and gt_meshes_v15/<key>.stl.
"""
import argparse
import json
import os
import pickle
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.dirname(HERE), HERE]
from cad_render import render_mesh, shared_frame  # noqa: E402
from rft_generate import exec_to_stl  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", nargs="+", required=True); ap.add_argument("--bench", nargs="+", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("prefixes", nargs="+")
    ap.add_argument("--iso", action="store_true", help="true isometric from +X -Y +Z (the drawing's ISO VIEW camera, draftwright "
                                                       "projection._project_iso) instead of the default 28/-55 view")
    a = ap.parse_args()
    V = dict(elev=float(np.degrees(np.arcsin(1 / np.sqrt(3)))), azim=-45.0) if a.iso else {}
    R = {}; where = {}
    for rec, bench in zip(a.records, a.bench):
        for l in open(rec):
            r = json.loads(l); R[r["key"]] = r; where[r["key"]] = bench
    caches = {b: pickle.load(open(f"{b}/eval_cache_v15.pkl", "rb"))["samples"] for b in set(a.bench)}

    def one(pre):
        k = next(x for x in R if x.startswith(pre)); r = R[k]; b = where[k]; d = f"{a.out}/{k}"; os.makedirs(d, exist_ok=True)
        open(f"{d}/drawing.png", "wb").write(caches[b][k]["png"])
        with tempfile.TemporaryDirectory(prefix="rco_") as td:
            stl = f"{td}/p.stl"
            if not exec_to_stl(r["codes"][r["chosen"][0]], stl, td, "p"):
                return k, False
            c = lambda m: (m.apply_translation(-(m.bounds[0] + m.bounds[1]) / 2), m)[1]
            gt = c(trimesh.load(f"{b}/gt_meshes_v15/{k}.stl", force="mesh")); pk = c(trimesh.load(stl, force="mesh"))
            sc = shared_frame([gt, pk], **V)
            render_mesh(gt, color="#8a8f99", size=600, scale=sc, center=np.zeros(3), **V).save(f"{d}/gt.png")
            render_mesh(pk, color="#2f6fd6", size=600, scale=sc, center=np.zeros(3), **V).save(f"{d}/pick.png")
        t = r["times"]
        json.dump({"key": k, "iou": r["iou_start"], "time": t["generate"] + t["execute"] + t["select"],
                   "stages": {s: t[s] for s in ("generate", "execute", "select")}}, open(f"{d}/meta.json", "w"))
        return k, True
    for k, ok in ThreadPoolExecutor(8).map(one, a.prefixes):
        print(k[:24], ok, flush=True)


if __name__ == "__main__":
    main()
