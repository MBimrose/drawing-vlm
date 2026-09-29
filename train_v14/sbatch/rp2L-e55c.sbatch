#!/bin/bash
#SBATCH --job-name=rp2L-e55c
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=96
#SBATCH --gres=gpu:H200:8
#SBATCH --mem=1400G
#SBATCH --time=20:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.e%j
set -euo pipefail
# RP2L: longer-trained visual repairer.
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
export DRAWING_VLM_TARS=$DV/step_to_drw/wds_dataset/tars_v14_dw423
export DRAWING_VLM_EVAL_CACHE_V15=$DV/step_to_drw/wds_dataset/eval_cache_v15_dw423.pkl
export DRAWING_VLM_RFT_SHARDS=$DV/rft_mix_rp2
bash $DV/train_v14/run.sh $DV/train_v14/configs/rp2L-e55c.yaml --model_id=$DV/runs/e55-rft-real-u5-gt-dw423/final --eval_every=0
