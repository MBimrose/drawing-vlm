#!/bin/bash
#SBATCH --job-name=bo8-verifier
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=64
#SBATCH --gres=gpu:H200:8
#SBATCH --mem=800G
#SBATCH --time=08:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.e%j
# Best-of-8 with three selection policies on IDENTICAL candidates:
#   first_exec (current serving) vs verifier-reranked vs oracle (upper bound).
set -euo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
export OPENBLAS_NUM_THREADS=1
source $DV/train_v14/env.sh
source $DV/.venv/bin/activate
python $DV/train_v14/geom/bestofn_verifier_eval.py \
  --ckpt $DV/runs/e24-rft/final --kind hf --run e24-rft \
  --verifier $DV/runs/v1-verifier-lora/final --verifier-run v1-verifier-lora \
  --n 96 --k 8 --temperature 0.7 --batch 8 \
  --out $DV/results/bo8_verifier_e24.json
bash $DV/scripts/snapshot_results.sh || true
