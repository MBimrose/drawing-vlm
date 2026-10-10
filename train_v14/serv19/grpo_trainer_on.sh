#!/bin/bash
# Start ONLY a fast-path GRPO trainer against an already-running LoRA-enabled vLLM server on serv-20
# (2026-10-06; e.g. to swap an arm on a GPU without restarting its server — the trainer sweeps stale
# pol_* adapters at start). Same defaults as grpo_vllm_arm.sh; later args win.
#   bash train_v14/serv19/grpo_trainer_on.sh <name> <gpu> <port> [grpo_round.py args]
set -uo pipefail
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4
cd /srv/scratch/bimrose2
name=${1:?name}; gpu=${2:?gpu}; port=${3:?port}; shift 3
E55=/srv/scratch/bimrose2/runs/e55-rft-real-u5-gt-dw423/final; POLICY=${POLICY:-$E55}
curl -s -m 5 http://127.0.0.1:$port/health >/dev/null || { echo "no server on :$port"; exit 2; }
mkdir -p runs/grpo_v_$name
COMMON=(--run e55-rft-real-u5-gt-dw423 --model-base /srv/scratch/bimrose2/models/Qwen3.8-27B
  --ckpt $POLICY --bench fp/h6/train_bench --n-parts 16 --g 8 --steps 300 --lr 1e-5 --kl-beta 0.02
  --train-batch 4 --score-workers 32 --score-timeouts --save-every 10 --rollout-url http://127.0.0.1:$port/v1)
CUDA_VISIBLE_DEVICES=$gpu PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
  setsid nohup .venv/bin/python train_v14/geom/grpo_round.py "${COMMON[@]}" "$@" --out runs/grpo_v_$name \
  >> logs/grpo_v_$name.log 2>&1 < /dev/null &
echo "trainer $name on GPU $gpu -> :$port (pid $!)"
