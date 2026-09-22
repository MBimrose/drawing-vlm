"""Thin-part thickness check: candidate mean wall thickness (2V/A) vs ground truth, and whether
the sheet prints any dimension matching the GT wall thickness.
    python thick_diag.py --shape results/ext/shape_<run>.json --bo <bo json> --bench <bench> --out <json> [--max-rel 0.06]
"""
import argparse, json, os, sys, tempfile, re
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from score_partials import execute
from iou import load_mesh
from shape_diag import thickness
from concurrent.futures import ProcessPoolExecutor

def job(a):
    key, code, gt_path, wd = a
    gt = load_mesh(gt_path); tg, Vg, Ag = thickness(gt)
    out = {"key": key, "gt_t": tg, "gt_V": Vg, "gt_A": Ag}
    stl = os.path.join(wd, key + ".stl")
    if code and execute(code, stl, wd, key, 90):
        m = load_mesh(stl)
        if m is not None:
            t, V, A = thickness(m); out.update(c_t=t, c_V=V, c_A=A)
    return out

ap = argparse.ArgumentParser(); ap.add_argument("--shape"); ap.add_argument("--bo"); ap.add_argument("--bench"); ap.add_argument("--out"); ap.add_argument("--max-rel", type=float, default=0.06)
a = ap.parse_args()
sh = {r["key"]: r for r in json.load(open(a.shape))["rows"]}
bo = {p["key"]: p for p in json.load(open(a.bo))["candidates"]}
rend = json.load(open(os.path.join(a.bench, "render", "renderers.json")))
labels = {}
for rk, v in rend.items():
    L = []
    for ann in v.get("annotations", {}).values():
        for x in re.findall(r"\d+(?:\.\d+)?", str(ann.get("label", ""))):
            L.append(float(x))
    labels[rk.rsplit("_v", 1)[0]] = L
wd = tempfile.mkdtemp(dir="/dev/shm")
jobs = []
for k, r in sh.items():
    if r.get("gt_rel_thick", 1) < a.max_rel and r.get("vote_idx") is not None:
        c = bo[k]["cands"][r["vote_idx"]]
        jobs.append((k, c.get("code"), os.path.join(a.bench, "gt_meshes_v15", k + ".stl"), wd))
rows = list(ProcessPoolExecutor(16).map(job, jobs))
for r in rows:
    L = labels.get(r["key"], []); r["n_labels"] = len(L)
    r["t_on_sheet"] = any(abs(x - r["gt_t"]) <= 0.15 * r["gt_t"] + 0.05 for x in L)
    r["iou"] = sh[r["key"]]["cands"][sh[r["key"]]["vote_idx"]]["iou"]
json.dump(rows, open(a.out, "w"), indent=1)
for F in "AF":
    R = [r for r in rows if r["key"][0] == F and "c_t" in r]
    ratio = np.array([r["c_t"] / r["gt_t"] for r in R]); io = np.array([r["iou"] for r in R]); ons = np.array([r["t_on_sheet"] for r in R])
    print(f"{F} thin parts n={len(R)}  thickness ratio cand/GT median {np.median(ratio):.2f}  |log| median {np.median(np.abs(np.log(ratio))):.2f}  "
          f"off by >25%: {np.mean(np.abs(np.log(ratio)) > np.log(1.25)):.2f}  GT thickness printed on sheet: {ons.mean():.2f}")
    for s in (True, False):
        m = ons == s
        if m.any(): print(f"    printed={s}: n={m.sum()} iou {io[m].mean():.3f} thickness |log| median {np.median(np.abs(np.log(ratio[m]))):.2f}")
