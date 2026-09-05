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
| e42 (40% certified / 40% RFT v1 / 20% plain) | 0.825 | 0.883 (74%) | 0.909 (80%) | 0.942 (89%) |
| e38 (RFT tier v1+v2+v3 at iou≥0.95, 113k, 4000 steps) | 0.812 / 0.837 | 0.889 (76%) | 0.912 (82%) | 0.943 (90%) |
| e43 (RFT tier = champion-generated rft_v3 at ≥0.8, one sample/part, 55.6k) | 0.816 | 0.881 (74%) | 0.912 (81%) | 0.937 (88%) |
| e44 (RFT tier v1 at iou≥0.9, 42.8k, 4000 steps) | — | 0.886 (76%) | 0.913 (81%) | 0.941 (88%) |
| e45 = e41 recipe, seed 43 | — | 0.897 (78%) | **0.921 (83%)** | 0.944 (89%) |
| e46 = champion recipe + real tier ×6 | 0.841 | 0.878 (73%) | 0.913 (81%) | 0.945 (89%) |
| e47 = e40 recipe (strict, 6000 steps) + real tier ×11 | 0.795 | **0.901 (79%)** | 0.920 (83%) | **0.950 (91%)** |
| e50 = e45 final + 800 steps at 2e-6 on a half-real mix | — | 0.894 (77%) | 0.921 (83%) | 0.948 (91%) |
| e48 = e45 recipe + union2 tier ×11 | — | 0.886 (76%) | 0.912 (81%) | 0.944 (90%) |
| e49 = champion recipe + union2 tier ×15 | — | 0.889 (74%) | 0.911 (81%) | 0.946 (90%) |
| **e51 = e45 recipe + union3 real tier (968 parts) ×5** | — | 0.894 (76%) | **0.917 (82%)** | 0.947 (90%) |
| **e40 (RFT tier v1+v2+v3 at iou≥0.95, 113k, 6000 steps)** | 0.817 | **0.899 (79%)** | **0.920 (84%, median 0.981)** | **0.947 (90%)** |

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
- **Visual self-check** (render the served part back through the real
  draftwright engine, show the model both sheets and its script, ask it to
  compare and revise): NULL. Same 96 parts: served 0.9231 → 0.9230 under every
  acceptance policy; 0 parts improved or worsened by >0.05; 10/96 scripts
  changed, all cosmetic. On 9 of the 15 failing parts the wrong envelope or
  volume was printed on the rendered sheet and the script came back unchanged.
  0/96 reasoning traces mention the render: the RFT'd model has collapsed onto
  drawing → plan → code and ignores a second image. Revisiting it needs
  training pairs (sheet, sheet-of-wrong-candidate, wrong script → GT) or a
  numeric dimension diff as text, which the repair loop does act on.
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

Three-model union at full scale (e24 ∪ e34 ∪ e37, 24 candidates per part,
1,030 parts): consistency **0.922 (83% ≥0.85, median 0.980)**, oracle 0.960
(93%), vs 0.914 / 0.946 for the best single model. The cross-model vote is
worth +0.008 on the full pool (the 96-pool two-model union showed nothing,
which was noise). At 3× serving cost it is the highest served number measured;
the single-model best-of-8 remains the cost-efficient deployment.

Strict-tier models serve better than they shoot (2026-09-03): e38/e40/e41
(acceptance ≥0.9-0.95 across rounds) scored 0.80-0.84 single-shot on the 96
pool — indistinguishable from or below the champion — yet on the full pool
under best-of-8 + consistency they are the best models measured: e40 0.920
(84%), e41 0.914 (82%), vs e24 0.912 (81%), e37 0.914, e34 0.910, e42 0.909.
Their first-to-execute (0.889-0.899 vs 0.878) and oracle (0.943-0.947 vs
0.942) are also higher, i.e. the per-candidate distribution is sharper even
though the greedy single shot is not. Single-shot eval would have discarded
all three. Decomposition: e38 (strict tier, 4000 steps) votes 0.912 = champion,
so the tier alone buys first-exec (+0.011) not the vote; e37 (plain tier, 6000
steps) votes 0.914; e40 (strict tier + 6000 steps) 0.920. The combination is
worth ≈+0.008 on the served number — small, but it is the only training-side
gain measured, and it is invisible to single-shot eval.

