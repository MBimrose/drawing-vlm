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
| e54 = e53 mix + ABC ground-truth-code tier (762 rows, both renderers) ×8 | — | 0.888 (75%) | 0.913 (82%) | 0.943 (90%) |
| e55 = e54 recipe on draftwright-0.4.23 sheets, judged on the 0.4.23 eval cache (e51 on the same cache: 0.907 / 0.940) | — | 0.886 (76%) | 0.909 (82%) | 0.935 (88%) |
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
Control for e54 on the ABC-code corpus (e53, 429 parts, first-exec / vote /
ceiling): 0.4.0 sheets 0.643 / 0.695 / 0.752, 0.4.23 sheets 0.568 / 0.620 /
0.689 — same as e51 within noise; the 48-part holdout slice of e54 is judged
against these. (serv-19 mech_benchmarks/rft_corpus_abccode*/results/bo8_*_e53-*)

## Training sheets re-rendered with draftwright 0.4.23 (2026-09-08)

Goal: move the training distribution to the deployment renderer (draftwright 0.4.23 +
the `_FONT_SIZE = 5.25` patch) so a model can be served on its sheets without the drift
measured above. The whole tars_v14 set (2,500 shards, 497k `{uuid}_v{N}` members, 59 GB)
is re-rendered on serv-19 under **identical member names**, so data_v14.py / the RFT
packers / the eval caches point at it unchanged (`DRAWING_VLM_TARS`).

**Pipeline** (`train_v14/mech/benchmarks/rerender_tars.{py,sh}`, `rerender_one.py`,
`rerender_exec.py`; serv-19 copies in `/srv/scratch/bimrose2/mech_benchmarks/`):
one worker process per shard; per member the `.py` is executed to STEP in a fresh
`.venv` python (build123d 0.11.1, `rerender_exec.py`, 120 s), and the STEP is rendered
by a fresh `dw_venv` python (`rerender_one.py` = render_ext.py's `worker_v11._process_one_part`
path, VLM_MODE, 1920×1280, seed crc32(uuid), real uuid in the title block, 400 s) with the
**variant forced to the member's `_vN`** (the original variant came from Python's
randomised `hash(uuid)` and is not reproducible otherwise). Output
`tars_v14_dw423/shard_XXXXXX.tar` (new PNG + unchanged .py) + `.renderers.json` sidecar
in the tars_v14 schema; parts that fail keep no member and are listed in
`tars_v14_dw423/failures/<shard>.json`; resumable per shard; one JSON line per shard in
`logs/rerender_tars_dw423.jsonl`. The 105,351 keys of `exec_bad_keys_v14.txt` (21%,
excluded from training by `exec_filter` anyway) are skipped, except the 1,072 certified
eval keys. Thread caps (`OMP/TBB/MKL/OPENBLAS=1`) matter: without them one exec burned
19 s of CPU for a 3 s wall import. Per part idle: exec ~3 s + render ~6 s.

**Stop-and-investigate (first hour).** The first pass dropped 11% of the certified eval
sheets and 24% of corpus-1 parts as `render_legacy` — the dispatcher's silent fallback
to the legacy renderer — and the existing `ext_bench_dw423` sidecar turned out to hold
**35/145 legacy sheets** (vs 6/1,527 with 0.4.0). Reasons (57 dropped eval parts):
31 `ScaleIncompatibilityError`, 5 `ViewNotPlanned`, 2 countersink `ValueError`,
2 `_DrawingTimeout`, 1 `_PocketAttributionError`, 1 `StopIteration`. draftwright 0.4.23
added `build_drawing(scale_policy=)`: with the default `"fallback"` an explicit `scale`
(our 0.62 fill scale) is retried over smaller ISO scales and **raises** when none keeps
every required annotation; `"permissive"` is the pre-0.4.23 best-effort behaviour. Fix:
`draftwright_compose.render_svg` now passes `scale_policy="permissive"` whenever the
installed draftwright accepts it (0.4.0 unaffected; `DW_SCALE_POLICY` overrides;
patch file `train_v14/mech/benchmarks/draftwright_compose_scale_policy.patch`, applied to
the serv-19 vendored copy, `.orig_dw400` kept). Re-rendering the same 57 parts recovers 47;
the residual is draftwright-internal (ViewNotPlanned / recognition errors / timeouts).
`rerender_one.py` also raises the per-view HLR / per-sheet drawing alarms to 60 s / 150 s
(worker_v11: 25 / 60 s) because a timed-out draftwright attempt also fell back silently.
All outputs of the first pass were discarded and everything re-rendered under the patched
dispatcher.

