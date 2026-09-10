#!/bin/bash
#SBATCH --job-name=gated-esc
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --gres=gpu:H200:1
#SBATCH --mem=250G
#SBATCH --time=6:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.err
# Verifier scoring for the in-distribution escalation subset (no split.json for the full pool).
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
export OPENBLAS_NUM_THREADS=1
R=e55-rft-real-u5-gt-dw423
STAGE_SHM=1 CUDA_VISIBLE_DEVICES=0 bash $DV/train_v14/geom/gated_step.sh \
  $DV/results/ext/bo32_esc_$R.json $DV/results/ext/bo32_esc_${R}_consistency.json \
  $DV/step_to_drw/wds_dataset/eval_cache_v15_dw423.pkl 32 none
