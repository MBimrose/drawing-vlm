# drawing_vlm — Project Status Report for the Paper

**Status date: 2026-10-05** (last experimental result: 2026-10-01, commit `bc9408b`;
no new results Oct 2–5 — only the daily trace-sync cron).

## Executive summary

Over five weeks (2026-08-27 → 10-01, 443 commits, 60+ experiments), the project built a
system that reads an engineering drawing and writes build123d CAD code, scored by exact
volumetric IoU:

- **In-distribution (1,030 certified synthetic parts): 0.920 mean IoU / 84% ≥ 0.85**
  served (best-of-8 + consistency), 0.854 best single shot — up from 0.559 at the first
  full fine-tune.
- **External real bench (146 held-out human-designed parts): 0.695** with the current
  best system (multi-start RP3 repair), up from 0.537 for the deployed generator —
  **+0.159, and above the generator's own best-of-8 oracle (0.591)**.
- Core empirical narrative: **verified self-generated data and serving/repair policies
  each bought more than model scale**; the ~0.40 real-part gap is a *shape-vocabulary*
  problem that only closed-loop visual repair has moved.

## 1. Task and metric

- **Input**: 1920×1280 PNG engineering sheet (orthographic views + iso, grid border,
  multi-cell title block, realistic callouts: ⌀ THRU, CBORE/CSK, M-threads, reams,
  radii, chamfers), rendered by the in-house draftwright pipeline (build123d/OCCT;
  v0.4.23 deployed).
- **Output**: one self-contained build123d Python script ending in
  `export_step(part, "output.step")`, produced after an optional think trace.
  (Not CadQuery. "ABC" in the logs is a dataset slice, not a code format.)
- **Metric**: exact volumetric IoU between generated solid and GT mesh, bbox-centered
  (translation-only; rotation/scale search ruled out in a frame-sensitivity study).
  Non-executing programs score 0. Headline: mean centered IoU + share ≥ 0.85
  (`train_v14/geom/iou.py`).
- **Eval pools**:
  - *In-distribution*: 1,030-part certified pool (from the 500k `tars_v14` corpus,
    Zero-To-CAD-derived; frozen split, uuid residue 0 mod 50).
  - *External real bench*: 146 held-out CADBench medium parts (88 Fusion 360 + 56 ABC,
    ≤ 80 faces, rescaled to 80 mm), rendered through draftwright. Repair loops use the
    143-part permissive 0.4.23 variant.
  - *Held-out families*: 200 synthesized out-of-vocabulary parts (out-of-sample check
    for the repair loop).

## 2. The system (deployed stack)

1. **Generator** — e55: Qwen3.8-27B full fine-tune, think mode, K=8 draws at T=0.7.
2. **Consistency vote** — execute all candidates, pick the medoid by pairwise IoU
   (label-free; captures ~62% of oracle headroom; every reweighting/clustering variant
   ties within ±0.005).
3. **Verifier** — low-agreement parts (gate 0.85) go to the v3b regression LoRA,
   expected-value argmax, one forward pass.
