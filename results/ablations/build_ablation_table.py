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


def load(b, n, d=D):
    f = f"{d}/{b}_{n}.json"
    if not os.path.exists(f):
        return None
    out = {}
    for p in json.load(open(f))["candidates"]:
        c = sorted(p["cands"], key=lambda c: c.get("draw", 0))
        iou = [float(x.get("iou") or 0) for x in c]
        out[p["key"]] = {"d0": iou[0], "ex": float(np.mean([bool(x.get("exec")) for x in c]))}
    cf = f"{d}/{b}_{n}_consistency.json"
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

# Paper table (2026-10-21): the user's results-table rows filled from the eval files. Real = held-out bench B only.
# Rows without "vote" = one draw (draw 0), vote rows = K=8 consistency vote, repair rows = the multi-start pipeline
# means from the S1/S2 summaries (bench-B protocol, results/bench_b/pipeline/summary_b.py).
ROOT = os.path.dirname(os.path.dirname(D))
GE, BE = f"{ROOT}/results/grpo_eval", f"{ROOT}/results/bench_b/eval"
SUMM = {"full": f"{ROOT}/results/indist_pipeline/summary_full.txt", "benchb": f"{ROOT}/results/bench_b/pipeline/summary_b.txt"}
S1, S2 = "S1 MULTI-START (3 chains, v3 pick)", "S2 MULTI-START (3 chains, v3 pick)"
# Flash-Next pipeline (results/flashnext/PLAN.md): GRPO/EI evals in results/flashnext/grpo, chains in summary_fn.txt (one file,
# one section per bench). FNEI_BEST = the EI step picked on real-144 + synthetic (written when picked).
FG, FNSUMM = f"{ROOT}/results/flashnext/grpo", f"{ROOT}/results/flashnext/pipeline/summary_fn.txt"
FNSEC = {"benchb": "## Bench B (held-out 280)", "full": "## Synthetic (1,027)"}
FNEI = open(f"{FG}/FNEI_BEST").read().strip() if os.path.exists(f"{FG}/FNEI_BEST") else None


def pcell(b, s):  # s = (dir, model, metric) | ("chain" | "fnchain", summary stage) | None
    if s is None:
        return "—"
    if s[0] == "fnchain":
        sec = None
        for line in open(FNSUMM) if os.path.exists(FNSUMM) else []:
            sec = line.strip() if line.startswith("## ") else sec
            c = [x.strip() for x in line.split("|")]
            if sec == FNSEC[b] and len(c) > 3 and c[1] == s[1]:
                return c[3]
        return "—"
    if s[0] == "chain":
        for line in open(SUMM[b]):
            c = [x.strip() for x in line.split("|")]
            if len(c) > 3 and c[1] == s[1]:
                return c[3]
        return "—"
    r = load(b, s[1], s[0])
    return "—" if r is None else f"{np.mean([x[s[2]] for x in r.values()]):.3f}"


def both(d, n, m):
    return {"full": (d, n, m), "benchb": (d, n, m)}


PAPER = [
    ("Qwen3.8-27B", "Off-the-shelf", {"full": (GE, "qwenbase", "d0"), "benchb": (BE, "qwenbase", "d0")}),
    ("Qwen3.8-27B", "LoRA r64, attention only ¹", both(D, "e10", "d0")),
    ("Qwen3.8-Flash-Next (180B-A6B)", "LoRA r64, attention + shared experts ²", both(D, "e26fl", "d0")),
    ("DeepSeek-V4.1-Flash", "Zero-shot, short reasoning ³", {"full": (BE, "dsv41_t0", "d0"), "benchb": (BE, "dsv41", "d0")}),
    ("DeepSeek-V4.1-Flash", "Reasoning LoRA ⁴", {}),
    ("DeepSeek-V4.1-Flash", "Self-training on own outputs ⁴", {}),
    ("DeepSeek-V4.1-Flash", "GRPO (LoRA), short reasoning ⁴", {}),
    ("Qwen3.8-27B", "Full fine-tune (FFT), vision frozen", both(D, "e55ctl", "d0")),
    ("Qwen3.8-27B", "FFT + 8 Candidate Vote", both(D, "e55ctl", "vote")),
    ("Qwen3.8-27B", "FFT + 8 Candidate Vote + GRPO ⁵", {"full": (GE, "rft2_rl_s60", "vote"), "benchb": (BE, "rft2_rl_s60", "vote")}),
    ("Qwen3.8-27B", "FFT + 8 Candidate Vote + Visual Repair", {"full": ("chain", S2), "benchb": ("chain", S2)}),
    ("Qwen3.8-27B", "FFT + 8 Candidate Vote + GRPO + Visual Repair ⁶", {"full": ("chain", S1), "benchb": ("chain", S1)}),
    ("Qwen3.8-Flash-Next (180B-A6B)", "Full fine-tune (FFT), same recipe as the 27B FFT", both(D, "e59", "d0")),
    ("Qwen3.8-Flash-Next (180B-A6B)", "FFT + 8 Candidate Vote", both(D, "e59", "vote")),
    ("Qwen3.8-Flash-Next (180B-A6B)", "FFT + 8 Candidate Vote + GRPO ⁷", both(FG, f"fneis{FNEI}", "vote") if FNEI else {}),
    ("Qwen3.8-Flash-Next (180B-A6B)", "FFT + 8 Candidate Vote + Visual Repair ⁸", {"full": ("fnchain", "FN " + S2), "benchb": ("fnchain", "FN " + S2)}),
    ("Qwen3.8-Flash-Next (180B-A6B)", "FFT + 8 Candidate Vote + GRPO + Visual Repair ⁸", {"full": ("fnchain", "FN " + S1), "benchb": ("fnchain", "FN " + S1)}),
]
def rng_cell(b):  # one-draw range of the all-linear LoRAs (e3/e4/e9)
    v = sorted(float(pcell(b, (D, n, "d0"))) for n in ("e3", "e4", "e9"))
    return f"{v[0]:.3f}–{v[-1]:.3f}"



