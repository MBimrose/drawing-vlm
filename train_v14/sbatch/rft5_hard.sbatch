#!/bin/bash
#SBATCH --job-name=rft5-hard
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=96
#SBATCH --gres=gpu:H200:8
#SBATCH --mem=800G
#SBATCH --time=12:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.e%j
# HARD-PART CURRICULUM (RFT round 5): 8 samples per part at T=0.9, restricted to
# the 33.8k near-miss parts (best-ever IoU in [0.5,0.8)) that no model has solved.
# Targets the tail instead of resampling parts already solved 65% of the time.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
export RFT_CKPT=${RFT_CKPT:-$DV/runs/e24-rft/final} RFT_RUN=${RFT_RUN:-e24-rft}
export RFT_OUT=$DV/rft_v5_hard RFT_MAX_ACCEPTED=8000 NODE_IDX=${NODE_IDX:-0}
export RFT_EXTRA="--n-samples 8 --temperature 0.9 --log-all --only-keys $DV/hard_keys_near_v1.txt"
bash $DV/train_v14/sbatch/rft_generate.sbatch
