#!/usr/bin/env bash
# Post-training evaluation of an e-series run with the GPUs on serv-04 and the CPUs on the
# cluster (no cluster GPU work): serve the final with vLLM on serv-04 and draw K=8 per part for
# the real bench (146), the permissive 0.4.23 bench and the full certified pool; ship the
# partials to the cluster; execute + score + consistency on the L40S node (score_generic);
# verifier-gated selection back on serv-04 (gated_step, v3b LoRA on the e55 base); analyze_ext
# on the cluster. Outputs land where the cluster sbatch chain would have put them
# (results/ext/<TAG>_<RUN>*.json, results/bo8_full_<RUN>*.json), so analyze/compare tools apply.
#   bash eval_run_split.sh <run> [K=8]           (run on the cluster login node)
set -uo pipefail
RUN=${1:?run name}; K=${2:-8}
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; S04=wpk-serv-04.mechse.illinois.edu; SDV=/srv/scratch/bimrose2
B=$DV/train_v14/mech/benchmarks/data; G=$DV/train_v14/geom
LOG=$DV/logs/bo8/split_$RUN.log; mkdir -p $DV/logs/bo8 $DV/results/ext
say() { echo "$(date '+%m-%d %H:%M') $*" | tee -a $LOG; }
s4() { timeout ${T:-120} ssh -o BatchMode=yes $S04 "$@"; }

# --- 1. serve the final on serv-04 (skip if a server for this run is already answering)
say "serving $RUN on serv-04"
if ! s4 "curl -s -m 5 http://127.0.0.1:8100/v1/models | grep -q '\"$RUN\"'"; then
  s4 "cd $SDV; pkill -f 'vllm serv[e]' 2>/dev/null; sleep 5; [ -d runs/$RUN/final ] || { echo 'no final on serv-04'; exit 2; }; \
      MODEL=$SDV/runs/$RUN/final NAME=$RUN setsid nohup bash train_v14/serv19/run_vllm_run_serv04.sh > logs/vllm-$RUN.log 2>&1 < /dev/null & sleep 2; echo started" || exit 2
  for i in $(seq 1 240); do s4 "curl -s -m 5 http://127.0.0.1:8100/health >/dev/null" && break; sleep 15; done
  s4 "curl -s -m 5 http://127.0.0.1:8100/health >/dev/null" || { say "vLLM never became ready"; s4 "tail -20 $SDV/logs/vllm-$RUN.log"; exit 2; }
fi
say "vLLM up"

# --- 2. generate K=8 per part for each bench (8 client shards x 16 threads, resumable)
declare -A BENCH=( [bo8_ext]=ext_bench [bo8_ext_dw423p]=ext_bench_dw423_perm [bo8_full]=fullpool_dw423 )
for TAG in bo8_ext bo8_ext_dw423p bo8_full; do
  bench=${BENCH[$TAG]}
  say "generating $TAG on $bench"
  T=7200 s4 "cd $SDV; for i in 0 1 2 3 4 5 6 7; do .venv/bin/python train_v14/geom/gen_openai_bo.py --bench mech_benchmarks/$bench --base-url http://127.0.0.1:8100/v1 --model $RUN --k $K --temperature 0.7 --shard \$i --nshards 8 --workers 16 --out results/split/${TAG}_$RUN > logs/gen_${TAG}_${RUN}_\$i.log 2>&1 & done; wait; grep -h 'DONE' logs/gen_${TAG}_${RUN}_*.log | head -8"
done
s4 "pkill -f 'vllm serv[e]'" ; say "generation done; vLLM stopped"

# --- 3. ship partials to the cluster and score + consistency on the L40S node (three CPU jobs share ccc0442)
declare -A DEST=( [bo8_ext]=$DV/results/ext [bo8_ext_dw423p]=$DV/results/ext [bo8_full]=$DV/results )
declare -A GTD=( [bo8_ext]=$B/ext_bench/gt_meshes_v15 [bo8_ext_dw423p]=$B/ext_bench_dw423_perm/gt_meshes_v15 [bo8_full]=$DV/step_to_drw/wds_dataset/gt_meshes_v15 )
JOBS=""
for TAG in bo8_ext bo8_ext_dw423p bo8_full; do
  rsync -a "$S04:$SDV/results/split/${TAG}_$RUN.shard*.json.partial.json" ${DEST[$TAG]}/ || { say "no partials for $TAG"; continue; }
  J=$(sbatch --parsable --job-name=score-$TAG --export=ALL,PARTIALS="${DEST[$TAG]}/${TAG}_$RUN.shard*.json.partial.json",GT=${GTD[$TAG]},OUT=${DEST[$TAG]}/${TAG}_$RUN.json $DV/train_v14/sbatch/score_generic.sbatch)
  say "scoring $TAG: job $J"; JOBS="$JOBS $J"
done
while [ -n "$(squeue -j ${JOBS// /,} -h 2>/dev/null)" ]; do sleep 300; done
say "scoring + consistency done"

# --- 4. verifier-gated selection for the two real benches on serv-04 (one GPU; v3b LoRA on the e55 base)
for TAG in bo8_ext bo8_ext_dw423p; do
  bench=${BENCH[$TAG]}; C=$DV/results/ext/${TAG}_$RUN
  [ -f $C.json ] && [ -f ${C}_consistency.json ] || { say "missing scored files for $TAG"; continue; }
  rsync -a $C.json ${C}_consistency.json $S04:$SDV/results/split/
  rsync -a $B/$bench/split.json $S04:$SDV/mech_benchmarks/$bench/split.json 2>/dev/null
  say "gated selection $TAG on serv-04"
  T=7200 s4 "cd $SDV; DV=$SDV PY=$SDV/.venv/bin/python VBASE=$SDV/runs/e55-rft-real-u5-gt-dw423/final CUDA_VISIBLE_DEVICES=0 bash train_v14/geom/gated_step.sh results/split/${TAG}_$RUN.json results/split/${TAG}_${RUN}_consistency.json mech_benchmarks/$bench/eval_cache_v14.pkl $K mech_benchmarks/$bench/split.json > logs/gated_${TAG}_$RUN.log 2>&1; tail -3 logs/gated_${TAG}_$RUN.log"
  rsync -a "$S04:$SDV/results/split/${TAG}_${RUN}_vsel.json*" "$S04:$SDV/results/split/${TAG}_${RUN}_gated*" $DV/results/ext/ 2>/dev/null
  source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
  python $DV/train_v14/mech/benchmarks/analyze_ext.py ${C}_consistency.json --split $B/$bench/split.json --gated ${C}_gated.json > ${C}_summary.txt 2>&1 || true
  say "$TAG summary:"; grep -vE "^\s*$" ${C}_summary.txt | head -12 | tee -a $LOG
done
say "full pool:"; tail -3 $DV/results/bo8_full_${RUN}_consistency.log | tee -a $LOG
say "SPLIT EVAL DONE $RUN"
