"""Offline selection ablation on serve_full_timed.py records (no repair): executes all 8 candidates of every part once,
scores ground-truth IoU (evaluation only), then compares label-free pick rules on the same candidates:
  both      verifier expected IoU + render-compare v3 (the served rule)
  ver       verifier only (no renders: the fast path)
  v3        render-compare only
  greedy    candidate 0 (greedy decode), no selection
  oracle    best of 8 by ground truth (reference)
Paired bootstrap 95% CI of each rule minus `both`.

    bash train_v14/serv19/cpu_run.sh -n ccc0441 -c 64 -- .venv/bin/python train_v14/geom/selection_ablation.py \
        --records results/figures/pipeline_timing/throughput/bf16_acc.jsonl --bench results/bench_b/bench
"""
import argparse
import json
import os
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from iou import iou_pair  # noqa: E402
from rft_generate import exec_to_stl  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", required=True); ap.add_argument("--bench", required=True); ap.add_argument("--workers", type=int, default=60)
    a = ap.parse_args()
    R = [json.loads(l) for l in open(a.records)]
    jobs = [(r["key"], j, c) for r in R for j, c in enumerate(r["codes"]) if c and r["exec"][j]]
    td = tempfile.mkdtemp(prefix="sab_", dir="/dev/shm")

    def score(item):
        (k, j, code), i = item
        stl = os.path.join(td, f"{i}.stl")
        try:
            if not exec_to_stl(code, stl, td, f"p{i}"):
                return 0.0
            return float(iou_pair(stl, os.path.join(a.bench, "gt_meshes_v15", k + ".stl"))["iou_centered"])
        except Exception:
            return 0.0
        finally:
            if os.path.exists(stl):
                os.remove(stl)
    iou = dict(zip([(k, j) for k, j, _ in jobs], ThreadPoolExecutor(a.workers).map(score, zip(jobs, range(len(jobs))))))
    rules = {"both": lambda r, j: r["ver"][str(j)] + r["v3"].get(str(j), 0.0), "ver": lambda r, j: r["ver"][str(j)],
             "v3": lambda r, j: r["v3"].get(str(j), 0.0)}
    out = {n: [] for n in ("both", "ver", "v3", "greedy", "oracle")}
    for r in R:
        idx = [j for j in range(len(r["codes"])) if (r["key"], j) in iou and str(j) in r["ver"]]
        if not idx:
            for n in out:
                out[n].append(0.0)
            continue
        for n, f in rules.items():
            out[n].append(iou[(r["key"], max(idx, key=lambda j: f(r, j)))])
        out["greedy"].append(iou.get((r["key"], 0), 0.0)); out["oracle"].append(max(iou[(r["key"], j)] for j in idx))
    rng = np.random.default_rng(0); n = len(R); base = np.array(out["both"])
    rec = [r["iou_start"] for r in R if r.get("iou_start") is not None]
    res = {"n": n, "served_iou_recorded": float(np.mean(rec)) if rec else None}
    for k, v in out.items():
        v = np.array(v); d = v - base; bs = [d[rng.integers(0, n, n)].mean() for _ in range(5000)]
        res[k] = {"mean": float(v.mean()), "minus_both": float(d.mean()), "ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]}
        print(f"{k:7s} {v.mean():.3f}  vs both {d.mean():+.3f} [{np.percentile(bs, 2.5):+.3f}, {np.percentile(bs, 97.5):+.3f}]")
    print("recorded served IoU", res["served_iou_recorded"])
    json.dump(res, open(a.records.replace(".jsonl", "_selection.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
