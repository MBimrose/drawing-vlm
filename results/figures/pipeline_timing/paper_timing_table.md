# Pipeline timing for the paper (SFT + GRPO, no repair)

Configuration: SFT + GRPO generator (Qwen3.8-27B), bf16, one copy per H200 on one 8×H200 node (vLLM data parallel 8,
wpk-serv-05, 21 Oct 2026). Per drawing: 8 candidates (1 greedy + 7 at T 0.7), execute each, pick the best
render-compare match. No verifier, no repair. Times are wall clock per drawing with 8 drawings in flight (light load,
so they are per-drawing latency rather than queueing). Sources: `throughput/bf16v3_plotpass_*.jsonl`,
`throughput/bf16v3_v3_*.jsonl`, `throughput/single_*.jsonl`.

## Table 1: time per drawing, mean ± std (s)

| Stage | Real parts (bench B, n = 280) | Synthetic parts (n = 1,027) |
|---|---|---|
| Generate 8 candidates | 9.9 ± 2.9 | 10.7 ± 2.3 |
| Execute candidates | 3.2 ± 0.5 | 3.2 ± 0.8 |
| Select (render-compare) | 8.9 ± 4.8 | 11.9 ± 21.4 |
| **Total, drawing to part** | **22.0 ± 6.4** (median 21.1) | **25.9 ± 22.0** (median 22.9) |
| Mean IoU | 0.677 | 0.943 |
| *Optional: repair (3 chains × 6 rounds)* | *+267.9 ± 142.9* | – |
| *Mean IoU with repair* | *0.680 → 0.706* | – |

Notes:
- Synthetic std is inflated by 7 of 1,027 drawings (193–315 s) where one candidate's drawing render hit the 300 s
  render timeout; without them the synthetic total is 24.2 ± 7.3 s.
- The repair rows come from the separate 20 Oct run with repair (verifier + render-compare starts, generator on
  2 GPUs and the rp3 repairer on 6, 6 drawings in flight), so they are not the same configuration as the rows above.
  Within that run, repair took IoU from 0.680 to 0.706 and the total from about 26 s to 294.3 ± 145.2 s.

## Table 2: throughput (bf16, render-compare pick)

| Deployment | Drawings in flight | Drawings / hour | Time per drawing (s) |
|---|---|---|---|
| 1 × H200 (one model copy) | 1 | 167 | 21.5 ± 5.0 |
| 1 × H200 | 8 | 1,053 | 25.3 ± 6.7 |
| 1 × H200 | 16 | 1,645 | 32.7 ± 7.8 |
| 1 × H200 | 32 | 1,688 | 55.0 ± 18.4 |
| 8 × H200 (one copy each) | 1 | 176 | 20.4 ± 7.3 |
| 8 × H200 | 8 | 1,001 (real) / 872 (synthetic) | 22.0 ± 6.4 / 25.9 ± 22.0 |
| 8 × H200 | 64 | 2,564 (real) | 71.9 ± 16.9 |
| 8 × H200 | 128 | 2,151 (synthetic) | 178.0 ± 27.8 |

Reading: one H200 saturates at about 1,650–1,700 drawings per hour. The 8-GPU node reaches only about 2,150–2,560 per
hour because its 128 CPU cores, which execute the candidates and render them for render-compare, run out first; the
GPUs are not the limit at the node level. With 8 copies and enough CPU the GPU-side ceiling would be about 8 × 1,650
≈ 13,000 drawings per hour. The full pipeline with repair served about 71 drawings per hour.

Accuracy checks of these settings (bench B, identical candidates re-scored offline, paired): render-compare alone vs
verifier + render-compare +0.002 [−0.004, +0.009]; FP8 vs bf16 serving +0.006 [−0.005, +0.018] (not used).
