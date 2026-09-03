"""Mechanism 2 (constraints before code) — offline feature pass, CPU only.

Executes every stored candidate and measures the built mesh: bounding-box
extents (x, y, z), volume, connected components. Also harvests the model's own
STATED constraints from text it already produced:
  * declared dims: top-level `name = <number>` assignments in the script
  * stated envelope: numbers in the first step of the <think> plan (when a
    think block is available, e.g. rft_scored_v1/scored-*.jsonl)
and the ground-truth extents (analysis only, never for selection).

Two sources:
  --bo8 results/bo8_full_e24.json            (eval pool, code + iou, no think)
  --scored rft_scored_v1/scored-000.jsonl ...  (train parts, think + code + iou)

    python envelope_features.py --bo8 results/bo8_full_e24.json --out out/env_bo8_full_e24.jsonl
    python envelope_features.py --scored rft_scored_v1/scored-00[0-3].jsonl --max 8000 --out out/env_scored_v1.jsonl
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import random
import re
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
sys.path.insert(0, f"{DV}/train_v14"); sys.path.insert(0, f"{DV}/train_v14/geom")
from rft_generate import exec_to_stl  # noqa: E402

GT_EVAL = f"{DV}/step_to_drw/wds_dataset/gt_meshes_v15"
GT_RFT = f"{DV}/rft_scored_v1/gt_stl_cache"

_ASSIGN = re.compile(r"^\s*([A-Za-z_]\w*)\s*=\s*(-?\d+(?:\.\d+)?)\s*(?:#.*)?$", re.M)
_NUM = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w.]|\d)")


def declared_dims(code: str) -> dict[str, float]:
    return {m.group(1): float(m.group(2)) for m in _ASSIGN.finditer(code)}


def stated_numbers(think: str) -> list[float]:
    """Numbers in the first plan step (the stock / envelope statement)."""
    if not think:
        return []
    first = think.strip().split("\n")[0]
    # drop enumerators like "1." and radius/fillet mentions are kept (harmless)
    first = re.sub(r"^\s*\d+[.)]\s*", "", first)
    return [float(x) for x in _NUM.findall(first)]


def mesh_features(stl: str) -> dict | None:
    import numpy as np
    import trimesh
    try:
        m = trimesh.load(stl, force="mesh", process=True)
    except Exception:
        return None
    if m is None or len(m.faces) == 0:
        return None
    ext = (m.bounds[1] - m.bounds[0]).tolist()
    try:
        vol = float(abs(m.volume))
    except Exception:
        vol = 0.0
    try:
        ncomp = len(m.split(only_watertight=False))
    except Exception:
        ncomp = -1
    genus = None
    try:
        if m.is_watertight and ncomp == 1:
            genus = int((2 - m.euler_number) // 2)   # = number of through-passages
    except Exception:
        pass
    return {"ext": [round(float(e), 3) for e in ext], "vol": round(vol, 3),
            "watertight": bool(m.is_watertight), "ncomp": int(ncomp),
            "genus": genus, "nfaces": int(len(m.faces))}


_gt_cache: dict[str, dict | None] = {}


def gt_features(path: str) -> dict | None:
    if path not in _gt_cache:
        _gt_cache[path] = mesh_features(path) if os.path.exists(path) else None
    return _gt_cache[path]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bo8", default="")
    ap.add_argument("--scored", nargs="*", default=[])
    ap.add_argument("--max", type=int, default=0, help="subsample scored candidates")
    ap.add_argument("--workers", type=int, default=28)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    recs: list[dict] = []
    if args.bo8:
        d = json.load(open(args.bo8))
        for p in d["candidates"]:
            for c in p["cands"]:
                recs.append({"key": p["key"], "draw": c["draw"], "code": c["code"],
                             "exec0": c["exec"], "iou": c["iou"], "think": "",
                             "gt": f"{GT_EVAL}/{p['key']}.stl"})
    for pat in args.scored:
        for f in glob.glob(pat):
            with open(f) as fh:
                for line in fh:
                    r = json.loads(line)
                    if not r.get("code"):
                        continue
                    recs.append({"key": r["key"], "draw": r.get("sample", 0), "code": r["code"],
                                 "exec0": r.get("exec", False), "iou": r["iou"],
                                 "think": r.get("think", ""),
                                 "gt": f"{GT_RFT}/{r['key']}.stl"})
    if args.max and len(recs) > args.max:
        random.Random(0).shuffle(recs)
        recs = recs[: args.max]
    print(f"[env] {len(recs)} candidates", flush=True)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    done = set()
    if os.path.exists(args.out):
        with open(args.out) as f:
            for line in f:
                try:
                    r = json.loads(line); done.add((r["key"], r["draw"]))
                except Exception:
                    pass
        print(f"[env] resuming, {len(done)} done", flush=True)
    todo = [r for r in recs if (r["key"], r["draw"]) not in done]

    outf = open(args.out, "a")
    with tempfile.TemporaryDirectory(prefix="envf_") as td:
        def one(i):
            r = todo[i]
            out = {"key": r["key"], "draw": r["draw"], "iou": r["iou"], "exec0": r["exec0"],
                   "declared": declared_dims(r["code"] or ""),
                   "stated": stated_numbers(r["think"]),
                   "think1": (r["think"] or "").strip().split("\n")[0][:300]}
            out["gt"] = gt_features(r["gt"])
            feat = None
            if r["code"]:
                stl = os.path.join(td, f"{i}.stl")
                if exec_to_stl(r["code"], stl, td, f"c{i}"):
                    feat = mesh_features(stl)
                    try:
                        os.remove(stl)
                    except OSError:
                        pass
            out["built"] = feat
            return out
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            for n, res in enumerate(ex.map(one, range(len(todo)))):
                outf.write(json.dumps(res) + "\n")
                if n % 200 == 0:
                    outf.flush(); print(f"[env] {n}/{len(todo)}", flush=True)
    outf.close()
    print("[env] done", flush=True)


if __name__ == "__main__":
    main()
