#!/bin/bash
# Latency study on serv-20 (2026-10-20, user chose "run now on serv-20" over waiting for serv-19).
# GPUs 0-3 only (shared with another user's idle processes; GPUs 4-7 hold an unrelated server of ours):
#   generator rft2_rl_s60 (merged)  TP2  GPUs 2,3  :8150
#   repairer rp3                    DP2  GPUs 0,1  :8151
#   verifier v3b (HF, in-process)        GPU 2
# Phases:  A  one candidate, single stream: synthetic pool (face-count scatter) + bench B (280)
#          B  full served system (K=16 -> execute -> render-compare + verifier -> 3 rp3 chains x 6 rounds), 40 bench-B parts
#   setsid nohup bash train_v14/serv19/latency_run_s20.sh > logs/latency/run_s20.log 2>&1 < /dev/null &
set -uo pipefail
DV=/srv/scratch/bimrose2; cd $DV
say() { echo "$(date '+%m-%d %H:%M') $*"; }
L=logs/latency; mkdir -p $L tmp
PIDS=()
cleanup() { for p in "${PIDS[@]}"; do kill -TERM -- -$p 2>/dev/null; done; say "servers stopped"; }
trap cleanup EXIT
SIF=$DV/containers/vllm-dsv41.sif
export VLLM_ENGINE_READY_TIMEOUT_S=3600 VLLM_NO_USAGE_STATS=1 APPTAINERENV_VLLM_NO_USAGE_STATS=1 TMPDIR=$DV/tmp
serve() {  # gpus port name model extra...
  local g=$1 port=$2 name=$3 model=$4; shift 4
  CUDA_VISIBLE_DEVICES=$g APPTAINERENV_CUDA_VISIBLE_DEVICES=$g setsid nohup apptainer exec --nv --bind $DV:$DV --bind /tmp:/tmp $SIF \
    vllm serve $model --served-model-name $name --host 127.0.0.1 --port $port --reasoning-parser qwen3 \
      --max-model-len 16384 --trust-remote-code "$@" > $L/s20_vllm_$name.log 2>&1 < /dev/null &
  PIDS+=($!)
}
serve 2,3 8150 gen $DV/runs/merged_bb_rft2_rl_s60 --tensor-parallel-size 2 --gpu-memory-utilization 0.35 --max-num-seqs 32 \
  --limit-mm-per-prompt '{"image": 1}'
serve 0,1 8151 rp3 $DV/runs/rp3-delta-e55/final --data-parallel-size 2 --gpu-memory-utilization 0.4 --max-num-seqs 64 \
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
  --model gen --tokenizer runs/merged_bb_rft2_rl_s60 --n 1100 --out $L/s20_single_synth.json > $L/s20_single_synth.log 2>&1
say "phase A2: one candidate, bench B"
$PY train_v14/geom/latency_one_candidate.py --bench mech_benchmarks/bench_b --base-url http://127.0.0.1:8150/v1 \
  --model gen --tokenizer runs/merged_bb_rft2_rl_s60 --n 280 --out $L/s20_single_benchb.json > $L/s20_single_benchb.log 2>&1
say "phase B: full served system, 40 bench-B parts"
CUDA_VISIBLE_DEVICES=2 $PY train_v14/geom/serve_full_timed.py --bench mech_benchmarks/bench_b \
  --gen-url http://127.0.0.1:8150/v1 --gen-model gen --rp-url http://127.0.0.1:8151/v1 --rp-model rp3 \
  --verifier runs/v3b-verifier-real-reg/final --base $DV/runs/e51-rft-real-u3-strict90/final \
  --rpy dw_venv/bin/python --script-dir mech_benchmarks/step_to_drw --n 40 --workers 64 \
  --out $L/s20_full_benchb.jsonl > $L/s20_full_benchb.log 2>&1
say "LATENCY STUDY DONE"
