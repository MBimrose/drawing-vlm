#!/bin/bash
# Render-compare-only pipeline (no verifier model, no LoRA) + per-part timing pass for the face count / time / IoU
# figure, wpk-serv-05, 2026-10-21. Offline ablation (bench B and synthetic): picking by render-compare alone ties
# verifier + render-compare (+0.002 both sets), verifier alone loses 0.014-0.016; the verifier LoRA on the generator
# engine also NaNs / crashes vLLM under load. Waits for throughput_s05.sh, then serves the generator alone on all 8
# H200s with the fastest setting that keeps accuracy (FP8 only if bench-B mean IoU drops < 0.01 vs bf16; n-gram
# speculation only if it raised throughput) and runs, all with --select v3:
#   v3_lat   1 drawing at a time, 40 bench-B parts           v3_acc  bench B, 64 in flight, GT IoU
#   v3_tp    synthetic pool, 128 in flight, no GT eval        plotpass_<bench>  bench B + synthetic, 8 in flight, GT IoU
#   setsid nohup bash train_v14/serv19/plotpass_s05.sh > /scratch/bimrose2/dv/logs/throughput/plotpass.log 2>&1 < /dev/null &
set -uo pipefail
D=/scratch/bimrose2/dv; cd $D; L=$D/logs/throughput
say() { echo "$(date '+%m-%d %H:%M:%S') $*"; }
# FORCE_QUANT=bf16 PFX=bf16v3_ skips the wait and the automatic choice (paper config: bf16, no speculation)
PFX=${PFX:-}
while pgrep -f throughput_s05.sh > /dev/null; do sleep 60; done
say "throughput study finished"
[ -n "${FORCE_QUANT:-}" ] && { QUANT=$FORCE_QUANT; SPEC=nospec; } || read -r QUANT SPEC <<< "$(python3 - <<EOF
import json, os
L = "$L"
def rec(n):
    p = f"{L}/{n}.jsonl"
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []
def tput(R): return len(R) / (max(r["t_end"] for r in R) - min(r["t_start"] for r in R)) if R else 0
def iou(R): return sum(r["iou_start"] for r in R) / len(R) if R else None
b, f = rec("bf16_acc"), rec("fp8_acc")
fp8 = bool(f) and iou(b) is not None and iou(b) - iou(f) < 0.01 and tput(rec("fp8_tp")) > tput(rec("bf16_tp"))
base = tput(rec("fp8_tp" if fp8 else "bf16_tp"))
spec = tput(rec("spec_tp")) > 1.05 * base
print("fp8" if fp8 else "bf16", "spec" if spec else "nospec")
EOF
)"
say "plot pass config: $QUANT $SPEC"
SIF=$D/containers/vllm-dsv41.sif
export VLLM_ENGINE_READY_TIMEOUT_S=3600 VLLM_NO_USAGE_STATS=1 APPTAINERENV_VLLM_NO_USAGE_STATS=1 TMPDIR=$D/tmp
export PYTHONPATH=$D/train_v14:$D/train_v14/geom
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
PY=$D/.venv/bin/python
extra=(); [ "$QUANT" = fp8 ] && extra+=(--quantization fp8)
[ "$SPEC" = spec ] && extra+=(--speculative-config '{"method": "ngram", "num_speculative_tokens": 4, "prompt_lookup_max": 4, "prompt_lookup_min": 2}')
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 APPTAINERENV_CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 setsid nohup apptainer exec --nv \
  --bind $D:$D --bind /srv/scratch:/srv/scratch --bind /tmp:/tmp $SIF \
  vllm serve $D/runs/merged_bb_rft2_rl_s60 --served-model-name gen --host 127.0.0.1 --port 8150 --reasoning-parser qwen3 \
    --dtype bfloat16 --max-model-len 16384 --trust-remote-code --gpu-memory-utilization 0.9 --data-parallel-size 8 \
    --max-num-seqs 256 --limit-mm-per-prompt '{"image": 1}' "${extra[@]}" \
    > $L/vllm_${PFX}plotpass.log 2>&1 < /dev/null &
SPID=$!; trap 'kill -TERM -- -$SPID 2>/dev/null' EXIT
for i in $(seq 1 240); do curl -s -m 5 http://127.0.0.1:8150/v1/models | grep -q '"gen"' && break; kill -0 $SPID 2>/dev/null || { say "server died"; exit 1; }; sleep 15; done
say "server ready"
run() {  # name bench concurrency extra...
  local name=$1 bench=$2 c=$3; shift 3; local t0=$(date +%s)
  CUDA_VISIBLE_DEVICES= $PY train_v14/geom/serve_full_timed.py --bench mech_benchmarks/$bench --k 8 --rounds 0 --chains 1 --select v3 \
    --concurrency $c --gen-url http://127.0.0.1:8150/v1 --gen-model gen --rp-url http://127.0.0.1:8150/v1 --rp-model gen \
    --py $PY --rpy $D/dw_venv/bin/python --script-dir mech_benchmarks/step_to_drw --workers 120 --out $L/$PFX$name.jsonl "$@" > $L/$PFX$name.log 2>&1
  local t1=$(date +%s) n=$(wc -l < $L/$PFX$name.jsonl) e=$(grep -c "^\[full\] ERROR" $L/$PFX$name.log)
  say "$PFX$name done: $n drawings in $((t1 - t0)) s -> $(python3 -c "print(round($n / max($t1 - $t0, 1) * 3600))") drawings/hour, $e errors"
}
run v3_warm bench_b 8 --n 8 --seed 99 --no-eval
run v3_lat bench_b 1 --n 40 --seed 1 --no-eval
run v3_acc bench_b 64 --all
run v3_tp fullpool_dw423 128 --all --no-eval
run plotpass_bench_b bench_b 8 --all
run plotpass_fullpool_dw423 fullpool_dw423 8 --all
say "PLOTPASS DONE ($QUANT $SPEC, render-compare only)"
