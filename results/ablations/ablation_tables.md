## Paper results table

Real Test = held-out bench B (280 parts). Rows without "vote" are one draw (draw 0: greedy for Qwen, sampled for
DeepSeek); vote rows are the K=8 consistency vote; the repair rows are the full repair pipeline.

| Base model | Method | Synthetic Test Mean IoU (1,027) | Real Test Mean IoU (280) |
|---|---|---|---|
| Qwen3.8-27B | Off-the-shelf | 0.041 | 0.017 |
| Qwen3.8-27B | LoRA r64, attention only ¹ | 0.550 | 0.152 |
| Qwen3.8-Flash-Next (180B-A6B) | LoRA r64, attention + shared experts ² | 0.731 | 0.255 |
| DeepSeek-V4.1-Flash | Zero-shot, short reasoning ³ | 0.655 | 0.315 |
| DeepSeek-V4.1-Flash | Reasoning LoRA ⁴ | — | — |
| DeepSeek-V4.1-Flash | Self-training on own outputs ⁴ | — | — |
| DeepSeek-V4.1-Flash | GRPO (LoRA), short reasoning ⁴ | — | — |
| Qwen3.8-27B | Full fine-tune (FFT), vision frozen | 0.804 | 0.402 |
| Qwen3.8-27B | FFT + 8 Candidate Vote | 0.917 | 0.509 |
| Qwen3.8-27B | FFT + 8 Candidate Vote + GRPO ⁵ | 0.932 | 0.665 |
| Qwen3.8-27B | FFT + 8 Candidate Vote + Visual Repair | 0.949 | 0.664 |
| Qwen3.8-27B | FFT + 8 Candidate Vote + GRPO + Visual Repair ⁶ | 0.961 | 0.721 |
| Qwen3.8-Flash-Next (180B-A6B) | Full fine-tune (FFT), same recipe as the 27B FFT | 0.796 | 0.412 |
| Qwen3.8-Flash-Next (180B-A6B) | FFT + 8 Candidate Vote | 0.911 | 0.525 |
| Qwen3.8-Flash-Next (180B-A6B) | FFT + 8 Candidate Vote + GRPO ⁷ | 0.929 | 0.655 |
| Qwen3.8-Flash-Next (180B-A6B) | FFT + 8 Candidate Vote + Visual Repair ⁸ | 0.952 | 0.682 |
| Qwen3.8-Flash-Next (180B-A6B) | FFT + 8 Candidate Vote + GRPO + Visual Repair ⁸ | — | — |

¹ Attention-only was trained at r64 only; the r64–256 runs are all-linear LoRAs (0.548–0.552 / 0.159–0.166). All these
  LoRAs used the early traced-only data. A full fine-tune on that same data scores 0.566 / 0.147 (e1), so at
  matched data LoRA ties full fine-tuning; the gap to the FFT row is the later data and recipe.
² Earlier recipe (e24: before RFT rounds 2–5), adapter merged.
³ Up to 3 calls per sample, with answer-now / execution-error retries the Qwen rows do not get. Long reasoning (one draw,
  T 0.7, no token cap) was measured only on the real-144 dev bench: 0.299.
⁴ Measured only as one draw on the real-144 dev bench: 0.208 / 0.301 / 0.327. The reasoning LoRA and the self-training
  run were trained through the HF-forward bug fixed on 2026-10-07 (compressed attention ran sliding-window only). 0.327 is
  the best GRPO round, picked on that same bench (later rounds +0.024 / +0.004 over the untrained 0.291).
⁵ GRPO plus two expert-iteration rounds. Each round fine-tunes on the best program per hard real training part (the
  model's own samples and search outputs, kept at IoU ≥ 0.75 against ground truth), then runs a short GRPO. This is the
  generator the full system uses. Best GRPO-only checkpoint: 0.922 / 0.640.
⁶ The full system: 16 candidates, verifier pick, 3 repair chains, render-compare pick. Its plain 16-candidate vote
  before repair: 0.936 / 0.668.
⁷ The 27B's GRPO recipe (entropy floor), 200 steps, step picked on the real-144 dev bench + synthetic, plus one
  expert-iteration round that reuses the 27B's round-2 SFT data (the 27B ran two rounds, the second on data built from its
  round-1 model).
  GRPO alone: 0.898 / 0.612.
⁸ The 27B's repair pipeline with a Flash-Next visual repairer (full fine-tune of the Flash-Next FFT on the 27B repairer's
  data and recipe). The GRPO + repair row uses the 27B's verifier. Its 16-candidate vote before repair:
  — / —.

## Ablations on the main-table protocol

Cells: vote mean IoU (share of parts ≥ 0.85) / single greedy draw. — = not yet scored.