## Frame sensitivity of the metric (2026-09-03)

The headline IoU centres both meshes (bbox centre → origin) and applies no
rotation, reflection or scale, because the drawing dictates orientation and
size. Measured on the 96-pool's 678 executing candidates
(train_v14/geom/align_study.py, results/align_study_96.json):

| best candidate per part | mean | ≥0.85 |
|---|---|---|
| centered (metric) | 0.953 | 94% |
| best of 24 proper rotations | 0.955 | 94% |
| best of 48 (+ reflections) | 0.955 | 94% |
| rotation + bbox rescale | 0.961 | 95% |

Orientation errors are rare (1.5% of candidates gain >0.05 under rotation;
0.7% >0.2); reflections never matter; scale/dimension errors are commoner
(10% of candidates gain >0.05 under rescale) but are genuine reading errors
and must stay penalised. On the external real-part bench the rotation search
lifts the ceiling by 0.012 (0.537 → 0.549). Verdict: a rigid-alignment
scorer would move in-distribution numbers by ≤0.004 and is not adopted for the
headline; it is useful only as a frame-vs-shape diagnostic.

Rigid ICP alignment (wpklab/meshalign, tuned profile, exact IoU after the
returned transform; results/align_study_meshalign_96.json): per-part best
0.953 → 0.963 (94% → 96% ≥0.85); per-candidate +0.017. Decomposition: 90% of
candidates get a pure translation (median 0, p90 0.25 mm; the 40 shifted by
>1 mm gain >0.05 in 75% — bbox-centre offsets from a missing/extra feature),
9% get a ≥90° yaw (38% of those gain >0.05 — orientation errors forgiven),
1% a small tilt. The gain lands on WRONG reconstructions (centered <0.5:
+0.11; 0.5-0.85: +0.065) while good ones lose slightly (0.85-0.95: −0.012)
because the aligner optimises surface distance, not volume overlap. Verdict:
rigid alignment inflates partial reconstructions and forgives flips; the
centered metric stays the headline. In the VOTE it is worse: a rigid-aligned
agreement matrix (strict scoring, selection only) serves 0.914 vs 0.923 on the
same 96 parts — selection changed on 15 parts, 5 worse / 1 better — because
aligning wrong candidates onto each other inflates their mutual agreement
(results/vote_study_meshalign_96.json). meshalign is not adopted anywhere in
the pipeline; it remains the frame-vs-shape diagnostic.
Volume-centroid centering (translation-only alternative to the bbox centre,
results/centroid_study_96.json): per-candidate −0.014, 30% of candidates lose
>0.02 (0.85-0.95 band: −0.041) — a missing feature moves the mass centre while
the envelope stays. bbox centering is the correct translation for this task.

## Real-geometry rejection-sampling round 1 (2026-09-03)

Corpus: 1,527 human-designed single-body parts (CADBench medium tiers: 739
Fusion 360, 562 ABC, 226 ABC sketch-extrude; ≤80 analytic faces, rescaled to
80 mm, the 146 held-out bench parts excluded), rendered through the vendored
draftwright engine into our sheet format (48% underdetermined). Generator:
e40, K=8, T=0.7 on serv-19 (12,195 candidates with code, 2.5 h).

| family | parts | exec | keys ≥0.8 | keys ≥0.9 | ceiling@8 mean / ≥0.85 |
|---|---|---|---|---|---|
| Fusion 360 | 739 | 72% | 210 (28%) | 107 | 0.572 / 21% |
| ABC | 562 | 65% | 76 (14%) | 23 | 0.488 / 9% |
| ABC sketch-extrude | 226 | 74% | 19 (8%) | 5 | 0.450 / 5% |
| total | 1,527 | 70% | **305 (20%)** | 135 | 0.530 / 15% |

