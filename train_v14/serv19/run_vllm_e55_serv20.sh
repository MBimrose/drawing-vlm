#!/usr/bin/env bash
# Serve e55 (Qwen3-VL, HF full fine-tune) with vLLM on wpk-serv-20 for bulk best-of-K generation:
# data-parallel 8 (one replica per B300, 54 GB bf16 each, one endpoint), reasoning parser for
# Qwen3 so `reasoning_content` carries the think trace. Same apptainer image as the DeepSeek
# probe (it is a general vLLM build). Leave it running; gen_openai_bo.py talks to :8100.
#   nohup ./run_vllm_e55_serv20.sh > logs/vllm-e55.log 2>&1 &
set -uo pipefail
DV=/srv/scratch/bimrose2
MODEL=${MODEL:-$DV/runs/e55-rft-real-u5-gt-dw423/final}
SIF=$DV/containers/vllm-dsv41.sif
export VLLM_ENGINE_READY_TIMEOUT_S=1800
mkdir -p $DV/tmp
exec apptainer exec --nv --bind $DV:$DV --bind /tmp:/tmp $SIF \
  vllm serve $MODEL --served-model-name e55 \
    --host 127.0.0.1 --port ${PORT:-8100} \
    --data-parallel-size ${DP:-8} --tensor-parallel-size 1 \
    --reasoning-parser qwen3 \
    --gpu-memory-utilization 0.90 --max-model-len 16384 --max-num-seqs ${SEQS:-64} \
    --limit-mm-per-prompt '{"image": 1}' --trust-remote-code
