#!/bin/bash
#SBATCH --job-name=e10-lora-attnonly
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=48
#SBATCH --gres=gpu:H200:4
#SBATCH --mem=700G
#SBATCH --time=48:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.e%j

set -euo pipefail
TRAIN=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/train_v14
bash "$TRAIN/run.sh" "$TRAIN/configs/e10-lora-attnonly.yaml"
