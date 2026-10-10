#!/bin/bash
# verifier v5 data: GRPO-generator candidates (bank v3, mix_t10 s120 K=16 T=1.0) on TRAINING real parts, held-out bench excluded
set -euo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV; D=train_v14/mech/benchmarks/data
SRC="--src results/selection/bo16_c2_t10.json"; [ -f results/selection/bo16_c4_t10.json ] && SRC="$SRC --src results/selection/bo16_c4_t10.json"
O=rft_scored_rl_v5/shards_${TAG:-c2}; rm -rf $O
.venv/bin/python train_v14/geom/pack_scored_real.py --out $O --heldout $D/heldout_file_ids.txt \
  --png $D/rft_corpus2_dw423/render/png --png $D/rft_corpus4/render/png $SRC 2>&1 | tail -20
M=rft_scored_rl_v5/train_${TAG:-c2}; rm -rf $M; mkdir -p $M; i=0
for f in $O/scored-train-*.tar; do ln -s $DV/$f $M/scored-train-$(printf %06d $i).tar; i=$((i+1)); done
NEW=$i; NOLD=$(( (NEW + 1) / 2 ))     # old v3b pool at ~1/3 of the mix (anti-forgetting)
for f in $(ls rft_scored_real/shards/scored-train-*.tar | head -$NOLD); do ln -s $DV/$f $M/scored-train-$(printf %06d $i).tar; i=$((i+1)); done
for f in $O/scored-eval-*.tar; do ln -s $DV/$f $M/; done
echo "mix: $NEW new + $NOLD old train shards -> $M"; ls -la $M
