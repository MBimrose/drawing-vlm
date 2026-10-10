#!/usr/bin/env bash
# Run geom/dsv41_vllm_layerdump.py inside the vLLM image on serv-19 GPUs 4-7 (same binds/env as dsv41_ft_serve_serv19.sh).
#   bash dsv41_vllm_layerdump.sh <ref.json> <n tokens> <out prefix> [model dir]
set -uo pipefail
H=/scratch/bimrose2/dsv41_flash; W=/scratch/bimrose2/dsv41_ft/writable_8200; mkdir -p $W/tmp $W/torch $W/vllm $W/numba
BASE=${4:-$(ls -d $H/models/models--deepseek-ai--DeepSeek-V4.1-Flash/snapshots/*/ | head -1)}
export APPTAINER_TMPDIR=$W/apptainer_tmp; mkdir -p $APPTAINER_TMPDIR
exec apptainer exec --nv --cleanenv --bind /scratch/bimrose2:/scratch/bimrose2 --bind $W/torch:/root/.cache/torch --bind $W/vllm:/root/.cache/vllm \
  --bind $W/numba:/root/.cache/numba --bind $W/tmp:/tmp --env HOME=/root --env CUDA_HOME=/usr/local/cuda --env VLLM_DO_NOT_TRACK=1 \
  --env CUDA_VISIBLE_DEVICES=4,5,6,7 --env HF_HUB_OFFLINE=1 --env TRANSFORMERS_OFFLINE=1 --env VLLM_ALLOW_INSECURE_SERIALIZATION=1 --env PYTHONPATH=/scratch/bimrose2/train_v14/geom --env VDUMP_IMAGE=${VDUMP_IMAGE:-} \
  --env VLLM_WORKER_MULTIPROC_METHOD=spawn --env TMPDIR=/tmp --env VLLM_CACHE_ROOT=/root/.cache/vllm --env XDG_CACHE_HOME=/root/.cache \
  --env TORCHINDUCTOR_CACHE_DIR=/root/.cache/torch/inductor --env TRITON_CACHE_DIR=/root/.cache/torch/triton --env PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
  $H/dsv41-flash-v0909.sif python3 /scratch/bimrose2/train_v14/geom/dsv41_vllm_layerdump.py "$1" "$2" "$3" "$BASE"
