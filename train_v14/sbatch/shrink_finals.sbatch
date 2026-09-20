#!/bin/bash
#SBATCH --job-name=shrink-finals
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=250G
#SBATCH --time=48:00:00
#SBATCH --nodelist=ccc0442
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/real/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/real/%x-%j.err
# Re-save run finals as bf16 (lossless for every consumer here; halves each 109 GB checkpoint).
#   sbatch --export=ALL,RUNS="<run dir> <run dir> ..." shrink_finals.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV
for r in $RUNS; do
  echo "=== $r $(date)"
  $DV/.venv/bin/python $DV/train_v14/geom/shrink_final_bf16.py --run "$r" || echo "  FAILED $r"
  df -h $DV | tail -1
done
echo "SHRINK DONE $(date)"