**Legacy fallback removed (user decision, 13:47 CDT).** "I would rather have a verbose
error than just falling back": the automatic legacy path in the vendored
`draw_generator.py` is gone — a draftwright failure now logs the full exception, records
`renderer="failed"` + `render_error` (+ lint counts, projection, fill scale) on the sidecar
meta, and raises; `worker_v11._process_one_part` keeps that meta for the failed variant,
`rerender_one.py` writes it to the meta file and exits 5 with the error as the last stderr
line, and the driver stores it as `render_fail: <exception>` in `failures/<shard>.json`.
The remaining `ViewNotPlanned` class turned out to be a draftwright 0.4.23 planner/linter
mismatch, not a lint failure: `build_drawing` succeeds (planned views `front/plan/iso`),
but `Drawing.export()` re-runs `lint()` whose `lint_prismatic_coverage` calls
`dwg.at("side", …)` unconditionally. Repair in `draftwright_compose.render_svg`: the
pre-export lint is made non-fatal (the sheet keeps the planner's own view set), and a
planner error raised by `build_drawing` itself is retried once with
`_views=("front","plan","side")`; both are recorded in the sidecar as `repair`. Probe part
`14378534-…` (a legacy sheet in `probe_dw423`) now renders as a real 0.4.23 sheet:
`serv-19:/srv/scratch/bimrose2/mech_benchmarks/probe_dw423_perm/render/png/14378534-e0be-eb12-e1f7-1019e5f62a84_v2.png`.
All three vendored files are patched on serv-19 (`*.orig_dw400` backups; combined diff
`train_v14/mech/benchmarks/step_to_drw_dw423.patch`). Because the driver spawns a fresh
renderer process per part, the bulk run switched to the no-fallback path mid-run without a
restart; `rerender_tars.py retry` then re-attempts the recorded failures of finished shards
and appends the recovered members (`failures/<shard>.json` → `"recovered"`), and
`rerender_finish_serv19.sh` runs that pass once more over every shard before packing. Before
the removal the bulk run had lost 900 of 40,248 attempted parts (2.24%; 256 shards) to
`render_legacy`; no legacy sheet was ever written (0 legacy sidecar entries, every failed key
absent from its tar).

**What actually breaks in draftwright 0.4.23** (no-fallback path; interim over the first 675
completed shards ≈ 106k attempted parts, 2,472 failures = 2.3% after the retry pass recovered
444 of 1,942 re-attempted first-pass failures = 22.9%, i.e. the `ViewNotPlanned` class):

| count | stage | exception | example key / message |
|---|---|---|---|
| 700 | render | `ValueError` (feature recognition) | `01639c4d-…_v5` "Hole cylindrical evidence does not prove one valid solid"; also "countersink defining face has no unambiguous valid solid" |
| 441 | exec | script timeout (120 s, build123d 0.11.1 under load) | `13c77b4f-…_v1` |
| 318 | render | `_DrawingTimeout` (150 s sheet alarm) | `0003880c-…_v5` |
| 316 | render | `Standard_ConstructionError` (OCCT, inside draftwright) | `019ba58d-…_v3` |
| 314 | render | `StopIteration` (draftwright internal) | `0044fca5-…_v5` |
| 173 | exec | script error (parts not on the blocklist; 0.11.1 kernel drift: fillet/chamfer) | `000bc5ac-…_v5` "Failed creating a fillet with radius of 2.0" |
| 129 | render | process timeout (400 s) | `04182dce-…_v3` |
| 53 | render | `_SlotAttributionError` "equal Slot record has competing source roles" | `04fe51a9-…_v1` |
| 14 | render | `AmbiguousTurnedOwnershipError` (groove profile membership) | `140c84f1-…_v1` |
| 6 | render | `_PocketAttributionError` "Pocket source faces do not prove one valid solid" | `03a6dc09-…_v3` |
| 4 | render | pre-removal `render_legacy` not yet re-attempted | — |
| 2 | render | `Standard_TypeMismatch` / `Standard_NullObject` (OCCT) | `0b6f79e9-…_v5` |

Per-key reasons with the full message: `tars_v14_dw423/failures/<shard>.json` (cluster copy
`step_to_drw/wds_dataset/tars_v14_dw423_failures/`, with `rerender_tars_dw423_summary.txt`).

**Final numbers (2,500 shards, run 11:52 → 23:15 CDT = 11.4 h wall, 2,785 worker-hours; mean
exec 6.5 s / render 19.1 s per part under load 300-560; 46 GB).** 498,799 members; 105,123
skipped (exec-bad blocklist); **393,676 attempted → 384,985 sheets (97.8%), 8,691 failed
(2.21%)** at the time e55 was submitted. Failure taxonomy over the whole set (no-fallback
path; the retry pass had recovered 472 of 2,623 re-attempted, 18%, before the finisher's own
final pass died on a bookkeeping bug — a second final pass over the remaining shards and the
exec timeouts runs after e55's start, see below):

| count | stage | exception |
|---|---|---|
| 2,795 | render | `ValueError` — 0.4.23 feature recognition ("Hole cylindrical evidence does not prove one valid solid", countersink …) |
| 1,294 | render | `_DrawingTimeout` (150 s sheet alarm under load) |
| 1,238 | render | `Standard_ConstructionError` (OCCT inside draftwright) |
| 1,145 | render | `StopIteration` (draftwright internal) |
| 755 | exec | script timeout (120 s, load-induced) |
| 625 | exec | script error under build123d 0.11.1 (486 `ValueError` fillet/chamfer, 41 `TypeError`, 23 `AttributeError`, 20 OCCT construction, …) |
| 559 | render | process timeout (400 s) |
| 183 / 54 / 25 / 4 / 1 | render | `_SlotAttributionError` / `AmbiguousTurnedOwnershipError` / `_PocketAttributionError` / `_PlateAttributionError` / `_RepeatingRadialAttributionError` |
| 12 | render | other OCCT / build123d (`Standard_TypeMismatch`, `Geom_UndefinedValue`, segfault rc=-11, …) |

So 0.4.23's own recognisers (hole / slot / pocket / turned / plate "does not prove one valid
solid") are the largest class (3,060 parts, 0.8%), then time (2,600 parts, load-dependent),
then OCCT errors inside the new renderer (1,250). `ViewNotPlanned` no longer occurs (repaired).

**After the second final retry pass** (96 workers on the idle box, 1.9 h; `rerender_tars.py
retry` incl. `exec_timeout`; 10,689 re-attempted, 1,669 recovered in total = 15.6%):
**386,182 sheets (98.1% of attempted), 7,494 failed (1.90%)** — exec timeouts 755 → 25,
`_DrawingTimeout` 1,294 → 860, render timeouts 559 → 506; the recogniser / OCCT /
`StopIteration` classes are unchanged (deterministic). `tars_v14_dw423` on the cluster was
re-synced in place (rsync renames atomically, so e55's running plain-tier stream is safe); the
RFT base `rft_strict90_all_dw423` and the mix were NOT re-packed while e55 reads them — they
reflect the 384,985-sheet snapshot (1,065 unfound keys; ~120 would now be found). Re-pack them
before the next run if wanted (`rerender_tars.sh pack` on serv-19, then the cluster finisher's
copy step).

**Artefacts.** Cluster: `step_to_drw/wds_dataset/tars_v14_dw423/` (2,500 tars + sidecars,
46 GB; /projects at 12.2 of 15 TB), `eval_cache_v15_dw423.pkl` (1,067 certified),
`eval_cache_v14_dw423.pkl` (legacy residue-7 holdout, 572 samples, pools 256/256/256),
`rft_strict90_all_dw423/shards` (**152,780 rows in 77 shards**; 1,065 of the 155,655 rows'
keys have no new sheet), `rft_real_union5_dw423/shards` (8,887 rows, 5 shards),
`rft_mix_u6_gt_dw423` = **110 shards = 77 base + 25 union5 links (×5) + 8 GT links** (the
rft_mix_u6_gt proportions: 78 + 25 + 8). serv-19 keeps the originals under
`/srv/scratch/bimrose2/{tars_v14_dw423,rft_strict90_all_dw423,rft_real_union5_dw423,data/eval_v15_dw423}`.

**e55-rft-real-u5-gt-dw423 = SLURM job 10433609** (ccc0451, submitted 2026-09-08 23:27 by the
cluster finisher; e54 config, 4,000 steps). `ship_finals.sh e55-…` is running (PID 975984,
`logs/ship_finals_e55.log`): when the final exists it submits the old-style external bench
(`bo8_ext_cluster.sbatch`, 0.4.0 sheets — expected to drop) and the serv-19 full pool on
`data/eval_cache_v15_dw423.pkl` via `configs/e55-…-serv19.env`; the cluster finisher then
submits the two new-renderer benches (`ext_bench_dw423`, TAG `bo8_ext_dw423`, and
`ext_bench_dw423_perm`, TAG `bo8_ext_dw423p`). Judge e55 against e51's 0.499 vote / 0.526
gated on `ext_bench_dw423_perm` (common keys) and e51 on the dw423 full pool (to be run:
`ship_finals`-style `run_bo8_full_generic.sh e51-…` with the same `.env`).

**Consequence for the drift numbers above.** Slicing e51's paired
`bo8_ext_dw423` result by the sidecar's renderer: on the 110 genuine 0.4.23 sheets
first-exec 0.486→0.450, vote 0.511→0.484 (−0.028), oracle 0.594→0.555; on the 35 legacy
sheets vote 0.507→0.318 (−0.19), oracle −0.20. **Most of the measured "renderer drift"
was legacy-renderer sheets the model never trained on**; the 0.4.23 style itself costs
e51 ~0.03 on the vote. `ext_bench_dw423` (and the abccode `_dw423` renders / tier rows)
were produced under the fallback policy; the consistent new-renderer bench is
`ext_bench_dw423_perm` (146 parts re-rendered under the permissive policy: 143 sheets,
all draftwright, 53 flagged underdetermined; cluster copy
`train_v14/mech/benchmarks/data/ext_bench_dw423_perm`). **e51 control on it** (job 10425867,
`results/ext/bo8_ext_dw423p_e51-*_summary.txt`), 143 parts, K=8:

| bench (e51, K=8) | n | first-exec | vote | gated 0.85 | oracle |
|---|---|---|---|---|---|
| ext_bench (0.4.0 sheets) | 146 | 0.484 / 14% | 0.510 / 17% | 0.530 / 16% | 0.594 / 22% |
| ext_bench_dw423 (0.4.23, fallback policy, 35 legacy sheets) | 145 | 0.415 | 0.444 | — | 0.516 |
| **ext_bench_dw423_perm** (0.4.23, permissive, 0 legacy) | 143 | 0.463 / 13% | 0.499 / 17% | 0.526 / 17% | 0.566 / 22% |

On genuine 0.4.23 sheets e51 is within 0.01 of its 0.4.0 numbers on the vote and the served
(gated) pick (oracle −0.03; determinate 78 parts: vote 0.579 / gated 0.600); the −0.07
"drift" was the legacy sheets. This is the baseline e55 has to beat on the new renderer.

**Rates and counts (permissive policy).** Certified eval sheets rendered from the
bundle's GT STEPs (`gt_meshes_v15/<uuid>.step`, manifest variant; 228 of these parts do not
execute under 0.11.1): 1,055/1,072 under the permissive policy, **1,067/1,072 after the
no-fallback re-attempt** (12 of the 17 were the `ViewNotPlanned` class; the 5 left are
recognition errors / timeouts) → `step_to_drw/wds_dataset/eval_cache_v15_dw423.pkl`
(`train_v14/build_eval_cache_dw423.py`; pool `certified` = 1,067, same code/trace/GT meshes;
serv-19 copy `data/eval_cache_v15_dw423.pkl`). Bench `ext_bench_dw423_perm`: 143 → **144/146**
sheets (the e51 control above ran on the 143; e55's run sees 144 — compare on common keys).
Corpora (`<corpus>/render_dw423/`): rft_corpus 1,490 → 1,493/1,527, rft_corpus2 1,648 →
1,652/1,684, rft_corpus3 1,487 → 1,489/1,494 (1.5% of the real parts fail in 0.4.23; 9 of the
80 recovered) → `rft_real_union5_dw423` = the union5 rows on the new sheets: **8,887 of 8,961
rows, 5 shards** (14 keys without a sheet).
Training tars, first 16 completed shards: 3,193 members, 786 skipped (exec-bad), 2,407
attempted, **2,362 ok, 45 failed (1.87%, all draftwright-internal legacy fallbacks)**; a
shard (≈157 attempted parts) takes ~62 min per worker with the box at load 400-530 on 344
cores (the user's cadfit jobs run alongside; mean exec 6.8 s, render 18 s under that load,
vs 3 + 6 s idle) → measured throughput ≈ 3.8 attempted parts/s at 256 workers, **~10 h for
the set** (started 11:52 CDT, first 100 shards at 1.16 h). Verification after the first 50
shards: `results/rerender_dw423_verify.txt` (20 random members: identical code, identical
1920×1280 PNG, same dimension values; 0.4.23 places more dimensions and merges callouts;
visual review of three pairs). Final failure summary:
`step_to_drw/wds_dataset/tars_v14_dw423_failures/` (`rerender_tars_dw423_summary.txt`,
written by the finisher; PENDING at the time of writing).

**Unattended tail.** `train_v14/serv19/rerender_finish_serv19.sh` (serv-19) waits for the
driver, writes the failure summary, aborts above 5%, packs `rft_strict90_all_dw423` from
the new tars (`pack_rft_shards.py`, DRAWING_VLM_TARS override) and flags done;
`train_v14/serv19/rerender_finish_cluster.sh` (login node) then copies
`step_to_drw/wds_dataset/tars_v14_dw423/` and the base shards back, builds
`eval_cache_v14_dw423.pkl` (legacy holdout, `build_eval_cache.py` with env overrides),
builds `rft_mix_u6_gt_dw423` (base + union5_dw423 ×5 + rft_real_abccode_train ×8, the
rft_mix_u6_gt proportions), submits **e55**, launches `ship_finals.sh e55-…`, and when the
final exists submits `bo8_ext_cluster.sbatch` on `ext_bench_dw423` (TAG bo8_ext_dw423) and
`ext_bench_dw423_perm` (TAG bo8_ext_dw423p).

**e55-rft-real-u5-gt-dw423** = the e54 config (configs/e55-…yaml, sbatch/e55-…sbatch) with
`DRAWING_VLM_TARS=tars_v14_dw423`, `DRAWING_VLM_EVAL_CACHE_V15=eval_cache_v15_dw423.pkl`
(new env, read by data_v14.EVAL_CACHE_V15 → EvalDatasetV2 / bestofn evals),
`DRAWING_VLM_RFT_SHARDS=rft_mix_u6_gt_dw423`. `env.sh` now respects a preset
`DRAWING_VLM_TARS`. The reasoning tier (v14_bundle, 0.4.0 sheets) is unchanged. Judged on:
(1) the full certified pool on the **new-style cache** — `serv19/run_bo8_full_generic.sh`
sources `configs/<run>-serv19.env` (ship_finals.sh copies it) which sets the serv-19 cache
path for the best-of-8 workers and the gated step; reference: e51 0.917 / 82% on the 0.4.0
cache (not directly comparable: 1,055 vs 1,030 parts and different sheets — the honest
comparison is e51 vs e55 both on the dw423 cache, or the drift-corrected 0.03); (2) the
146-part real bench in the new style, `ext_bench_dw423_perm`, against the e51 control
(job 10425867) and the e53 fallback-policy numbers (vote 0.456 / gated 0.486 on
`ext_bench_dw423`); (3) the old-style bench via the shipper's own `bo8_ext` submission
(expected to drop — the model no longer trains on 0.4.0 sheets). The lever question is
whether training on the deployment renderer's sheets closes the ~0.03 style gap and lifts
the new-renderer bench above e51's 0.484.

e54 results (2026-09-08), 146 real parts, K=8 (first-exec / vote / gated / ceiling):
old-renderer bench 0.477 / 0.503 / 0.545 / 0.589 (e53 control 0.472 / 0.503 /
0.529 / 0.581); permissive new-renderer bench (144) 0.490 / 0.513 / 0.539 /
0.580 (e51 control 0.463 / 0.499 / 0.526 / 0.566). The 432-part ground-truth
ABC tier does not move the medium bench beyond noise (+0.016 gated, +0.014 on
the new-renderer bench). Full pool and the ABC-code holdout pending.

Verifier seed replicate (v3c, seed 44, 1,000 steps, 2026-09-09; v3b was seed
42, best at step 750): on the 146 real parts verifier-argmax 0.526 / 17% at
K=8 and 0.565 / 23% at K=32 (v3b 0.533 / 0.578; vote 0.493 / 0.527), gate0.85
0.524 / 0.564. The verifier gain replicates to within 0.01; seed spread on the
146-part bench ≈ 0.01. (results/ext/vsel_v3cs44ev_e51_bo32_summary.txt)
e54 on the ABC-code corpus by slice (0.4.0 sheets, K=8, vote / ceiling, e53 → e54):
solved-by-e51 (240, in training) 0.885 / 0.923 → 0.873 / 0.919; unsolved but
IN TRAINING with ground-truth code (144) 0.455 / 0.541 → 0.467 / 0.545 (5 → 10
parts ≥0.8); unsolved HELD OUT (48) 0.465 / 0.533 → 0.470 / 0.554 (1 → 1).
0.4.23 sheets: same picture (unsolved-in-training 0.400 → 0.429, holdout 0.402
→ 0.406). **The model did not learn the ground-truth programs it was trained
on** — a 762-row tier at ≈5% of RFT draws leaves the trained parts unsolved.
Suspects: (a) the tier rows have empty think while inference always thinks, so
the learned no-think → code mapping never fires at serving time (testable with
no-think generation); (b) the converted dialect (Plane(origin=…) with 4-decimal
offsets, long polylines) is far from the model's own style; (c) too few
exposures. Full pool 0.913 / 82% (parity).
No-think diagnostic (e54, ABC-code corpus 0.4.0 sheets, K=8, `bestofn --no-think`):
unsolved-in-training parts solved at ≥0.8: **46/144 in no-think mode vs 10/144
in think mode** (ceiling 49 vs 17); held-out unsolved 4/48 vs 1/48; solved-by-e51
parts drop 0.873 → 0.785 (no-think is otherwise a worse mode). So the
ground-truth programs WERE learned, but only under the empty-think format they
were trained in, which serving never uses (inference always thinks first). Fix:
give ground-truth rows a reasoning trace in the model's own style
(rationalization: plan generated from drawing + correct code), then retrain.
Generalisation from 381 GT parts to the 48 held-out ones is small in either
mode (4 vs 1 solved) — the tier teaches specific parts more than the skill.
(results/ext/bo8_abccode_nothink_e54-*_consistency.json)
e51 control on the new-style full pool (`eval_cache_v15_dw423`, 1,027 parts,
run alias e51-dw423 on serv-19): vote 0.907 / 82%, gated 0.907, ceiling 0.940
— vs 0.917 / 0.916 / 0.947 on 0.4.0 sheets: −0.010 in-distribution, matching
the −0.01 on the permissive real-part bench. Baseline for e55.

e55 (e54 recipe trained on draftwright-0.4.23 sheets; 2026-09-09) on the
OLD-renderer 146-part bench: first-exec 0.500 / 17%, vote 0.526 / 17%, gated
**0.554 / 20%**, ceiling 0.592 / 23% — vs e51 0.483 / 0.509 / 0.530 / 0.594
and e54 0.477 / 0.503 / 0.545 / 0.589. Best vote and gated numbers so far on
the old bench, obtained by a model that never saw an old-style sheet in
training (the new sheets carry more dimensions). New-renderer benches and the
new-style full pool pending.

**Rationalized ground-truth tier** (2026-09-09, `train_v14/geom/rationalize_gt.py`):
e51 ignores a "write the plan" instruction 79% of the time and emits code
(consistent with earlier mechanism studies), so plans come from the base
Qwen3.8-27B instruct model given the drawing + the correct script, with a
drawing-alone prompt and a line scrub (0 of 392 plans mention the script or
identifiers afterwards; median 2,000 chars, numbered, every plan carries the
sheet's dimensions). 31 oversized polyline scripts (>12k chars) and 6 unusable
plans excluded → `rft_real_abccode_rat_train`: 702 rows (both renderers, same
48-part holdout). **e56** = the e54 mix with this tier swapped in
(`rft_mix_u6_gtrat`, 111 shards), job 10445918. Judged exactly like e54, plus
the think-mode ABC-corpus slices: if the trained-on unsolved parts now solve in
think mode, format was the blocker; the holdout slice then says whether
verified real-part code generalises.
e55 on the new-renderer benches: permissive (144 parts) first-exec 0.482 / vote
**0.533** / gated 0.539 / ceiling 0.591 (e51 0.463 / 0.499 / 0.526 / 0.566;
e54 0.490 / 0.513 / 0.539 / 0.580); fallback-policy bench (145, 35 legacy
sheets) 0.413 / 0.462 / 0.496 / 0.546 (e53 0.411 / 0.456 / 0.486 / 0.524).
Training on new-style sheets lifts the real-part vote by ≈0.02-0.03 on both
sheet styles. New-style full pool pending (baseline e51 0.907).
e55 on the ABC-code corpus by slice (vote / ceiling): 0.4.0 sheets —
solved-by-e51 0.871 / 0.918, unsolved-in-training 0.475 / 0.532 (9 of 144
≥0.8), held-out 0.497 / 0.572 (2 of 48); 0.4.23 sheets — 0.834 / 0.883,
0.415 / 0.496 (6), 0.461 / 0.501 (2). Same picture as e54 (the empty-think GT
tier is inert in think mode whatever the sheet style); on new-style sheets
e55 beats e54 on the solved slice 0.834 vs 0.794. e56 (rationalized tier) is
the test of the format fix.

e55 full pool on the new-style cache (2026-09-10, cluster): vote 0.909 / 82%,
first-exec 0.886, ceiling 0.935 — parity with e51 on the same sheets (0.907 /
0.940). With the real-part gains (old bench 0.526 vs 0.509, permissive new
bench 0.533 vs 0.499) **e55 is the serving candidate on draftwright 0.4.23
sheets**; the renderer switch costs ≈0.01 in-distribution relative to the
0.4.0 world and buys 0.02-0.03 on real parts.
e55 at K=32 (old bench): first-exec 0.483 / vote 0.539 (20%) / gated 0.571
(23%) / ceiling 0.646 (29%) — vs e51 0.527 / — / 0.639 and e52 0.536 / 0.645.

**e56 (rationalized ground-truth tier) — verdict: format was the blocker, but
the fix trades general skill for memorised parts; rejected** (2026-09-10).
Old-renderer bench (146): first-exec 0.455 / vote 0.503 / gated 0.538 / ceiling
0.575, exec≥1 97% (e54 0.477 / 0.503 / 0.545 / 0.589, 99%; e55 0.500 / 0.526 /
0.554 / 0.592, 100%). Permissive new-renderer bench (144): 0.447 / 0.475 /
0.495 / 0.534, exec≥1 **90%** (e54 0.490 / 0.513 / 0.539 / 0.580, 99%; e55
0.482 / 0.533 / 0.539 / 0.591, 99%). Full pool (0.4.0 cache) 0.911 / 81%,
first-exec 0.890, ceiling 0.942 (e54 0.913 / 82%): in-distribution parity, but
every real-part number is down and one part in ten on new-style sheets now
yields no executing draw at all.
ABC-code slices in THINK mode, 0.4.0 sheets (vote / ceiling, parts ≥0.8):
solved-by-e51 (240) 0.839 / 0.863 (191 / 199; e54 0.873 / 0.919, 200 / 228);
unsolved-in-training (144) 0.360 / 0.397 (**27** / 29; e54 0.467 / 0.545,
10 / 17); held-out (48) 0.248 / 0.271 (2 / 4; e54 0.470 / 0.554, 1 / 4).
0.4.23 sheets: 0.789 / 0.821 (177), 0.296 / 0.320 (25), 0.215 / 0.241 (3).
No-think mode: unsolved-in-training 2 / 144 solved (e54 46), held-out 1 / 48.
Reading: the rationalized plans moved the ground-truth programs into the
think-mode format the model serves in — trained-on parts solved in think mode
went 10 → 27 and the no-think route (46 → 2) closed, exactly the format
hypothesis. But what was learned is the specific programs, not the skill: the
held-out slice fell to 0.248 (e54 0.470, e55 0.497) with 2 of 48 solved, the
mean over the trained-on slice fell too (0.360 vs 0.467: the 117 still-unsolved
parts got worse, with many zero-execution parts), and execution reliability
on real sheets dropped 99% → 90%. The base-model plans are off-distribution
for e51's own reasoning style; training on them degrades the general
drawing → code mapping while installing 17 extra memorised parts.
Conclusion for the ground-truth-code direction: across e54 (empty think), e55
and e56 (rationalized think), a 381-part verified tier never generalises to the
48 held-out parts (1-2 of 48 solved in every variant). Growing the tier via the
mesh-to-CAD pipeline or DeepCAD / Fusion-Gallery converters is not worth the
compute unless the plan format is the model's own (e.g. self-distilled think
traces from e55 on the parts it does solve) — shelved. **e55 stays the
serving candidate on draftwright 0.4.23 sheets.** e56 checkpoint deleted;
`final` kept. (results/ext/bo8_{ext,ext_dw423p,full,abccode_*}_e56-rft-real-u5-gtrat_*)

## Serving switched to draftwright 0.4.23 with e55 (2026-09-10)

**Renderer.** `render_isolated.sh` now defaults to `RPY=/srv/scratch/bimrose2/dw_venv/bin/python`
(draftwright 0.4.23 + the `_FONT_SIZE = 5.25` patch, no legacy fallback); the retired 0.4.0
interpreter stays available by setting RPY. Every new corpus, bench and served sheet is 0.4.23
from here on.

**Generator.** `serve.py` / `serve.sbatch` default to `e55-rft-real-u5-gt-dw423`. On the sheets
it will actually see (permissive 0.4.23 bench, 144 parts) e55 votes 0.533 and gates 0.539
against e51's 0.499 / 0.526, and it is at parity in-distribution (new-style full pool 0.909 vs
0.907).

**Smoke test** (`serve.sbatch`, 4 real 0.4.23 sheets, 2026-09-10): 4/4 produced `chosen.py` +
`chosen.step` (valid BREP solids, 23-54 lines of code), 5-8 of 8 draws executing, model load 86 s
and the whole batch under 11 min on one H200. Every part took the VERIFIER branch (medoid
agreement 0.375 / 0.557 / 0.704 / 0.817, all under the 0.85 gate) — the serving-side face of the
83% escalation rate below. Job inputs must live under /projects: the first attempt pointed at a
node-local /tmp dir and `serve.py` read the missing directory as a single file ("1 drawing(s)").

**Verifier base.** The v3b LoRA was trained on e51's weights but `serve.py` stacks it on the
generator, so the switch needed a check: scoring e55's own candidates with the adapter on
**e55's** weights gives verifier 0.543 / gate0.85 0.540, against 0.542 / 0.539 on its e51 base
(144 parts, identical vote and oracle columns). Within noise, so serving still loads ONE model
and toggles the adapter. (`results/ext/bo8_ext_dw423p_e55vb55_gated_summary.txt`; re-run with
`VBASE=<dir>` on `gated_step.sh`.)

## Adaptive draw budget: the gate is a poor cost saver on real parts (2026-09-10)

`train_v14/geom/adaptive_k.py` replays a stored best-of-32 run as a two-stage policy: draw k0,
serve the medoid if its agreement clears the gate, otherwise escalate to k1 draws and take the
verifier argmax. Replay is exact — the first k0 candidates in draw order ARE the k0-draw run.
e55 on the 146-part bench (`bo32_ext_e55-rft-real-u5-gt-dw423_adaptive_summary.txt`):

| policy | mean | >=0.85 | draws/part | escalated |
|---|---|---|---|---|
| K=8 gate0.85 (deployed) | 0.535 | 18.5% | 8.0 | — |
| adaptive 8->16 | 0.563 | 20.5% | 14.6 | 82.9% |
| adaptive 8->32 | 0.569 | 21.9% | 27.9 | 82.9% |
| ladder 8->16->32 | 0.569 | 21.9% | 27.5 | 82.9% |
| K=32 gate0.85 | 0.571 | 23.3% | 32.0 | — |

**83% of real parts miss the gate**, so escalation saves only 13% of the draws of a fixed K=32 —
the same finding as the agreement scatter (deck sheet 12) seen from the cost side: real parts
rarely agree. The middle stop is the value: **8->16 buys 78% of the K=8 -> K=32 gain for 46% of
its cost**, and the three-stage ladder adds nothing over it (4 of 146 parts stop at 16).
0.55: 0.553 at 18.5) — `--gates` sweeps it. In-distribution only 201 of 1,027 parts (19.6%)
would escalate, and **escalation does pay there**. K=32 was run on exactly those 201 parts
(`escalate_keys_e55_fullpool.txt`, TAG=bo32_esc), and re-scored after repairing its pairwise
matrix (see below). Budget curve, every row from that ONE candidate file:

| budget | first-exec | vote | verifier | gate0.85 | >=0.85 | ceiling | draws/part |
|---|---|---|---|---|---|---|---|
| K=8 | 0.737 | 0.761 | 0.762 | 0.764 | 44% | 0.829 | 8.0 |
| K=16 | — | 0.788 | 0.787 | 0.791 | 49% | 0.877 | 16.0 |
| K=32 | 0.737 | 0.798 | 0.795 | 0.799 | 54% | 0.895 | 32.0 |
| adaptive 8->16 | — | — | — | 0.794 | 49% | — | 13.5 |
| adaptive 8->32 | — | — | — | **0.801** | 52% | — | 24.5 |

8 -> 32 draws is worth **+0.035 on the escalated fifth = +0.007 over the whole pool**, and the
adaptive policy reaches it in 24.5 draws instead of 32 — beating fixed K=32 outright, because the
gate stops early on the 31% that resolve by K=16. In production that is 11.1 draws per part over
the pool, 1.4x the compute of flat K=8, for +0.007 in-distribution, against +0.028 for 8->16 on
real parts. **Escalation earns its keep on real parts, not here.** Note too that by K=32 vote,
verifier and gate have converged (0.798 / 0.795 / 0.799): more draws make the vote healthy again,
the opposite of the real-part picture.

**Never read exec/iou out of a `_consistency.json`, and check its re-execution count before
trusting its `pair_iou`.** `consistency_rerank.py` RE-EXECUTES every candidate to build the STLs
for the pairwise matrix; it writes `exec` as `bool(c["stl"])` from that second run while leaving
`iou` at the original value, and a candidate whose re-run fails gets an all-None row in
`pair_iou`. Under load the re-run times out en masse. Compare `"n_exec"` in the merge log with
`[cons] re-executed N` in the consistency log:

| file | executed at generation | re-executed | lost |
|---|---|---|---|
| `bo32_ext_e55` (real bench) | 3,587 | 3,586 | 1 |
| `bo8_full_e55` (full pool) | 7,191 | 7,191 | 0 |
| `bo32_esc`, run beside two saturating jobs | 5,061 | 4,137 | **924 (18%)** |
| `bo32_esc`, repeated on an idle node | 5,061 | **5,061** | 0 |

Contention was the whole story — the same file on an idle node loses nothing
(`recheck_consistency.sh` + `.sbatch`, which reuse the cached verifier preds and warn if loss
recurs). The degradation cost the vote 0.016 (0.782 -> 0.798) and 7 points of escalation rate
(27% -> 34% voting), while the verifier column, the one policy that never touches the matrix,
came back byte-identical at 0.795 — which is how the diagnosis was confirmed. Three wrong
readings came out of the degraded file before it was traced: iou/exec taken straight from the
consistency file (vote 0.618 / 0.650 / 0.673 at K=8/16/32, ceiling 0.753 against the true 0.895),
the impossible conclusion that K=32 scored below K=8, and a +0.055 escalation gain that is really
+0.035.

## RFT base re-packed on the recovered sheets (2026-09-10)

`pack_rft_shards.py` re-run on serv-19 against the re-synced `tars_v14_dw423`:
**153,567 rows in 77 shards, 653 keys unfound** (was 152,780 / 1,065 — the second retry pass
recovered 787 rows). Packed to `rft_strict90_all_dw423b/` on both hosts so e55's inputs stay
byte-identical; the next training mix uses `b`.

## Scoring a K=32 real-part pass costs more than generating it (2026-09-11)

The self-distillation pass (below) generated 70,016 candidates over 2,188 real parts in ~14 h on
two nodes, then its execute-and-score phase ran 7 h and finished 681 of 35,744 on one corpus.
Three things were wrong, and only the first was obvious:

1. **`bestofn_verifier_eval.py` checkpoints generation but not scoring.** A walltime kill in that
   phase throws away every draw. `train_v14/geom/score_partials.py` re-runs just that phase from
   the `.partial.json` checkpoints, appending each result to `<out>.scored.jsonl` so it resumes
   freely, and writes a candidates file the rest of the chain accepts unchanged.
2. **The cost is the overlap, not the build.** On real-part geometry both boolean engines fail
   often and `iou.py` falls back to ray-parity Monte Carlo whose cost scales with face count:
   measured 143 s and 251 s for single 20k-face pairs (the module's own note records 56 min for
   a 1.13M-face candidate). Python threads cannot be interrupted, so each overlap now runs in a
   subprocess (`iou_once.py`) with a wall-clock budget (`--iou-timeout`, default 90 s); a pair
   that exceeds it scores 0. That is a REJECTION ON COST, not on measured geometry — it is
   flagged per candidate (`iou_timeout`) and counted at the end, and it is defensible only
   because a mesh that defeats both engines and the sampler is not one to train on.
3. **A free exact short-circuit exists and is, in practice, dead code.** IoU <=
   min(vA,vB)/max(vA,vB), so a volume ratio below the acceptance threshold settles the
   accept/reject decision without any boolean (`--accept`, flagged `iou_bound`). Validated on 40
   rebuilt candidates: never violated, 0.2 s against 470 s for the true overlaps. But it has now
   fired on **0 of 14,000** candidates in the real run, because volume is only trustworthy for a
   watertight mesh and the expensive cases are exactly the leaky ones. It costs nothing, so it
   stays, but **it is not where the speed came from** — do not reach for it again expecting one.

The whole gain is the TAIL. Only 0.6-0.7% of candidates hit the 90 s overlap cap, and bounding
that fraction is what turned 204 h into 4.6 h: a few pathological meshes were each consuming
tens of minutes and holding a worker thread the entire time. Fix the tail, not the average.

Build timeouts also dropped 120 s -> 60 s (`--exec-timeout`); half the budget was going to
failures sitting at the old limit. Together: **0.05 -> 2.11 candidates/s, 204 h -> 4.6 h.**
Budget a K=32 real-part pass accordingly: scoring is the expensive half, not generation.

## Self-distilled real-part tier (2026-09-11)

The tiers of rounds 1-5 were built at K=8: a part enters only if one of 8 draws verifies, so they
teach the parts the model already finds and saturate near 1,000 parts. The ceiling keeps rising
with K (e55 real bench: vote 0.539 but oracle 0.646 at K=32), so the parts solvable ONLY at 32
draws are the ones no tier has taught — and the winning draw carries the model's OWN think trace,
which is exactly what e54 (empty think) and e56 (base-model plans) lacked.

**Pass.** e55, K=32, T=0.7, over the 2,188 corpus keys still unsolved after rounds 1-5, on 0.4.23
sheets (`selfdistill_k32.sh` / `.sbatch`, `--keys` added to `bestofn_verifier_eval.py`).
70,016 candidates; generation ~14 h on two nodes, scoring 4.6 h on two more (see the scoring
entry above — it is the expensive half).

| corpus | parts | newly solved | rate | accepted rows | exec | iou timeouts |
|---|---|---|---|---|---|---|
| rft_corpus_dw423 | 1,117 | 115 | 10.3% | 1,049 | 69-77% | 206 (0.58%) |
| rft_corpus2_dw423 | 1,071 | 251 | 23.4% | 3,653 | 75-84% | 217 (0.63%) |

By family the split is wide: Fusion 360 15.6% and ABC 6.2% in corpus 1, the corpus-2 hard tier
25.2%. De-duplicating on (key, code) — the model re-emits the same program across draws — leaves
**2,061 distinct accepted programs over 366 parts, every one with a think trace**
(`rft_selfdistill_all`, 2 shards; `build_selfdistill_tier.sh` merges, packs and builds the mix).

**e57** = the e55 recipe with the re-packed base (`rft_strict90_all_dw423b`) and this tier in
place of the shelved ABC ground-truth tier, upweighted x8 — the SAME weighting e56 gave its
702-row borrowed-reasoning tier, so the two runs differ in the source of the reasoning and not in
how hard the tier is sampled. Mix `rft_mix_u7_sd_dw423` = 118 shards (77 base, 25 union5 x5,
16 self-distilled x8). Job 10481274. Judged like e55/e56: old bench, permissive 0.4.23 bench,
new-style full pool, and the ABC-corpus slices. The question is whether real-part reasoning the
model produced ITSELF transfers to parts it has never solved — the one form of the
ground-truth idea e56 did not rule out. Prior expectation is modest: 366 parts is +19% on
union5's 1,960, so a real-bench gain inside +-0.02 would be within single-run noise.

**e57 verdict: the tier is free but inert — self-generated reasoning does not transfer either**
(2026-09-13). Real benches (K=8, first-exec / vote / gated / ceiling), e55 -> e57:
old 146-part 0.500/0.526/0.554/0.592 -> 0.463/**0.522**/**0.559**/**0.604** (>=0.85 20% -> 25%);
permissive 0.4.23 144-part 0.482/0.533/0.539/0.591 -> 0.463/0.518/**0.554**/0.584. New-style full
pool 0.886/0.909/0.935 -> 0.891/**0.911**/**0.946**, exec 100%. ABC-corpus slices (vote, parts
>=0.8), 0.4.0 sheets: solved-by-e51 0.871 (190) -> **0.876 (202)**; ABC parts unsolved and NOT in
e57's tier 0.475 (9) -> 0.466 (8); held-out 48 0.497 (2) -> 0.485 (1). Same on 0.4.23 sheets.

Reading: **no transfer.** On ABC parts e57 never trained on it is 0.466 / 0.485 against e55's
0.475 / 0.497 — indistinguishable. 366 hard real parts carrying the model's OWN verified
reasoning generalise to other real parts no better than the self-written tiers of rounds 1-5 or
the ground-truth tiers of e54/e56. That closes the last variant of the idea: **empty reasoning is
invisible at serving (e54), borrowed reasoning memorises and costs execution reliability (e56),
self-generated reasoning is neutral (e57)** — the blocker was never the reasoning format.

But unlike e56 it is free, and every selection-side indicator moves slightly the right way: best
gated number on both real benches, best ceiling on the old bench and the full pool, >=0.85 up
20% -> 25%, 12 more of the ABC parts e51 already solved (202 vs 190), and no in-distribution cost
(0.911 vs 0.909). No single gap clears the +-0.02 single-run noise, so **e55 and e57 are
equivalent and e55 stays the serving candidate**; e57's edge is concentrated in gated/ceiling
metrics, i.e. in what the verifier can find among its candidates, not in what the vote picks.

Consequence for the roadmap: with self-distillation closed, the remaining levers on real parts
are all selection-side (the verifier, and more draws where the gate escalates — worth +0.028 at
8->16 on real parts, RECIPE "Adaptive draw budget") rather than data-side. A real-part data lever
would now need genuinely new geometry the model cannot already reach at K=32, not more of what it
can.

## Verifier retrained on the served distribution (v4) — neutral; escalation deployed (2026-09-15)

**v4-verifier-e55-reg**: v3b's recipe (LoRA r64, regression EV, 2,500 steps) on **e55's weights**
instead of e51's, trained on the union pool `rft_scored_union_e55` = `rft_scored_real` (94,553
candidates / 4,602 parts, 9.4% >= 0.8, the e51/e40/e45 pool on 0.4.0 sheets) + `rft_scored_real_e55`
(64,927 / 2,142 parts, 3.1% >= 0.8 — e55 at K=32 on 0.4.23 sheets from the self-distillation
pass; too negative to train on alone). Val loss 0.3607. Scored on the SAME stored candidates as
v3b (`<stem>_e55v4` symlinks, so the published v3b files are untouched):

