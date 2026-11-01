## Per-part mean face-type shares (each part weighted equally)

| set | n | plane | cylinder | cone | torus | sphere | bspline | parts with a hole-like concave cylinder | median fill | median aspect | median thin (min/max dim) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| plain | 1890 | 68.5% | 21.8% | 4.4% | 1.7% | 0.7% | 2.7% | 84% | 0.47 | 4.7 | 0.21 |
| eval_synth_step | 1027 | 67.4% | 25.6% | 3.2% | 1.1% | 1.0% | 1.6% | 91% | 0.58 | 5.3 | 0.19 |
| real144 | 144 | 56.1% | 33.0% | 3.5% | 5.8% | 1.6% | 0.0% | 74% | 0.35 | 3.5 | 0.29 |
| real144 [F] | 88 | 63.1% | 28.8% | 3.0% | 4.0% | 1.0% | 0.0% | 66% | 0.39 | 3.3 | 0.30 |
| real144 [A] | 56 | 45.0% | 39.6% | 4.4% | 8.4% | 2.6% | 0.0% | 86% | 0.32 | 4.3 | 0.23 |
| bench_b | 280 | 61.5% | 29.4% | 4.0% | 3.5% | 1.7% | 0.0% | 65% | 0.38 | 3.0 | 0.33 |
| bench_b [F] | 171 | 66.1% | 26.5% | 3.8% | 2.7% | 0.9% | 0.0% | 54% | 0.46 | 3.2 | 0.31 |
| bench_b [A] | 109 | 54.2% | 33.9% | 4.2% | 4.8% | 2.8% | 0.0% | 81% | 0.31 | 2.9 | 0.34 |
| pred_e55_benchb_vote | 279 | 65.1% | 23.8% | 4.8% | 1.9% | 2.4% | 1.9% | 66% | 0.59 | 3.2 | 0.31 |
| pred_e55_full_vote | 1023 | 68.4% | 25.0% | 3.5% | 1.0% | 0.9% | 1.2% | 92% | 0.60 | 5.3 | 0.19 |

## Paired vote pick vs GT (same part)

| model / bench | pairs | median fill pred / GT | pred fuller than GT | median faces pred / GT | pred fewer faces | genus exact | pred multi-solid | mean vote IoU |
|---|---|---|---|---|---|---|---|---|
| e55 benchb | 279 | 0.59 / 0.38 | 67% | 22 / 27 | 57% | 48% | 8.2% | 0.511 |
| e55 full | 1023 | 0.60 / 0.58 | 15% | 25 / 25 | 36% | 69% | 6.5% | 0.920 |
| glimmer benchb | 279 | 0.60 / 0.38 | 68% | 20 / 27 | 58% | 45% | 5.7% | 0.524 |
| glimmer full | 1026 | 0.60 / 0.58 | 15% | 23 / 25 | 39% | 69% | 6.3% | 0.920 |

### Vote IoU by GT fill tercile

- e55_benchb: fill <= 0.28: 0.282, fill 0.28-0.52: 0.499, fill > 0.52: 0.758
- e55_full: fill <= 0.43: 0.871, fill 0.43-0.75: 0.919, fill > 0.75: 0.972
- glimmer_benchb: fill <= 0.28: 0.279, fill 0.28-0.52: 0.512, fill > 0.52: 0.786
- glimmer_full: fill <= 0.43: 0.871, fill 0.43-0.75: 0.920, fill > 0.75: 0.969