| Model | Synthetic (1,027) | Real-144 | Real held-out (280) |
|---|---|---|---|
| Qwen3.8-27B full FT, traced-only data (verified traces, no aug), 2k steps [e1] | 0.838 (64%) / 0.566 | 0.305 (6%) / 0.160 | 0.317 (4%) / 0.147 |
| Qwen3.8-27B LoRA r64, attention only (q/k/v/o), e1 data [e10] | 0.803 (60%) / 0.550 | 0.283 (6%) / 0.147 | 0.302 (5%) / 0.152 |
| Qwen3.8-27B LoRA r64 (all linear layers), e1 data [e3] | 0.834 (65%) / 0.552 | 0.295 (5%) / 0.131 | 0.340 (5%) / 0.164 |
| Qwen3.8-27B LoRA r128 (all linear layers), e1 data, xhigh effort, lr 2e-4 [e4] | 0.845 (66%) / 0.552 | 0.316 (6%) / 0.142 | 0.325 (5%) / 0.166 |
| Qwen3.8-27B LoRA r256 (all linear layers), e1 data [e9] | 0.843 (66%) / 0.548 | 0.289 (3%) / 0.141 | 0.324 (4%) / 0.159 |
| Qwen3.8-27B LoRA r64 (all linear layers), e2 data [e12] | 0.867 (72%) / 0.632 | 0.373 (8%) / 0.186 | 0.355 (4%) / 0.188 |
| Qwen3.8-27B full FT, all ~500k rows (no filters) [e2] | 0.888 (76%) / 0.653 | 0.378 (7%) / 0.221 | 0.401 (7%) / 0.213 |
| e2 + drop non-executing GT (~18%) [e16] | 0.888 (76%) / 0.721 | 0.437 (10%) / 0.253 | 0.424 (8%) / 0.270 |
| + certified reasoning traces (1:4), 6k steps [e22] | 0.919 (83%) / 0.704 | 0.426 (13%) / 0.248 | 0.431 (11%) / 0.214 |
| + RFT round 1: 60% own verified samples (STaR) [e24] | 0.901 (79%) / 0.768 | 0.456 (13%) / 0.304 | 0.449 (9%) / 0.302 |
| + RFT rounds 2-5, real-geometry tier, dw-0.4.23 sheets (e55) [e55ctl] | 0.917 (83%) / 0.804 | 0.516 (17%) / 0.390 | 0.509 (15%) / 0.402 |
| Qwen3.8-Flash-Next 180B-A6B full FT: e24 recipe + its own RFT round [e32fn] | 0.897 (78%) / 0.773 | 0.455 (15%) / 0.299 | 0.463 (9%) / 0.348 |
| Qwen3.8-Flash-Next 180B-A6B LoRA r64 (attention + shared experts), e24 recipe [e26fl] | 0.875 (72%) / 0.731 | 0.374 (7%) / 0.258 | 0.387 (8%) / 0.255 |
| Qwen3.8-Flash-Next 180B-A6B: e32 + low-lr polish (1.5k steps) [e35fn] | 0.902 (79%) / 0.783 | 0.465 (12%) / 0.342 | 0.453 (10%) / 0.335 |
| Qwen3.8-Flash-Next 180B-A6B full FT, e55 recipe (final) [e59] | 0.911 (81%) / 0.796 | 0.523 (18%) / 0.391 | 0.525 (15%) / 0.412 |
| Qwen3.8-Flash-Next 180B-A6B full FT, e55 recipe (best val checkpoint) [e59best] | 0.909 (81%) / 0.798 | 0.518 (19%) / 0.389 | 0.527 (17%) / 0.403 |
| Nemotron-3.5-Super 120B-A12B full FT, e55 recipe (+ think prefill) [nemoft_pf] | 0.897 (78%) / 0.790 | 0.489 (17%) / 0.384 | 0.497 (13%) / 0.364 |

## Paired deltas: vote [95% CI]; d0 = single greedy draw [95% CI]