4. **Repair loop** — rp3: LoRA fine-tuned from e55, no-think, two-image input (target
   sheet + the candidate's own rendered sheet), K=16 × up to 6 rounds.
5. **Acceptance gate + multi-start** — adopt a repair only if the label-free
   render-compare score (v3) improves by margin 0.1; 3 chains from the top-3 distinct
   candidates, final pick by v3 across chains.

No GT, no hub model at serving time.

## 3. Training recipe

- **Full FT > LoRA** at 27B (0.559 vs 0.508 on identical data). FSDP2 FULL_SHARD,
  bf16 compute + fp32 master, vision tower frozen, seq 5120, effective batch 64,
  lr 6e-6, 4k steps sufficient.
- **Champion mixture 60/20/20**: RFT (own generations kept at exact IoU ≥ 0.8 with
  think traces, STaR rounds — each champion regenerates the tier) / certified Kimi-K3
  reasoning traces (53k, ±5% reverse-reconstruction gate) / plain-filtered GT.
  Ablations that survived: exec-bad GT filtering +0.05; dropping underdetermined sheets
  *hurts* (e23); acceptance 0.8 beats 0.9/0.95.
- **Run lineage** (`runs/`): e24 first RFT champion (0.827 single / 0.912 served) →
  e40–e45 strict-tier family → e46–e53 real-geometry RFT rounds → **e55 deployed**
  (draftwright-0.4.23 sheets) → e58 DeepCAD / e59 repair-tier / e60 long-program
  (all flat) → rp1–rp3 repairer chain → `dsv41_*` DeepSeek-V4.1-Flash campaign.

## 4. Results

### In-distribution (best-of-8 + consistency, 1,030-part pool)

All champion-family models sit in a 0.909–0.921 band — single-shot seed noise (±0.04)
is removed by the vote. Best served single model **e40: 0.920 / 84% ≥ 0.85**
(oracle@8 0.947). Best single shot e50: 0.854 (96-pool). The 180B Flash-Next on the
identical recipe scored 0.78–0.83 single-shot — scale is not the lever.

| Milestone | Run | 96-pool single | Full-pool vote | Real bench | Role |
|---|---|---|---|---|---|
| Baseline FT | e2 | 0.559 | — | — | all data, no filters |
| + exec filter | e16 | 0.612 | — | — | data filtering works |
| Certified + plain | e22 | 0.730 | — | — | pre-RFT champion |
| + RFT round 1 | e24 | 0.827 | 0.912 | 0.452 | first champion |
| Seed replicate | e34 | 0.803 | 0.910 | — | noise bar ±0.04 |
| Strict tier, 6k steps | e40 | 0.807 | **0.920** | 0.487 | best served single model |
| Real-adapt stage | e50 | 0.854 | 0.921 | 0.484 | best 96-pool single |
| + real tier round 3 | e51 | 0.797 | 0.917 | 0.509 | first real-tier win |
| **Deployed generator** | e55 | 0.783 | 0.909 | 0.533 / 0.539 | draftwright-0.4.23 |
| + DeepCAD 277k rows | e58 | — | 0.914 | 0.504 | inert tier |
| + long-program tier | e60 | — | 0.914 | — | flat |

Full 55-run ledger: `results/figures/history.json`.

### Real bench (143-part permissive bench, start = e55 vote pick 0.537)

| System | Mean IoU | Δ vs baseline |
|---|---|---|
| e55 vote pick (baseline) | 0.537 | — |
| RP1 · gated, 1 round | 0.577 | +0.040 |
| DeepSeek loop · 6 rounds | 0.606 | +0.070 |
| RP2 · gated, 1 round | 0.612 | +0.076 |
| RP2 · K8 × 3 rounds | 0.625 | +0.089 |
| RP2 · K16 × 5 rounds | 0.644 | +0.107 |
| RP3 · K8 × 3 rounds | 0.631 | +0.094 |
| RP3 · K16 × 6 rounds | 0.667 | +0.131 |
| **Multi-start RP3 · 3 chains** | **0.695** | **+0.159** |

- e55's own best-of-8 oracle: 0.591 — the repair system beats the generator's ceiling;
  oracle over the 3 chain finals: 0.721 (remaining headroom).
- By family: Fusion 0.567 → 0.757, ABC 0.487 → 0.598.
- Held-out synthesized families: 0.362 → 0.461 (out-of-sample for the margin choice).
- In-distribution, the gated repair is provably safe: 0.925 → 0.929.

### Real-part verifier (selection lever)

On the 146-part bench with e51 candidates at K=32: consistency vote 0.527 / 17% vs
v3b-EV verifier argmax **0.578 / 23%** (oracle 0.639). A verifier at 8 draws beats the
vote at 32. Serving uses the agreement gate: vote on parts the generator agrees on,
verifier on the rest.

## 5. Closed routes (negative results, all measured)

| Route | Evidence | Verdict |
|---|---|---|
| Bigger model, same recipe | Flash-Next 180B: e26/e32/e35 | 0.78–0.83 vs 27B 0.844 — scale not the lever |
| Stricter RFT acceptance (≥0.9/0.95) | e36/e38/e41 | ≤ champion; halves the pool, buys no geometry |
| Selector variants beyond the medoid | offline sweep, 1,030 parts | all within ±0.005; learned selector ties |
| Real-part RFT tiers, rounds 1–2 | e46–e50 | first-exec +0.02–0.04, vote/ceiling flat |
| Hub teacher (Kimi-K3) | 60-part pilot | 6% key acceptance — dropped |
| Privileged hints / feedback | gt_feedback passes | +1.2 pts acceptance, no serving effect |
| ABC ground-truth-code tier | e54 | flat |
| DeepCAD 87k-part tier | e58 | inert on real parts |
| Long-program tier | e60 | flat — length ceiling traced to RFT |
| Family-synthesis GT (think / no-think) | H6b–H6d | ≤ e55; both routes closed |
| DeepSeek generator (think-LoRA) | 2-node run | 0.208 vs vanilla 0.299 (−0.091) |
| DeepSeek repairer LoRA | rep_r32, merged FP8 | +0.000 gated vs RP2's +0.076 |
| Zero-shot repair (untrained) | vis vs blind arms | net hurts; render input +0.11 but training required |
| **DeepSeek self-training (own samples)** | `dsv41_selftrain_r32`, 125 steps, eval 2026-10-01 | **0.301 vs vanilla 0.299 (+0.002 [−0.038,+0.039]) — neutral** |

The self-training result closes the DeepSeek campaign: rejection sampling on
DeepSeek's own outputs (10,148 samples on 5,074 parts → 492 rows / 369 parts at
IoU ≥ 0.8, trained with exact banded attention for 32k-token rows) left it
statistically unchanged — slightly better exec (123 vs 120) and more ≥ 0.8 parts
(20 vs 16), Fusion +0.020 vs ABC −0.027, shorter reasoning (median 33.5k vs 37k
tokens), but no mean gain.

