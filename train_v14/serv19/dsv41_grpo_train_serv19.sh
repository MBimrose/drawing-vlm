#!/usr/bin/env bash
# DeepSeek GRPO round update ON serv-19 GPUs 4-7 (2026-10-06, user-approved; GPUs 0-3 = hub replica, never touched).
# One advantage-weighted pass (dsv41_lora_train.py --adv-weighted) over a round's rows; continues the previous adapter.
# LOGIT_TEMP must equal the rollout temperature (dsv41_grpo_loop.sh TEMP, default 0.8): CE on logits/T = the sampled policy.
#   bash dsv41_grpo_train_serv19.sh <tier dir> <out dir> [prev adapter dir|""]     (env: LR, ACCUM, MINL, RANK)
set -uo pipefail
cd /srv/scratch/bimrose2
TIER=$1; OUT=$2; PREV=${3:-}
export CUDA_VISIBLE_DEVICES=4,5,6,7 HF_HOME=/srv/scratch/bimrose2/.cache/huggingface PYTHONPATH=/srv/scratch/bimrose2/train_v14:/srv/scratch/bimrose2/train_v14/geom \
  OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 TRITON_CACHE_DIR=/srv/scratch/bimrose2/.cache/triton_dsv41 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
A=(); [ -n "$PREV" ] && A=(--adapter "$PREV" --opt-state "$PREV/optimizer.pt")
# per-run overrides (EFFORT, LOGIT_TEMP, MAXLEN, LR, ...) written by the loop driver next to the adapters
[ -f "$(dirname "$OUT")/train.env" ] && . "$(dirname "$OUT")/train.env"
exec .venv_dsv41/bin/python train_v14/geom/dsv41_lora_train.py --model models/DeepSeek-V4.1-Flash --tier "$TIER" \
  --prompts train_v14/geom/dsv41_grpo_prompts.json --reasoning-effort ${EFFORT:-50} --adv-weighted --const-lr --logit-temp ${LOGIT_TEMP:-0.8} \
  --rank ${RANK:-32} --lr ${LR:-2e-5} --accum ${ACCUM:-16} --min-layer ${MINL:-24} \
  --targets '(self_attn\.(q_a_proj|q_b_proj|kv_proj|o_b_proj))$' \
  --think --chunked-attn 256 --grad-ckpt ${CKPT_CHECK:+--ckpt-check} --max-len ${MAXLEN:-18000} --last-gpu-headroom ${HEADROOM:-60} --eval-n 0 --out "$OUT" "${A[@]}"
