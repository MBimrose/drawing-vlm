# Drawing→build123d fine-tuning recipe (v2, 2026-08-30)

The distilled, model-size-agnostic recipe from the e1–e32 sweep on
Qwen3.8-27B and Qwen3.8-Flash-Next (180B-A6B). Every ingredient here was validated in isolation (run in
parentheses); noise bar from the seed replicate (e18) is ±0.03–0.05 IoU.

## Data (the part that transfers unchanged)

Mixture per sample draw (`build_mixed_v2` in data_v14.py):
- **20% certified reasoning** — sft_manifest_v1 rows only (52k, 5%-volume
  reverse-gate). image → model-native think(plan) → code. (e19: the 1:4
  mixture beat pure-certified e21 on trace val.)
- **60% rejection-sampled (RFT)** — the model's own generations kept only
  at exact-IoU ≥ 0.8 vs GT, with their successful rationales (rft_v1,
  ~40–45% acceptance from an e16-class generator at T=0.6). Regenerate
  this tier with each new champion (STaR rounds).
- **20% plain filtered** — tars_v14 minus: exec-bad GT
  (exec_bad_keys_v14.txt, 21%!), legacy renderer (legacy_keys_v14.txt),
  both eval residues (uuid%50 in {0,7}). (e16: exec filter alone was
  +0.05 IoU, beyond noise.) Do NOT also drop underdetermined sheets:
  e23 tested it and it HURT (0.770 vs 0.834 on the determinate slice) —
  losing 33% of the corpus costs more than the ambiguity it removes.
- Image augmentation: keep or drop — measured no effect (e14 vs e2).
- Frozen eval: manifest eval split (1,072 certified) + STEP-derived GT
  meshes; report pooled AND determinate-slice (24% of eval sheets are
  underdetermined — an eval ceiling, not model error).

## Training (rescale per model size)

