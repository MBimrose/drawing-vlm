#!/bin/bash
# GRPO round 1: three parallel arms on serv-20 (2026-10-05).
#   E1 kl002 — Dr.GRPO loss + mean advantage + KL 0.02 anchor (delta-tax guard)
#   E2 kl0   — identical but KL off (literature consensus for verifiable rewards)
#   E3 tok   — DAPO token-level loss + KL 0.02 (aggregation ablation)
# All arms: e55 base, LoRA r64, G=8 at T=0.7, 16 parts/update, lr 1e-5,
# zero-variance groups skipped (DAPO dynamic sampling), rollouts logged.
# Run on serv-20:  bash train_v14/serv19/grpo_r1_launch.sh [steps]
set -uo pipefail
cd /srv/scratch/bimrose2
STEPS=${1:-60}
COMMON="--run e55-rft-real-u5-gt-dw423 --model-base /srv/scratch/bimrose2/models/Qwen3.8-27B \
  --ckpt /srv/scratch/bimrose2/runs/e55-rft-real-u5-gt-dw423/final --bench fp/h6/train_bench \
  --n-parts 16 --g 8 --steps $STEPS --lr 1e-5 --gen-batch 16 --train-batch 4 \
  --score-workers 24 --save-every 10"
launch() {
  name=$1; gpu=$2; shift 2
  mkdir -p runs/grpo_r1_$name
  CUDA_VISIBLE_DEVICES=$gpu PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
    setsid nohup .venv/bin/python train_v14/geom/grpo_round.py $COMMON "$@" \
    --out runs/grpo_r1_$name > logs/grpo_r1_$name.log 2>&1 < /dev/null &
  echo "arm $name on GPU $gpu (pid $!)"
}
launch kl002 4 --kl-beta 0.02
launch kl0   5 --kl-beta 0
launch tok   6 --kl-beta 0.02 --loss token
echo "GRPO R1 LAUNCHED (3 arms, $STEPS steps)"
