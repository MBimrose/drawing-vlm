#!/bin/bash
#SBATCH --job-name=e26-smoke
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=96
#SBATCH --gres=gpu:H200:8
#SBATCH --mem=1400G
#SBATCH --time=03:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.e%j

set -euo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
export TRAIN_VENV=$DV/.venv_next
export DRAWING_VLM_RFT_SHARDS=$DV/rft_all/shards
export FLASHNEXT_PLE_DIR=/dev/shm/flashnext_ple
bash "$DV/train_v14/stage_ple_shm.sh"
bash "$DV/train_v14/run.sh" "$DV/train_v14/configs/e26-flashnext-lora.yaml" --run_name=smoke-e26 --output_dir=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/runs/_smoke_e26 --max_steps=12 --eval_every=6 --eval_n=8 --eval_n_batches=2 --save_best=false
