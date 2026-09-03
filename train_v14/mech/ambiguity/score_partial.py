"""Execute + IoU-score the candidates in a gen_underdet.py per-draw checkpoint
(<out>.partial.json) for the first K draws, and write a results/bo8_*.json-format
file so consistency_rerank.py can be run on it unchanged.  Also writes the
stored-baseline candidates for the same keys restricted to the same K draws
(same selection code path for both).

    python score_partial.py --partial out/bo8_underdet_convention.json.partial.json --k 4 \
        --out out/bo4_underdet_convention.json --baseline-out out/bo4_underdet_baseline.json
"""
import argparse, json, os, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
sys.path.insert(0, os.path.join(DV, "train_v14")); sys.path.insert(0, os.path.join(DV, "train_v14", "geom")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import limited_exec  # noqa: E402,F401  (24 GB cap per candidate subprocess)
from iou import iou_pair  # noqa: E402
from rft_generate import exec_to_stl  # noqa: E402
GT_DIR = os.path.join(DV, "step_to_drw/wds_dataset/gt_meshes_v15")

ap = argparse.ArgumentParser()
ap.add_argument("--partial", required=True); ap.add_argument("--k", type=int, required=True)
ap.add_argument("--out", required=True); ap.add_argument("--baseline-out", required=True)
ap.add_argument("--bo8", default=os.path.join(DV, "results/bo8_full_e24.json"))
ap.add_argument("--workers", type=int, default=16)
a = ap.parse_args()
pd = json.load(open(a.partial))
keys = pd["keys"]; cands = [cs[:a.k] for cs in pd["cands"]]
assert all(len(cs) == a.k for cs in cands), "not enough draws in the checkpoint"
with tempfile.TemporaryDirectory(prefix="amb_score_") as td:
    def run_one(p):
        i, j = p; c = cands[i][j]
        c["exec"] = False; c["iou"] = 0.0
        if not c.get("code"):
            return
        stl = os.path.join(td, f"{keys[i]}_{j}.stl")
        if exec_to_stl(c["code"], stl, td, f"{keys[i]}_{j}"):
            c["exec"] = True
            if os.path.getsize(stl) > 150_000_000:   # pathological mesh (hundreds of MB): OOM risk, score 0
                print(f"[score] huge STL skipped {keys[i]}_{j} {os.path.getsize(stl)//1_000_000} MB", flush=True)
                c["iou"] = 0.0
            else:
                c["iou"] = iou_pair(stl, os.path.join(GT_DIR, f"{keys[i]}.stl"))["iou_centered"]
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        list(ex.map(run_one, [(i, j) for i in range(len(keys)) for j in range(a.k)]))
n_exec = sum(c["exec"] for cs in cands for c in cs)
print(f"[score] K={a.k}: executed {n_exec}/{len(keys) * a.k}", flush=True)
def summarize(cs_all):
    fe = [next((c["iou"] for c in cs if c["exec"]), 0.0) for cs in cs_all]
    orc = [max([c["iou"] for c in cs if c["exec"]] or [0.0]) for cs in cs_all]
    return {"first_exec": {"iou_mean": sum(fe) / len(fe), "frac_iou85": sum(x >= 0.85 for x in fe) / len(fe)},
            "oracle": {"iou_mean": sum(orc) / len(orc), "frac_iou85": sum(x >= 0.85 for x in orc) / len(orc)},
            "k": a.k, "n": len(cs_all)}
json.dump({"metrics": summarize(cands), "ckpt": "runs/e24-rft/final", "verifier": "", "variant": "convention",
           "candidates": [{"key": k, "cands": cs} for k, cs in zip(keys, cands)]}, open(a.out, "w"))
base = {p["key"]: p["cands"][:a.k] for p in json.load(open(a.bo8))["candidates"]}
bc = [base[k] for k in keys]
json.dump({"metrics": summarize(bc), "ckpt": "runs/e24-rft/final", "verifier": "", "variant": "baseline(stored)",
           "candidates": [{"key": k, "cands": cs} for k, cs in zip(keys, bc)]}, open(a.baseline_out, "w"))
print("[score] convention", json.dumps(summarize(cands)), "\n[score] baseline  ", json.dumps(summarize(bc)), flush=True)
