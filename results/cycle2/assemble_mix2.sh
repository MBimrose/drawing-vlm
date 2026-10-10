#!/bin/bash
# serv-20: cycle2/mix = the 13 replay shards (cycle2/replay, = rft1 mix rft-00000..00012) + tier2_cad shards x R_cad +
# tier2_rp2 shards x R_rp2 (symlinks), R from cycle2/MIX_INFO (build_mix2.sh).
set -euo pipefail
cd /srv/scratch/bimrose2/cycle2
read NC RC NR RR STEPS < MIX_INFO
rm -rf mix; mkdir mix; i=0
for f in replay/rft-*.tar; do ln -s $PWD/$f mix/rft-$(printf %05d $i).tar; i=$((i+1)); done
for r in $(seq 1 $RC); do for f in tier2_cad/shards/rft-*.tar; do ln -s $PWD/$f mix/rft-$(printf %05d $i).tar; i=$((i+1)); done; done
for r in $(seq 1 $RR); do for f in tier2_rp2/shards/rft-*.tar; do ln -s $PWD/$f mix/rft-$(printf %05d $i).tar; i=$((i+1)); done; done
echo "mix: $i shard links (CADBench $NC x $RC, realpool2 $NR x $RR), steps $STEPS"
