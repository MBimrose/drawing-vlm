#!/bin/bash
#SBATCH --job-name=rft-scored-gen
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=64
#SBATCH --gres=gpu:H200:8
#SBATCH --mem=800G
#SBATCH --time=24:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.e%j
# Verifier training data: 4 sampled candidates per part from the champion,
# EVERY candidate scored and logged (scored-*.jsonl), accepted ones also kept.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
export RFT_CKPT=$DV/runs/e24-rft/final RFT_RUN=e24-rft RFT_OUT=$DV/rft_scored_v1 RFT_MAX_ACCEPTED=20000 NODE_IDX=0
export RFT_EXTRA="--n-samples 4 --log-all --temperature 0.8"
bash $DV/train_v14/sbatch/rft_generate.sbatch
