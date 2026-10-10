#!/bin/bash
# Cluster half of grpo_eval.sh (2026-10-06): pull one model's held-out partials from serv-20 and
# score them on the CPU node (score_generic.sbatch, no consistency pass). Login-node safe: rsync + sbatch.
#   bash train_v14/serv19/grpo_eval_score.sh <name> [<name> ...]
# Results: results/grpo_eval/{real,famheld,indh}_<name>.json; summarize with geom/grpo_eval_summary.py.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; S20=wpk-serv-20.mechse.illinois.edu
B=$DV/train_v14/mech/benchmarks/data; O=$DV/results/grpo_eval; mkdir -p $O
declare -A GT=( [real]=$B/ext_bench_dw423_perm/gt_meshes_v15 [famheld]=$DV/results/h6b/bench_held2/gt_meshes_v15
                [indh]=$B/fullpool_dw423/gt_meshes_v15 )
for name in "$@"; do
  for b in real famheld indh; do
    [ -f $O/${b}_$name.json ] && { echo "have $b $name"; continue; }
    rsync -a "$S20:/srv/scratch/bimrose2/results/grpo_eval/${b}_$name.shard*.json.partial.json" $O/ || { echo "no partials $b $name"; continue; }
    sbatch --parsable --job-name=gsc-${b}-$name --time=03:00:00 \
      --export=ALL,PARTIALS="$O/${b}_$name.shard*.json.partial.json",GT=${GT[$b]},OUT=$O/${b}_$name.json,WORKERS=40,NO_CONS=1 \
      $DV/train_v14/sbatch/score_generic.sbatch
  done
done
