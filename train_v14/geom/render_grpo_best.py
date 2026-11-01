"""Render the SFT + GRPO pick (no repair: top verifier + render-compare candidate) and the GT for selected bench parts,
from serve_full_timed.py records. -> results/figures/pipeline_timing/best/<key>/{drawing,gt,pick}.png + meta.json"""
import json, os, pickle, sys, tempfile
import numpy as np, trimesh
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.dirname(HERE), HERE]
from cad_render import render_mesh, shared_frame
from rft_generate import exec_to_stl
from concurrent.futures import ThreadPoolExecutor
DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"; O = f"{DV}/results/figures/pipeline_timing/best"
BENCH = f"{DV}/results/bench_b/bench"
R = {json.loads(l)["key"]: json.loads(l) for l in open(f"{DV}/results/figures/pipeline_timing/s05_full_bench_b.jsonl")}
cache = pickle.load(open(f"{BENCH}/eval_cache_v15.pkl", "rb"))["samples"]
prefixes = open(sys.argv[1]).read().split()
def one(pre):
    k = next(x for x in R if x.startswith(pre)); r = R[k]; d = f"{O}/{k}"; os.makedirs(d, exist_ok=True)
    open(f"{d}/drawing.png", "wb").write(cache[k]["png"])
    with tempfile.TemporaryDirectory(prefix="rgb_") as td:
        stl = f"{td}/p.stl"
        if not exec_to_stl(r["codes"][r["chosen"][0]], stl, td, "p"):
            return k, False
        c = lambda m: (m.apply_translation(-(m.bounds[0] + m.bounds[1]) / 2), m)[1]
        gt = c(trimesh.load(f"{BENCH}/gt_meshes_v15/{k}.stl", force="mesh")); pk = c(trimesh.load(stl, force="mesh"))
        sc = shared_frame([gt, pk])
        render_mesh(gt, color="#8a8f99", size=600, scale=sc, center=np.zeros(3)).save(f"{d}/gt.png")
        render_mesh(pk, color="#2f6fd6", size=600, scale=sc, center=np.zeros(3)).save(f"{d}/pick.png")
    json.dump({"key": k, "iou": r["iou_start"], "time": r["times"]["generate"] + r["times"]["execute"] + r["times"]["select"]}, open(f"{d}/meta.json", "w"))
    return k, True
for k, ok in ThreadPoolExecutor(12).map(one, prefixes): print(k[:20], ok, flush=True)
