#!/bin/bash
#SBATCH --job-name=v4-verifier-e55-reg
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=96
#SBATCH --gres=gpu:H200:8
#SBATCH --mem=1400G
#SBATCH --time=24:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.e%j
set -euo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
if [ -z "$(ls $DV/rft_scored_union_e55/shards/scored-train-*.tar 2>/dev/null)" ]; then
  echo "no shards under $DV/rft_scored_union_e55/shards" >&2; exit 1
fi
export TRAIN_VENV=$DV/.venv_next
export DRAWING_VLM_SCORED_SHARDS=$DV/rft_scored_union_e55/shards
bash "$DV/train_v14/run.sh" "$DV/train_v14/configs/v4-verifier-e55-reg.yaml"