| candidates (e55) | v3b verifier / gate0.85 | v4 verifier / gate0.85 | delta (gate) |
|---|---|---|---|
| old bench, K=8 | 0.556 / 0.554 | 0.547 / 0.546 | -0.008 |
| permissive 0.4.23 bench, K=8 | 0.542 / 0.539 | 0.550 / 0.547 | +0.008 |
| old bench, K=32 | 0.573 / 0.571 | 0.580 / 0.577 | +0.006 |
| in-distribution escalated fifth, K=32 | 0.795 / 0.799 | 0.800 / 0.800 | +0.001 |

Mixed sign, every gap <= 0.009, all inside the +-0.02 band: **retraining the verifier on the
served generator and renderer does not help.** The verifier was not limited by distribution
mismatch — v3b on e51's weights already transfers to e55's candidates (RECIPE "Serving switched",
0.543 vs 0.542), and matching it exactly adds nothing. The remaining gap to the ceiling (0.577
vs 0.646 at K=32) is what the verifier cannot tell apart, not what it was never shown.
**v3b stays the deployed verifier**; v4 is kept as an equivalent with an e55 base.

**Draw budget re-verified with v4** on the real bench (one bo32 file, `bo32_ext_e55v4_adaptive`):
gate0.85 at K=8 / 16 / 32 = 0.536 / 0.565 / 0.577; adaptive 8->16 = 0.564 at 14.6 draws,
8->32 = 0.576 at 27.9 — within 0.007 of the v3b curve (0.535 / 0.564 / 0.571; 0.563 / 0.569)
at every point. The +0.028 for 8->16 is verifier-independent.

**Escalation is deployed.** `serve.py` draws `--k` (8), computes the medoid's agreement, and
raises only the drawings that miss the gate to `--k-max` (16) before the verifier picks;
`--k-max` equal to `--k` restores fixed-budget serving, and every record.json carries `k`,
`k_max` and `escalated`. Verified end to end on 4 real 0.4.23 sheets (job 10534414): all four
escalated (real parts rarely agree), 11-16 of 16 draws executing, valid solids served from the
enlarged pool. Two bugs caught in the wiring — the banner read the budget before it was defined
(would have crashed every launch) and the executed count was printed against the first-round
budget. In-distribution only ~20% of parts escalate (RECIPE "Adaptive draw budget"), so the
policy costs ~11 draws per part there for +0.007, and 14.6 on real parts for +0.028.

## What is left to try: real design idiom at scale, not surface types or model scale (2026-09-15)

**Where the real-part gap is NOT.** A face-type census of 150 solved vs 150 still-unsolved real
parts (OCCT surface types per STEP, serv-19) and 200 synthetic training parts:

| pool | median faces | plane | cylinder | torus |
|---|---|---|---|---|
| real, solved | 14 | 67% | 25% | 4% |
| real, unsolved | 41 | 67% | 28% | 2% |
| synthetic training (Zero-To-CAD-1m) | 24 (p90 61) | 67% | 23% | 2% |

Surface types are identical across all three and the synthetic pool already covers the
unsolved parts' complexity. Fillets, cones and face counts are not the gap; the earlier
diagnosis stands (bowed strips, multi-lug brackets, ring/boss stacks — idioms the synthetic
families never compose). Note the synthetic set IS ADSKAILab/Zero-To-CAD-1m, so it, CAD-Recode
and FllumaOne (all synthetic) are not new geometry.

**Models.** DeepSeek-V4.1-Flash (released 2026-09-10, MIT): 552B MoE, 8B/16B active, native
DeepSeek-ViT (32 layers, patch 14, <=1024 image tokens), 510 GB FP8 checkpoint (FP4 experts).
transformers vision support is a DRAFT inference-only PR (#48768, 2026-09-13; engram tables
~98 GB, training untested); vLLM serves it only from the Docker image
`vllm/vllm-openai:deepseekv41-flash-0909` (no wheel), stated minimum 614 GB VRAM = one 8xH200
node. So: zero-shot probe is tractable (`probe_openai_vlm.py` + `probe_dsv41.sbatch`, same
prompt and scorer as the bench), fine-tuning is a hand-port on a 552B MoE — not this month.
The 180B Flash-Next full FT already matched the 27B at 12x params, so scale alone is not the
lever; the probe answers whether V4.1's vision is qualitatively different.

