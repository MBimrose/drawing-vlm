"""Render-and-compare: score each best-of-N candidate by drawing it and comparing the drawing
with the INPUT sheet -- a label-free check (no ground-truth mesh) usable at serving time.

The sheet renderer derives its layout seed and title-block uuid from the part key
(render_ext.py: crc32(key) / md5(key)), so a candidate STEP rendered under the same key lands
in the same variant, the same view positions and the same scale policy as the input drawing;
a correct candidate reproduces the sheet almost pixel for pixel, a wrong one moves linework,
views and dimension text. Score = symmetric ink F1 at a pixel tolerance (distance transform),
so hairline shifts from tessellation do not count and missing / extra features do.

Per part this writes every candidate's score next to its true IoU (when the bo file has it) and
reports what selecting by the render score would give against first draw / ceiling -- the
experiment that decides whether this replaces or augments the verifier gate.

    python render_compare.py --bo results/ext/bo8_ext_dw423p_<run>.json \
        --bench train_v14/mech/benchmarks/data/ext_bench_dw423_perm --out results/ext/rc_<run>.json \
        --rpy dw_venv/bin/python --script-dir mech_step_to_drw [--workers 40] [--tol 3]
"""
from __future__ import annotations

import argparse
import glob
import io
import json
import os
import pickle
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.join(HERE, "exec_harness.py")
RENDER_EXT = os.path.join(os.path.dirname(HERE), "mech", "benchmarks", "render_ext.py")


def ink_mask(png_bytes: bytes, thresh: int = 160) -> np.ndarray:
    from PIL import Image
    g = np.asarray(Image.open(io.BytesIO(png_bytes)).convert("L"))
    return g < thresh


def ink_f1(a: np.ndarray, b: np.ndarray, tol: float) -> dict:
    """Symmetric tolerance F1 between two ink masks (a = input sheet, b = candidate sheet)."""
    from scipy.ndimage import distance_transform_edt
    if a.shape != b.shape:
        return {"f1": 0.0, "precision": 0.0, "recall": 0.0, "shape_mismatch": True}
    if not a.any() or not b.any():
        return {"f1": 0.0, "precision": 0.0, "recall": 0.0}
    da = distance_transform_edt(~a); db = distance_transform_edt(~b)
    recall = float((db[a] <= tol).mean())       # input ink explained by the candidate
    precision = float((da[b] <= tol).mean())    # candidate ink present in the input
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return {"f1": f1, "precision": precision, "recall": recall}


