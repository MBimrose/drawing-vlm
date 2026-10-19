#!/bin/bash
# E59 (2026-10-18): Flash-Next 180B on the e55 recipe (configs/e59-flashnext-e55recipe.yaml), then the main-table
# eval of final + best_model (abl_lane.sh, K=8 on real / benchb / full) for the fair scale comparison against e55.
# Code = cluster train_v14 snapshot in fn55/train_v14; data paths = nemotron/env_nemo19.sh (e55 data, md5-checked).
#   setsid nohup bash fn55/train_e59.sh > fn55/logs/train_e59.log 2>&1 < /dev/null &
# Waits for the ablation lanes holding the GPUs (abl/LANE_DONE_e35fn, abl/LANE_DONE_e26fl). GPU 0 also holds the
# user's ~2.5 GB render server: shared, never touched.
set -uo pipefail
cd /srv/scratch/bimrose2
say() { echo "$(date '+%m-%d %H:%M') $*"; }
for w in abl/LANE_DONE_e35fn abl/LANE_DONE_e26fl ${EXTRA_WAIT:-}; do say "waiting for $w"; until [ -f $w ]; do sleep 60; done; done
sleep 60
for g in 0 1 2 3 4 5 6 7; do
  used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $g)
  lim=2000; [ $g = 0 ] && lim=3500
  [ "$used" -lt $lim ] || { say "GPU $g busy ($used MiB) - abort"; exit 3; }
done
source nemotron/env_nemo19.sh
export TRAIN_VENV=/srv/scratch/bimrose2/.venv FLASHNEXT_PLE_DIR=/dev/shm/flashnext_ple
bash fn55/train_v14/stage_ple_shm.sh models/Qwen3.8-Flash-Next
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 OMP_NUM_THREADS=8 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
mkdir -p $TRITON_CACHE_DIR
say "TRAIN START e59"
taskset -c ${CORES:-0-95} bash fn55/train_v14/run.sh fn55/train_v14/configs/e59-flashnext-e55recipe.yaml
rc=$?; say "TRAIN DONE rc=$rc"
R=runs/e59-flashnext-e55recipe
[ -f $R/final/config.json ] || { say "no final model - stop"; exit 1; }
NAME=e59 GPUS=0,1,2,3 TP=4 PORT=8731 MODEL=$R/final setsid bash abl/abl_lane.sh > abl/logs/lane_e59.log 2>&1 < /dev/null &
if [ -f $R/best_model/config.json ]; then
  NAME=e59best GPUS=4,5,6,7 TP=4 PORT=8732 MODEL=$R/best_model setsid bash abl/abl_lane.sh > abl/logs/lane_e59best.log 2>&1 < /dev/null &
fi
wait
say "E59 EVAL LANES DONE"
