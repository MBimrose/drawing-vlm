#!/usr/bin/env bash
# Serve any vLLM-supported drawing->CAD checkpoint on wpk-serv-19 (2026-10-26 copy of run_vllm_qwen_serv19.sh for the American-VLM screen:
# Muse-Glimmer-30B, Gemma 4, ...). RPARSER picks the reasoning parser (qwen3 default; muse_glimmer, gemma4, nemotron_v3).
# Nemotron image (vLLM nightly-3f1bcfd8). Same flags as run_vllm_qwen_serv19.sh otherwise: max-model-len 16384, one image
# per prompt; model-specific processor options go in VLLM_EXTRA (Gemma 4: --mm-processor-kwargs {"max_soft_tokens":1120}).
#   MODEL=<dir> NAME=<served name> GPUS=0,1 TP=2 PORT=8901 RPARSER=muse_glimmer setsid bash run_vllm_any_serv19.sh > log 2>&1 &
set -uo pipefail
DV=/srv/scratch/bimrose2
MODEL=${MODEL:?}; SIF=${SIF:-$DV/containers/vllm-nemotron-3f1bcfd8.sif}
export CUDA_VISIBLE_DEVICES=${GPUS:?}
export VLLM_ENGINE_READY_TIMEOUT_S=3600 TMPDIR=$DV/tmp
CUDA=/software/cuda-13.0
export APPTAINERENV_CUDA_HOME=$CUDA APPTAINERENV_PREPEND_PATH=$CUDA/bin APPTAINERENV_CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES
mkdir -p $DV/tmp
RP=${RPARSER-qwen3}   # RPARSER= (set, empty) serves raw text: no reasoning parser (2026-10-27 parse check)
exec apptainer exec --nv --bind $DV:$DV --bind /tmp:/tmp --bind /software:/software $SIF \
  vllm serve $MODEL --served-model-name ${NAME:?} \
    --host 127.0.0.1 --port ${PORT:?} \
    --tensor-parallel-size ${TP:-1} --trust-remote-code \
    ${RP:+--reasoning-parser $RP} \
    --gpu-memory-utilization ${GMU:-0.85} --max-model-len ${MLEN:-16384} --max-num-seqs ${SEQS:-128} \
    --limit-mm-per-prompt "{\"image\": ${NIMG:-1}, \"video\": 0}" ${VLLM_EXTRA:-}   # NIMG=2: repairer (target + candidate sheet)