- Full FT > LoRA at 27B on identical data (e2 0.559 vs e12 0.508).
- FSDP2 FULL_SHARD, bf16 compute + fp32 master/AdamW, activation
  checkpointing, vision tower FROZEN (unfreezing last-4 didn't help: e7).
- seq 5120, max_pixels 1179648 (tuned: ~11px glyph legibility floor),
  effective batch 64, cosine→10% min LR, warmup 3%.
- LR by size: 27B → 6e-6. Scale ~1/sqrt(params): 35B→5e-6, 70B→3.5e-6.
- Steps: 6000 at batch 64 was still improving at 27B (e13); budget ≥6000.
- Best-only checkpointing: save on val-loss improvement, keep 1
  (EvalLossCallback save_best; FSDP checkpoints must keep optimizer
  state — save_only_model is rejected).
- Serve/eval with the same chat template + enable_thinking; repair loop
  (execute → traceback → regenerate ×2) adds ~+0.04 IoU and +5-8% exec.

## Cluster limits for larger models (measured on ccc0451/74/75)

- One node = 8×H200 (141 GB) ≈ 1.13 TB GPU. Full-FT state cost ≈ 16
  bytes/param sharded + ~30-60 GB/rank working memory.
- **Single-node full FT ceiling: ~45–50B dense.** (27B uses ~90-115
  GB/rank.)
- **~70B dense: memory-feasible only with 3-node FULL_SHARD or CPU
  offload.** Measured 3-node penalty on the 100GbE fabric: 116 s/step vs
  10.4 single-node (no HSDP in accelerate 1.14) — a 70B/3-node run is
  ~4-5 days per 3000 steps. Feasible, painful, correct only for a final
  production run.
- **LoRA/QLoRA on one node reaches 100–235B-class** (frozen bf16 base
  ~2 bytes/param sharded: 235B → ~59 GB/rank + adapters) — but LoRA
  measurably lags full FT on this task; use only if the base model jump
  outweighs the method penalty.
- MoE (e.g. 235B-A22B): full FT infeasible (optimizer states cover ALL
  params); LoRA fine on one node.

## Measured leaderboard (certified 96-pool, repair IoU)

| Run | Model | Recipe | Score |
|-----|-------|--------|-------|
| e24-rft final | 27B | RFT round 1 (60/20/20), 4000 steps | **0.844** |
| e34 final | 27B | e24 recipe, seed 43 (replicate) | 0.803 (73% ≥0.85) |
| e37 final | 27B | e24 recipe + seed, 6000 steps (val flat after 4000) | 0.846 (74% ≥0.85) |
| e39 soup | 27B | uniform weight average of e24 + e34 (no training) | 0.815 / 0.825 (serv-19 / cluster) |
| e28 ckpt-4500 | 27B | RFT v1+v2 (123k), 6000 steps | 0.837 |
| e33 ckpt-3500 | 27B | curated RFT tier (v1+v4+v5hard, 68k), 4000 steps | 0.833 |
| e38 final | 27B | RFT tier v1+v2+v3 at iou≥0.95 (113k), 4000 steps; lowest 4k-step val (0.438) | 0.812 / 0.837 (same weights, serv-19 B300 vs cluster L40S) |
| e36 final | 27B | RFT tier v1 at iou≥0.95 (30.7k), 4000 steps | 0.799 (65% ≥0.85) |
| e41 final | 27B | RFT tier v1+v2+v3 at iou≥0.9 (156k), 4000 steps | 0.808 (69%); full-pool served 0.914 / 82%, first-exec 0.894 |
| e29 ckpt-500 | 27B | continue from e28 on same mix | 0.806 |
| e26-full best | Flash-Next 180B | same recipe, 3000 steps | 0.782 |
| e32-r2 best | Flash-Next 180B | matched compute, lr 6e-6→3e-6 restart | 0.832 |
| e35 best | Flash-Next 180B | continue e32 at lr 8e-7, curated tier, 1500 steps | 0.819 |
| e22 ckpt-3500 | 27B | no RFT (certified+plain) | 0.792 |
| e2 final | 27B | all data, no filters | 0.594 |

Serving policies on identical e24 best-of-8 candidates (2026-08-31):
first-to-execute 0.879 (74% ≥0.85); learned verifier 0.878 (two attempts —
judging correctness from (image, code) is as hard as generating);
**consistency medoid 0.919 (82% ≥0.85, median 0.984)** — pick the candidate
whose mesh agrees most (pairwise volumetric IoU) with the other candidates.
No trained components, no GT at selection; captures ~62% of the oracle
(0.943) headroom. This is the deployable configuration.

## Noise bar (seed replicate e34, 2026-09-01)

Retraining the champion recipe with a different seed gave 0.803 mean repair
IoU vs 0.844 (iou85 73% vs 72%; at matched step 3250 the two runs were
0.801 vs 0.795). Seed-to-seed spread on the 96-part pool is therefore
≈±0.04 on the mean while the ≥0.85 fraction is stable. The same e38 weights
scored 0.812 on serv-19 and 0.837 on the cluster (hardware-level numerical
differences change greedy decodes), so even one model re-evaluated is ±0.025 — every 27B result in
the 0.80–0.84 band (e28, e32, e33, e34) is one cluster, and single-run
differences under ~0.05 are not decisions. The 1,030-part full-pool eval
(running on serv-19) is what separates them.

## Scale is not the lever (measured, 2026-08-30)

A full fine-tune of the 180B-A6B Flash-Next on the identical recipe scored
0.782 vs the 27B's 0.844, despite better zero-shot drawing reading and a
competitive val loss (0.4383 vs 0.4355). It was undertrained (24k samples
vs 32–48k) — e32 retested at matched compute (0.832) and e35 polished it
further at a properly scaled LR on the curated tier (val 0.4381, the
lowest Flash-Next val ever, yet 0.819 repair IoU) — but the ordering is
unambiguous: **verified self-generated data (RFT) and best-of-N serving
each bought more IoU than a 6.7× parameter increase.**

Practical consequences:
1. Spend GPU-hours on RFT rounds and candidate reranking before model size.
2. Serve the 27B champion behind best-of-N + repair.
3. Log EVERY scored candidate during RFT (`--log-all`): it is free verifier
   training data (105k candidates fell out of RFT round 3 alone).
4. Overlap generation with execution/IoU scoring in RFT workers (1.44×).

## DeepSeek-V4-Flash-Vision zero-shot smoke (2026-09-01): do not port

Reference runner on serv-19 (fp4 experts, TP8). Thinking mode never produced
code on our drawings — with a 16k window and a 12k-token budget both cases
loop on reconciling dimension lines and never close `</think>`. Chat mode
(T=0.6) executes but reads the geometry wrong: a 2 mm-wall tray became a solid
block (centered IoU 0.35), a 80×60×12 plate became 80×80 with a hallucinated
boss and a 40×40 hole grid instead of 50×30 (IoU 0.46). Full record in
`results/dsv4-zero-shot-smoke.json`. Hand-porting its vision stack into HF for
training is not justified; the 27B recipe stays the production path.

## Full-pool result (1,030 certified parts with GT meshes, 2026-09-02)

The deployed policy re-measured on every eval sheet that has a GT mesh (8
single-GPU workers on serv-19, ~3 h generation + 6 h reranking):

| Policy | 96-pool | 1,030-pool |
|---|---|---|
| Greedy single shot (oracle@1) | 0.819 | 0.793 |
| First-to-execute of 8 | 0.879 (74% ≥0.85) | 0.878 (73% ≥0.85) |
| **Consistency medoid of 8** | **0.919 (82%)** | **0.912 (81%, median 0.974, 97% ≥0.5)** |
| Oracle of 8 | 0.936 | 0.942 |

The 96-part pool was representative to within 0.01 on every policy. Files:
`results/bo8_full_e24.json` (all 8,240 candidates) and
`results/bo8_full_consistency.json`.

Seed robustness under serving: the e34 replicate, 0.803 single-shot vs the
champion's 0.844, scores 0.906 (84% ≥0.85) on the 96-pool and **0.910 (80%,
median 0.971) on the full 1,030-pool** with best-of-8 + consistency, vs
0.919 / 0.912 for the champion. The deployed policy is seed-invariant to
within 0.002 at full scale (first-exec 0.876 vs 0.878, oracle 0.941 vs 0.942);
the 0.04 single-shot seed gap is noise the vote removes.

