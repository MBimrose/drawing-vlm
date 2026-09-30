#!/usr/bin/env bash
# JOINT generator+repairer LoRA on serv-19 GPUs 4-7 (vanilla hub replica stays on 0-3): one adapter for both roles, so a
# single merged 4-GPU model could serve generation (plan in reasoning span) AND visual repair (two images, chat mode).
# Data: dsv41_gen_tier (think rows) + dsv41_repair_tier linked 3x (~40% of rows). (2026-09-30)
set -uo pipefail
SDV=/srv/scratch/bimrose2; cd $SDV
until grep -q "PROBE DONE\|never ready" /tmp/probe_sept.log 2>/dev/null; do sleep 60; done
for p in $(ps -u bimrose2 -o pid,args | grep -E "served-model-name sept_r32|dsv41_ft_serve_serv19.sh" | grep -v grep | awk '{print $1}'); do kill $p; done
sleep 60; for i in $(seq 1 30); do u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i 4,5,6,7 | sort -n | tail -1); [ "$u" -lt 5000 ] && break; sleep 20; done
rm -rf dsv41_joint_tier; mkdir -p dsv41_joint_tier
for f in dsv41_gen_tier/*.tar; do ln -s $SDV/$f dsv41_joint_tier/gen_$(basename $f); done
for c in 1 2 3; do for f in dsv41_repair_tier/*.tar; do ln -s $SDV/$f dsv41_joint_tier/rep${c}_$(basename $f); done; done
M=$(ls -d /scratch/bimrose2/dsv41_flash/models/models--deepseek-ai--DeepSeek-V4.1-Flash/snapshots/*/ | head -1)
export CUDA_VISIBLE_DEVICES=4,5,6,7 HF_HOME=$SDV/.cache/huggingface PYTHONPATH=$SDV/train_v14:$SDV/train_v14/geom OPENBLAS_NUM_THREADS=1 TRITON_CACHE_DIR=$SDV/.cache/triton_dsv41
exec .venv_dsv41/bin/python train_v14/geom/dsv41_lora_train.py --model $M --tier dsv41_joint_tier --prompts spike_dsv41/prompts.json \
  --rank 32 --lr 1e-4 --targets '(self_attn\.(q_a_proj|q_b_proj|kv_proj|o_b_proj)|shared_experts\.(gate_proj|up_proj|down_proj))$' \
  --think --min-layer 20 --max-len 6144 --max-mem-gib 150 --last-gpu-headroom 40 --steps ${STEPS:-600} --accum 8 --save-every 50 \
  --eval-n 0 --out runs/dsv41_joint_r32
