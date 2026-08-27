# Drawing→build123d fine-tuning recipe (v1, 2026-08-26)

The distilled, model-size-agnostic recipe from the e1–e24 sweep on
Qwen3.8-27B. Every ingredient here was validated in isolation (run in
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
  +0.05 IoU, beyond noise.) NEXT: also minus underdetermined sheets
  (unplaced_keys_v14.txt, 33% — untested, e23 candidate).
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

## Recommended big-model play

1. Prove the recipe fully at 27B (e22/e24 in flight).
2. Port to the largest ~30–50B-class sibling with vision in the lineage —
   single-node full FT, same data, LR per table: cheapest capability jump.
3. Only for the final production model, consider 70B via 3-node (slow) —
   or better, serve the 27B/50B champion behind best-of-N + repair, which
   measured cheaper per point of IoU than any size jump.
