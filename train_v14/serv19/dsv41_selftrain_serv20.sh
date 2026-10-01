#!/usr/bin/env bash
# DeepSeek-V4.1-Flash rejection-sampling self-training (2026-10-01): its OWN successful samples (IoU >= 0.8, own
# reasoning + own code, <= 32k tokens, 492 rows / 369 parts), think mode at the generation prompt (effort 75),
# exact banded attention (dsv41_chunked_attn) for long rows, LoRA on layers >= 24, 2 epochs, 8x B300.
cd /srv/scratch/bimrose2
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 HF_HOME=/srv/scratch/bimrose2/.cache/huggingface PYTHONPATH=/srv/scratch/bimrose2/train_v14:/srv/scratch/bimrose2/train_v14/geom OPENBLAS_NUM_THREADS=1 TRITON_CACHE_DIR=/srv/scratch/bimrose2/.cache/triton_dsv41
.venv_dsv41/bin/python train_v14/geom/dsv41_lora_train.py --model models/DeepSeek-V4.1-Flash --tier dsv41_selftrain_tier/shards --prompts spike_dsv41/prompts.json \
  --rank 32 --lr 1e-4 --targets '(self_attn\.(q_a_proj|q_b_proj|kv_proj|o_b_proj)|shared_experts\.(gate_proj|up_proj|down_proj))$' \
  --think --chunked-attn 256 --min-layer 24 --max-len 34000 --last-gpu-headroom 40 --steps ${STEPS:-125} --accum 8 --save-every 25 --eval-n 0 \
  --out runs/dsv41_selftrain_r32 > logs/dsv41_selftrain.log 2>&1
echo "TRAIN EXIT $?" >> logs/dsv41_selftrain.log
