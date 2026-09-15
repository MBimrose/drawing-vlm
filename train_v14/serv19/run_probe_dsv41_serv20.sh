#!/usr/bin/env bash
# Zero-shot DeepSeek-V4.1-Flash on the real bench, on wpk-serv-20 (8x B300): vLLM from the
# official Docker image via apptainer (FP4 experts are Blackwell-native), then
# probe_openai_vlm.py with the fine-tuned model's exact prompt and scorer.
#   nohup ./run_probe_dsv41_serv20.sh [BENCH_DIR] [TAG] [N] [K] > logs/probe_dsv41.log 2>&1 &
set -uo pipefail
DV=/srv/scratch/bimrose2
B=${1:-$DV/mech_benchmarks/ext_bench}; T=${2:-probe_dsv41_ext}; N=${3:-146}; K=${4:-1}
MODEL=$DV/models/DeepSeek-V4.1-Flash; SIF=$DV/containers/vllm-dsv41.sif
[ -f $MODEL/config.json ] && [ -f $SIF ] || { echo "missing model or image"; exit 1; }
mkdir -p $DV/results/ext $DV/logs
export VLLM_ENGINE_READY_TIMEOUT_S=3600
apptainer exec --nv --bind $DV:$DV --bind /tmp:/tmp $SIF \
  vllm serve $MODEL --served-model-name deepseek-ai/DeepSeek-V4.1-Flash \
    --host 127.0.0.1 --port 8000 --tensor-parallel-size 8 \
    --tokenizer-mode deepseek_v41 --reasoning-parser deepseek_v41 \
    --gpu-memory-utilization 0.90 --max-model-len 32768 --max-num-seqs 16 \
    --max-num-batched-tokens 16384 --limit-mm-per-prompt '{"image": 1}' \
    > $DV/logs/vllm-dsv41.log 2>&1 &
VPID=$!
for i in $(seq 1 360); do
  curl -s -m 5 http://127.0.0.1:8000/health >/dev/null 2>&1 && { echo "$(date) vllm ready after $((i*10)) s"; break; }
  kill -0 $VPID 2>/dev/null || { echo "vllm died; tail:"; tail -40 $DV/logs/vllm-dsv41.log; exit 1; }
  sleep 10
done
curl -s -m 5 http://127.0.0.1:8000/health >/dev/null || { echo "vllm never became ready"; tail -40 $DV/logs/vllm-dsv41.log; kill $VPID; exit 1; }
cd $DV && source train_v14/env.sh 2>/dev/null || true
export OPENBLAS_NUM_THREADS=1
$DV/.venv/bin/python $DV/train_v14/geom/probe_openai_vlm.py --bench $B --base-url http://127.0.0.1:8000/v1 \
  --model deepseek-ai/DeepSeek-V4.1-Flash --out $DV/results/ext/$T.json --n $N --k $K \
  --temperature ${TEMP:-0} --workers ${WORKERS:-4}
kill $VPID 2>/dev/null; wait $VPID 2>/dev/null
echo "PROBE DONE $T"
