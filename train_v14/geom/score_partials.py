"""Execute and score the candidates in a best-of-N run's .partial.json checkpoints.

`bestofn_verifier_eval.py` checkpoints after every DRAW (code + think per candidate) but its
execute-and-score phase is one un-checkpointed block: a job that hits its walltime there loses
hours of generation even though every candidate is already on disk. This re-runs just that
phase from the checkpoints, resumably, and writes a candidates file in the same shape as the
job would have (`{"metrics", "candidates": [{"key", "cands":[{draw, code, think, exec, iou}]}]}`),
so `merge_bo_shards.py` / `write_rft_real.py` / `consistency_rerank.py` accept it unchanged.

Resume: results are appended to <out>.scored.jsonl ({key, draw, exec, iou}) and re-read on a
second run, so it can be interrupted freely.

    python score_partials.py --partials '<dir>/bo32_*.shard?.json.partial.json' \
        --gt-dir <bench>/gt_meshes_v15 --out <dir>/bo32_<corpus>_<run>.json [--workers 16]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

from iou import iou_pair  # noqa: E402
from rft_generate import exec_to_stl  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--partials", required=True, help="glob of .partial.json checkpoints")
    ap.add_argument("--gt-dir", required=True, help="dir of <key>.stl ground-truth meshes")
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=16)
    args = ap.parse_args()

    files = sorted(glob.glob(args.partials))
    assert files, f"no checkpoints match {args.partials}"
    parts = []          # (key, [cand dicts in draw order])
    for f in files:
        d = json.load(open(f))
        for key, cs in zip(d["keys"], d["cands"]):
            cs = sorted(cs, key=lambda c: c.get("draw", 0))
            parts.append((key, cs))
    print(f"[score] {len(files)} checkpoints, {len(parts)} parts, "
          f"{sum(len(c) for _, c in parts)} candidates", flush=True)

    done = {}
    jl = args.out + ".scored.jsonl"
    if os.path.exists(jl):
        for line in open(jl):
            try:
                r = json.loads(line)
            except Exception:
                continue
            done[(r["key"], r["draw"])] = r
        print(f"[score] resuming: {len(done)} candidates already scored", flush=True)

    todo = [(key, c) for key, cs in parts for c in cs
            if c.get("code") and (key, c.get("draw")) not in done]
    print(f"[score] {len(todo)} to execute", flush=True)
    t0 = time.time()
    n_done = [0]
    out_f = open(jl, "a")

    with tempfile.TemporaryDirectory(prefix="score_") as td:
        def run_one(item):
            key, c = item
            stl = os.path.join(td, f"{key}_{c['draw']}.stl")
            ok = iou = None
            try:
                ok = exec_to_stl(c["code"], stl, td, f"{key}_{c['draw']}")
                if ok:
                    iou = iou_pair(stl, os.path.join(args.gt_dir, f"{key}.stl"))["iou_centered"]
            except Exception as e:
                print(f"[score] {key} draw {c['draw']}: {type(e).__name__}", flush=True)
                ok = False
            rec = {"key": key, "draw": c["draw"], "exec": bool(ok), "iou": float(iou or 0.0)}
            out_f.write(json.dumps(rec) + "\n")
            n_done[0] += 1
            if n_done[0] % 500 == 0:
                out_f.flush()
                rate = n_done[0] / max(1e-9, time.time() - t0)
                left = (len(todo) - n_done[0]) / max(1e-9, rate)
                print(f"[score] {n_done[0]}/{len(todo)}  {rate:.1f}/s  eta {left/3600:.1f} h", flush=True)
            return rec
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            for rec in ex.map(run_one, todo):
                done[(rec["key"], rec["draw"])] = rec
    out_f.close()

    n_exec = 0
    for key, cs in parts:
        for c in cs:
            r = done.get((key, c.get("draw")))
            c["exec"] = bool(r and r["exec"])
            c["iou"] = float(r["iou"]) if r else 0.0
            c.pop("pred", None)
            n_exec += c["exec"]
    metrics = {"n": len(parts), "k": max(len(cs) for _, cs in parts), "n_exec": n_exec,
               "source": "score_partials.py"}
    with open(args.out, "w") as f:
        json.dump({"metrics": metrics, "candidates": [{"key": k, "cands": cs} for k, cs in parts]}, f)
    print(f"[score] executed {n_exec}/{sum(len(c) for _, c in parts)} -> {args.out}", flush=True)


if __name__ == "__main__":
    main()
