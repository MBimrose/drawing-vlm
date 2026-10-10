#!/bin/bash
# rft1 consolidation mix (2026-10-08): tier shards (4 x ~465 rows) x 22 links + a d0-mix subset (10 base dw423b + 3 union5
# shards, ~25k rows). Shard-uniform sampling -> tier ~62% of RFT draws; with rft_frac 0.8 / reasoning 0.1 / plain 0.1 the
# tier is ~50% of all draws and the e55 SFT/RFT mix the other ~50%.
set -euo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; T=$DV/results/guide/rft1/tier; O=$DV/results/guide/rft1/mix
python3 $DV/train_v14/geom/pack_rft_shards_dir.py $T --per-shard 465
mkdir -p $O; rm -f $O/rft-*.tar; i=0
for b in 0 8 16 24 32 40 48 56 64 72; do ln -s "$(readlink -f $DV/rft_mix_d0/rft-$(printf %05d $b).tar)" $O/rft-$(printf %05d $i).tar; i=$((i+1)); done
for u in 77 79 81; do ln -s "$(readlink -f $DV/rft_mix_d0/rft-$(printf %05d $u).tar)" $O/rft-$(printf %05d $i).tar; i=$((i+1)); done
nb=$i
for r in $(seq 1 22); do for f in $T/shards/rft-*.tar; do ln -s "$f" $O/rft-$(printf %05d $i).tar; i=$((i+1)); done; done
echo "mix: $nb e55-mix shards + $((i-nb)) tier links = $i"; ls -L $O | head -2; for f in $O/rft-00000.tar $O/rft-00010.tar $O/rft-00013.tar; do echo "$f $(tar tf $f | grep -c code.py) rows -> $(readlink $f)"; done
for f in $T/shards/rft-*.tar; do echo "$f $(tar tf $f | grep -c code.py)"; done
