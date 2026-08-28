#!/bin/bash
#SBATCH --job-name=flashnext-prof
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --gres=gpu:H200:8
#SBATCH --mem=800G
#SBATCH --time=02:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.e%j
set -euo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/train_v14/env.sh
export FLASHNEXT_PLE_DIR=/dev/shm/flashnext_ple
bash $DV/train_v14/stage_ple_shm.sh
$DV/.venv_next/bin/python $DV/train_v14/geom/profile_flashnext.py
