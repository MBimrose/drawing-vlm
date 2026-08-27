#!/bin/bash
#SBATCH --job-name=e4-lora-r128-concise
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodelist=ccc0475
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
bash "$TRAIN/run.sh" "$TRAIN/configs/e4-lora-r128-concise.yaml"
