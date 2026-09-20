#!/usr/bin/env bash
# Detached: once the bf16 conversions free the L40S node, build the corpus-4 repair tier so the
# next training round has more real-part repair pairs (corpus 4 is bench-difficulty geometry).
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV
ids=$(cat logs/real/shrink_rest.txt | tr " " "," | sed "s/^,//")
while [ -n "$(squeue -j $ids -h 2>/dev/null)" ]; do sleep 900; done
echo "$(date) conversions done; queueing the corpus-4 repair tier"
C=$DV/train_v14/mech/benchmarks/data/rft_corpus4
J=$(sbatch --parsable --job-name=repair-c4 \
  --export=ALL,BO=$C/results/bo8_rft_corpus4_e55-rft-real-u5-gt-dw423.json,BENCH=$C,OUT=$DV/rft_repair_c4,MAXPP=4,BADMAX=0.78 \
  $DV/train_v14/sbatch/build_repair.sbatch)
echo "$(date) repair-c4 job $J"
while [ -n "$(squeue -j $J -h 2>/dev/null)" ]; do sleep 300; done
[ -f $DV/rft_repair_c4/stats.json ] && python3 -c "
import json; d=json.load(open('$DV/rft_repair_c4/stats.json'))
print(f\"corpus-4 repair tier: {d['pairs_written']} pairs over {d['parts']} parts\")"
echo "$(date) AFTER CONVERSIONS DONE"