def render_candidate(code: str, key: str, py: str, rpy: str, script_dir: str, exec_timeout: int, render_timeout: int):
    """code -> STEP (exec harness) -> sheet PNG bytes (render_ext under the part's key). Returns (png|None, info)."""
    with tempfile.TemporaryDirectory(prefix="rc_") as td:
        cp, stl, step = os.path.join(td, "c.py"), os.path.join(td, "c.stl"), os.path.join(td, "src", key + ".step")
        os.makedirs(os.path.dirname(step)); open(cp, "w").write(code)
        try:
            p = subprocess.run([py, HARNESS, cp, stl, step], capture_output=True, text=True, timeout=exec_timeout)
        except subprocess.TimeoutExpired:
            return None, {"stage": "exec", "error": "timeout"}
        if p.returncode != 0 or not os.path.exists(step):
            return None, {"stage": "exec", "error": (p.stderr or "")[-160:]}
        env = dict(os.environ, SCRIPT_DIR=script_dir, VLM_MODE="1", OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
        try:
            q = subprocess.run([rpy, RENDER_EXT, "--src", os.path.join(td, "src"), "--out", os.path.join(td, "out"), "--workers", "1"],
                               capture_output=True, text=True, timeout=render_timeout, env=env, cwd=td)
        except subprocess.TimeoutExpired:
            return None, {"stage": "render", "error": "timeout"}
        pngs = glob.glob(os.path.join(td, "out", "png", key + "_v*.png"))
        if not pngs:
            return None, {"stage": "render", "error": ((q.stderr or "") + (q.stdout or ""))[-200:]}
        return open(pngs[0], "rb").read(), {"variant": os.path.basename(pngs[0]).rsplit("_v", 1)[1][:-4]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bo", required=True)
    ap.add_argument("--bench", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--py", default=sys.executable, help="interpreter with build123d for the exec harness")
    ap.add_argument("--rpy", required=True, help="renderer interpreter (draftwright 0.4.23 + font patch)")
    ap.add_argument("--script-dir", required=True, help="step_to_drw dir with worker_v11.py")
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--tol", type=float, default=3.0)
    ap.add_argument("--n", type=int, default=0)
    ap.add_argument("--exec-timeout", type=int, default=90)
    ap.add_argument("--render-timeout", type=int, default=420)
    ap.add_argument("--gt-check", type=int, default=0, help="also re-render N ground-truth STEPs (bench step_mm) as a fidelity check")
    a = ap.parse_args()

    cache = pickle.load(open(os.path.join(a.bench, "eval_cache_v15.pkl"), "rb"))
    parts = json.load(open(a.bo))["candidates"]
    parts = [p for p in parts if p["key"] in cache["samples"]]
    if a.n:
        parts = parts[: a.n]
    done = {}
    if os.path.exists(a.out):
        done = {r["key"]: r for r in json.load(open(a.out)).get("parts", [])}
    jobs = []
    for p in parts:
        if p["key"] in done:
            continue
        seen = {}
        for i, c in enumerate(p["cands"]):
            code = (c.get("code") or "").strip()
            if code and code not in seen:
                seen[code] = i
                jobs.append((p["key"], i, code))
    print(f"[rc] {len(parts)} parts, {len(done)} done, {len(jobs)} distinct candidates to render, {a.workers} workers", flush=True)
    masks = {}

    if a.gt_check:   # fidelity: the ground-truth STEP re-rendered here must reproduce the input sheet (F1 ~ 1)
        import shutil
        env = dict(os.environ, SCRIPT_DIR=a.script_dir, VLM_MODE="1", OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
        f1s = []
        for p in parts[: a.gt_check]:
            key = p["key"]; src = os.path.join(a.bench, "step_mm", key + ".step")
            if not os.path.exists(src):
                print(f"[rc][gt] {key}: no step_mm file", flush=True); continue
            with tempfile.TemporaryDirectory(prefix="rcgt_") as td:
                os.makedirs(os.path.join(td, "src")); shutil.copy(src, os.path.join(td, "src", key + ".step"))
                t1 = time.time()
                q = subprocess.run([a.rpy, RENDER_EXT, "--src", os.path.join(td, "src"), "--out", os.path.join(td, "out"), "--workers", "1"],
                                   capture_output=True, text=True, timeout=a.render_timeout, env=env, cwd=td)
                pngs = glob.glob(os.path.join(td, "out", "png", key + "_v*.png"))
                if not pngs:
                    print(f"[rc][gt] {key}: render failed: {((q.stderr or '') + (q.stdout or ''))[-300:]}", flush=True); continue
                r = ink_f1(ink_mask(cache["samples"][key]["png"]), ink_mask(open(pngs[0], "rb").read()), a.tol)
                f1s.append(r["f1"])
                print(f"[rc][gt] {key}: F1 {r['f1']:.4f} (P {r['precision']:.3f} R {r['recall']:.3f}) variant v{os.path.basename(pngs[0]).rsplit('_v',1)[1][:-4]} {time.time()-t1:.0f}s", flush=True)
        print(f"[rc][gt] mean F1 of ground truth re-renders: {sum(f1s)/max(1,len(f1s)):.4f} over {len(f1s)}", flush=True)

    def work(job):
        key, i, code = job
        png, info = render_candidate(code, key, a.py, a.rpy, a.script_dir, a.exec_timeout, a.render_timeout)
        if png is None:
            return key, i, {"score": 0.0, **info}
        if key not in masks:
            masks[key] = ink_mask(cache["samples"][key]["png"])
        return key, i, {"score": ink_f1(masks[key], ink_mask(png), a.tol)["f1"], **info}

    t0 = time.time(); res = {}
    with ThreadPoolExecutor(a.workers) as ex:
        for n, (key, i, r) in enumerate(ex.map(work, jobs), 1):
            res.setdefault(key, {})[i] = r
            if n % 50 == 0:
                print(f"[rc] {n}/{len(jobs)} rendered, {(time.time()-t0)/n:.1f} s/candidate", flush=True)

    out_parts = list(done.values())
    for p in parts:
        if p["key"] in done:
            continue
        by_code = {}; rows = []
        for i, c in enumerate(p["cands"]):
            code = (c.get("code") or "").strip()
            r = res.get(p["key"], {}).get(i)
            if r is None and code in by_code:
                r = by_code[code]
            if r is None:
                r = {"score": 0.0, "stage": "nocode"}
            by_code.setdefault(code, r)
            rows.append({"draw": c.get("draw", i), "iou": float(c.get("iou", 0.0)), "exec": bool(c.get("exec")), **r})
        out_parts.append({"key": p["key"], "cands": rows})

    def sel(rows, f):
        return f(rows)["iou"] if rows else 0.0
    n = max(1, len(out_parts))
    summ = {
        "n_parts": len(out_parts),
        "first_draw": sum(sel(p["cands"], lambda r: r[0]) for p in out_parts) / n,
        "render_select": sum(sel(p["cands"], lambda r: max(r, key=lambda x: x["score"])) for p in out_parts) / n,
        "ceiling": sum(sel(p["cands"], lambda r: max(r, key=lambda x: x["iou"])) for p in out_parts) / n,
        "render_select_ge85": sum(sel(p["cands"], lambda r: max(r, key=lambda x: x["score"])) >= 0.85 for p in out_parts) / n,
        "ceiling_ge85": sum(sel(p["cands"], lambda r: max(r, key=lambda x: x["iou"])) >= 0.85 for p in out_parts) / n,
        "rendered": sum(1 for p in out_parts for c in p["cands"] if c.get("variant")), "tol_px": a.tol,
    }
    xs = [(c["score"], c["iou"]) for p in out_parts for c in p["cands"] if c.get("variant")]
    if len(xs) > 2:
        s, t = np.array(xs).T
        summ["pearson_score_vs_iou"] = float(np.corrcoef(s, t)[0, 1])
    json.dump({"summary": summ, "parts": out_parts}, open(a.out, "w"))
    print("[rc] " + json.dumps(summ), flush=True)


if __name__ == "__main__":
    main()
