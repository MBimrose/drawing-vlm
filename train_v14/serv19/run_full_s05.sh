#!/bin/bash
# Full served system, whole test sets, 8x H200 on wpk-serv-05 (2026-10-20). Optimized layout, all bf16, CUDA graphs,
# prefix caching (vLLM defaults):
#   generator rft2_rl_s60 (merged)  DP2  GPUs 0-1  :8150    K = 8 candidates per drawing (draw 0 greedy + 7 at T 0.7)
#     + verifier v3b LoRA served on the same engine (--lora-modules ver=...)   LEAN SETUP (user, 2026-10-20): one 27B
#     generator engine + one 27B repairer engine; no separate verifier base model
#   repairer  rp3                   DP6  GPUs 2-7  :8151    3 chains x 6 rounds x 16 repairs (S1 protocol)
# The repairer is the bottleneck (first try with gen DP4 / rp3 DP3: rp3 GPUs at 100%, generator idle), so it gets 5 GPUs.
# CPU: every exec / render / IoU subprocess is single-threaded (OMP/BLAS = 1); unpinned, each grabbed ~10 cores and the
# 128-core host sat at load ~230. 6 drawings in flight; bench B (280 real) first, then the synthetic pool (1,027).
# Resumable: parts already in the .jsonl are skipped.
#   setsid nohup bash train_v14/serv19/run_full_s05.sh > /scratch/bimrose2/dv/logs/latency/run_s05.log 2>&1 < /dev/null &
set -uo pipefail
D=/scratch/bimrose2/dv; cd $D
say() { echo "$(date '+%m-%d %H:%M') $*"; }
L=$D/logs/latency; mkdir -p $L $D/tmp
until grep -q "PULL DONE" $D/logs/pull.log; do sleep 60; done
grep -q FAILED $D/logs/pull.log && { say "copy failed"; exit 1; }
PIDS=()
cleanup() { for p in "${PIDS[@]}"; do kill -TERM -- -$p 2>/dev/null; done; say "servers stopped"; }
trap cleanup EXIT
SIF=$D/containers/vllm-dsv41.sif
export VLLM_ENGINE_READY_TIMEOUT_S=3600 VLLM_NO_USAGE_STATS=1 APPTAINERENV_VLLM_NO_USAGE_STATS=1 TMPDIR=$D/tmp
serve() {  # gpus port name model extra...
  local g=$1 port=$2 name=$3 model=$4; shift 4
  CUDA_VISIBLE_DEVICES=$g APPTAINERENV_CUDA_VISIBLE_DEVICES=$g setsid nohup apptainer exec --nv --bind $D:$D --bind /srv/scratch:/srv/scratch --bind /tmp:/tmp $SIF \
    vllm serve $model --served-model-name $name --host 127.0.0.1 --port $port --reasoning-parser qwen3 --dtype bfloat16 \
      --max-model-len 16384 --trust-remote-code --gpu-memory-utilization 0.88 "$@" > $L/s05_vllm_$name.log 2>&1 < /dev/null &
  PIDS+=($!)
}
serve 0,1 8150 gen $D/runs/merged_bb_rft2_rl_s60 --data-parallel-size 2 --max-num-seqs 64 --limit-mm-per-prompt '{"image": 1}' \
  --enable-lora --max-lora-rank 64 --max-loras 1 --lora-modules ver=$D/runs/v3b-verifier-real-reg/final
serve 2,3,4,5,6,7 8151 rp3 $D/runs/rp3-delta-e55/final --data-parallel-size 6 --max-num-seqs 128 --limit-mm-per-prompt '{"image": 2}'
for port in 8150 8151; do
  for i in $(seq 1 240); do curl -s -m 5 http://127.0.0.1:$port/v1/models | grep -q '"id"' && break; sleep 15; done
  curl -s -m 5 http://127.0.0.1:$port/v1/models | grep -q '"id"' || { say "server :$port never ready"; exit 1; }
done
say "servers ready"
[ -n "${STOP_AFTER_SERVERS:-}" ] && { say "STOP_AFTER_SERVERS set: servers up, holding for checks"; while [ ! -e $D/GO ]; do sleep 20; done; rm -f $D/GO; }
export PYTHONPATH=$D/train_v14:$D/train_v14/geom
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
PY=$D/.venv/bin/python
for b in bench_b fullpool_dw423; do
  say "full system on $b"
  CUDA_VISIBLE_DEVICES= $PY train_v14/geom/serve_full_timed.py --bench mech_benchmarks/$b --all --k 8 --concurrency 6 \
    --gen-url http://127.0.0.1:8150/v1 --gen-model gen --rp-url http://127.0.0.1:8151/v1 --rp-model rp3 \
    --ver-url http://127.0.0.1:8150/v1 --ver-model ver \
    --py $PY --rpy $D/dw_venv/bin/python --script-dir mech_benchmarks/step_to_drw --workers 120 \
    --out $L/s05_full_$b.jsonl > $L/s05_full_$b.log 2>&1
  say "$b: $(grep -c '^\[full\] ' $L/s05_full_$b.log) parts, $(grep -c 'ERROR' $L/s05_full_$b.log) errors"
done
say "S05 FULL DONE"