**DeepCAD as a real-sequence tier.** 215,093 Onshape parts (161,240 train) as raw
sketch-and-extrude sequences in METRES, from ABC links (`/srv/scratch/bimrose2/deepcad`).
`deepcad_to_b3d.py` emits build123d in our dialect, rescaled to 80 mm, following DeepCAD's own
OCC reconstruction (sketch-local 2D points on the transform plane; arcs by three points with
mid = center + R(mid_angle) @ reference_vector * radius; symmetric = extent_one both ways;
NewBody/Join fuse, Cut, Intersect). Two data facts that matter:
  * the raw `is_outer` flag is True on EVERY loop (4,477/4,477 multi-loop profiles) — the
    boundary must be taken as the largest-bbox loop, the rest as holes, else holes vanish
    silently and the bbox check cannot see it;
  * 25% of parts have a sketch no extrude consumes: the parser dropped the feature that used
    it (hole, revolve, fillet), so the recorded part is more than the sequence rebuilds — half
    of those still pass a bbox check, so they are skipped on the structural signal, not caught.
`deepcad_verify.py` executes each script and keeps it only if the solid's bbox matches
Onshape's own bbox within 2% (catches plane/unit/direction/symmetric errors): on 2,000 train
parts, 1,433 convert (567 skipped: 505 unused sketch, 42 profile-less extrude, 19 ambiguous
nesting) and the accepted ones match at p90 error 0.0000.
**Gate**: render the verified parts on 0.4.23 (`deepcad_gate.sh`), score e55 at K=8
(TAG=bo8_deepcad). If e55 solves them well under half the time they are new geometry; the
tier is then real code for every part (161k-scale, memorisation impossible) plus e55's own
think traces on the solved fraction (the e57 recipe) — the empty-think problem of e54 is the
open design question for the unsolved fraction.

## Second B300 host: wpk-serv-20 (2026-09-15)

Granted for experiments (serv-19's GPUs stay with the user's own model). 8x B300 SXM6 (275 GB
each), 344 cores, 2 TB RAM, 24 TB local `/scratch`, driver 615.71.09; apptainer 1.4.5 works,
rootless docker does not (no subuid). Set up as an exact mirror of serv-19's layout through a
symlink `/srv/scratch/bimrose2 -> /scratch/bimrose2`, so every serv-19 runner, the render
scripts and the uv venvs (absolute-path shebangs) work unchanged: `.venv`, `dw_venv`,
`train_v14`, `mech_benchmarks`, `data` rsynced from serv-19; `runs/e55.../final`, both
verifier LoRAs and `train_v14/configs` shipped from the cluster; `models/DeepSeek-V4.1-Flash`
copied; the vLLM V4.1 image pulled natively. Roles: DeepCAD tier generation (best-of-K with
e55 over ~100k verified real parts — a cluster-sized job that no longer needs the queue), the
DeepSeek-V4.1-Flash probe on Blackwell (fp4 experts are native there), and rendering on 344
idle cores.

**DeepCAD gate result (2026-09-15, job 10571393).** e55 at K=8 on 616 verified DeepCAD parts
rendered on 0.4.23 (family D, prep filters at the CADBench defaults): first-exec **0.713 / 44%**,
vote **0.746 / 49%**, ceiling **0.808 / 59%** (>=0.85), every part executing. That sits squarely
between the synthetic pool (0.91) and CADBench real parts (0.53): real Onshape idiom the model
half-knows — roughly two parts in five are NOT solved at 8 draws, which is exactly the regime
where the self-written tiers of rounds 1-3 paid off, and here the pool is 110k parts instead of
2k so it cannot saturate. Prep rejected half the verified gate parts (aspect 325, faces<6 278,
multi-body 89 of 1,325): plain plates, rods and cylinders — real parts, kept for the tier via
`--min-faces 3 --max-aspect 40` (multi-body stays out).
**Full split verified**: 110,046 of 119,954 converted train parts rebuild to Onshape's own
bbox (92%; 9,584 mismatches = dropped sketch-less features such as patterns/mirrors, 165 exec
errors, 144 timeouts). **serv-20** serves e55 end to end (escalating policy, 4/4 real sheets,
model load 19 s from local NVMe).

**vLLM generation path validated (2026-09-15, serv-20).** e55 served by vLLM (DP=8, one replica
per B300, `--reasoning-parser qwen3`) and driven by `gen_openai_bo.py` (draw 0 greedy, 7 at
T=0.7/top_p 0.95, the bestofn recipe) on the SAME 616 DeepCAD gate parts, scored by the same
`score_partials.py`: first-exec **0.713** (HF path 0.713), ceiling **0.802** (0.808), >=0.85
58% (59%), 4,585/4,928 executing, 4,928/4,928 with a think trace. On-policy-equivalent within
noise, and **256 s for 616 x 8** = ~144 parts/min (~70k candidates/h) against ~1.5 h on 8xH200
with HF generate — ~20x. The 87k-part full pass (K=8, ~700k candidates) is therefore ~10-15 h
of generation on serv-20 alone; scoring (CPU) is the other half. Drivers:
`run_vllm_e55_serv20.sh`, `run_vllm_gate_check.sh`, `run_deepcad_gen_serv20.sh`.
DeepCAD full split after prep with `--min-faces 3 --max-aspect 40`: **87,328 kept** of 110,046
(rejected: aspect 13,245, multi-body 6,810, faces<3 1,947, fill 714).

**DeepSeek-V4.1-Flash zero-shot on the real bench (2026-09-15, serv-20, vLLM tp=8 on 8x B300):**
146 parts, the served prompt, greedy, 24,000-token budget (`results/ext/probe_dsv41_ext_24k.json`):
**mean IoU 0.093, median 0.000, 4.1% >= 0.85, 8.9% >= 0.5** — against e55's 0.554 / 20% gated.
The failure mode is runaway reasoning: 114 of 146 replies never leave the thinking phase — the
trace runs 68k-101k characters and hits the 24k-token cap with no answer (a 6k budget yielded
1 answer in 16). The 32 that did answer executed 30 times with a mean of ~0.45 and included
exact solutions (0.93, 0.80), so the vision reads the sheets; the model cannot finish deciding.
Not a candidate as a generator, and its 552B/16B-active MoE has no training path anyway. A
no-think variant was set up (`probe_openai_vlm.py --no-think`) but not run: the engine went
down while being relaunched and another 25-minute start on all eight B300s is not worth it
against the full DeepCAD pass waiting for the same GPUs. DeepSeek is closed as a lever. Engine facts:
25 min to ready (DeepGEMM JIT + 510 GB), needs the host CUDA toolkit bound in, and the box
must not host a wide CPU job at the same time (froze at ~410 load).
Stage 0 passed (transformers 5.18.0.dev0 from PR #48768 + torch 2.13 cu130 in `.venv_dsv41`;
`DeepseekV41ForConditionalGeneration` instantiates, 755B params, config FP8 32x32 blocks with
ue8m0 scales and FP4 experts). Stage 1 needed three plumbing fixes before the GPUs were even
touched: the checkpoint ships a tokenizer but no processor config or chat template, so the
processor is built by hand (`DeepseekV41ImageProcessor()` defaults + the shipped tokenizer,
whose `<｜deepseek_image｜>` is token 129264 as the config expects) and the prompt is rendered
with the checkpoint's own `encoding/encoding.py` `encode_messages` (the reference format);
`torchvision` is a hard requirement of the processor; the class has no gradient checkpointing.
**The checkpoint loads for training in transformers**: 67 s, ~280 GB resident across the 8
B300s (41-44 GB each) with FP8/FP4 kept quantized — transformers routes the FP8 linears and
experts through Triton/grouped_mm when the model spans devices in one process (DeepGEMM's
kernels bind to one CUDA context). PEFT attaches LoRA to the attention projections
(`q_b_proj` matched first; 22.5M trainable at r=16). Forward/backward is the next kill point.
Two more plumbing steps followed: the LoRA target regex had to name all five attention
projections the draft class actually uses (`q_a_proj q_b_proj kv_proj o_a_proj o_b_proj`; there
is no `k_proj`/`v_proj`) — 200 targets, 45.9M trainable at r=16; and the first forward raised
`finegrained-fp8 kernel unavailable`: the multi-GPU FP8 path in this transformers build does
not ship its matmul, it fetches `kernels-community/finegrained-fp8` from the Hub through the
`kernels` package (0.16.x, not a dependency of the PR) — `uv pip install kernels==0.16.0` plus
`HF_HOME` on scratch fixed it (11 files cached under `.cache/huggingface/hub`). Attempt 6 is the
first that reaches the forward pass with the released encoder prompt (2,598 chars, one image
placeholder, 1,704 tokens with the answer).
Attempt 6 then aborted inside Triton on the first FP8 matmul (`LLVM ERROR: Cannot select:
intrinsic %llvm.nvvm.tcgen05.wait.ld`, target sm_103a): the venv was no longer the stack stage 0
had reported — installing `torchvision` from PyPI had silently replaced torch 2.13+cu130 with
torch 2.9.0 and Triton 3.5, which cannot lower Blackwell tcgen05 instructions for the B300.
Reinstalling `torch==2.13.0 torchvision` from the cu130 index restored Triton 3.7.1, and the
Hub kernel's `matmul_2d` now compiles and runs on one B300 (6.8 s JIT, 64x5120x1536 bf16 x
fp8 block-32). Attempt 7 is queued for when the DeepCAD generation releases the GPUs; the CPU
scoring that follows the generation does not block it.

