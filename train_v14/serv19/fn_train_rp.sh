#!/bin/bash
# Flash-Next visual repairer FNRP (2026-10-22): the rp3 recipe on e59/final (configs/fnrp-flashnext-rp3recipe.yaml), serv-19
# all 8 GPUs, after the Flash-Next GRPO evals (fn_eval_grpo.sh "GRPO EVALS DONE fn1"). Code = fn55/train_v14 (the e59
# snapshot) + the config; data = nemotron/env_nemo19.sh (e55 paths) with the RFT tier swapped for rft_mix_rp3.
#   setsid nohup bash fn55/fn_train_rp.sh > fn55/logs/train_fnrp.log 2>&1 < /dev/null &
# GPU 0 also holds the user's ~2.5 GB render server: shared, never touched.
set -uo pipefail
cd /srv/scratch/bimrose2
say() { echo "$(date '+%m-%d %H:%M') $*"; }
say "waiting for the fn1 checkpoint evals"
until grep -q "GRPO EVALS DONE fn1" fn55/logs/eval_grpo_fn1.log 2>/dev/null; do sleep 120; done
for i in $(seq 1 60); do
  busy=0
  for g in 0 1 2 3 4 5 6 7; do
    used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $g); lim=2000; [ $g = 0 ] && lim=3500
    [ "$used" -lt $lim ] || busy=1
  done
  [ $busy = 0 ] && break; sleep 30
done
[ $busy = 0 ] || { say "GPUs still busy - abort: $(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader | tr '\n' ' ')"; exit 3; }
source nemotron/env_nemo19.sh
export DRAWING_VLM_RFT_SHARDS=/srv/scratch/bimrose2/rft_mix_rp3
export TRAIN_VENV=/srv/scratch/bimrose2/.venv FLASHNEXT_PLE_DIR=/dev/shm/flashnext_ple
bash fn55/train_v14/stage_ple_shm.sh models/Qwen3.8-Flash-Next
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 OMP_NUM_THREADS=8 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
mkdir -p $TRITON_CACHE_DIR
say "TRAIN START fnrp (RFT tier $(ls $DRAWING_VLM_RFT_SHARDS | wc -l) shards)"
taskset -c ${CORES:-0-95} bash fn55/train_v14/run.sh fn55/train_v14/configs/fnrp-flashnext-rp3recipe.yaml
rc=$?; say "TRAIN DONE rc=$rc"
[ -f runs/fnrp-flashnext-rp3recipe/final/config.json ] || { say "no final model - stop"; exit 1; }
touch fn55/FNRP_DONE
say "FNRP DONE"
