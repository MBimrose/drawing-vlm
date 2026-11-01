#!/bin/bash
# Latency study on serv-19 (2026-10-20, user: "queue yourself up to use server 19 for optimized serving").
# Runs in the gap between Flash-Next e59's eval lanes and fn_after_e59.sh's gate A: fn_after_e59.sh waits while
# fn55/HOLD_FOR_LATENCY exists, so this script creates it first and ALWAYS removes it on exit.
# Optimized layout, all 8 B300 (bf16, CUDA graphs, prefix caching):
#   generator rft2_rl_s60 (merged)  TP4  GPUs 0-3  :8150
#   repairer rp3                    DP3  GPUs 4-6  :8151   (one replica per repair chain)
#   verifier v3b (HF, in-process)        GPU 7
# Phases:  A  one candidate, single stream: synthetic pool (face-count scatter) + bench B (280)
#          B  full served system (K=16 -> execute -> render-compare + verifier -> 3 rp3 chains x 6 rounds), 40 bench-B parts
#   setsid nohup bash train_v14/serv19/latency_queue_s19.sh > logs/latency/queue_s19.log 2>&1 < /dev/null &
set -uo pipefail
DV=/srv/scratch/bimrose2; cd $DV
say() { echo "$(date '+%m-%d %H:%M') $*"; }
L=logs/latency; mkdir -p $L tmp
HOLD=fn55/HOLD_FOR_LATENCY; touch $HOLD
PIDS=()
cleanup() { for p in "${PIDS[@]}"; do kill -TERM -- -$p 2>/dev/null; done; sleep 20; rm -f $HOLD; say "hold released"; }
trap cleanup EXIT
say "hold set; waiting for e59 eval lanes"
until grep -q "E59 EVAL LANES DONE\|no final model" fn55/logs/train_e59.log 2>/dev/null; do sleep 120; done
say "e59 lanes done; waiting for idle GPUs"
until [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '$1 > 5000' | wc -l)" -eq 0 ]; do sleep 60; done
until [ -f runs/merged_bb_rft2_rl_s60/config.json ] && [ -f runs/rp3-delta-e55/final/config.json ] && [ -f containers/vllm-dsv41.sif ]; do
  say "waiting for model copies from serv-20"; sleep 300; done

SIF=$DV/containers/vllm-dsv41.sif
export VLLM_ENGINE_READY_TIMEOUT_S=3600 VLLM_NO_USAGE_STATS=1 APPTAINERENV_VLLM_NO_USAGE_STATS=1 TMPDIR=$DV/tmp
serve() {  # gpus port name model extra...
  local g=$1 port=$2 name=$3 model=$4; shift 4
  CUDA_VISIBLE_DEVICES=$g APPTAINERENV_CUDA_VISIBLE_DEVICES=$g setsid nohup apptainer exec --nv --bind $DV:$DV --bind /tmp:/tmp $SIF \
    vllm serve $model --served-model-name $name --host 127.0.0.1 --port $port --reasoning-parser qwen3 \
      --max-model-len 16384 --trust-remote-code "$@" > $L/s19_vllm_$name.log 2>&1 < /dev/null &
  PIDS+=($!)
}
serve 0,1,2,3 8150 gen $DV/runs/merged_bb_rft2_rl_s60 --tensor-parallel-size 4 --gpu-memory-utilization 0.85 --max-num-seqs 32 \
  --limit-mm-per-prompt '{"image": 1}'
serve 4,5,6 8151 rp3 $DV/runs/rp3-delta-e55/final --data-parallel-size 3 --gpu-memory-utilization 0.85 --max-num-seqs 64 \
  --limit-mm-per-prompt '{"image": 2}'
for port in 8150 8151; do
  for i in $(seq 1 240); do curl -s -m 5 http://127.0.0.1:$port/health >/dev/null && break; sleep 15; done
  curl -s -m 5 http://127.0.0.1:$port/health >/dev/null || { say "server :$port never ready"; exit 1; }
done
say "servers ready"
export PYTHONPATH=$DV/train_v14:$DV/train_v14/geom
PY=$DV/.venv/bin/python

say "phase A1: one candidate, synthetic pool"
$PY train_v14/geom/latency_one_candidate.py --bench mech_benchmarks/fullpool_dw423 --base-url http://127.0.0.1:8150/v1 \
  --model gen --tokenizer runs/merged_bb_rft2_rl_s60 --n 1100 --out $L/s19_single_synth.json > $L/s19_single_synth.log 2>&1
say "phase A2: one candidate, bench B"
$PY train_v14/geom/latency_one_candidate.py --bench mech_benchmarks/bench_b --base-url http://127.0.0.1:8150/v1 \
  --model gen --tokenizer runs/merged_bb_rft2_rl_s60 --n 280 --out $L/s19_single_benchb.json > $L/s19_single_benchb.log 2>&1
say "phase B: full served system, 40 bench-B parts"
CUDA_VISIBLE_DEVICES=7 $PY train_v14/geom/serve_full_timed.py --bench mech_benchmarks/bench_b \
  --gen-url http://127.0.0.1:8150/v1 --gen-model gen --rp-url http://127.0.0.1:8151/v1 --rp-model rp3 \
  --verifier runs/v3b-verifier-real-reg/final --base $DV/runs/e51-rft-real-u3-strict90/final \
  --rpy dw_venv/bin/python --script-dir mech_benchmarks/step_to_drw --n 40 --workers 96 \
  --out $L/s19_full_benchb.jsonl > $L/s19_full_benchb.log 2>&1
say "LATENCY STUDY DONE"