Tier `rft_real/` (accepted-000.jsonl: 1,022 rows over 305 keys with the
model's own think text; scored-000.jsonl: all 12,195). Packed with
pack_rft_shards_dir.py (PNGs from rft_real/png). Mixes by shard repetition
(build_rft_mix.sh): rft_mix_real_v1 = rft_v1 (31 shards) + real ×6 (≈16% of
RFT draws), rft_mix_real_strict = rft_strict_all (57) + real ×11. Runs:
e46 (champion recipe + real), e47 (e40 recipe + real). Judged on the 146
held-out real parts (bo8_ext_cluster.sbatch) and the in-distribution full pool.
Second generator pass with e45 (K=8, T=0.7, 2.5 h): 298 keys at ≥0.8 (1,051
rows). Union with e40's set: **358 keys** (237 Fusion, 95 ABC, 26 sketch-extrude;
53 solved only by e45, 60 only by e40). Packed as `rft_real_union/`; mixes
rft_mix_union_v1 / rft_mix_union_strict for round 2.
K=16 extension of e40 on corpus 1: 355 keys (+50 over K=8). Corpus 2 (CADBench
DeepCAD medium+hard 1,530 + Fusion hard 154 at ≤120 faces; ABC hard tiers are
all >120 faces): e40 K=8 solved **586 keys** (DeepCAD 37% yield, ceiling@8
0.652; Fusion hard 16%). Round-3 tier `rft_real_union3/` = union2 ∪ corpus 2
(≈968 keys, ≈5,200 rows); mixes rft_mix_u3_strict90 (×5) and rft_mix_u3_v1 (×3)
give the real tier ≈25% of RFT draws.

External bench baselines by model (146 held-out real parts, best-of-8, strict metric):

| model | first-exec | vote | ceiling@8 |
|---|---|---|---|
| e24 champion (serv-19) | 0.398 / 10% | 0.452 / 14% | 0.534 / 16% |
| e40 strict tier, 6000 steps (H200) | 0.440 / 12% | 0.487 / 17% | 0.554 / 20% |
| e41 threshold 0.9, all rounds (H200) | 0.443 / 13% | 0.485 / 16% | 0.563 / 22% |
| e44 threshold 0.9, round 1 only (H200) | 0.434 / 12% | 0.495 / 16% | 0.550 / 20% |
| e45 = e41 seed 43 (H200) | 0.438 / 12% | 0.499 / 16% | 0.555 / 21% |
| **e46 = champion recipe + real tier ×6 (H200)** | 0.423 / 9% | 0.473 / 14% | 0.549 / 19% |
| e47 = e40 recipe + real tier ×11 (H200) | 0.446 / 12% | 0.484 / 17% | 0.556 / 21% |
| e48 = e45 recipe + union2 tier (382 parts) ×11 (H200) | 0.475 / 15% | 0.491 / 16% | 0.560 / 18% |
| e50 = e45 final + 800 steps on a half-real mix (H200) | 0.457 / 12% | 0.484 / 13% | 0.556 / 19% |
| e49 = champion recipe + union2 tier ×15 (~33% of RFT draws) (H200) | 0.418 / 14% | 0.470 / 14% | 0.551 / 21% |
| **e51 = e45 recipe + union3 tier (968 parts incl. DeepCAD) ×5 (H200)** | 0.483 / 13% | **0.509 / 16%** | **0.594 / 22%** |

The strict-threshold models transfer slightly better (+0.03-0.04 on the vote,
consistent across e40/e41/e44/e45). Round-1 real tier in the champion recipe
(e46): +0.02 on the vote, +0.025 first-exec — real but smaller than the
threshold effect; 305 parts at ~10% of draws is too little signal. On the
strict recipe (e47) the same tier is inert: 0.484 vs e40's 0.487. Round 1
verdict: the tier must be an order of magnitude larger (rounds 2/3).

Family summary after ten full-pool runs (2026-09-04): champion-recipe models
(e24, e34, e37, e42, e43) vote 0.909-0.914 (mean 0.911), first-exec
0.878-0.885; strict-threshold models (e38, e40, e41, e44, e45) vote
0.912-0.921 (mean 0.916), first-exec 0.886-0.899. Seed spread on the vote is
≈0.007 (e41 0.914 vs e45 0.921). The strict tier is a real but small lever:
+0.005 on the vote, +0.012 on first-exec, and +0.04 on real-part transfer.

