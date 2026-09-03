"""Execute stored best-of-N candidates for a subset of parts into a persistent
STL cache and record per-candidate geometry (axis-aligned extents, volume)
next to the GT mesh's extents/volume.  CPU only.

    python exec_cands.py --bo8 results/bo8_full_e24.json --keys keys.txt \
        --stl-dir <cache> --out cand_geom.jsonl --workers 16
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import trimesh

DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
sys.path.insert(0, os.path.join(DV, "train_v14")); sys.path.insert(0, os.path.join(DV, "train_v14", "geom"))
from rft_generate import exec_to_stl  # noqa: E402

GT_DIR = os.path.join(DV, "step_to_drw/wds_dataset/gt_meshes_v15")


def mesh_feats(path: str) -> dict | None:
    try:
        m = trimesh.load(path, force="mesh")
        if m is None or len(m.faces) == 0:
            return None
        return {"ext": [round(float(x), 3) for x in m.extents],
                "vol": round(float(abs(m.volume)), 3),
                "centroid": [round(float(x), 3) for x in m.bounding_box.centroid]}
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bo8", required=True)
    ap.add_argument("--keys", required=True, help="file of uuids (one per line)")
    ap.add_argument("--stl-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=16)
    args = ap.parse_args()
    os.makedirs(args.stl_dir, exist_ok=True)
    keys = [l.strip() for l in open(args.keys) if l.strip()]
    data = json.load(open(args.bo8))
    parts = {p["key"]: p["cands"] for p in data["candidates"]}
    todo = [(k, j, c) for k in keys for j, c in enumerate(parts[k]) if c.get("code") and c.get("exec")]
    print(f"[exec] {len(keys)} parts, {len(todo)} executing candidates", flush=True)
    work = os.path.join(args.stl_dir, "_work"); os.makedirs(work, exist_ok=True)

    def run_one(a):
        k, j, c = a
        stl = os.path.join(args.stl_dir, f"{k}_{j}.stl")
        if not os.path.exists(stl):
            exec_to_stl(c["code"], stl, work, f"{k}_{j}")
        return (k, j, os.path.exists(stl))

    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for k, j, ok in ex.map(run_one, todo):
            done += 1
            if done % 200 == 0:
                print(f"[exec] {done}/{len(todo)}", flush=True)
    with open(args.out, "w") as f:
        for k in keys:
            gt = mesh_feats(os.path.join(GT_DIR, f"{k}.stl"))
            cands = []
            for j, c in enumerate(parts[k]):
                stl = os.path.join(args.stl_dir, f"{k}_{j}.stl")
                feats = mesh_feats(stl) if os.path.exists(stl) else None
                cands.append({"draw": j, "iou": c.get("iou", 0.0), "exec": bool(feats),
                              "stl": stl if feats else None, **(feats or {})})
            f.write(json.dumps({"key": k, "gt": gt, "cands": cands}) + "\n")
    print("[exec] done", flush=True)


if __name__ == "__main__":
    main()
