"""Collect figure assets for selected test parts from the deployed e55
best-of-8 run: input drawing, GT mesh, all 8 candidate solids (re-executed),
GT IoU per candidate, the stored pairwise-IoU matrix and the medoid pick.

    bash train_v14/serv19/cpu_run.sh -c 32 -- .venv/bin/python \
        train_v14/geom/complex_parts_assets.py results/figures/complex_parts/picks12.txt
Writes results/figures/complex_parts/parts/<key>/{drawing.png,gt.stl,cand{j}.stl,cand{j}.py,data.json}.
"""
import io
import json
import os
import pickle
import shutil
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from rft_generate import exec_to_stl  # noqa: E402

DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
BO8 = f"{DV}/results/ext/bo8_full_e55-rft-real-u5-gt-dw423.json"
CONS = f"{DV}/results/ext/bo8_full_e55-rft-real-u5-gt-dw423_consistency.json"
CACHE = f"{DV}/step_to_drw/wds_dataset/eval_cache_v15_dw423.pkl"
GT_DIR = f"{DV}/step_to_drw/wds_dataset/gt_meshes_v15"
OUT = f"{DV}/results/figures/complex_parts/parts"

keys = open(sys.argv[1]).read().split()
bo8 = {p["key"]: p for p in json.load(open(BO8))["candidates"]}
cons = json.load(open(CONS)); cparts = {p["key"]: p for p in cons["parts"]}
cache = pickle.load(open(CACHE, "rb"))["samples"]

jobs = []
for k in keys:
    d = os.path.join(OUT, k); os.makedirs(d, exist_ok=True)
    s = cache[k]
    png = s["png"] if isinstance(s["png"], bytes) else s["png"].tobytes()
    open(os.path.join(d, "drawing.png"), "wb").write(png)
    open(os.path.join(d, "gt.py"), "w").write(s["code"])
    shutil.copyfile(os.path.join(GT_DIR, k + ".stl"), os.path.join(d, "gt.stl"))
    shutil.copyfile(os.path.join(GT_DIR, k + ".step"), os.path.join(d, "gt.step"))
    for j, c in enumerate(bo8[k]["cands"]):
        open(os.path.join(d, f"cand{j}.py"), "w").write(c.get("code") or "")
        if c.get("code") and c.get("exec"):
            jobs.append((k, j, c["code"]))

with tempfile.TemporaryDirectory(prefix="cxa_") as td:
    def run(a):
        k, j, code = a
        return k, j, exec_to_stl(code, os.path.join(OUT, k, f"cand{j}.stl"), td, f"{k}_{j}")
    with ThreadPoolExecutor(32) as ex:
        res = list(ex.map(run, jobs))

for k in keys:
    cp = cparts[k]; n = len(cp["iou"])
    M = cp["pair_iou"]
    agree = []
    for i in range(n):
        vals = [M[i][j] for j in range(n) if j != i and M[i][j] is not None]
        agree.append(sum(vals) / len(vals) if cp["exec"][i] and vals else None)
    medoid = max((i for i in range(n) if agree[i] is not None), key=lambda i: agree[i])
    data = {"key": k, "iou": cp["iou"], "exec": cp["exec"], "pair_iou": M, "agree": agree, "medoid": medoid,
            "oracle": max(range(n), key=lambda i: cp["iou"][i]), "per_part": cons["per_part"][k],
            "stl_ok": [os.path.exists(os.path.join(OUT, k, f"cand{j}.stl")) for j in range(n)]}
    json.dump(data, open(os.path.join(OUT, k, "data.json"), "w"), indent=1)
    print(k[:8], "medoid", medoid, f"iou {cp['iou'][medoid]:.3f} agree {agree[medoid]:.3f}", "exec", sum(cp["exec"]),
          "stl", sum(data["stl_ok"]), flush=True)
