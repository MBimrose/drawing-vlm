#!/bin/bash
#SBATCH --job-name=e58-rft-deepcad-dw423
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
# e55 recipe with the DeepCAD real-sequence tier (RECIPE "DeepCAD as a real-sequence tier").
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
export DRAWING_VLM_TARS=$DV/step_to_drw/wds_dataset/tars_v14_dw423
export DRAWING_VLM_EVAL_CACHE_V15=$DV/step_to_drw/wds_dataset/eval_cache_v15_dw423.pkl
export DRAWING_VLM_RFT_SHARDS=$DV/rft_mix_u8_deepcad_dw423
TRAIN=$DV/train_v14
bash "$TRAIN/run.sh" "$TRAIN/configs/e58-rft-deepcad-dw423.yaml"