| Comparison | Synthetic (1,027) | Real-144 | Real held-out (280) |
|---|---|---|---|
| e10 − e1 | -0.035 [-0.046,-0.023]; d0 -0.016 [-0.049,+0.015] | -0.023 [-0.054,+0.007]; d0 -0.013 [-0.051,+0.023] | -0.015 [-0.040,+0.012]; d0 +0.005 [-0.026,+0.038] |
| e3 − e1 | -0.004 [-0.014,+0.008]; d0 -0.014 [-0.047,+0.018] | -0.011 [-0.041,+0.020]; d0 -0.029 [-0.069,+0.007] | +0.023 [-0.003,+0.047]; d0 +0.017 [-0.018,+0.051] |
| e4 − e1 | +0.007 [-0.003,+0.017]; d0 -0.014 [-0.045,+0.017] | +0.011 [-0.018,+0.038]; d0 -0.018 [-0.058,+0.025] | +0.007 [-0.018,+0.032]; d0 +0.019 [-0.016,+0.054] |
| e9 − e1 | +0.005 [-0.005,+0.016]; d0 -0.018 [-0.050,+0.013] | -0.016 [-0.048,+0.013]; d0 -0.019 [-0.061,+0.025] | +0.007 [-0.018,+0.030]; d0 +0.012 [-0.022,+0.043] |
| e10 − e3 | -0.031 [-0.041,-0.020]; d0 -0.002 [-0.032,+0.028] | -0.012 [-0.044,+0.016]; d0 +0.016 [-0.025,+0.056] | -0.038 [-0.060,-0.016]; d0 -0.012 [-0.043,+0.022] |
| e12 − e2 | -0.021 [-0.030,-0.012]; d0 -0.021 [-0.048,+0.005] | -0.006 [-0.039,+0.028]; d0 -0.035 [-0.089,+0.019] | -0.046 [-0.072,-0.021]; d0 -0.025 [-0.062,+0.009] |
| e12 − e3 | +0.033 [+0.022,+0.044]; d0 +0.080 [+0.051,+0.109] | +0.078 [+0.035,+0.118]; d0 +0.055 [+0.010,+0.100] | +0.015 [-0.008,+0.040]; d0 +0.024 [-0.012,+0.060] |
| e16 − e2 | +0.001 [-0.008,+0.009]; d0 +0.068 [+0.042,+0.094] | +0.059 [+0.026,+0.092]; d0 +0.032 [-0.018,+0.082] | +0.023 [-0.002,+0.049]; d0 +0.057 [+0.021,+0.092] |
| e22 − e16 | +0.031 [+0.021,+0.040]; d0 -0.016 [-0.044,+0.012] | -0.011 [-0.042,+0.021]; d0 -0.004 [-0.052,+0.044] | +0.007 [-0.018,+0.030]; d0 -0.056 [-0.090,-0.022] |
| e24 − e22 | -0.018 [-0.026,-0.009]; d0 +0.064 [+0.037,+0.091] | +0.030 [-0.003,+0.064]; d0 +0.056 [+0.006,+0.108] | +0.018 [-0.005,+0.041]; d0 +0.088 [+0.050,+0.124] |
| e55ctl − e24 | +0.015 [+0.008,+0.023]; d0 +0.036 [+0.012,+0.061] | +0.060 [+0.026,+0.098]; d0 +0.086 [+0.036,+0.138] | +0.060 [+0.036,+0.086]; d0 +0.100 [+0.062,+0.139] |
| e32fn − e24 | -0.004 [-0.011,+0.003]; d0 +0.004 [-0.019,+0.027] | -0.001 [-0.033,+0.029]; d0 -0.005 [-0.053,+0.044] | +0.014 [-0.007,+0.035]; d0 +0.046 [+0.014,+0.079] |
| e26fl − e24 | -0.026 [-0.034,-0.018]; d0 -0.037 [-0.062,-0.011] | -0.082 [-0.122,-0.044]; d0 -0.046 [-0.096,+0.005] | -0.062 [-0.086,-0.037]; d0 -0.047 [-0.083,-0.010] |
| e35fn − e24 | +0.001 [-0.006,+0.008]; d0 +0.015 [-0.008,+0.037] | +0.009 [-0.019,+0.035]; d0 +0.038 [-0.008,+0.083] | +0.004 [-0.019,+0.027]; d0 +0.033 [-0.006,+0.072] |
| e32fn − e26fl | +0.022 [+0.014,+0.030]; d0 +0.042 [+0.017,+0.065] | +0.081 [+0.047,+0.120]; d0 +0.041 [-0.008,+0.091] | +0.076 [+0.050,+0.103]; d0 +0.093 [+0.061,+0.126] |
| e59 − e55ctl | -0.006 [-0.013,+0.000]; d0 -0.009 [-0.029,+0.012] | +0.006 [-0.020,+0.033]; d0 +0.001 [-0.046,+0.049] | +0.015 [-0.005,+0.034]; d0 +0.010 [-0.025,+0.048] |
| e59best − e55ctl | -0.008 [-0.014,-0.001]; d0 -0.006 [-0.026,+0.016] | +0.002 [-0.026,+0.030]; d0 -0.000 [-0.042,+0.039] | +0.018 [-0.004,+0.040]; d0 +0.001 [-0.035,+0.035] |
| nemoft_pf − e55ctl | -0.019 [-0.027,-0.012]; d0 -0.015 [-0.036,+0.006] | -0.028 [-0.062,+0.008]; d0 -0.005 [-0.048,+0.037] | -0.012 [-0.032,+0.006]; d0 -0.038 [-0.074,-0.004] |
