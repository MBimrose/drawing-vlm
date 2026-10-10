#!/bin/bash
# Bench B (2026-10-10): pre-merge the three GRPO adapters into e55 on CPU while GPU 7 is still busy.
cd /srv/scratch/bimrose2
export OMP_NUM_THREADS=16 MKL_NUM_THREADS=16
E55=/srv/scratch/bimrose2/runs/e55-rft-real-u5-gt-dw423/final
for spec in rft2_rl_s60=runs/grpo_v_rft2_rl/adapter_step60 rft1_rl2_s120=runs/grpo_v_rft1_rl2/adapter_step120 ent_t10_s120=runs/grpo_v_ent_t10/adapter_step120; do
  n=${spec%%=*}; ad=${spec#*=}; M=runs/merged_bb_$n
  [ -f $M/config.json ] && continue
  echo "$(date '+%H:%M') merging $n"
  CUDA_VISIBLE_DEVICES= nice -n 10 taskset -c 300-343 .venv/bin/python train_v14/geom/merge_grpo_lora.py --ckpt $E55 --adapter $ad \
    --out $M --model-base /srv/scratch/bimrose2/models/Qwen3.8-27B > bench_b/logs/merge_$n.log 2>&1 || echo "merge FAILED $n"
done
echo "PREMERGE DONE $(date)"