print("## Paper results table\n")
print("Real Test = held-out bench B (280 parts). Rows without \"vote\" are one draw (draw 0: greedy for Qwen, sampled for\n"
      "DeepSeek); vote rows are the K=8 consistency vote; the repair rows are the full repair pipeline.\n")
print("| Base model | Method | Synthetic Test Mean IoU (1,027) | Real Test Mean IoU (280) |\n|---|---|---|---|")
for base, meth, src in PAPER:
    print(f"| {base} | {meth} | {pcell('full', src.get('full'))} | {pcell('benchb', src.get('benchb'))} |")
print(f"""
¹ Attention-only was trained at r64 only; the r64–256 runs are all-linear LoRAs ({rng_cell('full')} / {rng_cell('benchb')}). All these
  LoRAs used the early traced-only data. A full fine-tune on that same data scores {pcell('full', (D, 'e1', 'd0'))} / {pcell('benchb', (D, 'e1', 'd0'))} (e1), so at
  matched data LoRA ties full fine-tuning; the gap to the FFT row is the later data and recipe.
² Earlier recipe (e24: before RFT rounds 2–5), adapter merged.
³ Up to 3 calls per sample, with answer-now / execution-error retries the Qwen rows do not get. Long reasoning (one draw,
  T 0.7, no token cap) was measured only on the real-144 dev bench: 0.299.
⁴ Measured only as one draw on the real-144 dev bench: 0.208 / 0.301 / 0.327. The reasoning LoRA and the self-training
  run were trained through the HF-forward bug fixed on 2026-10-07 (compressed attention ran sliding-window only). 0.327 is
  the best GRPO round, picked on that same bench (later rounds +0.024 / +0.004 over the untrained 0.291).
⁵ GRPO plus two expert-iteration rounds. Each round fine-tunes on the best program per hard real training part (the
  model's own samples and search outputs, kept at IoU ≥ 0.75 against ground truth), then runs a short GRPO. This is the
  generator the full system uses. Best GRPO-only checkpoint: {pcell('full', (GE, 'ent_t10_s120', 'vote'))} / {pcell('benchb', (BE, 'ent_t10_s120', 'vote'))}.
⁶ The full system: 16 candidates, verifier pick, 3 repair chains, render-compare pick. Its plain 16-candidate vote
  before repair: {pcell('full', ('chain', 'S1 K=16 vote'))} / {pcell('benchb', ('chain', 'S1 K=16 vote'))}.
⁷ The 27B's GRPO recipe (entropy floor), 200 steps, step picked on the real-144 dev bench + synthetic, plus one
  expert-iteration round that reuses the 27B's round-2 SFT data (the 27B ran two rounds, the second on data built from its
  round-1 model).
  GRPO alone: {pcell('full', (FG, 'fn1s200', 'vote'))} / {pcell('benchb', (FG, 'fn1s200', 'vote'))}.{'' if FNEI else ' The EI round is still running.'}
⁸ The 27B's repair pipeline with a Flash-Next visual repairer (full fine-tune of the Flash-Next FFT on the 27B repairer's
  data and recipe). The GRPO + repair row uses the 27B's verifier. Its 16-candidate vote before repair:
  {pcell('full', ('fnchain', 'FN S1 K=16 vote'))} / {pcell('benchb', ('fnchain', 'FN S1 K=16 vote'))}.
""")
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
