"""Figure assets for selected real-bench parts (143-part permissive CADBench bench): input drawing, GT mesh, the
served program of the deployed system (real_parts_served.py) and all 8 e55 best-of-8 candidates with the stored
pairwise-IoU matrix and medoid pick.

    bash train_v14/serv19/cpu_run.sh -c 32 -- .venv/bin/python train_v14/geom/real_parts_assets.py \
        results/figures/real_parts/picks12.txt
Writes results/figures/real_parts/parts/<key>/{drawing.png,gt.stl,served.{py,stl},cand{j}.{py,stl},data.json}.
"""
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
BENCH = f"{DV}/train_v14/mech/benchmarks/data/ext_bench_dw423_perm"
BO8 = f"{DV}/results/ext/bo8_ext_dw423p_e55-rft-real-u5-gt-dw423.json"
CONS = f"{DV}/results/ext/bo8_ext_dw423p_e55-rft-real-u5-gt-dw423_consistency.json"
SERVED = f"{DV}/results/figures/real_parts/served.json"
OUT = f"{DV}/results/figures/real_parts/parts"

keys = open(sys.argv[1]).read().split()
bo8 = {p["key"]: p for p in json.load(open(BO8))["candidates"]}
cons = json.load(open(CONS)); cparts = {p["key"]: p for p in cons["parts"]}
served = {r["key"]: r for r in json.load(open(SERVED))}
cache = pickle.load(open(f"{BENCH}/eval_cache_v15.pkl", "rb"))["samples"]

jobs = []
for k in keys:
    d = os.path.join(OUT, k); os.makedirs(d, exist_ok=True)
    png = cache[k]["png"]
    open(os.path.join(d, "drawing.png"), "wb").write(png if isinstance(png, bytes) else png.tobytes())
    shutil.copyfile(f"{BENCH}/gt_meshes_v15/{k}.stl", os.path.join(d, "gt.stl"))
    open(os.path.join(d, "served.py"), "w").write(served[k]["served_code"])
    jobs.append((k, "served", served[k]["served_code"]))
    for j, c in enumerate(bo8[k]["cands"]):
        open(os.path.join(d, f"cand{j}.py"), "w").write(c.get("code") or "")
        if c.get("code") and c.get("exec"):
            jobs.append((k, f"cand{j}", c["code"]))

with tempfile.TemporaryDirectory(prefix="rpa_") as td:
    def run(a):
        k, name, code = a
        return exec_to_stl(code, os.path.join(OUT, k, f"{name}.stl"), td, f"{k}_{name}")
    with ThreadPoolExecutor(32) as ex:
        list(ex.map(run, jobs))

for k in keys:
    cp = cparts[k]; n = len(cp["iou"]); M = cp["pair_iou"]
    agree = []
    for i in range(n):
        vals = [M[i][j] for j in range(n) if j != i and M[i][j] is not None]
        agree.append(sum(vals) / len(vals) if cp["exec"][i] and vals else None)
    medoid = max((i for i in range(n) if agree[i] is not None), key=lambda i: agree[i])
    s = {x: served[k][x] for x in ("served_iou", "served_chain", "served_round", "vote_iou", "first_iou", "oracle8")}
    data = {"key": k, "iou": cp["iou"], "exec": cp["exec"], "pair_iou": M, "agree": agree, "medoid": medoid,
            "oracle": max(range(n), key=lambda i: cp["iou"][i]), "per_part": cons["per_part"][k], **s,
            "stl_ok": [os.path.exists(os.path.join(OUT, k, f"cand{j}.stl")) for j in range(n)],
            "served_ok": os.path.exists(os.path.join(OUT, k, "served.stl"))}
    json.dump(data, open(os.path.join(OUT, k, "data.json"), "w"), indent=1)
    print(k[:14], f"served {s['served_iou']:.3f} (ok={data['served_ok']}) | medoid c{medoid} {cp['iou'][medoid]:.3f} "
          f"agree {agree[medoid]:.3f} exec {sum(cp['exec'])}/8", flush=True)
