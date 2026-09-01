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
| e28 ckpt-4500 | 27B | RFT v1+v2 (123k), 6000 steps | 0.837 |
| e33 ckpt-3500 | 27B | curated RFT tier (v1+v4+v5hard, 68k), 4000 steps | 0.833 |
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
