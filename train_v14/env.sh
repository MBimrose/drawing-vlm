# shellcheck shell=bash
# Sourced by run.sh / sbatch scripts. Idempotent. Campus Cluster (ccc) edition.

ROOT=/projects/illinois/eng/ece/wpk/bimrose2

export HF_HOME=$ROOT/.cache/huggingface
export HF_HUB_CACHE=$HF_HOME/hub
# Weights are local-only (models/Qwen3.8-27B); never attempt Hub downloads.
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export TORCH_HOME=$ROOT/.cache/torch
export WANDB_PROJECT=${WANDB_PROJECT:-drawing-vlm-v14}
export WANDB_DIR=$ROOT/.cache/wandb
export WANDB_CACHE_DIR=$ROOT/.cache/wandb
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=8
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

# Triton JIT cache must be node-local: Lustre file locks stall multi-rank JIT.
export TRITON_CACHE_DIR=/tmp/$USER/triton-cache
mkdir -p "$TRITON_CACHE_DIR"

# v14 dataset locations.
export DRAWING_VLM_TARS=$ROOT/drawing_vlm/step_to_drw/wds_dataset/tars_v14
export DRAWING_VLM_TRACES_JSON=$ROOT/drawing_vlm/step_to_drw/wds_dataset/traces_v14.json

mkdir -p "$HF_HUB_CACHE" "$WANDB_DIR" "$TORCH_HOME"
