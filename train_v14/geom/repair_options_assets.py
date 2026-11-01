"""Contact-sheet options for the repair slide: bench-B parts whose SERVED repair chain (of 3, the one with the best
render-compare score at the end) adopted >= 2 repairs and gained IoU, for both models:
  sft   e55 + rp3 repair  (results/bench_b/pipeline/chain_e55_rp3_c{1,2,3}.jsonl, 12 Oct)
  grpo  SFT + GRPO + rp3 repair (serv-05 run, 20 Oct: s05_full_bench_b.jsonl + repair_curve_bench_b_per_part.json for IoUs)
Every adopted program is executed and rendered on ONE camera with the ground truth (same scale), so the steps line up.
-> results/figures/repair_options/<model>/<key>/{drawing,gt,step<i>}.png + steps.json

    bash train_v14/serv19/cpu_run.sh -n ccc0441 -c 32 -- .venv/bin/python train_v14/geom/repair_options_assets.py --n 16
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

DV = os.environ.get("DV", "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"); BENCH = f"{DV}/results/bench_b/bench"
PT = f"{DV}/results/figures/pipeline_timing"; OUT = f"{DV}/results/figures/repair_options"


def sft_chains():
    C = [{json.loads(l)["key"]: json.loads(l) for l in open(f"{DV}/results/bench_b/pipeline/chain_e55_rp3_c{i}.jsonl")} for i in (1, 2, 3)]
    out = {}
    for k in C[0]:
        chs = [[{"round": h["round"], "iou": h["iou"], "v3": h.get("v3") or 0, "code": h["code"]} for h in c[k]["hist"] if h.get("adopted", True)]
               for c in C if k in c]
        out[k] = max(chs, key=lambda h: h[-1]["v3"])     # served = best render-compare score after the last round
    return out


def grpo_chains():
    R = {json.loads(l)["key"]: json.loads(l) for l in open(f"{PT}/s05_full_bench_b.jsonl")}
    per = {p["key"]: p for p in json.load(open(f"{PT}/repair_curve_bench_b_per_part.json"))}
    out = {}
    for k, r in R.items():
        bc = r["best_chain"]
        out[k] = [{"round": h["round"], "iou": p["iou"], "v3": h["v3"], "code": h["code"]} for h, p in zip(r["chains"][bc], per[k]["chains"][bc])]
    return out


def pick(chains, n):
    rows = []
    for k, ch in chains.items():
        io = [h["iou"] for h in ch]
        if len(ch) >= 3 and io[-1] - io[0] >= 0.1 and all(b >= a - 0.01 for a, b in zip(io, io[1:])):
            rows.append((io[-1] - io[0], k))
    return [k for _, k in sorted(rows, reverse=True)[:n]]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, default=16); ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--iso", action="store_true", help="true isometric from +X -Y +Z (the drawing's ISO VIEW camera); writes <model>_iso/")
    ap.add_argument("--only", nargs="*", default=[], help="model:key-prefix pairs to render instead of the automatic pick")
    a = ap.parse_args()
    V = dict(elev=float(np.degrees(np.arcsin(1 / np.sqrt(3)))), azim=-45.0) if a.iso else {}
    cache = pickle.load(open(f"{BENCH}/eval_cache_v15.pkl", "rb"))["samples"]
    jobs = []
    for model, chains in (("sft", sft_chains()), ("grpo", grpo_chains())):
        ks = ([next(k for k in chains if k.startswith(o.split(":", 1)[1])) for o in a.only if o.split(":", 1)[0] == model]
              if a.only else pick(chains, a.n)); print(model, len(ks), "options", flush=True)
        jobs += [(model, k, chains[k]) for k in ks]

    def one(job):
        model, k, ch = job; d = f"{OUT}/{model}{'_iso' if a.iso else ''}/{k}"; os.makedirs(d, exist_ok=True)
        open(f"{d}/drawing.png", "wb").write(cache[k]["png"])
        c = lambda m: (m.apply_translation(-(m.bounds[0] + m.bounds[1]) / 2), m)[1]
        with tempfile.TemporaryDirectory(prefix="rop_", dir="/dev/shm") as td:
            meshes = []
            for i, h in enumerate(ch):
                stl = f"{td}/s{i}.stl"
                if not exec_to_stl(h["code"], stl, td, f"s{i}"):
                    return model, k, False
                meshes.append(c(trimesh.load(stl, force="mesh")))
            gt = c(trimesh.load(f"{BENCH}/gt_meshes_v15/{k}.stl", force="mesh")); sc = shared_frame([gt] + meshes, **V)
            render_mesh(gt, color="#8a8f99", size=700, scale=sc, center=np.zeros(3), **V).save(f"{d}/gt.png")
            for i, m in enumerate(meshes):
                render_mesh(m, color="#2f6fd6", size=700, scale=sc, center=np.zeros(3), **V).save(f"{d}/step{i}.png")
        json.dump({"key": k, "model": model, "steps": [{"round": h["round"], "iou": h["iou"], "v3": h["v3"]} for h in ch]},
                  open(f"{d}/steps.json", "w"), indent=1)
        return model, k, True
    for model, k, ok in ThreadPoolExecutor(a.workers).map(one, jobs):
        print(model, k[:24], ok, flush=True)


if __name__ == "__main__":
    main()
