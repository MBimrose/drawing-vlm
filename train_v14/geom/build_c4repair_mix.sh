#!/usr/bin/env bash
# e59 mix: re-packed base + union5 x5 + the corpus-4 hard-real tier + the repair tier.
# Shards are sampled uniformly (webdataset resampled=True), so proportions follow shard counts.
#   build_c4repair_mix.sh [out=rft_mix_u9_c4rep_dw423]
set -euo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; OUT=${1:-$DV/rft_mix_u9_c4rep_dw423}
BASE=$DV/rft_strict90_all_dw423b/shards; U5=$DV/rft_real_union5_dw423/shards; C4=$DV/rft_real_corpus4/shards
bash $DV/train_v14/geom/build_rft_mix.sh $OUT $BASE $U5 5
i=$(ls $OUT | wc -l); nb=$i
for r in 1 2 3 4; do for f in $C4/rft-*.tar; do ln -s "$(readlink -f "$f")" "$OUT/rft-$(printf %05d $i).tar"; i=$((i+1)); done; done
nc4=$((i-nb)); nb=$i
# repair, real corpora first (bench idiom), each repeated; then an evenly spaced DeepCAD subset
for r in 1 2 3 4; do for d in rft_repair_c1 rft_repair_c2 rft_repair_c3; do for f in $DV/$d/shards/rft-*.tar; do
  ln -s "$(readlink -f "$f")" "$OUT/rft-$(printf %05d $i).tar"; i=$((i+1)); done; done; done
SEL=$(python3 -c "
import sys, glob; fs = sorted(glob.glob('$DV/rft_repair_deepcad/shards/rft-*.tar')); n = 12
print(' '.join(fs[j] for j in sorted({round(k*(len(fs)-1)/max(1,n-1)) for k in range(n)})))")
for f in $SEL; do ln -s "$(readlink -f "$f")" "$OUT/rft-$(printf %05d $i).tar"; i=$((i+1)); done
nrep=$((i-nb))
echo "$(basename $OUT): $i shards = $(ls $BASE | wc -l) base + 25 union5 + $nc4 corpus4 + $nrep repair"
python3 -c "print(f'  corpus4 {100*$nc4/$i:.0f}%, repair {100*$nrep/$i:.0f}% of shards')"
