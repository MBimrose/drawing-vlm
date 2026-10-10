#!/bin/bash
# One GRPO arm with vLLM rollouts on ONE serv-20 GPU (2026-10-06): a LoRA-enabled vLLM server
# (~33% of the B300; the trainer peaks ~150 GB) and the HF/peft trainer share the GPU and take turns (generate -> train).
# Each step the trainer saves its adapter and hot-loads it (load_lora_adapter), so rollouts stay
# on-policy while generation runs ~10x faster than HF generate.
#   bash train_v14/serv19/grpo_vllm_arm.sh <name> <gpu> <port> [grpo_round.py args; later ones win]
set -uo pipefail
# serv-20 has no thread caps in the login env: unset, every python child spawns ~core-count threads (load ~900, 2026-10-06)
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4
cd /srv/scratch/bimrose2
name=${1:?name}; gpu=${2:?gpu}; port=${3:?port}; shift 3
E55=/srv/scratch/bimrose2/runs/e55-rft-real-u5-gt-dw423/final
POLICY=${POLICY:-$E55}   # e.g. POLICY=.../rp3-delta-e55/final MM_LIMIT=2 for repairer RL
mkdir -p runs/grpo_v_$name logs tmp
export VLLM_ALLOW_RUNTIME_LORA_UPDATING=True
CUDA_VISIBLE_DEVICES=$gpu DP=1 SEQS=${SEQS:-256} PORT=$port GMU=${GMU:-0.33} MODEL=$POLICY NAME=e55 MM_LIMIT=${MM_LIMIT:-1} \
  VLLM_EXTRA="--enable-lora --max-lora-rank 64 --max-loras 2" \
  setsid nohup bash train_v14/serv19/run_vllm_e55_serv20.sh > logs/vllm-grpo_v_$name.log 2>&1 < /dev/null &
echo "vLLM for $name on GPU $gpu :$port (pid $!)"
ok=0; for i in $(seq 1 120); do curl -s -m 5 http://127.0.0.1:$port/health >/dev/null && { ok=1; break; }; sleep 15; done
[ $ok = 1 ] || { echo "vLLM never ready"; tail -20 logs/vllm-grpo_v_$name.log; exit 2; }
COMMON=(--run e55-rft-real-u5-gt-dw423 --model-base /srv/scratch/bimrose2/models/Qwen3.8-27B
  --ckpt $POLICY --bench fp/h6/train_bench --n-parts 16 --g 8 --steps 60 --lr 1e-5 --kl-beta 0.02
  --train-batch 4 --score-workers 32 --score-timeouts --save-every 10 --rollout-url http://127.0.0.1:$port/v1)
CUDA_VISIBLE_DEVICES=$gpu PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
  .venv/bin/python train_v14/geom/grpo_round.py "${COMMON[@]}" "$@" --out runs/grpo_v_$name \
  > logs/grpo_v_$name.log 2>&1 < /dev/null
echo "trainer exit $? for $name"
pkill -u bimrose2 -f "served-model-name e55 --host 127.0.0.1 --port $port[ ]" 2>/dev/null
