#!/bin/bash
# vote (consistency medoid) for real_rft1_s20 inside the ccc0475 overlap step (grpo-cons queue was ~2 h deep). 2026-10-08.
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV; source train_v14/env.sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
F=results/grpo_eval/real_rft1_s20.json; C=results/guide/rft1/real_rft1_s20_consistency.json
.venv/bin/python train_v14/geom/consistency_rerank.py $F $C > results/guide/rft1/real_rft1_s20_consistency.log 2>&1
echo "cons exit $?"
[ -f results/grpo_eval/real_rft1_s20_consistency.json ] || cp $C results/grpo_eval/real_rft1_s20_consistency.json
cp results/guide/rft1/real_rft1_s20_consistency.log results/grpo_eval/real_rft1_s20_consistency.log 2>/dev/null
