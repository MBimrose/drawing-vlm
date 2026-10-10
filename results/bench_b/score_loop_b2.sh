#!/bin/bash
# Score + vote every GPU-7 eval as soon as its generation is done (serv-20 CPU, 16 workers, sequential).
cd /srv/scratch/bimrose2; O=bench_b/eval
say() { echo "$(date '+%m-%d %H:%M') $*"; }
for spec in ${SPECS:-benchb_rft1_rl2_s120 benchb_qwenbase}; do
  until [ -f $O/GEN_DONE_$spec ]; do sleep 60; done
  case $spec in real_*) GT=mech_benchmarks/ext_bench_dw423_perm/gt_meshes_v15;; *) GT=mech_benchmarks/bench_b/gt_meshes_v15;; esac
  [ -f $O/${spec}_consistency.json ] && continue
  say "scoring $spec"; bash bench_b/code/score_vote_s20.sh $O/$spec $GT
done
say "SCORE LOOP B DONE"