Real-tier rounds 1-2 verdict (2026-09-05): every variant (champion recipe
+tier, strict recipe +tier, 382-part tier ×11, half-real adaptation stage)
raises first-exec on real parts by 0.02-0.04 and leaves the vote (0.47-0.49)
and the ceiling (0.55-0.56) flat. The tier makes the model more consistent on
parts it could already solve; it does not add solvable parts. Round 3 (e51,
968 parts incl. DeepCAD) tests whether 2.5× more real data changes that.

Round 3 result (2026-09-05): e51 is the first variant that moves the ceiling:
vote 0.509 (best so far, +0.01 over e45), first-exec 0.483 (+0.045), ceiling
0.594 / 22% (+0.03-0.04 over every earlier model, whose ceilings sat at
0.53-0.56). Gains are on the determinate slice (vote 0.597, ceiling 0.676) and
on ABC determinate (ceiling 0.670 vs ~0.60); the underdetermined slice is flat
(0.40 / 0.49). So real-part data does add solvable parts once the tier is ~1k
parts with DeepCAD-style topology. The 146-part bench has more seed noise than
the full pool (±0.02 on the vote), so treat the vote as "at least equal", the
ceiling as a real shift. Full pool (1,030): vote 0.917 / 82%, first-exec 0.894, ceiling 0.947 — strict-family parity, no in-distribution cost. **e51 is the serving candidate: best real-part transfer at equal in-distribution accuracy.**

### Supervision the model cannot self-generate (2026-09-05)

Unsolved set: 2,243 corpus parts (1,145 corpus 1, 1,098 corpus 2) that no
pass reached at IoU >= 0.8; every one has an executing prior candidate
(`unsolved_seeds.json`, best of up to 32 draws: mean 0.49, median 0.51, 804
keys between 0.6 and 0.8).

- **Hub teacher (Kimi-K3 via the lab router).** Only multimodal model on the
  hub (glm-5.3 rejects images). ~15k output tokens per drawing, the router
  serialises requests: ~13 answers/hour at concurrency 6 → a 2k-part round
  would take weeks. Quality on a 60-part pilot: first 19 answers 0 accepted;
  extents match the reference exactly (it reads dimensions) but volumes are
  off 30-70% (internal features wrong); rotation search does not rescue them
  (rescore_rot.py). Dropped as a tier source.
- **Privileged feedback as a repair turn (gt_feedback_gen.py --mode feedback).**
  Show the model its best script + measurements against the reference (volume
  ratio, extents, IoU, solids, octant material diff) and ask for a fix: 6 of 8
  samples were byte-identical copies of the seed, the rest ±0.01. The RFT'd
  model treats any second turn as "re-emit the script". Useless.
- **Privileged hints in the first turn (--mode hint).** Reference bbox, volume
  / fill ratio, solid count, centre-of-mass offset, per-octant material
  fractions appended to the user prompt; 4 draws at T=0.7 on 16 keys per
  corpus. Corpus 1: best-of-4 mean 0.476 (seeds 0.621), 0 accepted → gate
  stopped the job. Corpus 2 (DeepCAD): 0.557 vs 0.559, 1 accepted → full run
  (8 draws/key, e51) in progress alongside a no-hint control (`--mode plain`,
  same keys/draws) to separate "hints help" from "more draws help".
  Result at equal draws (4 per key, all 1,098 corpus-2 keys, e51): hinted 9.2%
  accepted / best-IoU mean 0.497 vs plain 8.0% / 0.487. Hints are a small lever
  (+1.2 points absolute); the bigger effect is the generator: e51 solves 8-9% of
  the parts that e40/e45 never solved in 32 draws (corpus 1: 1.8% — the
  Fusion/ABC unsolved set is hard for everyone). Both runs yield valid
  drawing→code pairs; hinted think texts read as normal drawing plans, rows
  whose think cites hint-only quantities (mm^3, octant, centre of mass, fill
  fraction) are dropped at packing.
