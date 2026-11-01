# DeepSeek-V4.1-Flash on the e55 recipe (dse55, queued 2026-10-21)

User request (2026-10-21): "queue up deepseek to run after any other experiments with the improved training recipe".

Every earlier DeepSeek fine-tune (reasoning LoRA, self-training) was trained through the HF-forward bug fixed on
2026-10-07: compressed attention ran sliding-window only. None of them was evaluated on the main-table protocol. dse55 is
the first DeepSeek fine-tune on the fixed trainer, and it uses the e55 data. It is evaluated exactly like the Qwen rows.

| | e55 (Qwen3.8-27B) | dse55 (DeepSeek-V4.1-Flash, 552B MoE) |
|---|---|---|
| Data | rft_mix_u6_gt_dw423 / v14_bundle / tars_v14_dw423 at 60/20/20, exec filter, image aug | same streams, filters and aug (`build_dsv41_e55_tier.py`), 256k fixed rows |
| Untraced rows | thinking mode, empty think | same (`--think-all`) |
| Prompt | SYSTEM_PROMPTS["detailed"] + USER_PROMPT | same (prompts.json, checked against vLLM by `dse55_promptcheck.py`) |
| Method | full FT, 4,000 x 64 rows, lr 6e-6 | LoRA r64 on attention (q_a/q_b/kv/o_b, layers >= 20), lr 1e-4, 16 rows/step, effort 25 |
| Budget | ~1 day on 8 GPUs | at most 48 h on serv-19 (two data-parallel 4-GPU replicas), at most 1 epoch of the tier |
| Eval | K=8 (draw 0 greedy + 7 at T 0.7 / top_p 0.95), think, 2400 tok, vote | same (`gen_openai_bo.py`, merged BF16-attention model in vLLM) |

DeepSeek cannot be fully fine-tuned on one 8-GPU box. A transformers pipeline replica needs 4 B300s, and one row keeps
one GPU busy at a time, so this run is a LoRA with a time cap. The row count is set from a 10-step timing smoke.

Pipeline: `train_v14/serv19/dsv41_e55_chain.sh` (serv-19, log `dsv41_e55/logs/chain.log`). Stages:
1. Build the tier (CPU).
2. Wait until Flash-Next fn1 and its evals are done.
3. Gates: the timing smoke, and the trainer-vs-vLLM prompt check.
4. Train (2 replicas).
5. Merge.
6. Serve 2 vLLM instances (TP4+EP).
7. Generate real / full / benchb into `abl/results/*_dse55`.

Scoring then runs on ccc0442 with `nemo_score.sbatch`, writing to `results/ablations`.

CPU encoding check (60-row test tier):
- The prompt is 1,134 tokens. Rows are about 1.7k tokens at the median, 4.7k at most.
- No row exceeds `--max-len` 6144.
- Untraced rows render as `<think></think>` followed by the code.

## Log
- 2026-10-21 23:54: chain launched; the 256k-row tier build started (nice 19, 12 workers). Waiting on the fn1 s200 eval.
- 2026-10-22 00:04: chain stopped before the GPU stages; the user put the Flash-Next visual-repair + GRPO rows first. The tier build kept running.
- 2026-10-22 01:05: tier done: 256,000 rows (rft 153,600 / reasoning 51,200 / plain 51,200; 200,142 with a plan), 77 GB.
- 2026-10-22 01:09: chain re-armed; it waits for `fnpipe/FN_DONE`, written by `fn_finish.sh` after the last Flash-Next repair chain.

**2026-10-27** Cancelled by the user before it started (American-VLM pivot): dsv41_e55_chain.sh waiter stopped on serv-19.