Determinate slice (uuids with no unplaced dimension in any render, 788/1,030):
first-to-execute 0.892 (77% ≥0.85), oracle@8 0.951 (91%); the 242
underdetermined sheets score 0.831 / 0.913 — the ambiguity ceiling is real
but the policy still recovers 82% of them to ≥0.85 at oracle.

Sampling temperature for best-of-8 + consistency (champion, 96-pool, 2026-09-02):

| T | first-exec | consistency | oracle@8 |
|---|---|---|---|
| 0.5 | 0.868 | 0.897 (80% ≥0.85) | 0.936 |
| 0.7 | 0.879 | **0.919 (82%)** | 0.936 |
| 1.0 | 0.885 | 0.917 (81%) | 0.945 |

Diversity helps the oracle monotonically but the medoid plateaus from 0.7 up;
too little diversity (0.5) costs 0.02. Keep T=0.7.

Cross-seed union (e24 ∪ e34, 16 candidates, 96-pool, 2026-09-02): consistency
0.918 (84% ≥0.85, median 0.985) vs 0.919 / 82% for e24's own 8 — the medoid
does not improve, while the oracle rises 0.936 → 0.953 (93% ≥0.85). Model
diversity raises the ceiling, not the vote; two models at 2× cost are not
worth it for serving. The remaining headroom (0.918 → 0.953) is in selection.

