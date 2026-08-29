#!/bin/bash
#SBATCH --job-name=v1-verifier-lora
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
# pack every scored candidate (idempotent) then train
[ -n "$(ls $DV/rft_scored_v1/shards/scored-train-*.tar 2>/dev/null)" ] || \
  OPENBLAS_NUM_THREADS=1 $DV/.venv/bin/python $DV/train_v14/geom/pack_scored_shards.py $DV/rft_scored_v1
export TRAIN_VENV=$DV/.venv_next
bash "$DV/train_v14/run.sh" "$DV/train_v14/configs/v1-verifier-lora.yaml"
