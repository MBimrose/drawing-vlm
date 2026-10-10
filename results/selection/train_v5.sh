#!/bin/bash
# verifier v5 (warm start from v3b) on ccc0451 GPU 7. Data under results/selection/v5data (a new top-level dir created on
# ccc0442 stayed invisible on ccc0451 for 30+ min - stale Lustre dentry; keep job inputs under dirs ccc0451 already lists).
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV
export CUDA_VISIBLE_DEVICES=7 TRAIN_VENV=/dev/shm/bimrose2/gf_11181389/venv
export DRAWING_VLM_SCORED_SHARDS=$DV/results/selection/v5data/train_${TAG:-c2}
export WANDB_MODE=${WANDB_MODE:-offline}
nvidia-smi --query-gpu=index,memory.used --format=csv | sed -n '1p;9p'
bash train_v14/run.sh train_v14/configs/v5-verifier-rl-warm.yaml > results/selection/train_v5.log 2>&1
echo "TRAIN V5 DONE $?"
