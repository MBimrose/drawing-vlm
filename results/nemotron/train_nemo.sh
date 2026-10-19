#!/bin/bash
# Nemotron SFT launcher (2026-10-15). serv-19 (all 8 GPUs ours; GPU 0 holds a ~2.5 GB user process) or serv-20 (4-7).
#   [GPUS=0,1] [CORES=a-b] setsid nohup bash nemotron/train_nemo.sh <config.yaml> [--key=value ...] > nemotron/logs/<run>.log 2>&1 &
cd /srv/scratch/bimrose2
case $(hostname) in
  wpk-serv-19*) source nemotron/env_nemo19.sh; DEF=0,1,2,3,4,5,6,7 ;;
  *) source nemotron/env_nemo.sh; DEF=4,5,6,7
     case ",${GPUS:-$DEF}," in *,0,*|*,1,*|*,2,*|*,3,*) echo "refusing: serv-20 GPUs 0-3 are not ours"; exit 3;; esac ;;
esac
GPUS=${GPUS:-$DEF}
for g in ${GPUS//,/ }; do
  used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $g)
  lim=${MAXUSED:-2000}; [ $g = 0 ] && lim=${MAXUSED0:-3500}
  [ "$used" -lt $lim ] || { echo "GPU $g busy ($used MiB) - abort"; exit 3; }
done
export CUDA_VISIBLE_DEVICES=$GPUS OMP_NUM_THREADS=8 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
mkdir -p $TRITON_CACHE_DIR
echo "START $(date) host=$(hostname) gpus=$GPUS cfg=$1"
taskset -c ${CORES:-0-95} bash nemotron/train_v14/run.sh "$@"
echo "TRAIN DONE $? $(date)"
