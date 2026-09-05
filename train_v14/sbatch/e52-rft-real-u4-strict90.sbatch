#!/bin/bash
#SBATCH --job-name=e52-rft-real-u4-strict90
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=96
#SBATCH --gres=gpu:H200:8
#SBATCH --mem=1400G
#SBATCH --time=48:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.e%j

set -euo pipefail
export DRAWING_VLM_RFT_SHARDS=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/rft_mix_u4_strict90
TRAIN=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/train_v14
bash "$TRAIN/run.sh" "$TRAIN/configs/e52-rft-real-u4-strict90.yaml"
