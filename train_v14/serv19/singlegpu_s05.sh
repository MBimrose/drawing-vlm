#!/bin/bash
# Per-H200 capacity of the paper pipeline (SFT + GRPO, no repair, render-compare pick, bf16), wpk-serv-05, 2026-10-21.
# One copy of the generator on ONE H200 (GPU 0), all 128 CPU cores available, so the GPU is the limit (on the full
# node, 8 copies saturate the CPUs first). Waits for plotpass_s05.sh. 120 bench-B drawings per load level, no GT eval.
#   setsid nohup bash train_v14/serv19/singlegpu_s05.sh > /scratch/bimrose2/dv/logs/throughput/single.log 2>&1 < /dev/null &
set -uo pipefail
D=/scratch/bimrose2/dv; cd $D; L=$D/logs/throughput
say() { echo "$(date '+%m-%d %H:%M:%S') $*"; }
while pgrep -f plotpass_s05.sh > /dev/null; do sleep 60; done
SIF=$D/containers/vllm-dsv41.sif
export VLLM_ENGINE_READY_TIMEOUT_S=3600 VLLM_NO_USAGE_STATS=1 APPTAINERENV_VLLM_NO_USAGE_STATS=1 TMPDIR=$D/tmp
export PYTHONPATH=$D/train_v14:$D/train_v14/geom
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
PY=$D/.venv/bin/python
CUDA_VISIBLE_DEVICES=0 APPTAINERENV_CUDA_VISIBLE_DEVICES=0 setsid nohup apptainer exec --nv \
  --bind $D:$D --bind /srv/scratch:/srv/scratch --bind /tmp:/tmp $SIF \
  vllm serve $D/runs/merged_bb_rft2_rl_s60 --served-model-name gen --host 127.0.0.1 --port 8150 --reasoning-parser qwen3 \
    --dtype bfloat16 --max-model-len 16384 --trust-remote-code --gpu-memory-utilization 0.9 \
    --max-num-seqs 256 --limit-mm-per-prompt '{"image": 1}' > $L/vllm_single.log 2>&1 < /dev/null &
SPID=$!; trap 'kill -TERM -- -$SPID 2>/dev/null' EXIT
for i in $(seq 1 240); do curl -s -m 5 http://127.0.0.1:8150/v1/models | grep -q '"gen"' && break; kill -0 $SPID 2>/dev/null || { say "server died"; exit 1; }; sleep 15; done
say "single-H200 server ready"
run() {  # name concurrency n
  local name=$1 c=$2 n=$3; local t0=$(date +%s)
  CUDA_VISIBLE_DEVICES= $PY train_v14/geom/serve_full_timed.py --bench mech_benchmarks/bench_b --n $n --seed 7 --k 8 --rounds 0 --chains 1 \
    --select v3 --no-eval --concurrency $c --gen-url http://127.0.0.1:8150/v1 --gen-model gen --rp-url http://127.0.0.1:8150/v1 \
    --rp-model gen --py $PY --rpy $D/dw_venv/bin/python --script-dir mech_benchmarks/step_to_drw --workers 120 \
    --out $L/$name.jsonl > $L/$name.log 2>&1
  local t1=$(date +%s) k=$(wc -l < $L/$name.jsonl) e=$(grep -c "^\[full\] ERROR" $L/$name.log)
  say "$name done: $k drawings in $((t1 - t0)) s -> $(python3 -c "print(round($k / max($t1 - $t0, 1) * 3600))") drawings/hour, $e errors"
}
run single_warm 4 8
run single_c1 1 20
run single_c8 8 120
run single_c16 16 120
run single_c32 32 120
say "SINGLE DONE"
