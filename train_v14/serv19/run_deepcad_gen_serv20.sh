#!/usr/bin/env bash
# DeepCAD full pass on wpk-serv-20: e55 best-of-K over the verified real-part corpus through vLLM
# (DP=8, one replica per B300), then execute-and-score on the CPUs, then the tier write.
# Concurrency is capped (16 client threads x 8 shards, 48 scoring workers): serv-20 froze at
# ~400 load when a 391-process render ran beside the DeepSeek engine (2026-09-15).
# Measured on the 616-part gate: ~100 parts/min at K=8 (~48k candidates/h), so ~87k parts take
# ~15 h of generation; scoring runs at ~2.4 candidates/s/worker-pool (score_partials, bounded
# overlap cost) and overlaps with nothing else. Every stage is resumable.
#   nohup ./run_deepcad_gen_serv20.sh [corpus=deepcad/corpus_full] [K=8] [tier=rft_deepcad_e55] > logs/deepcad_gen.log 2>&1 &
set -uo pipefail
DV=/srv/scratch/bimrose2; G=$DV/train_v14/geom; M=$DV/mech_benchmarks
C=$DV/${1:-deepcad/corpus_full}; K=${2:-8}; TIER=${3:-rft_deepcad_e55}; R=e55-rft-real-u5-gt-dw423
NS=${NSHARDS:-8}; OUT=$C/results_vllm/bo${K}_full_e55_vllm
[ -f $C/eval_cache_v15.pkl ] || { echo "no eval cache at $C"; exit 1; }
mkdir -p $C/results_vllm $DV/logs; cd $DV
export OPENBLAS_NUM_THREADS=1
# --- 1. serve e55 (skip if already up)
if ! curl -s -m 5 http://127.0.0.1:8100/health >/dev/null 2>&1; then
  setsid nohup bash $DV/train_v14/serv19/run_vllm_e55_serv20.sh > $DV/logs/vllm-e55.log 2>&1 < /dev/null &
  for i in $(seq 1 180); do curl -s -m 5 http://127.0.0.1:8100/health >/dev/null 2>&1 && break; sleep 10; done
  curl -s -m 5 http://127.0.0.1:8100/health >/dev/null || { echo "e55 vllm never ready"; tail -30 $DV/logs/vllm-e55.log; exit 1; }
fi
echo "$(date) [deepcad-gen] vllm up; generating K=$K over $C in $NS shards"
# --- 2. generate (resumable per key; each shard flushes every 50 parts)
T0=$(date +%s)
GEN_PIDS=""
for i in $(seq 0 $((NS-1))); do
  $DV/.venv/bin/python $G/gen_openai_bo.py --bench $C --base-url http://127.0.0.1:8100/v1 --model e55 --k $K \
    --shard $i --nshards $NS --workers ${WORKERS:-16} --out $OUT > $DV/logs/deepcad_gen_shard$i.log 2>&1 &
  GEN_PIDS="$GEN_PIDS $!"
done
wait $GEN_PIDS   # only the shards: a bare `wait` also waits on the vLLM server started above and blocks forever
echo "$(date) [deepcad-gen] generation done in $(( ($(date +%s)-T0)/60 )) min"
for p in $(pgrep -f "vllm serve.*served-model-name e5[5]"); do kill $p; done; sleep 15
# --- 3. execute + score on the CPUs (resumable, 90 s overlap cap)
EXEC_HARNESS=$G/exec_harness.py $DV/.venv/bin/python $G/score_partials.py \
  --partials "$OUT.shard*.json.partial.json" --gt-dir $C/gt_meshes_v15 --out $OUT.json \
  --workers ${SCORE_WORKERS:-48} --exec-timeout 60 --iou-timeout 90 2>&1 | tail -3
# --- 4. tier: accepted = exec and IoU >= 0.8, think trace kept (the e57 recipe, real parts)
$DV/.venv/bin/python $M/write_rft_real.py --bo8 $OUT.json --png-dir $C/render/png --manifest $C/manifest.json \
  --out $DV/$TIER 2>&1 | tail -2
python3 -c "import json;d=json.load(open('$DV/$TIER/stats.json'));print('TIER', d['accepted_records'], 'rows over', d['accepted_keys'], 'parts')"
echo "DEEPCAD GEN DONE $(date)"