### 2026-09-16 — DeepCAD full pass generated (4 h); work moves from serv-20 to serv-04
The full DeepCAD best-of-8 generation finished at 03:56: 86,904 parts x 8 draws through e55
on vLLM (DP=8) in 4 h 1 min — ~360 parts/min, 695k candidates with code (8 x ~104 MB
`results_vllm/bo8_full_e55_vllm.shard*.json.partial.json`). The driver then sat idle for six
hours: its bare `wait` also waited on the vLLM server it had started as a background child, so
scoring never began (fixed: `wait $GEN_PIDS`). The user asked for serv-20 to be cleared for
other people and offered **wpk-serv-04** (8x H200 143 GB, 128 cores, 1 TB RAM, 56 TB scratch)
instead; everything of mine on serv-20 was stopped and the layout is being pulled into the
same `/srv/scratch/bimrose2` path on serv-04 (code, venvs, benches, the DeepCAD corpus and
partials, then the 476 GB DeepSeek checkpoint and the e55 weights). Next: score the partials on
serv-04's CPUs, write `rft_deepcad_e55`, build the e58 mix on the cluster; DeepSeek stage 1
attempt 7 on the H200s once the checkpoint lands (Hopper is DeepGEMM's native target).
serv-04 turned out unusable for geometry: its glibc is 2.28 and the OCP wheel needs 2.29, so
`import build123d` fails and `score_partials` "finished" 695k candidates in 14 min with every
exec false and an empty tier (deleted; the resume file would have poisoned a rescore). The
partials, meshes and sheets were pulled to the cluster and scoring runs there as two shard
slices (`score_deepcad.sbatch`, merged by `merge_scored.py`). The H200s on serv-04 do work for
the spike: torch 2.13 cu130 loads the checkpoint in 60 s. Attempt 7 there found the last model-
side trap: `o_a_proj` is a `DeepseekV41GroupedLinear` (block-diagonal over `o_groups`,
subclassing nn.Linear), so PEFT's plain LoRA on it mis-shapes (1024 vs 8192 at dim 3); the
adapter now targets `q_a_proj q_b_proj kv_proj o_b_proj` only. The user also offered
ccc0451/474/475 with InfiniBand for the real run: the trainer gained `--dist` (one process per
node, full pipeline-split replica each, adapter gradients averaged over NCCL) and
`dsv41_lora_3node.sbatch` follows the connector-folder recipe; a one-node cluster smoke
(`dsv41_smoke.sbatch`, venv at `.venv_dsv41` on /projects) gates it.
Attempt 8 (serv-04) got through the forward — **answer loss 2.68 nats/token** on the certified
sample, 109 s for 1,704 tokens without gradient checkpointing — and died in the backward: the
Hub `finegrained-fp8` ops (`torch.ops._finegrained_fp8_cuda_89d4054.*`) ship no autograd
formula. Since the quantized weights are frozen, only the input gradient is needed, which is a
plain matmul against the dequantized weight; `train_v14/geom/dsv41_autograd.py` registers that
for the 2D, grouped and batched variants of the block-FP8 and MX (UE8M0 group-32, E4M3 or packed
E2M1) ops via `torch.library.register_autograd`. `dsv41_autograd_test.py` checks it on real
checkpoint tensors on one H200: kernel forward vs dequantized matmul 2.4% (block FP8 `wq_b`
32768x1280, UE8M0 32x32 scales) and 2.7% (MXFP4 expert `w1` 2304x2560, the kernel's own fp8
activation quantization), backward vs reference 0.17% for both and for the grouped op over two
experts; E2M1 nibbles are low-first (high-first gives 141% error). Attempt 9 / the cluster smoke
run with the formulas registered.
**Attempt 9 (serv-04, 8x H200): STAGE1 OK — the released checkpoint trains.** Forward 17 s
(Triton kernels warm), backward 11 s through the registered formulas, 320/320 LoRA tensors
received gradients (grad norm 0.48), and six AdamW steps (lr 1e-4) on the one sample drove the
answer loss **2.678 -> 1.031**; the greedy continuation afterwards is a coherent answer
("Based on the provided technical drawing, here is the step-by-step information to construct
the 3D model ... Length (X): 100 mm"). Resident ~280 GB over 8 GPUs at 1.7k tokens without
gradient checkpointing. Stage 2 (200 steps on the 2,061-row real tier, greedy eval on 48 bench
parts) follows on serv-04; the cluster smoke on ccc0451 gates the 3-node run.
The cluster smoke on ccc0451 (`dsv41_smoke.sbatch`, checkpoint read from Lustre: ~35 min to
load vs 60 s from local disk) passed identically (2.674 -> 1.007, peak 58 GB per H200). The
first 3-node submission brought NCCL up across ccc0451/474/475 over the mlx5 link (all three
ranks reported) and then failed on a missing `prompts.json` next to the union5 tier — the
trainer now falls back to `spike_dsv41/prompts.json`. Resubmitted as job 10583388: 600 steps,
accum 4 per node x 3 nodes = 12 samples per step, lr 1e-4, r=16 on the union5 real tier, then
a 96-part greedy eval on the real bench sharded across the ranks.
**Stage 2 on serv-04 (200 steps x 8 samples, lr 1e-4, r=16, 2,061-row real tier): training loss
2.60 -> 0.32** in 5.1 h (93 s/step, ~12 s per sample forward+backward at 1.2-4k tokens, no
gradient checkpointing); adapter at `spike_dsv41/lora_r16_s200` (38.0M params over 160
targets). Its in-job eval crashed: the spike venv has no trimesh, and serv-04 cannot run OCP at
all (glibc), so the eval is now split — the trainer dumps generations (`eval_gen.rank*.jsonl`)
and scores only when `--exec-python` names a CAD-capable interpreter; `dsv41_eval_score.py`
scores dumped generations on the cluster with the usual harness + centered IoU. An eval-only run
(`--steps 0 --adapter`, 48 parts, greedy, 3,000 new tokens) is generating on serv-04.
The 3-node run (job 10583388) trained 11 steps at **451 s/step** — 113 s per sample vs 12 s on
serv-04 — and died at step 12 when rank 1 hit NCCL's 10-min collective timeout waiting for the
others (timeout now 3 h). The cluster smoke had the same gap (first forward 431 s vs 17 s):
suspect the Triton JIT/autotune cache living in the NFS home dir; the job scripts now seed a
node-local `TRITON_CACHE_DIR` and a 1-node profiling job prints per-sample times before the
long run is relaunched. Until that is understood, serv-04 alone (12 s/sample) out-trains the
three cluster nodes (3 x 113 s).
**Stage 2 eval (serv-04 adapter, 48 real-bench parts, greedy, scored on the cluster):** mean IoU
**0.051**, median 0.007, 0% >= 0.85, 0% >= 0.5, best part 0.37; 46/48 answered with a build123d
script and 26/48 executed — against **e55's first draw on the same 48 parts: 0.442 / 18.8%**
(`runs/dsv41_s04_r16_s200/eval.json`). The model learned the DSL (parameter block, BuildPart,
export_step) but writes toy geometry (a revolved flange, a box minus a channel) and trips over
its own undefined names (`wall_thickness`, `outer_depth`, `chamfer_size`: 12 of the 22 exec
failures), i.e. it neither reads the sheet's features nor keeps a plan straight — the same
"cannot finish deciding" weakness the zero-shot probe showed, now without the runaway
reasoning. That is below the 0.3 kill line for the spike; it is also only 1,600 samples through
a 38M attention-only adapter, so the one experiment the user asked for — the 3-node run — gets
a properly sized attempt before closing: 600 steps x 12 samples on the union5 tier (8,887
rows, ~4.5x the data), rank 32, adapter also on the shared-expert MLP linears (`gate/up/down`
of `mlp.shared_experts`, FP8 like attention; the routed FP4 experts stay frozen). If that lands
under e55's first draw, DeepSeek is closed as a generator.
Profiling settles the cluster question: with the venv and Triton cache in node RAM the cluster
forward is still 90-190 s per sample while the backward is 11 s — and serv-04 on the very same
four rows does forward **1.1 s** (16.7 s for the first) and backward 10.8 s. The backward is
plain torch (my dequant matmuls) and is identical on both; only the Triton FP8 forward path
differs, by 100x, so it is kernel compilation/autotuning that never gets cached on the cluster,
not GPU speed (a diagnostic run with `FINEGRAINED_AUTOTUNE_TRIALS=1` and the autotune log is
queued). The scaled run therefore runs on serv-04: union5 tier, 600 steps x 8, lr 1e-4, r=32,
attention + shared-expert MLP targets (`spike_dsv41/lora_u5_r32_s600`, ~16 h), eval generations
scored on the cluster.
Root cause of the cluster slowness (torch profiler on one forward, job 10592288): GPU time
0.98 s total; **six CPU `index_select` calls of 15.4 s each = 92.6 s** — the two ~98 GB engram
n-gram tables, which transformers keeps in host RAM (`_no_placement_params`) and which stay
memory-mapped from the safetensors files, so every gather page-faults across Lustre; on serv-04
the same mmap is on local NVMe (forward 1.1 s). The Hub-kernel autotuner was innocent (its log
stayed empty with `FINEGRAINED_AUTOTUNE_TRIALS=1`). Fix: after loading, clone the engram
parameters off the mmap into RAM (~196 GB; the nodes have 1.5 TB) in both the smoke and the
trainer; profile job 5 verifies.
Profile job 5 confirms it: engram copy 189 GiB in 50 min (once per job), then **forward 1.2 s,
backward 10.8 s** per sample on ccc0451 — the cluster now matches serv-04. The 3-node scaled run
is submitted: 600 steps x (4 per node x 3 nodes) = 7,200 samples of the union5 tier, lr 1e-4,
r=32, attention + shared-expert MLP targets, ~48 s/step -> ~8 h plus 1.6 h startup, then the
96-part greedy eval sharded across the ranks and scored in-job with the main venv.

### 2026-09-17 — DeepCAD full pass scored: e55 solves 70% of 86,904 Onshape parts at K=8
Both cluster slices finished (venv in node RAM: 13-16 candidates/s per 120-worker node, ~6 h
each; 651,106 of 695,232 candidates executed, 2,226 IoU overlaps timed out at 90 s). Merged
(`deepcad/corpus_full/results_vllm/bo8_full_e55_vllm.json`, 86,904 parts): **first draw 0.739
mean / 55.8% >= 0.85; best-of-8 ceiling 0.854 mean / 70.3% >= 0.85 / 75.8% >= 0.80** — the
2,000-part gate (0.713 / 0.808) generalised. So roughly 61-66k DeepCAD parts have at least one
certified-quality solution to distil, ~30x the union5 real tier.
`write_rft_real` accepted **419,249 rows over 65,891 parts** (IoU >= 0.8; 277,004 distinct
samples after dedup) but timed out in its PNG loop — a per-key glob over the 87k-file render
dir on Lustre — so the last 12,939 sheets and `stats.json` were written by hand (one listing).
Packed: `rft_deepcad_e55/shards` = 139 shards. At R=1 that is 58% of the RFT draws, well past
the 35% the mix was designed for, so `build_deepcad_mix.sh` now takes an evenly spaced subset
of shards when the tier is oversized: `rft_mix_u8_deepcad_dw423` = 77 base + 25 union5 + 55
DeepCAD shards (~110k samples, 35%). **e58** submitted (`e58-rft-deepcad-dw423.sbatch`, one
H200 node, 4,000 steps); it queues behind the 3-node DeepSeek run.

### 2026-09-17 — DeepSeek-V4.1-Flash LoRA at scale on three H200 nodes: 0.136 vs e55's 0.435
The 3-node run (job 10593793, ccc0451/474/475, one pipeline-split replica per node, adapter
gradients averaged over NCCL/IB) trained cleanly: 600 steps x 12 samples = 7,200 union5 rows in
8.0 h at 48 s/step (startup 1.6 h: Lustre load + engram copy), loss 2.4 -> 0.26, r=32 on
attention + shared-expert MLPs (52.3M params). **96-part real-bench eval, greedy, scored
in-job: mean IoU 0.136, median 0.059, 0% >= 0.85, 5/96 >= 0.5 (best 0.82), 72/96 executed,
mean reply 634 chars** — against e55's first draw on the same 96 parts, **0.435 / 17.7%**
(`runs/dsv41_lora_r32_s600/eval.json`). Scaling from the 200-step adapter (1,600 samples,
0.051) to 4.5x the data and a wider adapter moved it to 0.136: a real slope, but the line would
need another ~10x to reach e55's first draw, i.e. the full RFT corpus for a 552B model at 48 s
per 12 samples, for a generator that then still has to beat the 27B's best-of-8 + verifier
serving stack. **DeepSeek-V4.1-Flash is closed as a generator.** What the spike leaves behind is
reusable: the checkpoint trains in transformers (`dsv41_autograd.py` for the Hub FP8/MXFP4 ops,
LoRA on `q_a/q_b/kv/o_b` + shared experts), the 3-node one-replica-per-node recipe with the
engram/venv/Triton staging, and the split generate-then-score eval. The serv-04 run (4,800
samples, same recipe) finishes next as a third point on the same curve.
The serv-04 run (4,800 samples, same r=32 recipe) scored **0.133 / 0% >= 0.85** on 48 parts
(36/48 executed) — the same as the 3-node run's 0.136 at 7,200 samples: the curve is flat
between 4.8k and 7.2k samples. Verdict unchanged.

### 2026-09-17 — cluster GPUs released: e58 moves to serv-04
The user asked for no more GPU work on the cluster (CPU work on the L40S nodes stays fine):
e58 (job 10595888, 2 h in) and the pending geom-eval were cancelled and the e58 eval chain
watcher stopped. e58 now trains on serv-04's 8x H200 with the same `run.sh` / FSDP2 path:
`env.sh` takes `DRAWING_VLM_ROOT` (serv-04: `/srv/scratch/bimrose2` with a `drawing_vlm -> .`
self-link), `serv19/launch_e58_serv04.sh` relinks the mix and disables the in-training geometry
eval (`--eval_every=0`; serv-04 cannot load OCP), and the venv there is pinned to the cluster's
transformers 5.15.1 / trl 1.10 / peft 0.20. Data pushed: the 137 mix shards (31 GiB), the two
eval caches, the 47 GB tars_v14_dw423 set and the 52 GB Qwen3.8-27B base. Post-training evals
will be split: generate on serv-04 (vLLM), execute/score/consistency on cluster CPUs.

### 2026-09-17 — render-and-compare (the user's idea): a label-free candidate score from the drawing itself
Draw every candidate with the sheet renderer and compare it with the INPUT drawing — no ground
truth needed, so it is usable at serving. Set-up on the cluster (CPU only, L40S node): `dw_venv`
(draftwright 0.4.23 + font patch, `sbatch/dw_venv_build.sh`), the renderer scripts copied to
`mech_step_to_drw/`, `geom/render_compare.py` + `sbatch/render_compare.sbatch` (venvs staged in
/dev/shm: 1,152 candidates in 14 min). Fidelity: ground-truth STEPs re-rendered under the part key
reproduce the bench sheets at **ink F1 0.998**, so the comparison is sound.
Result on the permissive 0.4.23 real bench (144 parts, e55 K=8; vote 0.533, verifier 0.542,
vote+verifier 0.547, ceiling 0.591):

| sheet score | Pearson vs true IoU | select by it | + vote + verifier |
|---|---|---|---|
| whole-sheet ink F1 (tol 3 px) | 0.46 | 0.514 | 0.540 |
| black geometry only, views matched (v2) | 0.59 | 0.519 | 0.543 |
| + one global scale per sheet pair (v3) | **0.67** | **0.529** | 0.542 |

Why the naive score is blunt: geometry is black but every annotation is blue, and the renderer
picks page zoom, title block and auxiliary views (section vs detail) along a geometry-dependent
random path — two candidates of one part get different px/mm and different extra views (same
`_vN`, different style). `geom/rc_metric2.py` therefore keeps black ink only, splits it into
views, matches them (Hungarian), fits one scale and compares silhouettes + linework.
Reading: as a **selector** it ties the agreement vote and does not add to vote+verifier — all three
label-free signals pick the same "typical" candidate and the K=8 selection headroom on this bench
is only ~0.05. 41 of 892 executed candidates failed to render (mean true IoU 0.47), a small
handicap. Its value is elsewhere: a 0.67-correlated GT-free reward, and above all the material
for a **visual repair turn** (input sheet with the candidate's views overlaid in red, per matched
view) — new information at test time, which is what raising the ceiling on hard parts needs.

**Repair turn — plan (2026-09-17).** Selection cannot pass the K=8 ceiling (0.591 on the real
bench); a repair turn adds information. Prototype: `geom/rc_overlay.py` paints the candidate's
linework in red on the input sheet, per matched view (example: a 0.83-IoU candidate's wrong pin
positions and spurious pockets are obvious at a glance). Matching views between two full sheets
is fragile because the candidate's own sheet carries different auxiliary views and zoom, so the
next version projects the candidate solid directly (build123d `project_to_viewport`, 0.3 s for
7 views vs ~8 s per sheet) into the input's standard views; the axis-to-view convention of the
sheet renderer gets calibrated once on ground-truth parts. Then: (1) repair tier = (overlay of a
wrong candidate + its code) -> a certified candidate of the same part, mined from the 695k
scored DeepCAD candidates and the real corpora; (2) train it into the RFT mix after e58;
(3) serving: when the gate fails, overlay the medoid and draw K repair candidates; judge by
gated / ceiling gains on the real benches.
**Real corpus 4.** CADBench holds 18,000 parts (DeepCAD, Fusion 360, ABC, a fourth STEP family,
MCB, Objaverse); 13,135 were never used here and 7,148 of those carry a STEP body
(`build_corpus4.py`, exclusion = every file_id in an existing manifest, so the held-out benches
stay held out). Stage 1 (prep at max 120 faces + 0.4.23 sheets) runs as a CPU job on ccc0442
(`sbatch/corpus_stage1.sbatch`); the K=8 solving pass waits for serv-04's GPUs after e58.

### 2026-09-18 — e58 verdict: the DeepCAD tier is inert on real parts (a third neutral tier)
Trained on serv-04 (4,000 steps, 13.5 h, the cluster GPUs having been released), evaluated by the
split chain (generate on serv-04's native vLLM, score + consistency on the L40S CPUs, verifier
gate back on serv-04). K=8, first-exec / consistency / gated / oracle:

| bench | e55 | e57 | **e58** |
|---|---|---|---|
| old 146-part real | 0.500 / 0.526 / 0.554 / 0.592 | 0.463 / 0.522 / 0.559 / 0.604 | **0.484 / 0.504 / 0.545 / 0.595** |
| permissive 0.4.23 (144) | 0.482 / 0.533 / 0.539 / 0.591 | 0.463 / 0.518 / 0.554 / 0.584 | **0.498 / 0.528 / 0.545 / 0.599** |
| full certified pool | 0.886 / 0.909 / — / 0.935 | 0.891 / 0.911 / — / 0.946 | **0.889 / 0.914 / — / 0.944** |

Every gap is inside the +-0.02 single-run noise: **65,891 DeepCAD parts (277k samples, 35% of the
RFT draws) bought nothing on out-of-distribution real parts** — and cost nothing in distribution
(gated 0.916 / 82% on the 1,030-part in-dist slice vs e55's 0.915 / 81%). By family on the
permissive bench e58 is 0.587 gated on Fusion360 (88) and 0.478 on ABC (56); the old bench splits
the same way. e55 remains the serving candidate.
**Why, and the rule it gives:** the tier was mined from parts e55 *already solved* — the full pass
scored best-of-8 0.854 / 70% >= 0.85, i.e. the accepted rows are the easy end of DeepCAD, and
DeepCAD's sketch+extrude idiom is narrower than the bench's ABC/Fusion parts. Together with e56
(borrowed reasoning: memorises, costs execution) and e57 (self-distilled hard real parts: neutral),
the pattern is now explicit: **distilling what the model can already do adds nothing, whatever the
source or the volume.** The remaining levers are a genuinely harder supervised signal (real parts
with ground-truth code the model cannot yet reproduce) and test-time mechanisms that add
information rather than data — the repair turn.

### 2026-09-19 — zero-shot repair fails; the corpus-4 hard-real tier; e59
**Zero-shot repair probe (e55, 140 permissive-bench parts).** `make_repair_bench.py` overlays the
candidate the gate actually served onto its drawing and asks for a correction
(`repair_probe_split.sh`; generation on serv-04, scoring on the L40S CPUs):

| | mean | >=0.85 |
|---|---|---|
| served pick (baseline) | 0.540 | 19.3% |
| repair, first draw | **0.515** | 18.6% |
| repair, best of 8 | 0.553 | 19.3% |
| original best-of-8 ceiling | 0.594 | 24.3% |

Net **-0.025**: 7 parts improved, 21 got worse. **e55 cannot read the overlay untrained** — as
expected, since nothing in its training looks like one. So the repair turn is only worth anything
with supervision, which makes the repair tier the decisive test rather than a guess.
**Repair tier** (`build_repair_tier.py`, `sbatch/build_repair.sbatch`): every failed candidate is
executed, drawn under its part key and painted over the drawing in red; the member carries the
overlay as its image, the failed code in a per-member `user.txt` prompt (new: `data_v14` reads it,
`collate_v14` uses it instead of USER_PROMPT) and the part's certified code as the target. The
failure range is matched to serving (`bad-max 0.78`, since the served pick averages 0.54, not 0.5):
**46,656 pairs** — 2,531 over 831 real parts (c1/c2/c3) and 44,125 over 27,149 DeepCAD parts.
**Real corpus 4 solved** (`solve_corpus_split.sh`: generate on serv-04, score on the cluster).
3,007 fresh CADBench parts, e55 K=8: **first draw 0.473 / 22% >= 0.85, best-of-8 0.648 / 41% >=
0.80** — against DeepCAD's 0.713 / 0.854 / 76%. These are bench-difficulty real parts, exactly the
harder signal e58 lacked; tier `rft_real_corpus4` = 1,230 parts / 5,069 samples.
**e59** (`rft_mix_u9_c4rep_dw423` = 77 base + 25 union5 + 12 corpus4 + 24 repair = 138 shards;
corpus4 9%, repair 17%) trains on serv-04. The two levers are read by different evals — corpus4 by
the normal benches, repair by the probe — so one run tests both without confounding.
**Trap fixed:** `repair_probe_split.sh` never stopped its vLLM server, which then held all 8 H200s
for 11.5 h. Every split driver now stops the server after generating and rsyncs `train_v14` to
serv-04 first (a client-side flag was missing there and the whole probe ran with no output).

### 2026-09-20 — repo cleanup (/projects was 88% full, 1.9 TB free, this account holding 10 TB)
Reclaimed without touching anything an experiment reads:
* **302 GB** — `runs/e58-rft-deepcad-dw423/checkpoint-500`, orphaned by the cluster job cancelled on
  09-17 when e58 moved to serv-04 (its real `final/` is there and e58 was already evaluated).
* **5.2 GB** — `geom/cleanup_intermediates.sh --apply`: 91,290 per-part renderer scratch dirs
  (`<corpus>/render/iso/<key>`, whose sheets were long since moved into `render/png`), plus 459
  generation checkpoints and per-GPU shard files, each only where the merged result that supersedes
  it exists. A `<stem>.shardN.json.partial.json` is matched against the run's merged `<stem>.json`.
* **576 MB** — `rft_corpus4.filt120`, the first corpus-4 prep at the old filters (759 parts, a
  subset of the 3,007 kept at `--max-faces 400 --max-aspect 40`).
**The big finding: every run `final/` is stored as float32 (355 F32 tensors/shard, 109 GB) while its
own `config.json` declares `torch_dtype: bfloat16`** — and every consumer loads bf16
(`train_sft_v14.py` passes `dtype=torch.bfloat16`; vLLM serves at the config dtype), so the fp32
mantissa is discarded at load in every path. `geom/shrink_final_bf16.py` +
`sbatch/shrink_finals.sbatch` re-save a final as bf16: each shard is cast, **verified tensor by
tensor for exact equality against the bf16 cast of the source**, and only then swapped in, so a
failure leaves the run untouched. 109 -> 54 GB per run, **~2.2 TB over the 43 runs**; the cost is
I/O-bound on Lustre (~45-60 min per run). Deleting the ~36 superseded runs outright would free
~3.7 TB instead but is irreversible, so it is the user's call; the load-bearing ones are e51 (the
verifier base), e55 (serving), e57, e58, e59.

## 2026-09-21 — Title-block presentation overrides (DW_DESIGNER / DW_DRAWING_NUMBER / DW_TOLERANCE)
`draw_generator._pick_title_block_meta` now honours `DW_DESIGNER` / `DW_DRAWING_NUMBER`, and the
draftwright call takes `tolerance=$DW_TOLERANCE` (passed through `draftwright_compose.render_svg`,
which forwards it to `build_drawing`). All three are unset for corpus renders, so training sheets
keep the seeded designer pool, the seeded `PROJ-nnnn` number and draftwright's own "ISO 2768-m";
they exist only for one-off presentation sheets. The general-tolerance cell fits ~22 characters at
A4 — "ALL UNITS MM · ISO 2768-m" overruns the cell divider, "ALL UNITS MM" sits centred.

Also: `conn_bench` is rebuilt at the STEP's native size. `Connector_Simple_bruh.STEP` measures
27 x 19 x 8 mm as supplied; the first sheets went through the corpus normalisation (longest edge
-> 80/81 mm) and so were ~3x oversized. At `--target-mm 27` the prep reports `scale: 1.0` and the
sheet carries the part's real dimensions (volume 2354 mm3, drawn 2:1 on A4).

## 2026-09-21 — No compute on the login node
Campus-cluster process control kills any login-node process past 30 min CPU/wall and mails the
account owner (it caught a filesystem-wide `find /` of mine). Renders, eval-cache builds, scoring,
image work and broad find/grep now go through `train_v14/serv19/cpu_run.sh` — an srun wrapper on
the wpk partition, node ccc0442 (L40S), default 8 cpus / 64 G / 2 h. The login node keeps only
editing, short greps, sbatch/squeue, rsync and the sleep-loop watchers.

## 2026-09-21 — connector result, e59 held-out, DeepSeek in-distribution
- conn_bench (Connector_Simple_bruh at true 27 × 19 × 8 mm), e55 best-of-8: first draw 0.366, agreement vote 0.378 = oracle. Five of eight draws byte-identical. Served pick is a 12-face rounded slab: sketch on Plane.XZ extrudes toward −Y, the model shelled it (8 → 5 mm) and aimed every cut at +Y, so all features missed. Recon + views under `data/conn_bench/recon/` (rendered via cpu_run.sh).
- e59-rft-c4-repair-dw423 held-out: ext 0.517 vote / 0.588 oracle, dw423p 0.513 / 0.591 — vs e55 0.526 / 0.592 and 0.533 / 0.591. Flat within noise. Its repair-probe rerun died "vLLM never ready" (12:40); not yet relaunched.
- DeepSeek-V4.1-Flash LoRA on the 96-part in-distribution pool (fullpool_dw423 certified): first-exec 0.169, 72/96 executed, 1 part >= 0.85 (Qwen rows ~0.9). `runs/dsv41_indist/eval.json` also holds 48 stale `F_*` generations with no GT in that bench; they score 0 and must be excluded (the headline 0.113 over 144 is wrong).
- runs/ cleanup (2026-09-21, "keep more runs for now"): staged into `runs/_trash/` — _smoke_e26, dsv41_profile{,2..5}, empty e58, and 12 superseded finals (e29, e37, e39-soup, e42, e43, e44, e45, e47, e49, e50, e53, e56; ~612 GB). Nothing deleted; `rm -rf runs/_trash` when ready. Kept: all milestones, served lineage, LoRA and verifier runs (40 run dirs). e8 fp32→bf16 conversion queued (job 10670017). e59's final lives only on serv-04.

## 2026-09-22 — why ABC parts score low; orientation and dimension-audit diagnostics; repair accept/reject
- **ABC is not a renderer failure.** 56/58 ABC parts render (2 refused: hole/pocket evidence checks). At matched fill, ABC ≈ Fusion (vote by fill bucket: <0.25: 0.32 vs 0.35; 0.25–0.45: 0.44 vs 0.55; 0.45–0.7: 0.72 vs 0.66; >0.7: 0.88 vs 0.80). ABC's deficit (0.479 vs 0.567 vote) comes from its part statistics: median 48 faces vs 14, fill 0.35 vs 0.44, 33% of parts with fill <0.25 (thin shells, furniture, pipes; IoU is unforgiving there), and the renderer's auto-dimensioning covers them less well: 0.17 dims/face vs 0.37, 2.2 unplaced dims per sheet (46% of sheets have some) vs 0.6, 6.4 lint warnings vs 2.2, 18 s vs 8 s render. corr(vote, fill) = +0.66 on ABC, +0.57 on Fusion; corr(vote, unplaced dims) = −0.31.
- **Orientation is not the failure class** (`geom/orient_dim_diag.py`, voxel-proxy IoU at 96³ under all 48 signed axis permutations; proxy corr +0.987 with exact IoU): only 2% of executed candidates gain >0.2 from a frame change; fixing orientation lifts the vote 0.567 → 0.579 and the oracle 0.627 → 0.640 on the 144-part real bench. The ring A_00941921 (axis along Y, model built it along Z, IoU 0.05) is a real but rare case.
- **Dimension audit** (sheet envelope callouts m_env_width/depth/dim_height vs candidate sorted extents; labels match the GT bbox within 5% on 133/133 sheets): at 10% tolerance passes 97% of candidates with IoU ≥ 0.85 and 44% of those < 0.5; passing candidates average 0.611 vs 0.313 failing. As a pre-filter it lifts first-execute 0.512 → 0.534 (≥0.85 17% → 19%) but does not lift the agreement vote (0.567 → 0.561): the vote already rejects what the audit rejects. Use it as a cheap sanity gate (the connector's 5 mm vs 8 mm pick fails it), not as a selector.
- **Repair accept/reject by render score** (rc_orig_e55_same_metric.json vs rc_repair_e59.json, same metric): repair draws score 0.494 vs the served pick's 0.340 because the repair prompt shows the model its own rendered sheet and it mimics the drawing's look, so the score is biased toward repairs. Best margin (+0.05) gives 0.560 vs 0.540 pick, 39 helped / 24 hurt; render-select over the 16-candidate pool 0.541. ≤ +0.02 — within best-of-8 noise. Repair oracle 0.614 remains unreachable label-free.
- Exec failures worth a serving fix: A_00989278 (80 mm shell, all 8 draws died on `fillet(all edges, R5.7)` with 5.5 mm walls) — no exec-error repair loop exists in serving, only in geom_eval.
- Conversion collision: shrink-r3 picked up e8 after e52 while shrink-finals 10670017 was already converting it (shrink_final_bf16.py rmtree's final.bf16 at start). `chmod a-w runs/e8-full-lowlr` guards the fp32 from being swapped/removed; rerun e8's conversion alone once both jobs are gone, then `chmod u+w`.

## 2026-09-22 (cont.) — ABC: shape is right, material and program size are wrong
- **Geometry-controlled regression** (144 parts, e55 vote): fill (+0.71, t 8.3) and log faces (−0.12, t −2.4) explain R² 0.40; with them in, being ABC is +0.11 (t 1.6, i.e. no ABC penalty) and the sheet-information terms (dims/face, unplaced dims, lint warnings) add R² 0.015, none |t| > 1.3.
- **Surface score** (`geom/shape_diag.py`, 20k samples, F@τ of the GT diagonal, bbox-centred; results/ext/shape_e55.json): vote picks score F@2% 0.650 ABC vs 0.668 Fusion and F@5% 0.859 vs 0.812; wrong gross shape (F@5% < 0.5) 4% ABC vs 15% Fusion. corr(GT relative thickness, IoU) +0.48 but with F@2% only +0.11. On the thinnest ABC parts (2V/A < 3% of max extent) IoU 0.28 at F@5% 0.90 and bbox within 3%.
- **Excess material** (`geom/thick_diag.py`, thin parts < 6%): candidate/GT volume ratio median 1.69 ABC, 1.87 Fusion (75th pct 3.8 / 2.8) with area ratio ≈ 1.05 — walls too thick or hollows filled. Same with or without a sheet label matching the GT thickness on ABC (mostly the envelope depth of plates); on Fusion a printed thickness helps (|log| 0.14 vs 0.45).
- **Idiom bug:** `offset(solid, amount=-t)` with no `openings` shrinks the solid (Box 80×40×60: 162,393 mm³ vs a 29,607 mm³ shell); only with openings is it a shell. 12% of ABC / 8% of Fusion candidates use the no-openings form (mean IoU 0.21 / 0.32 vs 0.34 / 0.45); only 14 vote picks, so ≤ +0.02.
- **Program size is flat:** vote-pick programs hold ~6 construction ops / 35 lines / 12 distinct numbers whether the GT has <12 or 50-100 B-rep faces, while the sheet's dimension count rises 4.5 → 10 (corr with log faces +0.43 vs +0.15 for ops). Base synthetic training programs: median 7 ops, p90 11, 42 lines; the real tiers are the model's own solutions, so nothing teaches longer programs. Example: the desk A_00953690 (1.4 mm panels, drawer pitches all dimensioned) came back as "shelled box with opening and pocket", every size rounded, IoU 0.07.
- **Renderer causal test** (`serv19/variant_bench_eval.sh`, `sbatch/render_variant.sbatch`, `geom/variant_compare.py`; e55 bo8, same parts and key-seeded layouts, paired bootstrap 95% CI):
  | sheet variant vs permissive bench | ABC vote | Fusion vote | ABC oracle | Fusion oracle |
  |---|---|---|---|---|
  | no dimensions (DW_AUTO_DIMS=0), 144 parts | 0.479→0.309 (−0.169 [−0.23,−0.11]) | 0.567→0.397 (−0.171 [−0.22,−0.12]) | −0.136 | −0.153 |
  | scale_policy=fallback, 110 parts | 0.456→0.421 (−0.035, ns) | 0.576→0.553 (−0.023, ns) | −0.026 | −0.014 |
  The model reads dimensions, and ABC gains exactly as much from them as Fusion does — ABC is not dimension-starved relative to Fusion. The fallback policy protects only "required" dims (unplaced per ABC sheet 1.42→1.28), costs view scale and refuses 34/146 parts; DRAW_FILL_VIEWS=0.45 leaves unplaced dims unchanged (2.16→2.29), so a "complete dimensioning" sheet cannot be produced by these knobs. ABC's unplaced dims are mostly slot length/width/pos (54 of ~120) on 7 very thin parts (fill 0.18, vote 0.28): ≤ +0.03 on ABC even if fully causal.
- **Verdict:** ABC parts are not too complex for the renderer. The deficit is (1) thin geometry that volume IoU punishes, where the model gets the envelope and surfaces right but adds material (thick walls, filled hollows), and (2) a program-size ceiling inherited from the synthetic corpus (~7 ops) that turns 50-face parts into generic templates. Levers: training programs with more operations on thin/shelled real parts (a converted-GT tier failed as memorisation in e56, so it needs the model's own long solutions or a curriculum), and a thickness/hollowness check (volume vs the sheet's printed wall thickness) as a repair trigger.

## 2026-09-22 (evening) — the program-length ceiling comes from RFT; e60 long-program tier
- **In-distribution too** (`geom/length_diag.py pool`, e59 bo8 on the certified pool, 1,027 parts): GT ops [0,5) → model 3 ops, first 0.913; [5,8) → 5.5, 0.805; [8,12) → 7, 0.738; [12,16) → 8, **0.588 first / 0.919 oracle**; ≥16 (n=7) → 8.5, 0.59 / 0.83. The model *can* write the long program (oracle) but its default is ~8 ops.
- **Longer draws are not better within a part** on the real bench (`length_diag.py within`): corr(ops, IoU) −0.06 ABC complex, +0.02 Fusion complex; the longest draw scores 0.03-0.04 below the median draw. Length-aware selection is dead.
- **RFT compresses length.** Base corpus (tars_v14_dw423, 370,819 train sheets): 10.0% have ≥ 12 ops. RFT tiers (60% of training draws): rft_strict90_all_dw423b median 6 ops, 2.9% ≥ 12; union5 median 5, 3.9%; corpus4 median 4, 1.1%. Self-training keeps what the model already solves, which is short programs.
- **e60** (`configs/e60-rft-synthlong-dw423.yaml`): corpus `synth_long` = 12,000 train sheets with GT ≥ 12 ops (`mech/benchmarks/build_synth_long.py`; eval residue 0 and holdout 7 excluded), e55 best-of-8 split over serv-04 (8 H200) and serv-20 GPUs 4-7 (`serv19/solve_corpus_2box.sh`), tier rft_synth_long = IoU ≥ 0.9, ≤ 2 draws per part; mix `rft_mix_u10_synthlong_dw423` = dw423b + union5 x5 + tier at ~25% of shard draws (`geom/build_synthlong_mix.sh`). Chain `logs/real/run_e60_chain.sh` ships, trains on serv-04 (~14 h) and runs `eval_run_split.sh`. Judge: real benches vote/oracle and ABC split vs e55/e57, full-pool parity, and model ops on [12,16) GT.
- **synth_long solve (2026-09-22):** 12,000 parts x 8 in 49 min on serv-04 + serv-20 GPUs 4-7; e55 first draw 0.602, best-of-8 0.814, 50.3% of parts >= 0.9; 79,421/96,000 executed. Tier rft_synth_long: 10,997 rows (IoU >= 0.9, <= 2 per part) over 6,037 parts, 6 shards, think kept on 100%. Tier programs: median 8 ops (p90 12), 17.4% >= 12 ops vs 2.9% in rft_strict90_all_dw423b; GT median 13, so e55 often reaches 0.9 with a shorter program and the tier shifts length only partway. Mix: 138 shards, synth_long 26% of draws. e60 training on serv-04 from 23:37 at 12.2 s/step (~13.5 h); first losses match e58/e59.
- Scoring note: score_generic.sbatch runs consistency_rerank after scoring; on a 96k-candidate RFT solve it made no progress in 3.5 h and a tier does not need it -- cancel once `[score] executed` is logged (the scored json is complete).

## 2026-09-23 — the real-part gap is not thinness: synthetic thin parts score like thick ones
`geom/fill_match.py` (e59 bo8, mean candidate IoU; GT fill = V / bbox V and relative thickness 2V/A / max extent):
| fill | synthetic n / mean / oracle | real n / mean / oracle |
|---|---|---|
| < 0.15 | 41 / 0.728 / 0.905 | 18 / 0.244 / 0.392 |
| 0.15-0.30 | 178 / 0.732 / 0.905 | 40 / 0.280 / 0.481 |
| 0.30-0.50 | 190 / 0.779 / 0.939 | 36 / 0.341 / 0.560 |
| 0.50-0.75 | 278 / 0.745 / 0.940 | 36 / 0.510 / 0.728 |
| > 0.75 | 339 / 0.867 / 0.973 | 14 / 0.694 / 0.886 |
By relative thickness the synthetic pool is flat (0.787 at < 3% to 0.795 at 12-25%) while real falls from 0.585 to 0.214. Reweighting the synthetic pool to the real fill mix moves it only 0.788 → 0.760 against real 0.389. So thin geometry and IoU harshness explain ~0.03 of a ~0.40 gap; at matched fill/thickness real parts lose 0.2-0.5. **Correction to 2026-09-22:** "thin parts that volume IoU punishes" is not the mechanism — the model draws thin *synthetic* parts fine. What differs is the shape vocabulary of real thin parts (multi-panel furniture, shells with internal structure, sheet-metal-like bodies) that Zero-To-CAD's families do not contain; the model maps them onto its nearest template (desk -> "shelled box with opening and pocket"). Program length is one symptom of that, not the whole cause. Drawing complexity is ruled out by the no-dims ablation.

## 2026-09-23 — moved off serv-04; family synthesis (Zero-to-CAD method, our vocabulary)
- **serv-04 is off-limits** (user, 2026-09-23). e60 was killed there at ~step 400 and restarted from scratch on serv-20 GPUs 4-7 (`configs/e60-rft-synthlong-dw423-s20.yaml`: `accelerate_fsdp2_4gpu.yaml`, grad-accum 16 = same 64-sample global batch; inputs shipped from the cluster by `sbatch/ship_train_serv20.sbatch`; launcher `serv19/launch_train_serv20.sh`; eval `serv19/eval_run_serv20.sh`; chain `logs/real/run_e60_s20_chain.sh`).
- **Zero-to-CAD's recipe** (arXiv 2604.24479): gpt-oss-120b in a CadQuery execute-and-validate loop (<= 10 turns x 100 attempts), dimension-free one-sentence descriptions from 65 mechanical-catalog categories, single connected solid, >= 7 faces. Multi-body is not our gap: 94% of real bench GT meshes are one body.
- **`mech/familysynth/family_synth.py`** — same method, our vocabulary, build123d, lab hub models (user: DeepSeek / Kimi / GLM 5.3, never gpt-oss). Stage 1: Kimi-K3 reads the sheet of a real training-side part e55 fails (corpus 4, best-of-8 < 0.5; `pick_seeds.py`) and writes a family name + 3 dimension-free descriptions (the part, two siblings). Stage 2: GLM-5.3 / DeepSeek-V4.1-Flash / Kimi-K3 round-robin, <= 6 repair turns, exec_harness + `validate_step.py` (one valid solid, >= 10 faces, 10-400 mm). Runs on serv-20 CPUs (the hub rejects cluster compute nodes). Traps: pass an explicit thinking budget (GLM otherwise thinks to max_tokens: 30k tokens / 4 min per turn); build123d's `is_valid` is a property here; /dev/shm -> disk needs shutil.move. Smoke: 5/6 accepted, mostly first turn, 33-239 faces; renders are real-looking knob, link plate, louvred grille. Pilot: 120 seeds -> 360 programs.
- **Hub usage attribution:** every hub request now carries `x-hub-user: bimrose2` (family_synth.py, teacher/hub_smoke.py, teacher/teacher_round.py); the router logs it as `hub_user` in serv-07 `/srv/scratch/claude-hub/usage.jsonl` (lab hosts otherwise land as key_name "lab-network" with no user). Concurrency caps per the user (final, "don't saturate the box"): Kimi-K3 <= 2, GLM-5.3 <= 4, DeepSeek uncapped; coder mix 6 DeepSeek : 2 GLM : 1 Kimi, 40 workers.

## 2026-09-23 — first-principles stage tests (offline part)
Pipeline = see the sheet -> infer the 3D structure -> write it as code -> select. Tests per stage (scripts `geom/fp_*.py`, outputs `results/firstprinciples/`):
- **H3 sheet ambiguity — rejected.** render_compare v3 (per-view silhouette + edge agreement with the input sheet) calibrated on correct candidates (IoU >= 0.9): of candidates at or above the correct median (v3 >= 0.914) 0% have IoU < 0.5; at >= p25 (0.752) 5.3% (ABC 16.7% of 30, Fusion 1.2% of 84). Mean v3 by IoU: 0.31 (<0.3), 0.39, 0.46, 0.60, 0.84 (>=0.9). Wrong candidates visibly contradict the drawing; the information is on the sheet.
- **H2 dimension transcription — real but second-order.** Share of printed values that appear as literals in the program (value, /2 or x2, 1%): real 0.407 vs synthetic 0.755; even correct real candidates (IoU >= 0.85) 0.561 vs 0.787. Cause: synthetic sheets are 94.9% round values (integer or .5), real 38.6%; the model copies round values (0.64 real / 0.77 synthetic) but non-round ones only 0.17 in BOTH pools, with 31% of real non-round values off by < 5% (rounded: 54.9 -> 55, 37.5 -> 40). Snapping near-miss literals to printed values (`fp_snap.py`, tol 8%, label-free) HURTS: voxel IoU 0.509 -> 0.464 (ABC 0.479 -> 0.371), 10.6% stop executing — without knowing which value belongs to which feature, snapping moves numbers to the wrong dimension. Lever, if any: train on non-round dimensions (random rescale of synthetic parts), not post-hoc repair.
- **H5 learning signal — large.** e55 best-of-8 on corpus 4 (3,007 real parts): RFT (>= 0.8) uses 40.9% of parts; 34.6% have a best draw in 0.4-0.8 with best-minus-median 0.23; 18.2% have best in 0.4-0.8 and >= 0.15 above their median. A relative/dense reward (GRPO-style on IoU) could learn from ~35% more real parts than RFT does.
- Running: H4 stage oracles (Kimi describes GT 3D views -> (a) e55 with the description, (b) DeepSeek writes code from description + printed labels, no image; `geom/fp_oracle.py`), H1 native resolution and H7 K=128 search (`serv19/fp_gpu_diag.sh`, queued behind e60 eval and the family pilot solve on serv-20 GPUs 4-7).

## 2026-09-24 — e60 flat; first-principles GPU tests; synthesized families reproduce the gap
- **e60 (long-program tier) is flat.** Old bench vote/gated/oracle 0.522 / 0.534 / 0.586 vs e55 0.526 / 0.554 / 0.592; permissive bench 0.524 / 0.546 / 0.590 vs 0.533 / 0.539 / 0.591; full pool cons 0.902 vs 0.909. It did NOT lengthen programs (GT 12-16 ops: model 7.5 ops vs 8.0) but first draw on those 59 parts rose 0.588 -> 0.667. Length as a lever is closed.
- **H1 resolution — rejected.** e55 served at native sheet resolution (max_pixels 2,457,600 vs 1,179,648 trained): mean candidate +0.001, vote -0.012, oracle +0.006 (all CIs span 0). Pixel-level perception is not the bottleneck.
- **H7 search — near misses, not answers.** 40 hard real parts (best-of-8 0.2-0.8), K=128: mean best 0.340 (K=1), 0.498 (8), 0.556 (32), 0.607 (128), ~+0.03 per doubling; >= 0.85 stays 0% to K=64 and 2% at 128. The correct program is not in the sampling distribution; search cannot close the gap.
- **H4 oracle b — language is a lossy channel.** DeepSeek-V4.1-Flash writing build123d from Kimi's description of the GT 3D views plus the printed labels (no image), 6 repair turns: 92/142 executed, voxel IoU 0.230 vs e55 vote 0.569 (beats e55 on 11% of parts). A verbal structural description does not carry enough geometry for a strong coder; it says nothing against e55's own understanding. Oracle a (e55 + description) rerun queued (first run started before Kimi finished the descriptions).
- **Synthesized families reproduce the gap with ground truth.** e55 on the 291 rendered family_pilot parts: first 0.264, best-of-8 0.475, 15% >= 0.8, 43% in 0.4-0.8 — as hard as real ABC — and every part has a verified GT program. This is a proxy real-gap benchmark on which GT-supervised and dense-reward experiments can be run and measured. Tier rft_family_pilot: 38 rows / 23 parts (pack fixed: read PNGs from the tier's own png dir).
- **H4 oracle a — e55 cannot use extra text.** e55 K=8 on the permissive bench with Kimi's GT-view structural description appended to the user prompt: vote 0.533 -> 0.468 (-0.065 [-0.092,-0.039]), mean candidate -0.046, oracle -0.029, exec 0.774 -> 0.722; ABC hurt more (vote -0.071). Like the ignored second image and the +1.2-point privileged hints, the RFT'd model cannot condition on a channel it never trained on, so H4 cannot split "can't see" from "can't express" through text. Remaining evidence favours expression: errors visibly contradict the sheet (H3), search yields near misses (H7), GT-backed synthesized families reproduce the gap.
- **Family scale-up started (2026-09-24 10:5x):** all 956 hard corpus-4 seeds (836 new, `seeds_scale1_s20.json`) -> serv-20 `familysynth/scale1` (Kimi describe at 2 concurrent ~7 h, then ~2,500 programs; caps Kimi 2 / GLM 4 / DeepSeek uncapped, x-hub-user bimrose2).
- **H6 overfit test launched (2026-09-24):** `configs/h6-overfit-family.yaml` — full FT from e55, 120 steps (~38 epochs) on 50 family GT programs (empty think = no-think rows, no augmentation); judged in no-think mode on the 50 trained and 50 seed-disjoint held-out family parts vs e55 (`mech/familysynth/build_h6.py`, `serv19/h6_chain.sh`).
- **Relative-tier delta experiment queued:** `geom/build_relative_tier.py` -> rft_rel_corpus4 = 543 corpus-4 parts whose best-of-8 is in [0.4, 0.8) and >= 0.15 above the part's median (best draw's own think + code). Three 300-step continued fine-tunes from e55 at lr 2e-6 (`configs/d{0,1,2}-delta-e55.yaml`, `geom/build_delta_mixes.sh`): d0 control (base + union5 x5), d1 + corpus-4 >= 0.8 tier, d2 + relative tier (each extra tier ~25% of draws). Judged on the permissive real bench (paired vs e55) and the held-out families (`serv19/delta_chain.sh`, after H6).
- **H6 result — capacity is not the limit; 50 parts memorise.** No-think K=8 (results/firstprinciples/h6/): trained 50 family parts e55 first 0.150 / best-of-8 0.343 / exec 59% -> h6 **0.985 / 0.994 / 98% >= 0.8 / exec 100%** (loss 9.68 -> 0.0004); held-out 50 (seed-disjoint) e55 0.212 / 0.416 / exec 65% -> h6 0.099 / 0.327 / exec 31%. e55 can learn real-vocabulary programs exactly from the drawing (contrast e54's 10/144 in think mode — that was the no-think format, not capacity), but 50 parts x 38 epochs is pure memorisation and damages unseen families. Open question = breadth: learning curve with ~2,000 family GT programs at normal epochs (scale-up running).
- Family scale-up progress (15:45): 827 descriptions, 460/2,481 programs with 75% accepted (effort control lifted acceptance from 59%).
- **H6b learning curve queued** (`serv19/h6b_chain.sh`, `mech/familysynth/build_h6b.py`): pool pilot + scale-up family parts, seed-split (pilot held-out seeds + 20% of the rest, <= 200 held-out parts), GT-code tiers of 500 and all training parts on top of the d0 control mix (~25% of draws), 300 steps from e55. Judged no-think on held-out families (primary), no-think and think on the real bench; baselines e55 and d0 in the same modes.

## 2026-09-25 — delta tiers flat; H6b: family GT generalises to real parts, but only in no-think mode
- **Delta fine-tunes (300 steps from e55, lr 2e-6; paired vs e55 on the permissive bench, vote):** d0 control 0.501 (-0.032 [-0.061,-0.005]), d1 +corpus-4 >= 0.8 tier 0.493 (-0.040), d2 +relative tier 0.489 (-0.043). Family held-out (pilot bench_held) best-of-8: e55 0.519, d0 0.529, d1 0.538, d2 0.511. Continued training from e55 costs ~0.03 by itself; neither threshold nor relative self-generated tiers add anything. **Partial-credit self-training closed** (no dense-reward RL build on this evidence).
- **H6b (family GT, empty think, ~25% of draws, 300 steps from e55)** — family scale-up gave 1,983 accepted / 2,481 programs, 1,806 rendered; seed-split into 1,655 train parts (718 seeds) and 200 held-out parts (139 seeds). No-think K=8 (first / mean / best-of-8 / exec):
  | model | held-out families | real bench (144) |
  |---|---|---|
  | e55 | 0.204 / 0.173 / 0.388 / 60% | 0.151 / 0.138 / 0.308 / 27% |
  | d0 control | 0.196 / 0.173 / 0.377 / 61% | 0.186 / 0.179 / 0.382 / 35% |
  | h6b N=500 | 0.235 / 0.194 / 0.455 / 57% | 0.202 / 0.207 / 0.446 / 41% |
  | h6b N=1,655 | 0.287 / 0.231 / 0.507 / 58% | 0.256 / 0.238 / 0.523 / 52% |
  Real bench no-think, paired vs e55: vote 0.275 -> **0.457 (+0.182 [+0.133,+0.230])**, ABC +0.249, Fusion +0.140; vs d0 the family tier is worth ~+0.115 vote. The curve is still rising steeply from 500 to 1,655 parts, on unseen families AND on real parts: unlike e54's 381-part real-GT tier, broad synthetic-family GT teaches transferable skill.
  **Think mode (serving) is flat:** h6b-n1655 vote 0.522 (-0.011 [-0.033,+0.009]), oracle 0.596, first 0.405 (+0.021); N=500 vote 0.507. Same format trap as e54: empty-think rows train the no-think route only. Pooling modes gives nothing at equal budget (oracle T4+N4 0.596 = T8 0.597).
- **Next (H6c, 2026-09-28):** move the family skill into think mode and scale the GT pool. (1) style-matched rationalized traces: DeepSeek-V4.1-Flash (sees the sheet; it accepts images on the hub, ~9 s/call) + the GT program, few-shot on e55's own terse numbered plans (350-1000 chars; e56's base-model plans were ~2,000 chars and off-style), `mech/familysynth/rationalize_family.py`; (2) self-distilled traces: h6b-n1655 in think mode on its own 1,655 training parts, keep IoU >= 0.8 (`serv19/h6c_gen.sh`, `mech/familysynth/tier_to_bench.py`); (3) scale: Zero-to-CAD-100k (Apache-2.0, CadQuery) translated to build123d by DeepSeek with a repair loop, accepted at centred IoU >= 0.95 vs the dataset's STL (`mech/familysynth/zerocad_translate.py`), pilot 200.
- Inspiration check, pzfreo/cadgenbench-build123d (CADGenBench submission harness): frontier agent + build123d-mcp tools, validate() after every change, prompt ranks absolute dimensions > feature set > form > cosmetics, writes a named dimension table before any geometry, and warns that covers/housings/castings are usually thin-walled shells, not solid blocks. It is an inference-time agent loop (no training); the relevant ideas for us are the dimension-table-first plan format and the thin-wall prior, both of which the rationalized traces can carry.

## 2026-09-28 — H6c: think-format family tiers (first pass)
All 300-step delta fine-tunes from e55 on the d0 control mix + tier (~25% of draws); think mode, K=8, permissive real bench, paired vs e55 (vote / oracle); control d0 = 0.501 / 0.572.
| run | tier | vote | oracle | ABC vote / oracle | family held-out think best-of-8 |
|---|---|---|---|---|---|
| h6b-n1655 | 1,655 GT, empty think | 0.522 | 0.596 | 0.457 / 0.543 | 0.521 (e55 0.483) |
| h6c-rat | 583 rationalized plans + GT | 0.511 | 0.599 | 0.474 / 0.551 (+0.024 [0.000,+0.048]) | 0.519 |
| h6c-ratnt | same 583 + 1,655 empty-think | 0.485 | 0.603 | 0.436 / 0.555 | 0.529 |
| h6c-self | 532 self-distilled think rows (319 parts) | 0.509 | 0.565 | 0.452 / 0.512 | 0.504 |
Reading: none beats e55 on vote; every family variant beats the d0 control on oracle (+0.03) and the rationalized ones lift ABC oracle ~+0.025, but the ~0.03 "delta tax" of continuing training from e55 (d0) eats it. Self-distilled traces are the weakest (they only cover the 19% of parts the model already solves in think mode — trainT best-of-8 0.536). **Bug:** h6c-rat/ratnt trained on a stale 583-plan copy of tier_rat (the first rationalizer pass lost 63% of plans to the 6k-token cap; the chain was relaunched before the fixed rerun finished). Rerun as H6c2 with the full 1,630-plan tier (`serv19/h6c2_train.sh`: rat2, rat2nt), then H6d (Zero-to-CAD) follows.
Hub: DeepSeek capped at 48 in flight total (user, 2026-09-28; `DS_CAP` semaphore in family_synth.py).

## 2026-09-29 — first-principles reset: closed-loop visual repair is the first positive test-time lever
- **H6c2 (full 1,630 rationalized plans):** vote 0.493 (-0.039 [-0.065,-0.015]) vs e55, oracle 0.582. The think-trace route for family GT is closed (four variants, all <= e55).
- **Reasoning:** the information is on the sheet (H3), but the pipeline is open-loop: the model never sees what its program draws. Test: DeepSeek-V4.1-Flash (hub, vision) repairs e55's vote pick on the permissive real bench, 2 rounds, exec-error feedback within a round (`geom/vis_repair.py`). Arm **vis** sees [target sheet, the sheet the current program draws (same renderer + layout seed)] + code; arm **blind** sees only the target + code.
  | 143 parts | start (e55 vote pick) | final | helped / hurt | best round |
  |---|---|---|---|---|
  | vis | 0.537 | 0.493 | 46 / 64 | 0.610 |
  | blind | 0.537 | 0.385 | 30 / 82 | 0.587 |
  Seeing the candidate's render is worth +0.11 over blind; untrained repair still net-hurts; best-round 0.610 exceeds e55's best-of-8 ceiling (0.591).
- **Label-free acceptance by render-compare v3** (every round rendered, `geom/vr_to_bo.py` -> render_compare.sbatch -> rc_metric2.py; v3 vs IoU Pearson 0.74 on this pool): keep the best-v3 repair only if its v3 beats the start's by a margin. Margin 0.05: **0.537 -> 0.569 (+0.032 [+0.005,+0.061])**, Fusion +0.050 [+0.013,+0.089], ABC +0.003; 35 helped / 20 hurt; stable over margins 0.02-0.10 (+0.030..+0.033). First statistically positive lever on the real bench since e55 — from an untrained repairer. (results/visrepair/)
- **In flight:** RP1 = trained visual-repair model (`serv19/rp1_chain.sh`): 4,321 wrong family-part draws rendered -> rows [target, candidate sheet] + REPAIR_PROMPT(code) -> GT program, empty think (`geom/pack_repair_shards.py`; data_v14 reads optional `cand.png` as a second image; vLLM `MM_LIMIT=2`), 300 steps from e55 on the d0 mix; judged by `geom/vr_serve.py` (e55 generates, rp1 repairs K=8) vs e55 zero-shot on the same prompt. Serving pairs e55 (first pass) with the repair model, so the delta tax on e55 does not apply. H6d (Zero-to-CAD GT, no-think) queued after it; its DeepSeek rationalization step dropped.
- **Render-guided repair search** (`vis_repair.py --adopt v3`: each round repairs the current program from its own render; a repair is adopted only if its v3 beats the current v3 by the margin; 4 rounds, margin 0.02): real bench 0.537 -> r1 0.549 -> r2 0.558 -> r3 0.562 -> **r4 0.570 (+0.034 [-0.001,+0.069], 53 helped / 27 hurt)**, still rising per round; Fusion **+0.067 [+0.019,+0.114]**, ABC -0.020; best round 0.644. Per-edit analysis: corr(dv3, dIoU) 0.61 Fusion vs 0.42 ABC; adopted ABC edits at margin 0.02 average -0.027 IoU (44% hurt) but +0.022 at margin 0.15; Fusion +0.070 -> +0.173. Since that analysis used bench labels, the margin is fixed at 0.1 a priori for a fresh 6-round run on the real bench AND on the 200 held-out family parts (start = e55 first-executing draw, 0.360) as the out-of-sample check (results/visrepair/{real,fam}_m10.jsonl).
- **Confirmation at the a-priori margin 0.1, 6 rounds** (DeepSeek 24 + 24 in flight):
  | | start | r1 | r2 | r3 | r6 | best round |
  |---|---|---|---|---|---|---|
  | real bench (143) | 0.537 | 0.569 | 0.592 | 0.603 | **0.606 (+0.070 [+0.039,+0.104]), 50 helped / 14 hurt** | 0.657 |
  | - Fusion (88) | 0.567 | 0.612 | 0.644 | 0.656 | **0.656 (+0.089 [+0.046,+0.137])** | 0.704 |
  | - ABC (55) | 0.487 | 0.500 | 0.508 | 0.517 | **0.526 (+0.039 [+0.004,+0.080])** | 0.581 |
  | held-out families (200, start = e55 first-exec) | 0.362 | 0.397 | 0.409 | 0.411 | **0.427 (+0.065 [+0.036,+0.096])** | 0.517 |
  Mostly converged by round 3. The real-bench result (0.606) is above e55's best-of-8 ceiling (0.591) and is the best real-bench number of the project; the family held-out run is out-of-sample for the margin choice. The pipeline is e55 (first pass, vote pick) -> [DeepSeek repair from target + own render -> v3-gated adopt] x 3-6. It depends on the hub; rp1 (trained repairer) is the in-house version.
- **Trap:** rp1_chain.sh / h6d_chain.sh reused `T` (the ssh helper's timeout variable) for a tier path, so every remote step failed ("vLLM never ready", no training) for ~2 h; fixed (TIER / TZ) and relaunched.

## 2026-09-29 — RP1: trained in-house visual repairer
- **rp1-delta-e55** (300 steps from e55, d0 mix + 3,880 repair rows from synthesized-family parts: [target sheet, sheet of a wrong h6b draw] + REPAIR_PROMPT(code) -> GT program, empty think; `serv19/rp1_chain.sh`). Served with vLLM `MM_LIMIT=2`, no-think, K=8 repairs of e55's vote pick (`geom/vr_serve.py`), real bench (143):
  | | start | first-exec repair | mean repair | best of start+K | exec |
  |---|---|---|---|---|---|
  | e55 zero-shot (same prompt) | 0.537 | 0.499 (4 helped / 27 hurt) | 0.417 | 0.553 | 78% |
  | rp1 | 0.537 | 0.429 (26 / 74) | 0.246 | **0.628** | 53% |
  rp1 proposes much better fixes (oracle 0.628 > e55's K=8 ceiling 0.591) but half its programs fail and it cannot rank them.
- **rp1 + render-compare v3 gate (one round, label-free):** margin 0.1 -> **0.577 (+0.040 [+0.018,+0.063])**, **ABC +0.058 [+0.019,+0.102]**, Fusion +0.029 [+0.004,+0.056]; margin 0.05 +0.042, 0.15 +0.032. First in-house (no hub) real-bench gain since e55, and the largest ABC gain of any method. (results/repair/rc_vs_rp1_v3.json)
- In flight: 3-round in-house loop (`serv19/rp1_loop.sh`, `vr_serve.py --rounds 3 --margin 0.1`) on the real bench + held-out families; H6d on cluster ccc0451; e55 K=4 on Zero-to-CAD parts (ccc0474, more repair rows); DeepSeek repair search on corpus-4 real parts (real-shape repair rows).
- **rp1 in-house loop, 3 rounds** (`serv19/rp1_loop.sh`: K=8 repairs per round rendered on serv-20 CPUs, adopt best-v3 if > current + 0.1): real bench 0.537 -> r1 0.557 -> r2 0.580 -> **r3 0.585 (+0.049 [+0.011,+0.089])**, ABC 0.487 -> 0.536, Fusion 0.567 -> 0.616, best 0.628; held-out families 0.362 -> **0.461 (+0.099 [+0.072,+0.127])** (DeepSeek search there: +0.065). Round-1 here (+0.020) vs the separately rendered one-round run (+0.040) = sampling noise between two K=8 draws. In-house loop recovers ~70% of the DeepSeek loop's real-bench gain (0.606) with no hub.
- **DeepSeek search on corpus 4** (2,108 real training parts, start = e55 first-exec < 0.8, margin 0.1, 3 rounds): 0.397 -> 0.458 (+0.061 [+0.052,+0.069]), 625 helped / 208 hurt — the loop's gain holds at scale. -> 1,577 real-part repair pairs (813 parts; target = best program found, inputs <= best - 0.1; `geom/build_c4_repair.py`) for **rp2** (`serv19/rp2_chain.sh`: family + corpus-4 repair tiers).

## 2026-09-29 — RP2: real-part repair rows make the in-house repairer beat the DeepSeek loop in one round
- **rp2-delta-e55** = rp1 recipe + 1,486 real corpus-4 repair rows (input = a weaker program from DeepSeek's search trajectory + its sheet, target = best program found; mixed ~1:1 with the 3,880 family rows), 300 steps from e55 on serv-20. One round, K=8, e55 vote pick start, real bench (143):
  | | first-exec repair | mean repair | best of start+K | exec | **v3-gated (margin 0.1)** |
  |---|---|---|---|---|---|
  | rp1 | 0.429 | 0.246 | 0.628 | 53% | 0.577 (+0.040) |
  | **rp2** | **0.552** | **0.423** | **0.680** | **72%** | **0.612 (+0.076 [+0.045,+0.107])** |
  rp2 gated by family: ABC 0.487 -> 0.540 (+0.053 [+0.010,+0.102]), Fusion 0.567 -> 0.658 (+0.090 [+0.049,+0.136]); margins 0.05 / 0.15 give +0.079 / +0.070. One in-house round beats the 6-round DeepSeek loop (0.606) and e55's K=8 ceiling (0.591). **Best real-bench result of the project, no hub at serving.** Serving = e55 (think, K=8, vote) -> render pick -> rp2 (no-think, 2 images, K=8) -> render repairs -> v3 gate.
- Lesson: the repairer learns mostly from real-shape repairs (the DeepSeek search on training parts is a teacher that needs no ground-truth code, only GT meshes).
- In flight: rp2 3-round loop (serv-20); rp2L (900 steps, cluster ccc0475); rp1 K=16 x 5 rounds (ccc0442); DeepSeek search on corpora 1+2 (~2,000 more real parts -> rp3 rows); e55 on Zero-to-CAD parts (ccc0474); H6d no-think eval (ccc0451).
- **Search budget (rp1, cluster ccc0442, K=16 x 5 rounds, margin 0.1):** real bench 0.537 -> r1 0.584 -> r2 0.603 -> r5 **0.614 (+0.077 [+0.041,+0.115])** (K=8 x 3: 0.585); Fusion +0.103, ABC +0.036; best 0.651. More repairs per round and more rounds both help. rp2 at K=16 x 5 queued.
- **H6d (cluster; family n1655 + 3,891 Zero-to-CAD translated GT, empty think, 300 steps from e55):** think vote 0.522 (-0.011 vs e55, flat); no-think vote 0.410 / oracle 0.466 (HF generator) vs h6b-n1655 0.457 / 0.523 (vLLM) and e55 0.275 / 0.308. Adding Zero-to-CAD GT did not extend the no-think curve (if anything diluted the family tier). **The no-think GT route is closed; repair is the lever.**
- **rp2 in-house loop, K=8 x 3 rounds (serv-20):** real bench 0.537 -> r1 0.590 -> r2 0.615 -> **r3 0.625 (+0.089 [+0.056,+0.123])**, Fusion 0.682 (+0.115), ABC 0.534 (+0.047); held-out families 0.360 -> 0.445 (+0.085). New best.
- **In-distribution safety (rp2, one round K=8, 295 random full-pool parts, e55 vote pick 0.925):** v3-gated margin 0.1 -> 0.929 (+0.004 [-0.005,+0.012]); ungated first-exec repair would be 0.872 (22 helped / 73 hurt). The gate leaves solved parts alone — the repair stage is safe to apply to every part. (results/repair/cluster/full300_rp2_r1.jsonl)
- **rp2 at K=16 x 5 rounds (cluster ccc0442):** real bench 0.537 -> r1 0.625 -> r3 0.632 -> **r5 0.644 (+0.107 [+0.072,+0.141]), 70 helped / 16 hurt**; ABC 0.487 -> 0.557 (+0.070 [+0.026,+0.117]), Fusion 0.567 -> 0.698 (+0.130 [+0.083,+0.179]); best 0.672. **Best configuration to date.**
- test_part.pdf (user's real SolidWorks drawing, 3 sheets, inches): run through the full pipeline per sheet (`sbatch/test_part_pipeline.sbatch`, reference model `data_ext/test_part/reference.py`, thickness measured from the side view = 1.00 in).
- **test_part.pdf result (2026-09-29) — the pipeline FAILS on a real customer SolidWorks sheet.** Reference: 8.780 x 8.780 x 1.00 in plate (223 x 223 x 25.4 mm), 4x dia .257 on 7.000 sq, 4x M8 tap on 3.68 sq, 2x 8.5 mm x 6 deep dowels, R.10 corners. e55 K=8 per sheet: every draft is a template plate 80-120 mm x 4-6 mm thick with invented bosses/ribs/hole circles; numbers are read but misassigned (sheet 3's 120 / 101.5 dowel dimensions became the plate size). Vote picks: shape-IoU 0.348 / 0.299 / 0.243 (absolute IoU 0.03-0.05). **The repair gate never fired: v3 = 0.000-0.016**, because rc_metric2 separates geometry (black) from annotations (blue) by colour — draftwright's convention — and on an all-black SolidWorks sheet dimensions, leaders, notes and title block all count as geometry. DeepSeek-V4.1-Flash zero-shot on sheet 1: 223 x 223 plan read correctly 3/3, thickness guessed (6.3-9.5 mm; only the side view gives 1.00 in) -> IoU 0.25-0.37.
  Causes: (1) sheet-style domain gap — every training and bench sheet is draftwright (mm, blue annotations, parts normalised to ~80 mm, one sheet); this one is inch/dual-dimension, black annotations, heavy notes/title block, 223 mm, information split over 3 sheets; (2) the v3 gate is style-specific. Fixes to try: render training sheets in varied styles (black annotations, inch + [mm] dual dims, true scale, notes, multi-sheet) and make the gate colour-independent (e.g. mask text/dimension lines by line-width/shape, or render the candidate in the input's style).
- **DeepSeek search on corpora 1 + 2** (margin 0.1, 3 rounds): c1 0.332 -> 0.381 (+0.050), c2 0.382 -> 0.475 (+0.093) -> 583 + 723 more real repair rows.
- **rp3** (rp2 tiers + corpora 1/2 rows; repair ~1/3 of draws, 3/4 of it real), K=8 x 3 rounds: real bench r1 0.614 / r3 **0.631 (+0.094 [+0.065,+0.125])** (rp2: 0.590 / 0.625), ABC 0.545 (+0.058), Fusion 0.685; families +0.091. Modest gain from more real rows (mostly in round 1).
- **test_part.pdf rendered by draftwright** (reference part, our sheet style): e55 vote pick IoU 0.915 (shape 0.953) vs 0.03-0.05 (shape 0.24-0.35) on the SolidWorks sheets -> the failure there is sheet style, not the part. rp2 (K=16 x 5) proposed a 0.998-IoU program in round 1 (v3 +0.084, just under the 0.1 margin) and adopted a 0.903 one in round 3 (v3 +0.119): near-correct parts are where v3 differences stop tracking IoU; a dimension-consistency check would help there.

## 2026-09-29 — DeepSeek-V4.1-Flash reopened: generator (think-format) + repairer LoRAs
- User goal: a fine-tuned DeepSeek **generator and repairer** that fit together on one 8x B300 box (two merged FP8 checkpoints at TP4 each, ~510 GB each, or one base + two LoRAs). Draftwright data only.
- **Why the September generator LoRA likely failed (H1):** it was trained in chat mode (no reasoning) — its 0.136 first draw matches **e55's own no-think first draw (0.151)**, while e55 thinking gets 0.384. The model was trained into the weak route. Fix: plan (e55's think.txt) in DeepSeek's reasoning span, `thinking_mode="thinking"`. **H2 (throughput):** backward (10.8 s) >> forward (1.2 s); LoRA only on layers >= 26 of 40 stops backward early.
- Trainer (`geom/dsv41_lora_train.py`): `cand.png` second image + per-row `user.txt` (repair rows, ~3.2k tokens), `think.txt` -> reasoning span with `--think` (~1.8k tokens, plan supervised), `--min-layer`. CPU encoding test passed for both.
- Quick tests in flight: (T0) hub DeepSeek zero-shot WITH brief reasoning on the real bench (never measured; the 0.093 probe had runaway reasoning); (T1) 1-node generator pilot `dsv41_gen_pilot_think` (union5 real RFT rows with plans, 150 x 8 samples, r32, layers >= 26) + greedy 48-part eval — vs September's no-think 200-step adapter 0.051 and e55 on the same 48 parts (all Fusion): draw-0 0.429 / first-exec 0.495; (T2) repairer LoRA on serv-20 GPUs 4-7 (`serv19/dsv41_rep_serv20.sh`, 2-step Blackwell smoke first), after rp4.
- Consensus vs v3 as repair selector (rp2 K=16 round-1 pool, 139 parts, `geom/rep_consensus.py`): v3 gate 0.627, medoid of pool 0.607, medoid of repairs 0.600, oracle 0.701 — v3 stays the selector (test_part's near-correct case was the exception).
- **T0 result — hub DeepSeek-V4.1-Flash zero-shot, brief reasoning (effort low, "do not deliberate"), one draw, real bench 143:** mean **0.308**, ABC 0.293, Fusion 0.318, 132/143 execute, 17 parts >= 0.8 — vs e55 first draw 0.384 (ABC 0.297), e55 no-think 0.151, September no-think LoRA 0.136. Untrained DeepSeek with reasoning already equals e55 on ABC; the September LoRA made it WORSE than zero-shot by removing reasoning. Strong support for H1 (format). (results/visrepair/ds_scratch_real.jsonl)
