"""Full pipeline on the GRPO generator (2026-10-08): repair-chain start files from label-free SELECTION ranking.

Per part, rank the executing candidates (exec + non-empty code, read from the scored candidates file -- the
sel_study.py convention) by verifier(v3b EV) + render-compare v3 (raw sum; missing verifier pred = -1, exactly
sel_study.py's "ver+v3"), then take the top-3 DISTINCT ones with make_vote_picks.py's distinctness rule (pairwise IoU
from the consistency matrix < --distinct with every earlier pick; None counts as distinct). Parts with fewer distinct
executing candidates repeat the last pick; parts with no executing candidate start from draw 0. Writes
<out_stem>_r{1,2,3}.json in the vr_serve.py --picks format {key: {code, iou, draw, score}} (iou = evaluation only).

    python pg_make_starts.py --cands X.json --cons X_consistency.json --vpreds vpreds_X.json --rc X_rc_v3.json \
        --out-stem results/pipeline_grpo/starts_sel [--k 16] [--top 3] [--distinct 0.95]
"""
import argparse
import json

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cands", required=True); ap.add_argument("--cons", required=True)
    ap.add_argument("--vpreds", required=True); ap.add_argument("--rc", required=True)
    ap.add_argument("--out-stem", required=True)
    ap.add_argument("--k", type=int, default=16); ap.add_argument("--top", type=int, default=3)
    ap.add_argument("--distinct", type=float, default=0.95)
    a = ap.parse_args()
    mats = {p["key"]: p["pair_iou"] for p in json.load(open(a.cons))["parts"]}
    vp = json.load(open(a.vpreds))
    rc = {p["key"]: p["cands"] for p in json.load(open(a.rc))["parts"]}
    outs = [dict() for _ in range(a.top)]
    for p in json.load(open(a.cands))["candidates"]:
        k = p["key"]; cs = sorted(p["cands"], key=lambda c: int(c.get("draw", 0)))[: a.k]
        n = len(cs)
        rrows = rc[k][:n]
        assert len(rrows) == n and all(abs(float(r["iou"]) - float(c.get("iou") or 0.0)) < 1e-6 for r, c in zip(rrows, cs)), k
        ver = vp.get(k) or [None] * n
        assert len(ver) >= n, k
        ex = [j for j, c in enumerate(cs) if bool(c.get("exec")) and bool((c.get("code") or "").strip())]
        P = mats.get(k) or [[None] * n for _ in range(n)]
        if not ex:
            ranked, score = [0], {0: float("nan")}
        else:
            score = {j: (float(ver[j][0]) if ver[j] is not None else -1.0) + float(rrows[j].get("v3", 0.0)) for j in ex}
            ranked = sorted(ex, key=lambda j: (-score[j], j))    # ties -> lower draw index (= sel_study argmax)
        chosen = []
        for i in ranked:
            if all(P[i][j] is None or P[i][j] < a.distinct for j in chosen):
                chosen.append(i)
            if len(chosen) == a.top:
                break
        while len(chosen) < a.top:
            chosen.append(chosen[-1])
        for r, i in enumerate(chosen):
            outs[r][k] = {"code": cs[i].get("code") or "", "iou": float(cs[i].get("iou") or 0.0), "draw": i,
                          "score": score.get(i)}
    for r, o in enumerate(outs):
        f = f"{a.out_stem}_r{r + 1}.json"
        json.dump(o, open(f, "w"))
        print(f"{f}: n={len(o)} mean start IoU {np.mean([v['iou'] for v in o.values()]):.3f} "
              f"(distinct from r1: {sum(o[k]['draw'] != outs[0][k]['draw'] for k in o)})")


if __name__ == "__main__":
    main()
