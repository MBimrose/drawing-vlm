#!/usr/bin/env bash
# Serve a Qwen3.8 drawing->CAD checkpoint (27B Qwen3_5ForConditionalGeneration or Flash-Next 180B Qwen4Exp) with vLLM on
# wpk-serv-19 (2026-10-17, results-table ablations). serv-19 has no vllm-dsv41.sif (that was serv-20), so this uses the
# Nemotron image (vLLM nightly-3f1bcfd8, registers both architectures). Same flags as run_vllm_e55_serv20.sh: qwen3
# reasoning parser, max-model-len 16384, one image per prompt.
#   MODEL=<dir> NAME=<served name> GPUS=1 TP=1 PORT=8701 setsid bash run_vllm_qwen_serv19.sh > log 2>&1 &
set -uo pipefail
DV=/srv/scratch/bimrose2
MODEL=${MODEL:?}; SIF=${SIF:-$DV/containers/vllm-nemotron-3f1bcfd8.sif}
export CUDA_VISIBLE_DEVICES=${GPUS:?}
export VLLM_ENGINE_READY_TIMEOUT_S=3600 TMPDIR=$DV/tmp
CUDA=/software/cuda-13.0
export APPTAINERENV_CUDA_HOME=$CUDA APPTAINERENV_PREPEND_PATH=$CUDA/bin APPTAINERENV_CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES
mkdir -p $DV/tmp
exec apptainer exec --nv --bind $DV:$DV --bind /tmp:/tmp --bind /software:/software $SIF \
  vllm serve $MODEL --served-model-name ${NAME:?} \
    --host 127.0.0.1 --port ${PORT:?} \
    --tensor-parallel-size ${TP:-1} --trust-remote-code \
    --reasoning-parser qwen3 \
    --gpu-memory-utilization ${GMU:-0.85} --max-model-len ${MLEN:-16384} --max-num-seqs ${SEQS:-128} \
    --limit-mm-per-prompt '{"image": 1, "video": 0}' ${VLLM_EXTRA:-}
