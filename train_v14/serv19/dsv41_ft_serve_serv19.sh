#!/usr/bin/env bash
# Serve a merged fine-tuned DeepSeek-V4.1-Flash on serv-19 GPUs 4-7 (TP4+EP, port 8200), next to the vanilla replica
# (GPUs 0-3, port 8000). Same image/flags as launch_dsv41_flash.sh minus the API key and speculative decoding.
#   (on serv-19) bash dsv41_ft_serve_serv19.sh <merged dir> <served name> [port] [gpus]
set -uo pipefail
M=$1; NAME=$2; PORT=${3:-8200}; GPUS=${4:-4,5,6,7}; N=$(echo $GPUS | tr , '\n' | grep -c .)
H=/scratch/bimrose2/dsv41_flash; W=/scratch/bimrose2/dsv41_ft/writable_$PORT; mkdir -p $W/tmp $W/torch $W/vllm $W/numba $W/modules
export APPTAINER_TMPDIR=$W/apptainer_tmp; mkdir -p $APPTAINER_TMPDIR
exec apptainer exec --nv --cleanenv --bind /scratch/bimrose2:/scratch/bimrose2 --bind $W/torch:/root/.cache/torch --bind $W/vllm:/root/.cache/vllm \
  --bind $W/numba:/root/.cache/numba --bind $W/tmp:/tmp --env HOME=/root --env CUDA_HOME=/usr/local/cuda --env VLLM_DO_NOT_TRACK=1 \
  --env VLLM_ENGINE_READY_TIMEOUT_S=3600 --env CUDA_VISIBLE_DEVICES=$GPUS --env HF_HUB_OFFLINE=1 --env TRANSFORMERS_OFFLINE=1 \
  --env VLLM_WORKER_MULTIPROC_METHOD=spawn --env TMPDIR=/tmp --env VLLM_CACHE_ROOT=/root/.cache/vllm --env HF_HOME=/root/.cache/huggingface --env XDG_CACHE_HOME=/root/.cache --env TORCHINDUCTOR_CACHE_DIR=/root/.cache/torch/inductor --env TRITON_CACHE_DIR=/root/.cache/torch/triton --env PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
  $H/dsv41-flash-v0909.sif python3 -m vllm.entrypoints.openai.api_server --model $M --served-model-name $NAME \
    --host 0.0.0.0 --port $PORT --tokenizer-mode deepseek_v41 --reasoning-parser deepseek_v41 --mm-encoder-tp-mode data \
    --tensor-parallel-size $N --enable-expert-parallel --gpu-memory-utilization 0.80 --load-format safetensors \
    --max-num-seqs 64 --max-num-batched-tokens 32768 ${MAXLEN:+--max-model-len $MAXLEN} --limit-mm-per-prompt '{"image": 2}'
