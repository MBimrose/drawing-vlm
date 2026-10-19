#!/usr/bin/env bash
# Serve NVIDIA Nemotron-3.5-Super-VL-120B-A12B (BF16, base or merged fine-tune) with vLLM on wpk-serv-20,
# TP4 on GPUs 4-7 ONLY (GPUs 0-3 belong to other users). Model-card flags: --trust-remote-code,
# --reasoning-parser nemotron_v3 (reasoning_content = think trace), MTP speculative decoding (lossless: drafts are
# verified against the target distribution, so greedy and T>0 sampling are unchanged).
# Image: the card's pinned vLLM build (vllm/vllm-openai:nightly-3f1bcfd8..., v0.32.0 was not tagged on 2026-10-15).
#   MODEL=<dir> NAME=<served name> PORT=8600 MLEN=24576 setsid bash run_vllm_nemotron_serv20.sh > log 2>&1 &
# Env: GMU (0.85), SEQS (64), MTP (3 draft tokens; 0 = off), MLEN (max model len), VLLM_EXTRA.
set -uo pipefail
DV=/srv/scratch/bimrose2
MODEL=${MODEL:-$DV/models/Nemotron-3.5-Super-VL-120B-A12B-BF16}
SIF=${SIF:-$DV/containers/vllm-nemotron-3f1bcfd8.sif}
export CUDA_VISIBLE_DEVICES=${GPUS:-4,5,6,7}
case ",$CUDA_VISIBLE_DEVICES," in *,0,*|*,1,*|*,2,*|*,3,*) echo "refusing: GPUs 0-3 are not ours"; exit 3;; esac
export VLLM_ENGINE_READY_TIMEOUT_S=3600 TMPDIR=$DV/tmp
# host CUDA 13.0 toolkit for any JIT (FlashInfer / DeepGEMM) inside the image (serv-20 container trap 2)
CUDA=/software/cuda-13.0
export APPTAINERENV_CUDA_HOME=$CUDA APPTAINERENV_PREPEND_PATH=$CUDA/bin APPTAINERENV_CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES
mkdir -p $DV/tmp
SPEC=()
[ "${MTP:-3}" -gt 0 ] && SPEC=(--speculative_config.method mtp --speculative_config.num_speculative_tokens ${MTP:-3})
exec apptainer exec --nv --bind $DV:$DV --bind /tmp:/tmp --bind /software:/software $SIF \
  vllm serve $MODEL --served-model-name ${NAME:-nemotron} \
    --host 127.0.0.1 --port ${PORT:-8600} \
    --tensor-parallel-size ${TP:-4} --trust-remote-code \
    --reasoning-parser nemotron_v3 "${SPEC[@]}" \
    --gpu-memory-utilization ${GMU:-0.85} --max-model-len ${MLEN:-24576} --max-num-seqs ${SEQS:-64} \
    --limit-mm-per-prompt '{"image": 1, "video": 0}' ${VLLM_EXTRA:-}
