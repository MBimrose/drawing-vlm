"""Real-bench repair-loop trajectory: mean IoU of the currently adopted program after each repair round, for the
pooled rp3 chain (chain 1) and for the 3-chain multi-start (v3 pick across chains at every round), from the system
jsonl logs (hist = adopted programs; rounds[i] = the 16 draws of round i+1).

    python train_v14/geom/repair_curve.py   -> results/figures/results_deck/data/repair_curve.json
"""
import json

import numpy as np

DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
CHAINS = [f"{DV}/results/repair/{c}.jsonl" for c in ("sys_pooled_rp3_rep_r32_r6", "sys_rp3_rank2_r6", "sys_rp3_rank3_r6")]
CONS = f"{DV}/results/ext/bo8_ext_dw423p_e55-rft-real-u5-gt-dw423_consistency.json"
N_ROUNDS = 6


def trajectory(r):
    """Adopted (iou, v3) after rounds 0..N_ROUNDS; an adoption's round is the round whose draws contain its code."""
    h = r["hist"]; adopt_round = [0]
    for y in h[1:]:
        hit = [i + 1 for i, rd in enumerate(r["rounds"]) if any((d.get("code") or "").strip() == y["code"].strip() for d in rd)]
        adopt_round.append(hit[0] if hit else adopt_round[-1] + 1)
    out, cur = [], 0
    for t in range(N_ROUNDS + 1):
        while cur + 1 < len(h) and adopt_round[cur + 1] <= t and h[cur + 1].get("adopted", True):
            cur += 1
        out.append((h[cur]["iou"], h[cur].get("v3", 0) or 0))
    return out


chains = [{json.loads(l)["key"]: json.loads(l) for l in open(f)} for f in CHAINS]
keys = sorted(chains[0])
traj = [{k: trajectory(c[k]) for k in keys if k in c} for c in chains]
c1 = np.array([[traj[0][k][t][0] for t in range(N_ROUNDS + 1)] for k in keys])
ms = np.array([[max((tr[k][t] for tr in traj if k in tr), key=lambda x: x[1])[0] for t in range(N_ROUNDS + 1)] for k in keys])
cons = json.load(open(CONS))["per_part"]
oracle8 = float(np.mean([cons[k]["oracle"] for k in keys]))
res = {"n": len(keys), "rounds": list(range(N_ROUNDS + 1)),
       "chain1_mean": c1.mean(0).tolist(), "chain1_sem": (c1.std(0, ddof=1) / np.sqrt(len(keys))).tolist(),
       "multistart_mean": ms.mean(0).tolist(), "multistart_sem": (ms.std(0, ddof=1) / np.sqrt(len(keys))).tolist(),
       "chain1_frac85": (c1 >= 0.85).mean(0).tolist(), "multistart_frac85": (ms >= 0.85).mean(0).tolist(),
       "e55_vote": float(c1[:, 0].mean()), "e55_oracle8": oracle8,
       "fusion_ms_final": float(ms[[k[0] == "F" for k in keys], -1].mean()), "abc_ms_final": float(ms[[k[0] == "A" for k in keys], -1].mean())}
json.dump(res, open(f"{DV}/results/figures/results_deck/data/repair_curve.json", "w"), indent=1)
print(f"n={res['n']}  chain1 {np.round(res['chain1_mean'], 3)}\n  multi-start {np.round(res['multistart_mean'], 3)}\n"
      f"  e55 vote {res['e55_vote']:.3f}  e55 oracle@8 {oracle8:.3f}  F {res['fusion_ms_final']:.3f} A {res['abc_ms_final']:.3f}")
