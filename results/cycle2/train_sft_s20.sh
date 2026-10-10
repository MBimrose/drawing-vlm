#!/bin/bash
# Cycle-2 SFT on serv-20 (2026-10-09): train_v14 snapshot from the cluster (cycle2/train_v14, has lora_init_adapter),
# one B300.   GPU=<g> RFT=<shard dir> bash cycle2/train_sft_s20.sh <config.yaml> <log>
cd /srv/scratch/bimrose2
for g in ${GPU//,/ }; do
  used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $g)
  [ "$used" -lt ${MAXUSED:-2000} ] || { echo "GPU $g busy ($used MiB) - abort"; exit 3; }
done
export CUDA_VISIBLE_DEVICES=$GPU TRAIN_VENV=/srv/scratch/bimrose2/.venv DRAWING_VLM_ROOT=/srv/scratch/bimrose2
export OMP_NUM_THREADS=8 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export DRAWING_VLM_TARS=/srv/scratch/bimrose2/step_to_drw/wds_dataset/tars_v14_dw423
export DRAWING_VLM_EVAL_CACHE_V15=/srv/scratch/bimrose2/step_to_drw/wds_dataset/eval_cache_v15_dw423.pkl
export DRAWING_VLM_RFT_SHARDS=$RFT WANDB_MODE=offline
# cluster-default paths in data_v14.py -> serv-20 copies (legacy/bad-key files md5-identical to the cluster's)
export DRAWING_VLM_BUNDLE=/srv/scratch/bimrose2/data/v14_bundle DRAWING_VLM_TRACES_JSON=/srv/scratch/bimrose2/cycle2/wds/traces_v14.json
export DRAWING_VLM_BAD_KEYS=/srv/scratch/bimrose2/step_to_drw/wds_dataset/exec_bad_keys_v14.txt
export DRAWING_VLM_EVAL_CACHE=/srv/scratch/bimrose2/step_to_drw/wds_dataset/eval_cache_v14.pkl
echo "START $(date)"
taskset -c ${CORES:-200-231} bash cycle2/train_v14/run.sh $1 > $2 2>&1
echo "TRAIN DONE $? $(date)"
