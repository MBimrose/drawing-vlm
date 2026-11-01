"""Assets for the full-pipeline figures (filmstrip, time-to-scale bars, scatter callouts) from serve_full_timed.py
records: per selected part, execute every stored program (8 candidates, each chain's accepted repairs, the served
final), compute its IoU vs ground truth (evaluation only), and render the solids + GT on one camera. The input drawing
comes from the bench's eval cache.

    bash train_v14/serv19/cpu_run.sh -n ccc0441 -c 32 -- .venv/bin/python train_v14/geom/pipeline_fig_assets.py \
        --records results/figures/pipeline_timing/s05_full_bench_b.jsonl --bench results/bench_b/bench KEY_PREFIX ...
Writes results/figures/pipeline_timing/parts/<key>/{drawing.png, gt.png, cand{j}.png, c{chain}_r{round}.png, final.png,
assets.json}.
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

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from cad_render import render_mesh, shared_frame  # noqa: E402
from iou import iou_pair  # noqa: E402
from rft_generate import exec_to_stl  # noqa: E402

OUT = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/figures/pipeline_timing/parts"


def centred(m):
    m = m.copy(); m.apply_translation(-(m.bounds[0] + m.bounds[1]) / 2); return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", required=True); ap.add_argument("--bench", required=True)
    ap.add_argument("prefixes", nargs="+")
    a = ap.parse_args()
    R = {json.loads(l)["key"]: json.loads(l) for l in open(a.records)}
    cache = pickle.load(open(os.path.join(a.bench, "eval_cache_v15.pkl"), "rb"))["samples"]
    for pre in a.prefixes:
        k = next(x for x in R if x.startswith(pre)); r = R[k]; d = os.path.join(OUT, k); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "drawing.png"), "wb").write(cache[k]["png"])
        gt_stl = os.path.join(a.bench, "gt_meshes_v15", k + ".stl")
        progs = {f"cand{j}": c for j, c in enumerate(r["codes"]) if c}
        for ci, ch in enumerate(r["chains"]):
            for h in ch[1:]:
                progs[f"c{ci}_r{h['round']}"] = h["code"]
        progs["final"] = r["final_code"]
        with tempfile.TemporaryDirectory(prefix="pfa_") as td:
            def run(item):
                name, code = item; stl = os.path.join(td, name + ".stl")
                if not exec_to_stl(code, stl, td, f"{k}_{name}"):
                    return name, None, 0.0
                try:
                    iou = iou_pair(stl, gt_stl)["iou_centered"]
                except Exception:
                    iou = 0.0
                return name, stl, iou
            res = list(ThreadPoolExecutor(16).map(run, progs.items()))
            meshes = {n: centred(trimesh.load(s, force="mesh")) for n, s, _ in res if s}
            gt = centred(trimesh.load(gt_stl, force="mesh"))
            sc = shared_frame([gt] + list(meshes.values()))
            render_mesh(gt, color="#8a8f99", size=600, scale=sc, center=np.zeros(3)).save(os.path.join(d, "gt.png"))
            def rend(n):
                render_mesh(meshes[n], color="#2f6fd6", size=600, scale=sc, center=np.zeros(3)).save(os.path.join(d, n + ".png"))
            list(ThreadPoolExecutor(16).map(rend, list(meshes)))
        meta = {"key": k, "times": r["times"], "chosen": r["chosen"], "best_chain": r["best_chain"],
                "ver": r["ver"], "v3": r["v3"], "exec": r["exec"], "iou": {n: i for n, _, i in res},
                "rendered": sorted(meshes), "chains": [[{"round": h["round"], "v3": h["v3"]} for h in ch] for ch in r["chains"]],
                "iou_start": r["iou_start"], "iou_final": r["iou_final"], "round_times": r["round_times"]}
        json.dump(meta, open(os.path.join(d, "assets.json"), "w"), indent=1)
        print(k[:24], "rendered", len(meshes), "of", len(progs), "final IoU", round(meta["iou"].get("final", 0), 3), flush=True)


if __name__ == "__main__":
    main()
