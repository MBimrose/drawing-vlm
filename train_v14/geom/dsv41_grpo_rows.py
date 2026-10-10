"""DeepSeek GRPO round -> advantage-weighted training rows + round stats (2026-10-06).

Inputs: the rollout log (<roll>.jsonl from dsv41_grpo_rollout.py: think / reply / code / finish per draw) and the
score_partials outputs (<scored>_<bench>.json: exec / iou per draw). Reward = centred IoU if the program executed,
else 0 (truncated / no code / exec failure all 0). Per part: A = r - mean(r) over its G draws (Dr.GRPO), optionally
divided by the std of all non-degenerate groups' rewards (--adv batchstd). Zero-variance groups are skipped. Rows
kept = draws that produced code (incl. reward-0 exec failures = negative signal); truncated / no-code draws are not
trained (they still count in the group mean, so a short successful answer is pushed up relative to them).

Writes <tier>/grpo-00000.tar (<key>__d<draw>.{png,code.py,think.txt,reply.txt,adv.txt}) and <stats>.json.
    python dsv41_grpo_rows.py --roll runs/r00/roll.jsonl --scored 'runs/r00/scored_*.json' --tier runs/r00/tier \
        --stats runs/r00/stats.json [--adv batchstd]
"""
from __future__ import annotations

import argparse
import glob
import io
import json
import os
import pickle
import statistics
import tarfile


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roll", required=True)
    ap.add_argument("--scored", required=True, help="glob of score_partials outputs")
    ap.add_argument("--tier", required=True)
    ap.add_argument("--stats", required=True)
    ap.add_argument("--adv", choices=["mean", "batchstd"], default="batchstd")
    ap.add_argument("--max-train-tokens", type=int, default=0, help="drop rows whose completion exceeds this (0 = keep)")
    a = ap.parse_args()

    roll = {}
    for line in open(a.roll):
        r = json.loads(line); roll[(r["bench"], r["key"], r["draw"])] = r
    score = {}
    for f in glob.glob(a.scored):
        if f.endswith(".scored.jsonl"):
            continue
        for p in json.load(open(f))["candidates"]:
            for c in p["cands"]:
                score[(p["key"], c["draw"])] = (bool(c.get("exec")), float(c.get("iou", 0.0)))
    groups = {}
    for (b, k, d), r in roll.items():
        ex, iou = score.get((k, d), (False, 0.0))
        r["exec"] = ex; r["reward"] = iou if ex else 0.0
        groups.setdefault((b, k), []).append(r)

    live = {g: rs for g, rs in groups.items() if len(rs) > 1 and max(x["reward"] for x in rs) - min(x["reward"] for x in rs) > 1e-6}
    std = 1.0
    if a.adv == "batchstd" and live:
        allr = [x["reward"] for rs in live.values() for x in rs]
        std = max(statistics.pstdev(allr), 0.05)
    rows = []
    for g, rs in live.items():
        m = sum(x["reward"] for x in rs) / len(rs)
        for x in rs:
            x["adv"] = (x["reward"] - m) / std
            if x.get("code") and x.get("finish") != "length" and abs(x["adv"]) > 1e-9:
                if a.max_train_tokens and x.get("completion_tokens", 0) > a.max_train_tokens:
                    continue
                rows.append(x)

    os.makedirs(a.tier, exist_ok=True)
    pngs = {}
    for b in sorted({x["bench"] for x in rows}):
        c = pickle.load(open(os.path.join(b, "eval_cache_v15.pkl"), "rb"))["samples"]
        for x in rows:
            if x["bench"] == b:
                pngs[x["key"]] = c[x["key"]]["png"]
        del c

    def add(t, name, data):
        ti = tarfile.TarInfo(name); ti.size = len(data); t.addfile(ti, io.BytesIO(data))
    with tarfile.open(os.path.join(a.tier, "grpo-00000.tar"), "w") as t:
        for x in rows:
            n = f"{x['key']}__d{x['draw']}"
            add(t, n + ".png", pngs[x["key"]]); add(t, n + ".code.py", x["code"].encode())
            add(t, n + ".think.txt", (x.get("think") or "").encode()); add(t, n + ".reply.txt", x["reply"].encode())
            add(t, n + ".adv.txt", f"{x['adv']:.6f}".encode())

    allx = [x for rs in groups.values() for x in rs]
    toks = sorted(x.get("completion_tokens", 0) for x in allx)
    mean = lambda v: sum(v) / len(v) if v else 0.0
    st = {"parts": len(groups), "samples": len(allx),
          "mean_reward": mean([x["reward"] for x in allx]),
          "best_of_g": mean([max(x["reward"] for x in rs) for rs in groups.values()]),
          "first_draw": mean([next((x["reward"] for x in rs if x["draw"] == 0), 0.0) for rs in groups.values()]),
          "exec_rate": mean([float(x["exec"]) for x in allx]),
          "code_rate": mean([float(bool(x.get("code"))) for x in allx]),
          "trunc_rate": mean([float(x.get("finish") == "length") for x in allx]),
          "error_rate": mean([float("error" in x and "reply" not in x) for x in allx]),
          "mean_completion_tokens": mean(toks), "median_completion_tokens": toks[len(toks) // 2] if toks else 0,
          "mean_reasoning_chars": mean([len(x.get("think") or "") for x in allx]),
          "frontier_frac": len(live) / max(1, len(groups)), "rows": len(rows), "adv_std": std,
          "pos_rows": sum(x["adv"] > 0 for x in rows), "neg_rows": sum(x["adv"] < 0 for x in rows)}
    json.dump(st, open(a.stats, "w"), indent=1)
    print("[rows] " + json.dumps(st), flush=True)


if __name__ == "__main__":
    main()
