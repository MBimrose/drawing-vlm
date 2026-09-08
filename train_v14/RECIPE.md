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
| e52 = e45 recipe + union4 real tier (1,177 parts) ×5 | — | 0.893 (76%) | 0.913 (82%) | 0.942 (89%) |
| e53 = e45 recipe + union5 real tier (1,960 parts, real ≈24% of draws) ×5 | — | 0.891 (77%) | 0.919 (82%) | 0.944 (89%) |
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
| e52 = e45 recipe + union4 tier (1,177 parts: union3 + 209 formerly-unsolved) ×5 (H200) | 0.485 / 14% | 0.510 / 17% | 0.587 / 25% |
| e53 = e45 recipe + union5 tier (1,960 parts incl. 762 easy-tier) ×5, real ≈24% of draws (H200) | 0.472 / 14% | 0.503 / 18% | 0.581 / 22% |

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
  would take weeks. 60-part pilot (7 h): 79 answers on 47 keys, 41 router
  errors, 3 keys accepted (6% of keys, mean IoU 0.25) vs 2.8% for e51 plain on
  the same corpus-1 unsolved set;
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

Round 4 tier `rft_real_union4/` (2026-09-05): union3 ∪ e51 passes on the
unsolved set (corpus 2 hinted 139 keys / plain 121 keys, corpus 1 plain ~25
keys at 8 draws) = **1,177 keys, 5,521 rows** (+209 keys over union3; 13
hint-leaking rows dropped). Same 3-shard ×5 mix as e51 (`rft_mix_u4_strict90`,
78 base + 15 links) → **e52** (e45 recipe, seed 43, 4000 steps, ccc0475);
shipper set for the 146-part bench + full pool. Question: does +22% more real
parts (all from the previously-unsolved set) move the ceiling again.

K-scaling on real parts (e45, 146 held-out, 2026-09-05): K=8 → K=32 lifts the
best-of-K ceiling 0.555 / 21% → **0.612 / 25%** (determinate 0.690 / 38%) but
the served vote only 0.499 → 0.512 / 17% and first-exec is unchanged (0.451 vs
0.438, noise). So the generator can reach ~5 points more of the real parts with
4× the draws, and the medoid vote does not cash it in: on real parts the
correct candidate is usually an outlier among 32, not the centre. Picking it
needs a real verifier or an executable check, not more agreement.
(results/ext/bo32_ext_e45-rft-strict90-all-s43_summary.txt)

Corpus 3 (2026-09-05): the CADBench **easy** tiers (F 269 / A 678 / E 546 =
1,493 parts after the ≤120-face prep; median 10 faces; 30% flagged
underdetermined; one part segfaults the renderer). e51 K=8 solves **762 keys
(51%)** at ≥0.8 — A 47%, E 54%, F 54%; ceiling@8 0.71-0.75 — versus 20% on
corpus 1. Renderer note: a single segfaulting STEP breaks the shared
ProcessPoolExecutor (1,184 spurious failures); train_v14/mech/benchmarks/
render_isolated.sh renders one process per part.

Round 5 tier `rft_real_union5/`: union4 ∪ corpus 3 ∪ hinted corpus-1 rows =
**1,960 keys, 8,961 rows** (+783 keys); 5 shards ×5 = 25 links on the 78-shard
strict90 base (`rft_mix_u5_strict90`, real ≈24% of RFT draws vs ≈16% for
e51/e52) → **e53** (same recipe). Tests whether easy real parts (simple
topology, high yield) transfer to the medium held-out bench.

