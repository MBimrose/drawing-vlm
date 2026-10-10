#!/bin/bash
# rft1 consolidation SFT on ccc0475 GPU 3 (inside grpo-fast job 11182777, overlapping step). 2026-10-08.
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV
used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i 3)
[ "$used" -lt 2000 ] || { echo "GPU 3 busy ($used MiB) - abort"; exit 3; }
export CUDA_VISIBLE_DEVICES=3 TRAIN_VENV=/dev/shm/bimrose2/gf_11182777/venv
export OMP_NUM_THREADS=8 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export DRAWING_VLM_TARS=$DV/step_to_drw/wds_dataset/tars_v14_dw423
export DRAWING_VLM_EVAL_CACHE_V15=$DV/step_to_drw/wds_dataset/eval_cache_v15_dw423.pkl
export DRAWING_VLM_RFT_SHARDS=$DV/results/guide/rft1/mix
export WANDB_MODE=${WANDB_MODE:-offline}
echo "START $(date)"
bash train_v14/run.sh train_v14/configs/rft1-from-t10.yaml > results/guide/rft1/train_rft1.log 2>&1
echo "TRAIN RFT1 DONE $? $(date)"
