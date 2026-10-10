"""Assets for a repair-loop example figure: for selected real-bench parts, every program the served repair chain
adopted (round 0 = its starting e55 candidate), executed and rendered on one camera with the GT.

    bash train_v14/serv19/cpu_run.sh -n ccc0451 -c 4 -- .venv/bin/python train_v14/geom/repair_progression.py KEY_PREFIX ...
Writes results/figures/repair_example/<key>/{drawing.png, gt.png, step{i}.png, steps.json}.
"""
import json
import os
import pickle
import sys
import tempfile

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from cad_render import render_mesh, shared_frame  # noqa: E402
from rft_generate import exec_to_stl  # noqa: E402

DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
BENCH = f"{DV}/train_v14/mech/benchmarks/data/ext_bench_dw423_perm"
CHAINS = [f"{DV}/results/repair/{c}.jsonl" for c in ("sys_pooled_rp3_rep_r32_r6", "sys_rp3_rank2_r6", "sys_rp3_rank3_r6")]
SERVED = f"{DV}/results/figures/real_parts/served.json"
OUT = f"{DV}/results/figures/repair_example"


def adopt_rounds(r):
    rounds = [0]
    for y in r["hist"][1:]:
        hit = [i + 1 for i, rd in enumerate(r["rounds"]) if any((d.get("code") or "").strip() == y["code"].strip() for d in rd)]
        rounds.append(hit[0] if hit else rounds[-1] + 1)
    return rounds


def centred(m):
    m = m.copy(); m.apply_translation(-(m.bounds[0] + m.bounds[1]) / 2); return m


def main():
    served = {r["key"]: r for r in json.load(open(SERVED))}
    chains = [{json.loads(l)["key"]: json.loads(l) for l in open(f)} for f in CHAINS]
    cache = pickle.load(open(f"{BENCH}/eval_cache_v15.pkl", "rb"))["samples"]
    for pre in sys.argv[1:]:
        k = next(x for x in served if x.startswith(pre)); s = served[k]; r = chains[s["served_chain"]][k]
        d = os.path.join(OUT, k); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "drawing.png"), "wb").write(cache[k]["png"])
        gt = centred(trimesh.load(f"{BENCH}/gt_meshes_v15/{k}.stl", force="mesh"))
        steps, meshes = [], []
        with tempfile.TemporaryDirectory(prefix="rpx_") as td:
            for i, (h, rd) in enumerate(zip(r["hist"], adopt_rounds(r))):
                stl = os.path.join(d, f"step{i}.stl")
                ok = exec_to_stl(h["code"], stl, td, f"s{i}")
                steps.append({"step": i, "round": rd, "iou": h["iou"], "v3": h.get("v3"), "ok": bool(ok)})
                if ok:
                    meshes.append((i, centred(trimesh.load(stl, force="mesh"))))
        sc = shared_frame([gt] + [m for _, m in meshes])
        render_mesh(gt, color="#8a8f99", size=700, scale=sc, center=np.zeros(3)).save(os.path.join(d, "gt.png"))
        for i, m in meshes:
            render_mesh(m, color="#2f6fd6", size=700, scale=sc, center=np.zeros(3)).save(os.path.join(d, f"step{i}.png"))
        meta = {"key": k, "chain": s["served_chain"], "vote_iou": s["vote_iou"], "served_iou": s["served_iou"], "steps": steps}
        json.dump(meta, open(os.path.join(d, "steps.json"), "w"), indent=1)
        print(k[:24], "chain", s["served_chain"], [(x["round"], round(x["iou"], 3), x["ok"]) for x in steps], flush=True)


if __name__ == "__main__":
    main()
