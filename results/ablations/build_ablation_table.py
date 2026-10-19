"""Results-table ablations (2026-10-17): training-choice / data-ladder / scale rows on the main-table protocol
(K=8: draw 0 greedy + 7 at T 0.7, think, 2400 tok; consistency vote), three benches. Files in this directory:
<bench>_<model>.json (score_partials) + <bench>_<model>_consistency.json (consistency_rerank). Paired 2,000-sample
bootstrap 95% CIs (rng 0, as eval_table.py).
    python build_ablation_table.py > ablation_tables.md"""
import json
import os

import numpy as np

D = os.path.dirname(os.path.abspath(__file__))
BENCH = [("full", "Synthetic (1,027)"), ("real", "Real-144"), ("benchb", "Real held-out (280)")]
LABEL = {
    "e1": "Qwen3.8-27B full FT, traced-only data (verified traces, no aug), 2k steps",
    "e10": "Qwen3.8-27B LoRA r64, attention only (q/k/v/o), e1 data",
    "e3": "Qwen3.8-27B LoRA r64 (all linear layers), e1 data",
    "e4": "Qwen3.8-27B LoRA r128 (all linear layers), e1 data, xhigh effort, lr 2e-4",
    "e9": "Qwen3.8-27B LoRA r256 (all linear layers), e1 data",
    "e12": "Qwen3.8-27B LoRA r64 (all linear layers), e2 data",
    "e2": "Qwen3.8-27B full FT, all ~500k rows (no filters)",
    "e16": "e2 + drop non-executing GT (~18%)",
    "e22": "+ certified reasoning traces (1:4), 6k steps",
    "e24": "+ RFT round 1: 60% own verified samples (STaR)",
    "e55ctl": "+ RFT rounds 2-5, real-geometry tier, dw-0.4.23 sheets (e55)",
    "e32fn": "Qwen3.8-Flash-Next 180B-A6B full FT: e24 recipe + its own RFT round",
    "e26fl": "Qwen3.8-Flash-Next 180B-A6B LoRA r64 (attention + shared experts), e24 recipe",
    "e35fn": "Qwen3.8-Flash-Next 180B-A6B: e32 + low-lr polish (1.5k steps)",
    "e59": "Qwen3.8-Flash-Next 180B-A6B full FT, e55 recipe (final)",
    "e59best": "Qwen3.8-Flash-Next 180B-A6B full FT, e55 recipe (best val checkpoint)",
    "nemoft_pf": "Nemotron-3.5-Super 120B-A12B full FT, e55 recipe (+ think prefill)",
}
# (row, partner) pairs for the paired-delta column
PAIRS = [("e10", "e1"), ("e3", "e1"), ("e4", "e1"), ("e9", "e1"), ("e10", "e3"), ("e12", "e2"), ("e12", "e3"), ("e16", "e2"), ("e22", "e16"), ("e24", "e22"), ("e55ctl", "e24"),
         ("e32fn", "e24"), ("e26fl", "e24"), ("e35fn", "e24"), ("e32fn", "e26fl"), ("e59", "e55ctl"), ("e59best", "e55ctl"), ("nemoft_pf", "e55ctl")]


def load(b, n):
    f = f"{D}/{b}_{n}.json"
    if not os.path.exists(f):
        return None
    out = {}
    for p in json.load(open(f))["candidates"]:
        c = sorted(p["cands"], key=lambda c: c.get("draw", 0))
        iou = [float(x.get("iou") or 0) for x in c]
        out[p["key"]] = {"d0": iou[0], "ex": float(np.mean([bool(x.get("exec")) for x in c]))}
    cf = f"{D}/{b}_{n}_consistency.json"
    if not os.path.exists(cf):
        return None
    for k, v in json.load(open(cf))["per_part"].items():
        if k in out:
            out[k]["vote"] = float(v["consistency"])
    return out if all("vote" in v for v in out.values()) else None


rng = np.random.default_rng(0)


def ci(d):
    bs = [rng.choice(d, len(d)).mean() for _ in range(2000)]
    return np.percentile(bs, 2.5), np.percentile(bs, 97.5)


R = {(b, n): load(b, n) for b, _ in BENCH for n in LABEL}
print("## Ablations on the main-table protocol\n")
print("Cells: vote mean IoU (share of parts ≥ 0.85) / single greedy draw. — = not yet scored.\n")
print("| Model | " + " | ".join(t for _, t in BENCH) + " |\n|---|" + "---|" * len(BENCH))
for n, lab in LABEL.items():
    cells = []
    for b, _ in BENCH:
        r = R[(b, n)]
        if r is None:
            cells.append("—"); continue
        v = np.array([x["vote"] for x in r.values()])
        cells.append(f"{v.mean():.3f} ({(v >= 0.85).mean():.0%}) / {np.mean([x['d0'] for x in r.values()]):.3f}")
    print(f"| {lab} [{n}] | " + " | ".join(cells) + " |")
print("\n## Paired deltas: vote [95% CI]; d0 = single greedy draw [95% CI]\n")
print("| Comparison | " + " | ".join(t for _, t in BENCH) + " |\n|---|" + "---|" * len(BENCH))
for a, p in PAIRS:
    cells = []
    for b, _ in BENCH:
        ra, rp = R[(b, a)], R[(b, p)]
        if ra is None or rp is None:
            cells.append("—"); continue
        ks = sorted(set(ra) & set(rp))
        dv = np.array([ra[k]["vote"] - rp[k]["vote"] for k in ks]); dd = np.array([ra[k]["d0"] - rp[k]["d0"] for k in ks])
        lv, hv = ci(dv); ld, hd = ci(dd)
        cells.append(f"{dv.mean():+.3f} [{lv:+.3f},{hv:+.3f}]; d0 {dd.mean():+.3f} [{ld:+.3f},{hd:+.3f}]")
    print(f"| {a} − {p} | " + " | ".join(cells) + " |")
