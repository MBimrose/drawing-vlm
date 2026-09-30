#!/usr/bin/env bash
# DeepSeek-V4.1-Flash visual-REPAIR LoRA on serv-20 as TWO data-parallel replicas (GPUs 0-3 and 4-7, one pipeline-split
# replica each, adapter grads averaged over NCCL) -- the single 8-GPU pipeline replica kept one GPU busy at a time.
# max-len 6144 (4096 skipped ~6% of the two-image rows, the longest programs). (2026-09-30)
set -uo pipefail
SDV=/srv/scratch/bimrose2; cd $SDV
for p in $(ps -u bimrose2 -o pid,args | grep "dsv41_lora_train.py" | grep -v grep | awk '{print $1}'); do kill $p; done; sleep 30
export HF_HOME=$SDV/.cache/huggingface PYTHONPATH=$SDV/train_v14:$SDV/train_v14/geom OPENBLAS_NUM_THREADS=1 TRITON_CACHE_DIR=$SDV/.cache/triton_dsv41
export MASTER_ADDR=127.0.0.1 MASTER_PORT=29613 WORLD_SIZE=2 NCCL_P2P_LEVEL=NVL
ARGS="--dist --model models/DeepSeek-V4.1-Flash --tier dsv41_repair_tier --prompts spike_dsv41/prompts.json --rank 32 --lr 1e-4
 --targets (self_attn\.(q_a_proj|q_b_proj|kv_proj|o_b_proj)|shared_experts\.(gate_proj|up_proj|down_proj))\$ --max-len 6144 --eval-n 0
 --max-mem-gib 150 --last-gpu-headroom 40 --steps ${STEPS:-500} --accum 4 --min-layer 20 --save-every 50 --out runs/dsv41_rep_r32_dp"
for r in 0 1; do
  G=$([ $r = 0 ] && echo 0,1,2,3 || echo 4,5,6,7)
  CUDA_VISIBLE_DEVICES=$G RANK=$r setsid nohup .venv_dsv41/bin/python train_v14/geom/dsv41_lora_train.py $ARGS > logs/dsv41_rep_dp.rank$r.log 2>&1 < /dev/null &
done
sleep 5; echo "launched 2 replicas"; ps -u bimrose2 -o pid,args | grep -c "dsv41_lora_trai[n]"
