"""Repair-loop curve on a bench from serve_full_timed.py records (current pipeline: generator K=8 -> verifier +
render-compare starts -> 3 rp3 chains x 6 rounds, render-compare gate). Executes every stored program once (the 8
candidates, each chain's start and accepted repairs), scores IoU vs ground truth (evaluation only), then per round:
  single chain   = the chain from the top-ranked start (chain 0)
  multi-start    = per part, the chain whose current program has the highest render-compare score (the served pick)
  best of 8      = oracle over the 8 generated candidates (no repair), reference line
Output in the format plot_results_deck.repair_loop reads.

    bash train_v14/serv19/cpu_run.sh -n ccc0441 -c 64 -- .venv/bin/python train_v14/geom/repair_curve_from_records.py \
        --records results/figures/pipeline_timing/s05_full_bench_b.jsonl --bench results/bench_b/bench \
        --out results/figures/pipeline_timing/repair_curve_bench_b.json
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
    ap.add_argument("--records", required=True); ap.add_argument("--bench", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--rounds", type=int, default=6); ap.add_argument("--workers", type=int, default=60)
    a = ap.parse_args()
    R = [json.loads(l) for l in open(a.records)]
    jobs = {}
    for r in R:
        for c in r["codes"]:
            if c:
                jobs[(r["key"], c)] = None
        for ch in r["chains"]:
            for h in ch:
                jobs[(r["key"], h["code"])] = None
    print(f"[curve] {len(R)} parts, {len(jobs)} unique programs", flush=True)
    td = tempfile.mkdtemp(prefix="rcr_", dir="/dev/shm")

    def score(item):
        (k, code), i = item
        stl = os.path.join(td, f"{i}.stl")
        if not exec_to_stl(code, stl, td, f"p{i}"):
            return 0.0
        try:
            return float(iou_pair(stl, os.path.join(a.bench, "gt_meshes_v15", k + ".stl"))["iou_centered"])
        except Exception:
            return 0.0
        finally:
            if os.path.exists(stl):
                os.remove(stl)
    keys = list(jobs)
    vals = list(ThreadPoolExecutor(a.workers).map(score, zip(keys, range(len(keys)))))
    iou = dict(zip(keys, vals))

    T = a.rounds + 1; single, multi, best8, per = [], [], [], []
    for r in R:
        k = r["key"]
        best8.append(max([iou[(k, c)] for c in r["codes"] if c] or [0.0]))
        traj = []
        for ch in r["chains"]:                     # state after round t = last accepted program with round <= t
            row = []
            for t in range(T):
                h = [x for x in ch if x["round"] <= t][-1]
                row.append((iou[(k, h["code"])], h["v3"]))
            traj.append(row)
        single.append([traj[0][t][0] for t in range(T)])
        multi.append([max((tr[t] for tr in traj), key=lambda x: x[1])[0] for t in range(T)])
        per.append({"key": k, "single": single[-1], "multi": multi[-1], "best8": best8[-1],
                    "chains": [[{"round": h["round"], "iou": iou[(k, h["code"])], "v3": h["v3"]} for h in ch] for ch in r["chains"]]})
    S, M = np.array(single), np.array(multi); n = len(R)
    res = {"n": n, "rounds": list(range(T)),
           "chain1_mean": S.mean(0).tolist(), "chain1_sem": (S.std(0, ddof=1) / np.sqrt(n)).tolist(),
           "multistart_mean": M.mean(0).tolist(), "multistart_sem": (M.std(0, ddof=1) / np.sqrt(n)).tolist(),
           "chain1_frac85": (S >= 0.85).mean(0).tolist(), "multistart_frac85": (M >= 0.85).mean(0).tolist(),
           "e55_vote": float(S[:, 0].mean()), "e55_oracle8": float(np.mean(best8)),
           "fusion_ms_final": float(M[[k["key"][0] == "F" for k in per], -1].mean()),
           "abc_ms_final": float(M[[k["key"][0] == "A" for k in per], -1].mean())}
    json.dump(res, open(a.out, "w"), indent=1)
    json.dump(per, open(a.out.replace(".json", "_per_part.json"), "w"))
    print(f"[curve] single {np.round(res['chain1_mean'], 3)}\n  multi {np.round(res['multistart_mean'], 3)}\n"
          f"  best of 8 {res['e55_oracle8']:.3f}  served (multi, round 6) {res['multistart_mean'][-1]:.3f}")


if __name__ == "__main__":
    main()