## Acceptance threshold is not the lever either (2026-09-02)

Filtering the RFT tier at iou≥0.95 instead of 0.8 scored 0.799 on round-1
data alone (e36, 30.7k) and 0.812 across rounds 1-3 (e38, 113k) vs 0.844 for
the champion's 60k at ≥0.8. Stricter acceptance halves the pool without
buying geometry; e38's lowest-ever 4k-step val loss (0.438) did not transfer.
The 0.8 threshold on one generator round remains the recipe. Longer training
(e37, 6000 steps) did not move val after step 4000 and scored 0.846 — equal to
the champion within noise; 4000 steps is sufficient.

Determinate slice under the deployed policy (e34 replicate, full pool, per-part
selections): consistency medoid **0.925 (84% ≥0.85)** on the 788 determinate
sheets vs 0.863 (69%) on the 242 underdetermined ones; oracle 0.949 vs 0.914.
On fully specified drawings the served system is within 0.024 of its own
best-of-8 ceiling.

## Selector sweep on stored agreement matrices (full pool, 2026-09-02)

`consistency_rerank` now persists every part's 8×8 pairwise-IoU matrix, so
selectors are evaluated offline in seconds (`results/bo8_full_e24_consistency_v2.json`):

| selector | mean | ≥0.85 |
|---|---|---|
| first-to-execute | 0.878 | 73% |
| **medoid, mean agreement (deployed)** | **0.912** | **82%** |
| medoid, squared weights | 0.912 | 82% |
| medoid, ^4 weights | 0.911 | 82% |
| top-3 / top-2 agreement | 0.911 / 0.908 | 81% / 81% |
| largest cluster at τ=0.80 / 0.90 / 0.95, then medoid | 0.908 / 0.905 / 0.904 | 81% / 80% / 79% |
| oracle | 0.942 | 89% |

Every reweighting or clustering variant is within ±0.005 of the plain medoid;
the remaining 0.03 to the oracle is not recoverable from agreement structure
alone. A learned selector on serving-time features (agreement, max pair IoU,
greedy flag, voter count, rank; 5-fold CV by part) ties the medoid exactly
(logistic 0.912) and boosted trees overfit (0.903-0.909).
Repairing individual failed candidates before the vote is also capped
low: only 5/1,030 parts have no executing candidate and 88% already have ≥5
voters. The 11% of parts with no candidate ≥0.85 are a generation problem.

Full-pool serving scores, three champion-recipe models (best-of-8 + consistency, 1,030 parts):

| model | single-shot 96 | first-exec | consistency | oracle@8 |
|---|---|---|---|---|
| e24 (seed 42, 4000 steps) | 0.844 | 0.878 | 0.912 (81%) | 0.942 |
| e34 (seed 43) | 0.803 | 0.876 | 0.910 (80%) | 0.941 |
| e37 (seed 42, 6000 steps) | 0.846 | 0.885 | **0.914 (82%)** | 0.945 |
| e41 (RFT tier v1+v2+v3 at iou≥0.9, 156k) | 0.808 | **0.894 (77%)** | **0.914 (82%)** | **0.946 (91%)** |

The served number is 0.910-0.914 regardless of seed or schedule: the recipe
is reproducible, and the 96-pool single-shot spread (0.80-0.85) is noise.

## Agreement is a confidence signal (full pool, 2026-09-02)

The medoid's mean agreement with the other candidates predicts whether the
served part is right (AUROC 0.872 for "served IoU < 0.85"). Unsolved parts
(no candidate ≥0.85, 11%) have mean candidate agreement 0.66 vs 0.89 for
solved ones; 38% of them are underdetermined sheets (base rate 23%), the rest
are genuine model failures with a median oracle of 0.74.

Selective serving — flag parts whose medoid agreement is below τ for review:

