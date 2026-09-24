#!/usr/bin/env bash
# Delta fine-tune mixes (continued training from e55, 2026-09-24): d0 control = base dw423b + union5 x5;
# d1 = d0 + corpus-4 IoU>=0.8 tier; d2 = d0 + relative tier (best-over-median, 0.4-0.8). Extra tier ~25% of shard draws.
set -euo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; BASE=$DV/rft_strict90_all_dw423b/shards; U5=$DV/rft_real_union5_dw423/shards
bash $DV/train_v14/geom/build_rft_mix.sh $DV/rft_mix_d0 $BASE $U5 5
for v in d1:rft_real_corpus4 d2:rft_rel_corpus4; do n=${v%%:*}; t=${v#*:}; O=$DV/rft_mix_$n
  bash $DV/train_v14/geom/build_rft_mix.sh $O $BASE $U5 5 >/dev/null
  i=$(ls $O | wc -l); ns=$(ls $DV/$t/shards/rft-*.tar | wc -l); R=$(python3 -c "print(max(1, round(($i/3)/$ns)))")
  for r in $(seq 1 $R); do for f in $DV/$t/shards/rft-*.tar; do ln -s "$(readlink -f "$f")" "$O/rft-$(printf %05d $i).tar"; i=$((i+1)); done; done
  echo "rft_mix_$n: $i shards ($ns $t shards x $R)"
done