Round 4 result (e52, 2026-09-06): vote 0.510 / first-exec 0.485 / ceiling 0.587
— identical to e51. Adding the 209 hardest leftovers of the same corpora (solved
only at 8-32 draws) adds nothing; the tier needs new parts, not deeper mining.
Corpus-1 unsolved set, e51, 8 draws: plain 32 keys (2.8%), hinted 43 keys
(3.8%) — same +1 point as on corpus 2. Hinting is not worth its own pass.
e51 at K=32 (146 real parts): vote **0.527 / 17%**, first-exec 0.470, ceiling
**0.639 / 29%** (determinate 0.711 / 40%) vs e45 at K=32 0.512 / 0.612 — the
round-3 tier's gain (+0.015 vote, +0.027 ceiling) holds at equal draws, so the
reachable set grew, not just the K=8 sample. Real-part progression of the
served vote: champion 0.452 → strict tier 0.499 → round-3 tier 0.509 (K=8) →
0.527 (K=32).

Round 5 result (e53, 2026-09-06): vote 0.503 / first-exec 0.472 / ceiling 0.581
— flat vs e51/e52 (single-shot 96-pool 0.790, within noise). Rounds 3-5 (968 →
1,177 → 1,960 real parts, real share 16 → 24% of RFT draws) all land at vote
0.50-0.51 / ceiling 0.58-0.59 at K=8. **The self-written real tier saturates
at ~1k parts**; easy-tier parts (median 10 faces) do not teach the medium
bench's topology. Remaining headroom on real parts is selection: K=32 ceiling
0.64 vs vote 0.53 (e51). Next: a verifier trained on real-part candidates
(≈40k scored (drawing, script, IoU) triples from the corpus passes), judged
offline on the stored K=32 candidates of the 146 held-out parts.
K=32 on the 146 real parts, by model: e45 0.512 / ceiling 0.612; e51 0.527 /
0.639; **e52 0.536 / 0.645** (determinate 0.630 / 0.719). The real-tier models
gain ~0.02-0.03 on both at equal draws; the e51→e52 step is inside noise.
e53 at K=32: vote 0.531 / 19%, ceiling 0.645 / 26% — e51/e52/e53 are one model
on real parts at any K (vote 0.527-0.536, ceiling 0.639-0.645).

## Real-part verifier (v3) — selection is the real-part lever (2026-09-06)

Question: on the 146 held-out real parts the K=32 ceiling of e51 is 0.639 /
29% while the consistency vote serves 0.527 / 17% and first-to-execute 0.470;
can a verifier trained on real-part candidates pick the outliers the medoid
misses? In-distribution verifiers (v1 regression, v2 binary) never beat the
vote, but there the vote was already at 0.919 vs a 0.943 ceiling.

