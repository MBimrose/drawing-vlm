"""CPU pre-stage for the visual self-check on the 96-part dev pool.

For every part in the 96-pool (keys of results/bo8_verifier2_e24.json), using
the champion's STORED full-pool candidates (results/bo8_full_e24.json) and
the stored 8x8 agreement matrices (results/bo8_full_e24_consistency_v2.json):
  1. pick the served candidate = consistency medoid (max mean pairwise IoU
     among executing candidates; ties -> lowest draw index);
  2. re-execute all 8 candidates, keeping STLs (for agreement scoring of the
     revision) and the served candidate's STEP;
  3. render the served part back into a dimensioned drawing (render_drawing.py);
  4. write out/prestage/<key>/meta.json.

    python prestage.py --out out/prestage --workers 10
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
DV = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PY = sys.executable
BO8 = os.path.join(DV, "results", "bo8_full_e24.json")
CONS = os.path.join(DV, "results", "bo8_full_e24_consistency_v2.json")
POOL96 = os.path.join(DV, "results", "bo8_verifier2_e24.json")


def medoid(part: dict) -> tuple[int | None, float, list[float]]:
    mat, ex = part["pair_iou"], part["exec"]
    idx = [j for j in range(len(ex)) if ex[j]]
    agree = [0.0] * len(ex)
    best, bs = None, -1.0
    for j in idx:
        s = [mat[j][i] for i in idx if i != j and mat[j][i] is not None]
        a = sum(s) / len(s) if s else 0.0
        agree[j] = a
        if a > bs:
            best, bs = j, a
    return best, bs, agree


def run_exec(code: str, workdir: str, tag: str, stl: str, step: str | None) -> dict:
    cp = os.path.join(workdir, tag + ".py")
    with open(cp, "w") as f:
        f.write(code)
    cmd = [PY, os.path.join(HERE, "exec_keep.py"), cp, stl] + ([step] if step else [])
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=150)
        return {"rc": p.returncode, "ok": p.returncode == 0, "err": p.stderr[-800:]}
    except subprocess.TimeoutExpired:
        return {"rc": -9, "ok": False, "err": "timeout"}


def do_part(args):
    key, part, cons_part, out_dir = args
    d = os.path.join(out_dir, key)
    os.makedirs(d, exist_ok=True)
    meta_path = os.path.join(d, "meta.json")
    if os.path.exists(meta_path):
        return json.load(open(meta_path))
    served, agree_served, agree = medoid(cons_part)
    meta = {"key": key, "served": served, "served_agree": agree_served, "agree": agree,
            "stored_iou": cons_part["iou"], "stored_exec": cons_part["exec"],
            "served_iou": cons_part["iou"][served] if served is not None else 0.0,
            "cand_stl": [None] * 8, "render": None, "step": None}
    for j, c in enumerate(part["cands"]):
        if not c.get("code"):
            continue
        stl = os.path.join(d, f"cand{j}.stl")
        step = os.path.join(d, "served.step") if j == served else None
        r = run_exec(c["code"], d, f"cand{j}", stl, step)
        if r["ok"]:
            meta["cand_stl"][j] = stl
            if step:
                meta["step"] = step
    if meta["step"]:
        png = os.path.join(d, "served_render.png")
        t = time.time()
        p = subprocess.run([PY, os.path.join(HERE, "render_drawing.py"), meta["step"], png],
                           capture_output=True, text=True, timeout=240)
        if p.returncode == 0 and os.path.exists(png):
            meta["render"] = png
            meta["render_info"] = p.stdout.strip()[-600:]
        else:
            meta["render_err"] = p.stderr[-800:]
        meta["render_s"] = round(time.time() - t, 1)
    json.dump(meta, open(meta_path, "w"), indent=1)
    print(f"[pre] {key[:8]} served={served} agree={agree_served:.3f} iou={meta['served_iou']:.3f} "
          f"execs={sum(x is not None for x in meta['cand_stl'])} render={'ok' if meta['render'] else 'FAIL'}",
          flush=True)
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "out", "prestage"))
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    keys = [p["key"] for p in json.load(open(POOL96))["candidates"]]
    if a.limit:
        keys = keys[: a.limit]
    bo8 = {p["key"]: p for p in json.load(open(BO8))["candidates"]}
    cons = {p["key"]: p for p in json.load(open(CONS))["parts"]}
    os.makedirs(a.out, exist_ok=True)
    jobs = [(k, bo8[k], cons[k], a.out) for k in keys]
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        metas = list(ex.map(do_part, jobs))
    n_r = sum(1 for m in metas if m["render"])
    print(f"[pre] done: {len(metas)} parts, {n_r} rendered, served mean IoU "
          f"{sum(m['served_iou'] for m in metas) / len(metas):.4f}", flush=True)


if __name__ == "__main__":
    main()
