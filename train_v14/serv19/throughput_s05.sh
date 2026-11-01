#!/bin/bash
# Throughput / latency study of the SFT + GRPO pipeline WITHOUT repair on wpk-serv-05 (8x H200), 2026-10-21.
# Pipeline per drawing: 8 candidates (greedy + 7 at T 0.7) -> execute -> select (verifier LoRA served on the generator
# engine [+ render-compare]) -> served program. Generator on all 8 GPUs (DP8). Configurations:
#   bf16   : bf16 weights, max-num-seqs 256
#   fp8    : dynamic FP8 weights/activations (H200 native), otherwise identical
#   spec   : best of the above + n-gram speculative decoding (prompt lookup), if the server accepts it with LoRA
# Runs per configuration (logs/throughput/<cfg>_<run>.jsonl):
#   lat    : 1 drawing at a time, 40 bench-B parts                (best-case latency)
#   acc    : bench B (280), 64 in flight, with GT IoU             (accuracy + throughput on real parts)
#   tp     : synthetic pool (1,027), 128 in flight, no GT eval    (max throughput)
#   tpver  : bf16 only, synthetic, 128 in flight, verifier-only selection (no renders)
#   setsid nohup bash train_v14/serv19/throughput_s05.sh > /scratch/bimrose2/dv/logs/throughput/run.log 2>&1 < /dev/null &
set -uo pipefail
D=/scratch/bimrose2/dv; cd $D
L=$D/logs/throughput; mkdir -p $L $D/tmp
say() { echo "$(date '+%m-%d %H:%M:%S') $*"; }
SIF=$D/containers/vllm-dsv41.sif
export VLLM_ENGINE_READY_TIMEOUT_S=3600 VLLM_NO_USAGE_STATS=1 APPTAINERENV_VLLM_NO_USAGE_STATS=1 TMPDIR=$D/tmp
export PYTHONPATH=$D/train_v14:$D/train_v14/geom
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
PY=$D/.venv/bin/python
SPID=""
start() {  # cfg extra-vllm-args...
  local cfg=$1; shift
  CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 APPTAINERENV_CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 setsid nohup apptainer exec --nv \
    --bind $D:$D --bind /srv/scratch:/srv/scratch --bind /tmp:/tmp $SIF \
    vllm serve $D/runs/merged_bb_rft2_rl_s60 --served-model-name gen --host 127.0.0.1 --port 8150 --reasoning-parser qwen3 \
      --dtype bfloat16 --max-model-len 16384 --trust-remote-code --gpu-memory-utilization 0.9 --data-parallel-size 8 \
      --max-num-seqs 256 --limit-mm-per-prompt '{"image": 1}' \
      --enable-lora --max-lora-rank 64 --max-loras 1 --lora-modules ver=$D/runs/v3b-verifier-real-reg/final "$@" \
      > $L/vllm_$cfg.log 2>&1 < /dev/null &
  SPID=$!
  for i in $(seq 1 240); do curl -s -m 5 http://127.0.0.1:8150/v1/models | grep -q '"ver"' && { say "$cfg server ready"; return 0; }
    kill -0 $SPID 2>/dev/null || break; sleep 15; done
  say "$cfg server FAILED: $(grep -m3 -E 'Error|error' $L/vllm_$cfg.log | cut -c1-300)"; stop; return 1
}
stop() { [ -n "$SPID" ] && kill -TERM -- -$SPID 2>/dev/null; sleep 30; SPID=""; }
trap stop EXIT
run() {  # cfg name bench concurrency extra...
  local cfg=$1 name=$2 bench=$3 c=$4; shift 4
  say "$cfg $name: $bench, $c in flight $*"
  local t0=$(date +%s)
  CUDA_VISIBLE_DEVICES= $PY train_v14/geom/serve_full_timed.py --bench mech_benchmarks/$bench --k 8 --rounds 0 --chains 1 \
    --concurrency $c --gen-url http://127.0.0.1:8150/v1 --gen-model gen --rp-url http://127.0.0.1:8150/v1 --rp-model gen \
    --ver-url http://127.0.0.1:8150/v1 --ver-model ver --py $PY --rpy $D/dw_venv/bin/python \
    --script-dir mech_benchmarks/step_to_drw --workers 120 --out $L/${cfg}_$name.jsonl "$@" > $L/${cfg}_$name.log 2>&1
  local t1=$(date +%s) n=$(wc -l < $L/${cfg}_$name.jsonl) e=$(grep -c "^\[full\] ERROR" $L/${cfg}_$name.log)
  say "$cfg $name done: $n drawings in $((t1 - t0)) s -> $(python3 -c "print(round($n / max($t1 - $t0, 1) * 3600))") drawings/hour, $e errors, $(grep -o "retries: [0-9]*" $L/${cfg}_$name.log)"
}
warm() { CUDA_VISIBLE_DEVICES= $PY train_v14/geom/serve_full_timed.py --bench mech_benchmarks/bench_b --n 8 --seed 99 --k 8 --rounds 0 --chains 1 \
    --concurrency 8 --gen-url http://127.0.0.1:8150/v1 --gen-model gen --rp-url http://127.0.0.1:8150/v1 --rp-model gen \
    --ver-url http://127.0.0.1:8150/v1 --ver-model ver --py $PY --rpy $D/dw_venv/bin/python --script-dir mech_benchmarks/step_to_drw \
    --workers 64 --no-eval --out $L/warm_$1_$RANDOM.jsonl > /dev/null 2>&1; }

for cfg in bf16 fp8; do
  extra=(); [ $cfg = fp8 ] && extra=(--quantization fp8)
  start $cfg "${extra[@]}" || continue
  warm $cfg
  run $cfg lat bench_b 1 --n 40 --seed 1 --no-eval
  run $cfg acc bench_b 64 --all
  run $cfg tp fullpool_dw423 128 --all --no-eval
  [ $cfg = bf16 ] && run $cfg tpver fullpool_dw423 128 --all --no-eval --select ver
  stop
done
# speculative decoding on top of the faster precision (n-gram prompt lookup; code often repeats the drawing's numbers)
best=$(python3 - <<EOF
import json, os
r = {}
for c in ("bf16", "fp8"):
    p = "$L/" + c + "_tp.jsonl"
    if os.path.exists(p):
        R = [json.loads(l) for l in open(p)]
        if R: r[c] = len(R) / (max(x["t_end"] for x in R) - min(x["t_start"] for x in R))
print(max(r, key=r.get) if r else "bf16")
EOF
)
extra=(); [ "$best" = fp8 ] && extra=(--quantization fp8)
if start spec "${extra[@]}" --speculative-config '{"method": "ngram", "num_speculative_tokens": 4, "prompt_lookup_max": 4, "prompt_lookup_min": 2}'; then
  warm spec
  run spec lat bench_b 1 --n 40 --seed 1 --no-eval
  run spec tp fullpool_dw423 128 --all --no-eval
  stop
fi
say "THROUGHPUT DONE (spec base: $best)"
