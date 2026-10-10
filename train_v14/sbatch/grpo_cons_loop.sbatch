#!/bin/bash
#SBATCH --job-name=grpo-cons
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodelist=ccc0442
#SBATCH --cpus-per-task=32
#SBATCH --mem=300G
#SBATCH --time=48:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.out
# Vote (consistency medoid) for every GRPO real-bench eval (2026-10-06): pull results/grpo_eval/real_*.json from
# serv-20 every 15 min and run consistency_rerank on each one without a _consistency.json (needs ~300 G).
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; S20=wpk-serv-20.mechse.illinois.edu
source $DV/train_v14/env.sh; export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1; cd $DV
while true; do
  rsync -a "$S20:/srv/scratch/bimrose2/results/grpo_eval/real_*_s[0-9]*.json" results/grpo_eval/ 2>/dev/null
  for f in results/grpo_eval/real_*.json; do
    case $f in *_consistency.json|*.partial.json) continue;; esac
    c=${f%.json}_consistency.json; [ -f $c ] && continue
    echo "$(date '+%m-%d %H:%M') consistency $f"
    .venv/bin/python train_v14/geom/consistency_rerank.py $f $c > ${c%.json}.log 2>&1 || echo "failed $f"
  done
  sleep 900
done
