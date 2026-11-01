| Serving | Selection | Test set | In flight | Drawings | Drawings/hour | Time per drawing (s) | Mean IoU |
|---|---|---|---|---|---|---|---|
| bf16 | verifier + render-compare | Real (40 of bench B) | 1 | 40 | 188 | 19.1 ± 4.4 | – |
| FP8 | verifier + render-compare | Real (40 of bench B) | 1 | 40 | 212 | 17.0 ± 5.3 | – |
| FP8 + n-gram speculation | verifier + render-compare | Real (40 of bench B) | 1 | 40 | 191 | 18.9 ± 6.9 | – |
| FP8 | render-compare | Real (40 of bench B) | 1 | 40 | 201 | 17.9 ± 6.7 | – |
| bf16 (paper), 1 x H200 | render-compare | Real (20 of bench B) | 1 | 20 | 167 | 21.5 ± 5.0 | – |
| bf16 (paper), 1 x H200 | render-compare | Real (120 of bench B) | 8 | 120 | 1053 | 25.3 ± 6.7 | – |
| bf16 (paper), 1 x H200 | render-compare | Real (120 of bench B) | 16 | 120 | 1645 | 32.7 ± 7.8 | – |
| bf16 (paper), 1 x H200 | render-compare | Real (120 of bench B) | 32 | 120 | 1688 | 55.0 ± 18.4 | – |
| bf16 (paper) | render-compare | Real (40 of bench B) | 1 | 40 | 176 | 20.4 ± 7.3 | – |
| bf16 (paper) | render-compare | Real (bench B) | 8 | 280 | 1001 | 22.0 ± 6.4 | 0.677 |
| bf16 (paper) | render-compare | Synthetic | 8 | 1027 | 872 | 25.9 ± 22.0 | 0.943 |
| bf16 (paper) | render-compare | Real (bench B) | 64 | 280 | 2564 | 71.9 ± 16.9 | 0.673 |
| bf16 (paper) | render-compare | Synthetic | 128 | 1027 | 2151 | 178.0 ± 27.8 | – |
| FP8 | render-compare | Real (bench B) | 8 | 280 | 1044 | 20.4 ± 7.3 | 0.673 |
| FP8 | render-compare | Synthetic | 8 | 1027 | 921 | 23.7 ± 18.0 | 0.942 |
| bf16 | verifier + render-compare | Real (bench B) | 64 | 280 | 2134 | 88.1 ± 19.4 | 0.678 |
| FP8 | verifier + render-compare | Real (bench B) | 64 | 280 | 2131 | 86.8 ± 18.8 | 0.684 |
| FP8 | render-compare | Real (bench B) | 64 | 280 | 2204 | 77.1 ± 18.0 | 0.669 |
| bf16 | verifier + render-compare | Synthetic | 128 | 1027 | 1819 | 214.8 ± 34.1 | – |
| FP8 | verifier + render-compare | Synthetic | 128 | 1027 | 1855 | 214.8 ± 35.2 | – |
| FP8 | render-compare | Synthetic | 128 | 1027 | 2004 | 195.6 ± 32.5 | – |
