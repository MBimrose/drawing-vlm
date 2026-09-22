#!/usr/bin/env bash
# e60 mix: re-packed base (rft_strict90_all_dw423b) + union5 x5 (the e57/e58/e59 structure) + the long-program
# synthetic tier (e55's own >=0.9 solutions to GT programs with >=12 ops), repeated so it is ~25% of shard draws.
# Rationale (RECIPE 2026-09-22): RFT tiers are 60% of training draws and hold median-6-op programs (2.9% >= 12
# ops vs 10% of the base corpus), which caps program length -- e55 writes ~8 ops for 12-16-op programs.
#   build_synthlong_mix.sh [out=rft_mix_u10_synthlong_dw423]
set -euo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; OUT=${1:-$DV/rft_mix_u10_synthlong_dw423}
BASE=$DV/rft_strict90_all_dw423b/shards; U5=$DV/rft_real_union5_dw423/shards; SL=$DV/rft_synth_long/shards
bash $DV/train_v14/geom/build_rft_mix.sh $OUT $BASE $U5 5
i=$(ls $OUT | wc -l); nb=$i; ns=$(ls $SL/rft-*.tar | wc -l)
R=$(python3 -c "print(max(1, round(($nb/3)/$ns)))")
for r in $(seq 1 $R); do for f in $SL/rft-*.tar; do ln -s "$(readlink -f "$f")" "$OUT/rft-$(printf %05d $i).tar"; i=$((i+1)); done; done
echo "$(basename $OUT): $i shards = $nb base+union5 + $((i-nb)) synth_long links ($ns shards x $R) -> $(python3 -c "print(f'{100*($i-$nb)/$i:.0f}%')") of draws"
