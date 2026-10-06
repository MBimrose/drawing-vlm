"""Round-0 frontier analysis: from a scored best-of-K JSON (score_partials/score_generic
format), report the GRPO gradient budget and write the frontier key list for training.

Outputs:
  - group-variance structure (how many parts carry gradient at each K)
  - reward distribution by band (0 / 0-0.5 / 0.5-0.8 / >=0.8)
  - frontier keys (group std >= min-var, at least one exec, mean in [lo, hi])
  - per-key best/mean for curriculum ranking

    python grpo_frontier.py --bo results/h6c/bo8_famtrain_e55.json --out results/h6c/famtrain_frontier
"""
import argparse
import json
import os

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bo", required=True)
    ap.add_argument("--out", required=True, help="prefix: writes <out>_keys.txt + <out>_stats.json")
    ap.add_argument("--min-var", type=float, default=1e-4)
    ap.add_argument("--lo", type=float, default=0.0, help="min group mean for frontier")
    ap.add_argument("--hi", type=float, default=1.0, help="max group mean for frontier")
    args = ap.parse_args()

    d = json.load(open(args.bo))
    cands = d["candidates"]
    stats = {"n_parts": len(cands)}
    bands = {"zero": 0, "low": 0, "mid": 0, "high": 0}
    frontier, hard, solved = [], [], []
    for p in cands:
        rs = [float(c.get("iou") or 0) for c in p["cands"]]
        best = max(rs) if rs else 0.0
        mean = float(np.mean(rs)) if rs else 0.0
        var = float(np.var(rs)) if rs else 0.0
        nexec = sum(bool(c.get("exec")) for c in p["cands"])
        if best >= 0.8:
            bands["high"] += 1
            solved.append(p["key"])
        elif best >= 0.5:
            bands["mid"] += 1
        elif best > 0:
            bands["low"] += 1
        else:
            bands["zero"] += 1
        # frontier: carries gradient (variance) and not already solved at ceiling
        if var >= args.min_var and nexec > 0 and args.lo <= mean < args.hi and best < 0.95:
            frontier.append((p["key"], best, mean, var))
        elif best < 0.5 and nexec == 0:
            hard.append(p["key"])
    stats["bands"] = bands
    stats["n_frontier"] = len(frontier)
    stats["n_solved_ge_08"] = len(solved)
    stats["n_zero_signal"] = len(hard)
    stats["mean_best_of_k"] = float(np.mean([max(float(c.get("iou") or 0) for c in p["cands"])
                                             for p in cands])) if cands else 0.0
    stats["mean_first_exec"] = float(np.mean([
        next((float(c["iou"]) for c in p["cands"] if c.get("exec")), 0.0) for p in cands]))
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out + "_keys.txt", "w") as f:
        for k, best, mean, var in sorted(frontier, key=lambda x: -x[3]):
            f.write(f"{k}\n")
    with open(args.out + "_stats.json", "w") as f:
        json.dump(stats, f, indent=1)
    print(json.dumps(stats, indent=1))
    print(f"frontier keys -> {args.out}_keys.txt ({len(frontier)} parts)")


if __name__ == "__main__":
    main()