## 6. Diagnosis and limitations

- The real-part gap is **shape vocabulary** (real design idiom — bowed strips,
  multi-lug brackets, ring/boss stacks — that the synthetic families never compose),
  not resolution, dimensions, thinness, search budget, or surface types
  (face-census evidence; `results/firstprinciples/`).
- Real-part RFT data helps only at ~1k-part scale (e51) and moves the ceiling,
  not the vote.
- **Documented failure mode** (paper limitation): a real customer SolidWorks sheet
  (inch dimensions, black ink, heavy notes, 3 sheets) breaks both the model
  (IoU 0.03–0.05) and the colour-based v3 gate, which never fires on all-black
  sheets. The same part rendered by draftwright scores 0.915 — the failure is sheet
  style, not part difficulty (`test_part.pdf` case).

## 7. What this gives the paper

1. **A task and benchmark**: drawing → parametric CAD code with executable evaluation
   (exact volumetric IoU), 1,030-part in-distribution pool + 146-part external real
   bench + 200-part held-out family check.
2. **A training recipe** (verified-data flywheel, 60/20/20) that took a 27B VLM from
   0.56 to 0.85 single-shot — with the negative result that a 6.7× larger model bought
   less than RFT rounds or best-of-N serving.
3. **Label-free selection**: consistency medoid (62% of oracle headroom, no trained
   components) and the agreement-gated verifier (real-part selection lever).
4. **Closed-loop visual repair** as the headline test-time result: 0.537 → 0.695 on
   real parts, above the generator's best-of-8 oracle (0.591), with a label-free
   render-compare acceptance gate; safe in-distribution (+0.004).
5. **An honest OOD analysis**: the gap is shape vocabulary, not scale or surface
   types; plus the style-gap limitation on real customer sheets.

## 8. Current state and next steps

- Best deployed system: **e55 generator → best-of-8 consistency vote (agreement gate
  0.85 → v3b-EV verifier) → rp3 repair loop (K=16 × up to 6 rounds) with render-compare
  v3 gate → multi-start across 3 chains = 0.695 real bench, 0.91/82% in-distribution.**
- The DeepSeek-V4.1-Flash campaign is fully closed (generator LoRA, repairer LoRA,
  joint adapter, and self-training all ≤ vanilla or neutral). Zero-shot with brief
  reasoning (0.308) matches e55's first draw on ABC but trails on Fusion; it remains a
  possible diverse draft source, not a replacement.
- Remaining headroom is concentrated in: chain count / final selection for multi-start
  (oracle 0.721 vs served 0.695), ABC-family repair accuracy (0.598 vs Fusion 0.757),
  and the sheet-style gap (black-ink / inch / multi-sheet drawings).

## Key sources

- Lab notebook: `train_v14/RECIPE.md` (2,052 lines, dated entries 2026-08-27 → 10-01)
- 55-run ledger: `results/figures/history.json`
- Full-pool results: `results/bo8_full_*.json` (+ `_consistency.json`)
- External bench: `results/ext/` (incl. `probe_selftrain_r32_t07_uncapped.json`)
- Repair era: `results/repair/`, `results/visrepair/`
- Mechanism studies: `train_v14/mech/{constraints,ambiguity,selfcheck,benchmarks}/RESULTS.md`,
  `results/firstprinciples/`
- Git: 443 commits, 2026-08-27 → 2026-10-01
