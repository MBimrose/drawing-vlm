# Rigid-alignment column (wpklab/meshalign) for every table cell

Centered = the tables' metric (bbox-centred exact IoU, stored value); aligned = max(centered, IoU after meshalign rigid ICP of the centred prediction onto the centred GT). Selection unchanged. flips = parts whose gain came from a >=90 deg rotation. (partial n) = repair chains still running.

| Model | Row | Synthetic centered | Synthetic aligned | Held-out centered | Held-out aligned | flips (syn / held-out) |
|---|---|---|---|---|---|---|
| Gemma 4 31B | FFT + vote + GRPO + repair | 0.932 | 0.942 (+0.010) | 0.630 | 0.659 (+0.029) | 20 / 37 |

Checks (recomputed centred IoU vs stored, |diff| > 0.02; unscored = exec/align timeout or not yet run):
- none
