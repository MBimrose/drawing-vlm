#!/usr/bin/env bash
# Serve any e-series final with vLLM on serv-04 (DP=8, one replica per H200), via the
# vllm-dsv41 apptainer image already on the box (rootless docker does not work there).
#   MODEL=$DV/runs/<run>/final NAME=<run> [PORT=8100 DP=8 SEQS=64] bash run_vllm_run_serv04.sh
set -uo pipefail
DV=/srv/scratch/bimrose2
MODEL=${MODEL:?MODEL=<final dir>}; NAME=${NAME:?NAME=<served-model-name>}
SIF=$DV/containers/vllm-dsv41.sif
export VLLM_ENGINE_READY_TIMEOUT_S=1800
mkdir -p $DV/tmp
exec apptainer exec --nv --bind $DV:$DV --bind /tmp:/tmp $SIF \
  vllm serve $MODEL --served-model-name $NAME \
    --host 127.0.0.1 --port ${PORT:-8100} \
    --data-parallel-size ${DP:-8} --tensor-parallel-size 1 \
    --reasoning-parser qwen3 \
    --gpu-memory-utilization 0.90 --max-model-len 16384 --max-num-seqs ${SEQS:-64} \
    --limit-mm-per-prompt '{"image": 1}' --trust-remote-code
