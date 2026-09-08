#!/bin/bash
#SBATCH --job-name=e55-rft-real-u5-gt-dw423
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
# e54 recipe on the draftwright-0.4.23 re-render (RECIPE "Training sheets re-rendered with draftwright 0.4.23").
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
export DRAWING_VLM_TARS=$DV/step_to_drw/wds_dataset/tars_v14_dw423
export DRAWING_VLM_EVAL_CACHE_V15=$DV/step_to_drw/wds_dataset/eval_cache_v15_dw423.pkl
export DRAWING_VLM_RFT_SHARDS=$DV/rft_mix_u6_gt_dw423
TRAIN=$DV/train_v14
bash "$TRAIN/run.sh" "$TRAIN/configs/e55-rft-real-u5-gt-dw423.yaml"
