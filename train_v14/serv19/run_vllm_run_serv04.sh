#!/usr/bin/env bash
# Serve any e-series final with vLLM on serv-04 (DP=8, one replica per H200) from a native venv.
#   MODEL=$DV/runs/<run>/final NAME=<run> [PORT=8100 DP=8 SEQS=64] bash run_vllm_run_serv04.sh
set -uo pipefail
DV=/srv/scratch/bimrose2
MODEL=${MODEL:?MODEL=<final dir>}; NAME=${NAME:?NAME=<served-model-name>}
# apptainer needs glibc >= 2.32 and serv-04 has 2.28, so vLLM runs natively from a venv:
# VLLM_BIN overrides; default .venv_vllm (fresh wheels), then the older vllm_env.
VLLM_BIN=${VLLM_BIN:-$( [ -x $DV/.venv_vllm/bin/vllm ] && echo $DV/.venv_vllm/bin/vllm || echo $DV/vllm_env/bin/vllm )}
export VLLM_ENGINE_READY_TIMEOUT_S=1800 HF_HUB_OFFLINE=1
exec $VLLM_BIN serve $MODEL --served-model-name $NAME \
    --host 127.0.0.1 --port ${PORT:-8100} \
    --data-parallel-size ${DP:-8} --tensor-parallel-size 1 \
    --reasoning-parser qwen3 \
    --gpu-memory-utilization ${GPU_UTIL:-0.90} --max-model-len 16384 --max-num-seqs ${SEQS:-64} \
    --limit-mm-per-prompt '{"image": 1}' --trust-remote-code
