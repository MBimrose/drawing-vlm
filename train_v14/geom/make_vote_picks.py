"""Repair-loop start files from a scored best-of-K run + its consistency_rerank output (2026-10-06).

    python make_vote_picks.py <scored.json> <consistency.json> <out_stem> [--top 3] [--distinct 0.95]

Writes <out_stem>_r1.json (the vote pick = medoid: highest mean pairwise IoU with the other executing
candidates, label-free) and <out_stem>_r2/_r3.json (next-ranked candidates whose agreement with every
earlier pick is < --distinct), in the vr_serve.py --picks format {key: {code, iou, draw}}. Parts with
fewer distinct executing candidates repeat the last pick. Prints the mean IoU of each start file.
"""
import argparse
import json

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scored"); ap.add_argument("consistency"); ap.add_argument("out_stem")
    ap.add_argument("--top", type=int, default=3); ap.add_argument("--distinct", type=float, default=0.95)
    a = ap.parse_args()
    code = {}
    for p in json.load(open(a.scored))["candidates"]:
        for c in p["cands"]:
            code[(p.get("key") or p.get("part"), c.get("draw", 0))] = c.get("code")
    outs = [dict() for _ in range(a.top)]
    for p in json.load(open(a.consistency))["parts"]:
        k, iou, ex, P = p["key"], p["iou"], p["exec"], p["pair_iou"]
        idx = [i for i in range(len(iou)) if ex[i]]
        if not idx:
            ranked = [0]
        else:
            agree = {i: np.mean([P[i][j] for j in idx if j != i and P[i][j] is not None] or [0.0]) for i in idx}
            ranked = sorted(idx, key=lambda i: -agree[i])
        chosen = []
        for i in ranked:
            if all(P[i][j] is None or P[i][j] < a.distinct for j in chosen):
                chosen.append(i)
            if len(chosen) == a.top:
                break
        while len(chosen) < a.top:
            chosen.append(chosen[-1])
        for r, i in enumerate(chosen):
            outs[r][k] = {"code": code.get((k, i)), "iou": float(iou[i] or 0.0), "draw": i}
    for r, o in enumerate(outs):
        f = f"{a.out_stem}_r{r + 1}.json"
        json.dump(o, open(f, "w"))
        print(f"{f}: n={len(o)} mean start IoU {np.mean([v['iou'] for v in o.values()]):.3f}")


if __name__ == "__main__":
    main()
