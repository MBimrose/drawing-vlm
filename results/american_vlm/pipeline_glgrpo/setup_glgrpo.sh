#!/bin/bash
# Glimmer FFT + vote + GRPO + visual repair (2026-10-29): S2 chains as pipeline/ (glS2) with starts from the gl1 step-180
# K=8 vote (step picked on real-144 + synthetic: real-144 vote 0.618, synthetic 0.900; bench B not looked at):
# make_vote_picks top-3 distinct -> 3 chains, K=16 x 6 rounds, same repairer (am-glimmer-rp3recipe). 24-key blocks
# glgS2_*, bench B first. Runs on ccc0474 (am_rp_cluster.sbatch MODEL=glgrpo) until STOP_h474 at STOP_AT, which frees
# the node for the Kimi-trace A/B sampling (ab-sample-b); the remaining synthetic blocks go on the next free node.
#   nohup bash setup_glgrpo.sh > logs/setup.log 2>&1 &   (login node: waits, then light json work + sbatch)
set -uo pipefail
P=$(cd $(dirname $0); pwd); A=$(dirname $P); DV=$(dirname $(dirname $A)); cd $P; mkdir -p logs
say() { echo "$(date '+%m-%d %H:%M') $*"; }
until [ -s $A/benchb_gl1s180_consistency.json ] && [ -s $A/benchb_gl1s180.json ]; do sleep 120; done
for b in benchb full; do
  $DV/.venv/bin/python $DV/train_v14/geom/make_vote_picks.py $A/${b}_gl1s180.json $A/${b}_gl1s180_consistency.json \
    $P/starts_gl1s180_$b || { say "make_vote_picks $b failed"; exit 1; }
  for r in 1 2 3; do python3 make_blocks.py starts_gl1s180_${b}_r$r.json glgS2_${b}_c$r; done
done
ls blocks | sed 's/\.json$//' | sort > blocks.txt; say "$(wc -l < blocks.txt) blocks"
J=$(sbatch --parsable --nodelist=ccc0474 --export=ALL,MODEL=glgrpo,NR=8,W=12 $A/pipeline/am_rp_cluster.sbatch); say "repair job $J"
STOP_AT=${STOP_AT:-2026-10-29 10:45}
while [ $(date +%s) -lt $(date -d "$STOP_AT" +%s) ]; do sleep 300; done
touch $P/h474/STOP_h474; say "STOP_h474 written (in-flight blocks finish, no new claims)"