**Dataset** (`train_v14/geom/pack_scored_real.py`, driver
`pack_scored_real.sh` → `rft_scored_real/shards`, same member layout as
`pack_scored_shards.py`): every scored candidate on the real-part corpora —
corpus-1 best-of-8/16 (e40) and best-of-8 (e45), corpus-2 best-of-8 (e40),
corpus-3 best-of-8 (e51) (merged JSONs copied from serv-19 to
`mech/benchmarks/data/<corpus>/results/`), plus the four gt_feedback_gen
passes (rft_gtfb_c1/c2, rft_plain_c1/c2). PNGs are the corpus sheets
(rsynced `render/png`, one variant per key). 110,168 rows → 95 without code
dropped, 13,332 duplicate scripts per part dropped (the K=16 run shares its
first 8 draws with the K=8 run) → **96,741 candidates over 4,704 parts**;
0 rows on held-out file_ids (verified). Balance: 75.5% execute, **9.4% ≥ 0.8,
6.8% ≥ 0.85**, 1,536 parts have at least one positive — positives-light, so
no subsampling (v1's collapse was on a positives-heavy pool). Split by part
hash: 94,553 train (4,602 parts) / 2,188 eval (102 parts); 13 GB.

**Models** (LoRA r64 on **e51 final**, the serving generator; v2 optimiser
settings, 2500 steps, one H200 node ≈ 8.5 h each):
- `v3-verifier-real` (job 10388737): binary yes/no at IoU ≥ 0.85, ranked by
  logit(yes) − logit(no). Train loss 0.09 → 0.01-0.02 (over the whole
  assistant turn); val/loss on the negatives-dominated eval slice saturates
  at 0.0000 by step 1000 and is useless for checkpoint choice. best_adapter =
  final (step 2500).
- `v3b-verifier-real-reg` (job 10389493): same pool, v1 regression target
  ("0.73" as text). Train loss 0.52 → 0.22-0.28 (0.229 at step 2500);
  val/loss best 0.2816 at step 750 and 0.29-0.35 afterwards, so best_adapter
  = step 750 — yet the final adapter selects slightly better (below):
  val loss does not select verifiers either.

**Scoring** (`train_v14/geom/verifier_select_offline.py`, one GPU, ~10 min
per 3.5k candidates on an H200): the prompt is the exact training text
(VERIFIER_BIN_USER / VERIFIER_USER + the `<think>\n\n</think>\n\n` assistant
prefix the chat template inserts) and the logits are read at the answer
position. `bestofn_verifier_eval.py`'s binary mode scored v2 with the
regression prompt at the `<think>\n` position — a train/serve mismatch; the
`--prompt-mode legacy` switch reproduces it. Regression verifiers are scored
two ways: greedy decode of the number (`reg`, 2-decimal ties broken by draw
order — half of the executing candidates decode to 0.00) and the **expected
value** from one forward pass on prefix + "0." (`reg_ev`: p(first token = 1)
plus the first-decimal digit distribution), which is continuous. Policies on
identical stored candidates, K = first K draws; the vote reuses the stored
pairwise-IoU matrices.

146 held-out real parts, e51 candidates (`results/ext/bo32_ext_e51-…`), mean IoU / share ≥ 0.85:

| selector (K=8 draws) | all | determinate (80) | underdet. (66) |
|---|---|---|---|
| first-exec | 0.463 / 12% | 0.542 / 19% | 0.367 / 5% |
| consistency vote | 0.493 / 14% | 0.569 / 21% | 0.400 / 5% |
| v2 binary (in-dist verifier, e24 base) argmax | 0.498 / 17% | 0.583 / 26% | 0.394 / 6% |
| v3 binary final argmax | 0.505 / 18% | 0.590 / 28% | 0.401 / 8% |
| v3b regression step 750, EV argmax | 0.527 / 18% | 0.611 / 26% | 0.426 / 8% |
| v3b regression final (step 2500), EV argmax | **0.533 / 17%** | **0.614 / 25%** | **0.435 / 8%** |
| v3b final EV, agreement gate 0.7 (vote if medoid agreement ≥ 0.7, else verifier) | 0.519 / 15% | 0.595 / 22% | 0.427 / 6% |
| oracle (ceiling) | 0.573 / 21% | 0.649 / 32% | 0.480 / 8% |

| selector (K=32 draws) | all | determinate (80) | underdet. (66) |
|---|---|---|---|
| first-exec | 0.468 / 12% | 0.552 / 19% | 0.367 / 5% |
| consistency vote | 0.527 / 17% | 0.611 / 26% | 0.424 / 6% |
| v2 binary argmax | 0.511 / 18% | 0.604 / 28% | 0.399 / 8% |
| v3 binary final argmax | 0.527 / 21% | 0.605 / 30% | 0.433 / 9% |
| v3 binary, top-4 then vote | 0.533 / 21% | 0.611 / 28% | — |
| v3b regression step 250, greedy number | 0.542 / 21% | 0.636 / 31% | 0.429 / 8% |
| v3b regression step 250, EV | 0.548 / 20% | 0.640 / 30% | 0.436 / 8% |
| v3b regression step 750, EV argmax | 0.572 / 23% | 0.665 / 35% | 0.458 / 9% |
| v3b step 750 EV, agreement gate 0.7 | 0.553 / 18% | 0.641 / 29% | 0.446 / 5% |
| v3b step 750 EV, top-4 then vote | 0.555 / 18% | 0.642 / 26% | 0.449 / 9% |
| v3b regression final (step 2500), EV argmax | **0.578 / 23%** | **0.669 / 31%** | **0.468 / 12%** |
| v3b final EV, agreement gate 0.7 | 0.562 / 18% | 0.646 / 26% | 0.461 / 8% |
| oracle (ceiling) | 0.639 / 29% | 0.711 / 40% | 0.550 / 15% |

Verifier quality on the executing candidates (K=32, 3,537 candidates, 19.7% ≥ 0.8):

| verifier | Spearman pooled | Spearman per part | AUROC ≥0.8 | AUROC ≥0.85 |
|---|---|---|---|---|
| v2 binary (synthetic pool, e24 base) | 0.709 | 0.273 | 0.900 | 0.902 |
| v3 binary step 250 / 1000 / final | 0.736 / 0.730 / 0.785 | 0.271 / 0.262 / 0.313 | 0.934 / 0.933 / **0.956** | 0.948 / 0.943 / 0.965 |
| v3b regression step 250 greedy / EV | 0.609 / 0.815 | 0.265 / 0.366 | 0.855 / 0.933 | 0.887 / 0.944 |
| v3b regression step 750 EV | **0.874** | **0.475** | 0.954 | 0.959 |
| v3b regression final EV | 0.873 | **0.521** | 0.946 | 0.955 |

Reading: the binary verifiers are the better *classifiers* (AUROC 0.96 at
≥ 0.8, up from 0.90 for the in-distribution v2) but cannot rank the wrong
candidates among themselves (per-part Spearman ≈ 0.3), and 70% of the real
parts have no candidate ≥ 0.85, so their argmax only lifts the ≥ 0.85 share
(17 → 21%) and leaves the mean at the vote. The regression target ranks
(per-part Spearman 0.52) and its expected-value argmax is the first selector
that beats the vote on real parts at every K: **K=32 0.578 / 23% vs 0.527 /
17% (46% of the vote→oracle gap), K=8 0.533 / 17% vs 0.493 / 14% (50%)** — a
verifier at 8 draws beats the vote at 32. Step 750 → 2500 adds +0.006 at both
K (same ≥ 0.85 share), so the checkpoint choice is not critical. Every hybrid (top-k then vote,
vote then verifier, rank average, confidence gates) is worse than the plain
verifier argmax on real parts. The greedy-decoded number is a weaker score
than its expected value (0.542 vs 0.548 at step 250) because half the
candidates decode to exactly 0.00.

**In-distribution control** (300-part seeded random subset of e51's K=8
full-pool candidates, `results/bo8_full_e51-…`, `--subset 300 --seed 0`;
the subset's own first-exec / vote / oracle are 0.900 / 75%, 0.926 / 82%,
0.952 / 90%, i.e. representative of the 1,030-pool 0.894 / 0.917 / 0.947):

| selector (K=8) | v3b regression final, EV | v3b step 750, EV | v3 binary final |
|---|---|---|---|
| consistency vote | 0.926 / 82% | 0.926 / 82% | 0.926 / 82% |
| verifier argmax | 0.911 / 81% | 0.911 / 81% | 0.914 / 81% |
| verifier top-4 then vote | 0.923 / 82% | 0.922 / 82% | — |
| vote top-4 then verifier | 0.920 / 83% | 0.923 / 83% | — |
| agreement gate 0.7 | 0.922 / 82% | 0.921 / 82% | 0.924 / 82% |
| verifier quality | Spearman 0.685 / per-part 0.271, AUROC 0.85 | 0.658 / 0.280, AUROC 0.83 | 0.586 / 0.284, AUROC 0.85 |
| oracle | 0.952 / 90% | 0.952 / 90% | 0.952 / 90% |

The real-part verifier does **not** hold the in-distribution vote on its own
(−0.015 mean, −1 point ≥ 0.85; its AUROC drops to 0.83 on synthetic parts,
whose candidates are 85% ≥ 0.8). The agreement gate — serve the medoid when
its mean agreement is ≥ 0.7 (the confident, in-distribution-like case,
AUROC 0.87 as a confidence signal), otherwise the verifier's argmax — keeps
0.921-0.924 / 82% in-distribution and takes most of the real-part gain
(0.519 vs 0.493 at K=8, 0.562 vs 0.527 at K=32). Verdict: **serve
agreement-gated v3b-EV**: vote on parts the generator agrees on, verifier on
the rest; or the plain verifier when the input is known to be a real part.
Cost: one forward pass per executing candidate (~0.1 s on an H200), no
generation.

Left undone: threshold 0.7 and the top-k were picked on the same 146/300
parts (a 2-point sweep, both directions reported; the ordering vote <
gate < verifier on real parts and verifier < gate ≈ vote in-distribution is
stable across every checkpoint); no seed replicate of v3b; the verifier is
not yet wired into the serving chain (`bestofn_verifier_eval.py` still uses
the mismatched legacy prompt).

Full-pool in-distribution control of the real-part verifier (e51 K=8
candidates, all 1,030 parts, v3b-final EV, 2026-09-06): first-exec 0.894 /
76%, vote 0.917 / 81%, verifier-argmax 0.912 / 82%, agreement gate 0.7 → 0.915
/ 81%, **gate 0.85 → 0.916 / 82%**, ceiling 0.947 / 90%. The gated policy is
within noise of the vote in-distribution and +0.03-0.05 on real parts:
serving candidate = e51 + best-of-8 + agreement-gated v3b-EV verifier.
(results/vsel_v3bfinalev_e51_bo8full_all_summary.txt)

## Serving policy — agreement-gated verifier, wired end to end (2026-09-07)

The served selection is now **e51 best-of-8 + agreement gate 0.85 + v3b-EV
verifier**: execute the 8 draws, take the consistency medoid if its mean
pairwise IoU with the other executing candidates is ≥ 0.85, otherwise score
every executing candidate with `v3b-verifier-real-reg/final` (expected IoU,
`reg_ev`) and serve the argmax. Every eval chain reports it.

**Files**
- `train_v14/geom/gated_select.py` — CPU, idempotent: merged candidates +
  `_consistency.json` (pair_iou) + verifier preds (`<vsel>.preds.json`) →
  per-part picks for first_exec / vote / verifier / gate0.85 / gate0.7 /
  oracle, metrics (mean, median, ≥0.85, ≥0.5; determinate / underdetermined /
  F / A slices with `--split`), branch shares; `<stem>_gated.json` +
  `_gated_summary.txt`. Same arithmetic as `verifier_select_offline.select()`.
- `train_v14/geom/gated_step.sh` — the chain step: `verifier_select_offline.py
  --prompt-mode reg_ev` on one GPU (base staged to /dev/shm with
  `STAGE_SHM=1`; skipped when `<stem>_vsel.json.preds.json` exists) then
  `gated_select.py`. Called by `sbatch/bo8_ext_cluster.sbatch`,
  `sbatch/boK_ext_cluster.sbatch` (after consistency_rerank, GPU 0) and by
  `serv19/run_bo8_full_generic.sh` (`results/bo8_full_<run>_gated.json`;
  serv-19 holds the adapter at `runs/v3b-verifier-real-reg/final` and
  `configs/v3b-verifier-real-reg.yaml` with the serv-19 e51 path).
  `sbatch/gated_step.sbatch` runs it on an existing candidate file.
- `mech/benchmarks/analyze_ext.py` — prints a `gated` column (gate0.85)
  between consistency and oracle when `<stem>_gated.json` exists; the
  in-distribution reference row is now e51's full pool.
- `train_v14/geom/serve.py` (+ `sbatch/serve.sbatch`) — single drawing or a
  directory of PNGs on one GPU: e51 loaded once, the verifier LoRA on top
  (PEFT adapter disabled for generation, enabled for scoring), K=8 (draw 0
  greedy, 7 at T=0.7 / top_p 0.95, `run_config('e51-rft-real-u3-strict90')`
  prompts), execution via `exec_harness.py` (now also emits the STEP), pairwise
  IoU + medoid, gate, verifier EV only when the gate fails; writes
  `<out>/<stem>/chosen.py`, `chosen.step`, `record.json` (all candidates,
  agreement matrix, verifier scores, branch, timings) and
  `serve_summary.json`.
- `verifier_select_offline.reg_ev_scores()` is the shared EV scorer (the
  offline study's `reg_ev` mode delegates to it; numbers unchanged).

**Regression** (`gated_select.py` on the stored e51 candidates + cached
preds, max |diff| vs `verifier_select_offline` 1e-16, 0 per-part mismatches):
146 real parts K=8 vote 0.493 / 14%, verifier **0.533 / 17%**, gate0.85
0.530 / 16%; K=32 vote 0.527 / 17%, verifier **0.578 / 23%**, gate0.85 0.575 /
21% (`results/ext/bo32_ext_e51-…_gated.json`); full pool K=8 vote 0.917 / 81%,
**gate0.85 0.916 / 82%**, verifier 0.912 / 82% (`results/bo8_full_e51-…_gated.json`).
The same step re-run on serv-19 (B300, its own e51 copy) gives gate0.85 0.915
/ 82%, verifier 0.911 / 81% (`…_gated_serv19_summary.txt`) — bf16 hardware
noise of 0.001.

**Chain check on other generators** (verifier trained on e51 candidates;
`gated_step.sbatch`, ~9 min per 146-part K=8 file incl. staging): e53 K=8
vote 0.503 / 18% → gate0.85 **0.529 / 18%** (verifier 0.531 / 19%, oracle
0.581); e52 K=8 vote 0.510 / 17% → gate0.85 **0.543 / 21%** (verifier 0.549 /
23%, oracle 0.587). Verifier AUROC ≥0.8 on their candidates 0.95 — it
transfers across the real-tier generators.

**serve.py test** (job 10411837, ccc0474, one H200, `results/serve_test_e51/`):
three held-out real drawings decoded from `ext_bench/eval_cache_v14.pkl`.
Weights staged to /dev/shm in 2 min, models loaded in 78 s, 24 draws in 220 s,
execution 73 s, pairwise IoU < 0.5 s per part, verifier scoring 23 s for the
one part that needed it. Both branches ran: `F_56494_0f3437d4_3_medium`
(8/8 executed, medoid agreement 0.950 → vote, served IoU 1.000 vs GT) and
`F_91100_df680fe7_1_medium` (8/8, 0.981 → vote, 0.995); `F_83938_d6cf9eca_0_medium`
(7/8, 0.646 → verifier argmax, EV 0.72 vs 0.23-0.69 for the rest, served
0.676 = the oracle of its 7 candidates; the offline gate on the stored e51
draws also fell to the verifier there, 0.660 vs the vote's 0.413). Served
picks are the oracle of their own candidate sets on all three; the offline
picks on the stored candidates took the same branch for every key.

## ABC ground-truth-code corpus (2026-09-08)

Question: the self-written real tier saturates at ~1k parts; can real ABC parts with a
**ground-truth build123d program** supply what the model cannot self-generate? Source: the
user's mesh→CAD pipeline (MBimrose/agentic-mesh-to-cad, `dataset/{ds0b,v1..v17}`: mesh.stl +
program.py + model.step per part, banked at IoU ≥ 0.85 vs the mesh, normalised frame with max
extent 2, emitter dialect `import build123d as b` / `_safe_fuse` / `result`). 523 unique
8-digit ABC ids (best version per part from cadfit_abc_best.json), 0 overlap with the 146
held-out bench parts; ds0r (programs only), ds0c (synthetic) and paper300 (CadQuery) skipped.

Conversion (`train_v14/mech/benchmarks/convert_cadfit_program.py`): AST span edits scale every
length literal by f = 80 / max extent of model.step (≈40, rounded to 4 decimals so the sheet's
numbers are the code's numbers; direction vectors, angles, counts untouched), rename
`result → part`, `b.X → X` with `from build123d import *`, append `export_step`, drop the
`_safe_*` helpers for plain `.fuse/.cut` (kept only where the plain version fails), and
optionally replace circle-fitting polylines (residual < 1e-3·r) by `Circle` / `ThreePointArc`.
Every stage is executed in a fresh subprocess and must reach centred IoU ≥ 0.99 against the
banked STEP scaled by f. Pass counts over 523 parts: original program re-executes in
build123d 0.11.1 at 517 (493 at ≥ 0.99 — 28 parts are kernel-version drift); scaled + plain
423 pass; helpers rescue 9; a 6-decimal retry rescues 14 (sub-1e-4 mm features collapsed);
**432 verified (82.6%)**, mean IoU vs STEP 0.9995, mean IoU vs the raw mesh 0.92. Polyline
cleaning: attempted on 184 parts, kept on **104** (162 Circle + 831 ThreePointArc
replacements; the other 80 drop below 0.99 because the reference itself is the polygon).
The 91 failures: 28 build123d drift, 39 execute at 0.9-0.99 (scale-dependent boolean
tolerances — 25 of them are *closer* to the raw mesh than the banked STEP), 24 crash.

Corpus `rft_corpus_abccode` (serv-19 mech_benchmarks/, cluster
train_v14/mech/benchmarks/data/): keys `A_<id>_code`, step_mm/ + gt_meshes_v15/ from the
converted program's own STEP, gt_code/<key>.py + gt_code.jsonl, manifest with per-part stats
and the renderer record. Rendered twice: `render_dw400/` (sibling dir
rft_corpus_abccode_dw400 with its own caches: /software python 3.11 + ~/.local draftwright
**0.4.0** + `_FONT_SIZE = 5.25`, exactly as corpora 1-3) 432/432, and `render/` (fresh venv
/srv/scratch/bimrose2/dw_venv: draftwright **0.4.23** + the same font patch, cairosvg added,
render_isolated.sh `RPY=`) 429/432 (three polyline-heavy parts exceed the 400 s render
timeout). 0.4.23 merges identical callouts ("14× R2.7"), moves the ISO view and marks fewer
sheets underdetermined (52 vs 66 on the held-out bench); one bench part fails its new
`ScaleIncompatibilityError` check. Shape census: median 30 faces, but only 192/432 pass the
CADBench single-body filter of corpora 1-3 (142 thin profiles with aspect > 15, 92 with > 120
faces, 50 multi-solid) — `cadbench_filter_pass` is stored per row.

**Renderer-drift control** (`ext_bench_dw423`, the 146 held-out parts re-rendered with 0.4.23,
e51 best-of-8, paired over the 145 parts both renderers produce;
results/ext/bo8_ext_dw423_e51-rft-real-u3-strict90_{summary,drift}.txt):

| slice (146-part bench) | n | first-exec old → new | vote old → new | oracle old → new |
|---|---|---|---|---|
| ALL | 145 | 0.484 → 0.415 (−0.069) | 0.510 → 0.444 (−0.067) | 0.594 → 0.516 (−0.078) |
| determinate (old sidecar) | 80 | 0.567 → 0.529 | 0.597 → 0.546 | 0.676 → 0.619 |
| underdetermined (old sidecar) | 65 | 0.383 → 0.276 | 0.403 → 0.317 | 0.494 → 0.388 |
| determinate under both | 68 | 0.532 → 0.507 | 0.559 → 0.516 | 0.646 → 0.591 |
| Fusion (F) | 88 | 0.519 → 0.447 | 0.540 → 0.494 | 0.634 → 0.570 |
| ABC (A) | 57 | 0.431 → 0.367 | 0.464 → 0.365 | 0.532 → 0.432 |

The renderer alone costs the served vote 0.07 (per-part oracle delta median −0.04; 63 parts
worse by > 0.05, 22 better; solved ≥ 0.8: 41 → 32). The model was trained on 0.4.0 sheets;
0.4.23 is a distribution shift, largest on sheets it lays out differently (the 52 it flags
underdetermined lose 0.14). Consequence: every new tier/bench must be rendered with 0.4.0
until the training sheets move, and "cannot write" below is judged on the 0.4.0 sheets.

**e51 baseline on the ABC-code corpus** (best-of-8, T=0.7, 429 parts scored under both
renderings; results/ext/bo8_abccode_e51-rft-real-u3-strict90_summary.txt):

| slice | n | 0.4.0: first-exec / vote / oracle | 0.4.23: first-exec / vote / oracle |
|---|---|---|---|
| ALL | 429 | 0.637 (36%) / 0.685 (41%) / 0.741 (46%) | 0.573 (30%) / 0.618 (35%) / 0.687 (42%) |
| determinate (own sidecar) | 332 / 322 | 0.680 / 0.727 / 0.778 | 0.638 / 0.685 / 0.750 |
| underdetermined (own sidecar) | 97 / 107 | 0.488 / 0.543 / 0.617 | 0.376 / 0.418 / 0.498 |
| ds0b (first harvest) | 152 | 0.672 / 0.711 / 0.758 | 0.599 / 0.652 / 0.727 |
| v5-v17 (re-exec gated) | 274 | 0.614 / 0.668 / 0.729 | 0.557 / 0.596 / 0.662 |
| GT polyline-cleaned | 104 | 0.587 / 0.659 / 0.721 | 0.546 / 0.608 / 0.684 |

(percentages = share ≥ 0.85.) These parts are easier than the held-out medium tiers (many are
single-profile extrusions): e51 solves 55% at ≥ 0.8 on the 0.4.0 sheets. Renderer agreement:
unsolved (best-of-8 < 0.8) **192 on 0.4.0** vs 225 on 0.4.23 — 178 unsolved under both, 14 only
on 0.4.0, 47 only on 0.4.23; per-part oracle delta mean −0.055 (median 0.000; 126 parts worse
by > 0.05, 58 better). Per-part numbers: results/abccode_render_deltas_e51-rft-real-u3-strict90.json.

Tier `rft_real_abccode/` (README there): the 192 unsolved parts with the verified GT program as
target (`src: "gt"`, empty think), 0.4.0 sheets; `rft_real_abccode_dw423/` the same parts on
0.4.23 sheets (keys suffixed `_dw423`); `rft_real_abccode_all{,_dw423}/` all 429. Packed with
pack_rft_shards_dir.py (1 shard each). Of the 192 unsolved, 77 pass the CADBench filter.
Open: train a round with the GT tier (e.g. rft_mix_u3_strict90 + rft_real_abccode ×k) and judge
on the 146-part bench (0.4.0 sheets) — the first real-part supervision that is not the model's
own output; whether 192 programs in the emitter's style transfer is the question.

**e54** (2026-09-08): e45 recipe + union5 ×5 + `rft_real_abccode_train` ×8 —
the ABC ground-truth-code tier: all 429 verified parts in both renderer
styles (0.4.0+patch and 0.4.23+patch sheets, 762 rows, empty think) minus a
seeded 48-part holdout of the 192 e51-unsolved parts
(`rft_real_abccode_train/holdout.json`). Mix `rft_mix_u6_gt` = 78 base + 25
union5 links + 8 GT links (GT ≈ 5% of RFT draws). Judged on: the 146-part
bench (old renderer, primary), `ext_bench_dw423` (new renderer), and the
ABC-code corpus in both renderings with the holdout slice reported
separately (does ground-truth code for the same distribution transfer to
parts the model has never seen, and does the new-renderer tier lift the
new-renderer bench).
Control for e54 on the new-renderer bench (`ext_bench_dw423`, 145 parts, e53):
first-exec 0.411 / vote 0.456 / gated 0.486 / ceiling 0.524 — same drift as e51
(vote 0.444, ceiling 0.516). (results/ext/bo8_ext_dw423_e53-*_summary.txt)