| τ | flagged | precision (flagged is wrong) | recall of failures | unflagged mean IoU | unflagged ≥0.85 |
|---|---|---|---|---|---|
| 0.70 | 8% | 0.74 | 0.33 | 0.936 | 86% |
| 0.80 | 16% | 0.64 | 0.55 | 0.948 | 90% |
| 0.90 | 35% | 0.46 | 0.86 | 0.968 | 96% |

No extra compute: the agreement matrix is already computed for the vote.

Adaptive K (simulated on the stored K=16 candidates, 96-pool): drawing 8 more
candidates only when the medoid's agreement is below τ gains ≤0.004 (τ=0.9,
35% of parts re-drawn) — no better than K=16 for everyone (+0.007). Low
agreement flags a hard part; more samples of the same model do not fix it.

## Mechanism sweep (agents, 2026-09-03) — three closed, one changes the story

Details in train_v14/mech/<name>/RESULTS.md.

- **Constraints before code** (extract a dimension list, generate against it,
  verify envelope/holes, repair): NEGATIVE. Same 96 parts, same job: base
  greedy+repair 0.846 (72%) → two-stage 0.785 (64%), repair rounds inert.
  Stage A emits valid JSON 94/96 but reads no better than the generator builds;
  a wrong list costs −0.12. Offline, gating the vote on envelope agreement
  scores 0.908 vs 0.912: the model misreads envelopes by consensus.
- **Ambiguity-aware handling of underdetermined sheets**: NEGATIVE, with a
  measured ceiling. The model already resolves the dropped dimension (modal
  extent = GT in 86% of env-axis parts; vote takes the mode 98%). The
  oracle−vote gap on those sheets is 85% ordinary feature misreads; half of the
  determinate/underdetermined deficit is sheet crowding (10.1 vs 6.5 dims).
  Convention prompt: medoid −0.002 at K=4; extent-invariant voting −0.002 to
  −0.009. Upper bound of any ambiguity fix on the full pool: +0.004.
- **Visual self-check** (render the served part back to a sheet, ask the model
  to compare and revise): first 20 parts with a fallback renderer showed the
  model declaring "matches" and one harmful revision; rerun with the real
  renderer pending.
- **External benchmark — real geometry, our drawings**: 146 human-designed
  single-body parts (CADBench medium tiers of Fusion 360 Gallery + ABC,
  ≤80 analytic faces, rescaled to 80 mm) rendered through the vendored
  draftwright engine into our exact sheet format. Champion, best-of-8:
  **first-exec 0.398 (10% ≥0.85), vote 0.452 (14%), oracle 0.534 (16%)** vs
  0.878 / 0.912 / 0.942 in-distribution. Determinate slice 0.466 / 0.526 / 0.619;
  Fusion 0.416 / 0.478 / 0.566, ABC 0.371 / 0.413 / 0.486. Frame diagnostic: the
  best of 24 axis-aligned rotations lifts the oracle only 0.537 → 0.549 and the
  pred/GT scale ratio is centred on 1.00 — dimensions are read at the right
  scale, the shapes are wrong (bowed strips, multi-lug brackets, ring/boss
  stacks: idioms the synthetic families never produce).
  Controls: 48 in-distribution parts re-rendered through the same engine score
  0.889 / 0.911 / 0.942 (renderer and launcher reproduce the stored chain);
  projection angle and sheet variant have no effect. Failure correlates with
  low fill ratio (<0.3: oracle 0.37), many cylindrical faces, fillets, and
  crowded sheets. The synthetic parts are ADSKAILab/Zero-To-CAD-1m; the model
  does not generalise from those families to real parts even in our own
  drawing format. This gap (−0.4) dwarfs every recipe lever (±0.03): the next
  data investment is a real-geometry training tier (CADBench medium tiers give
  ~1,600 STEP parts per family; code via CADFit-style mesh→program recovery or
  RFT against the STEP mesh; hold out these 146).
