#!/usr/bin/env bash
# Causal renderer test (2026-09-22): e55 best-of-8 on re-rendered copies of the permissive real
# bench (same STEPs, same key-seeded layouts), GPUs on serv-04, scoring on ccc0442.
#   bash variant_bench_eval.sh <bench_name>...     (cluster login node; setsid nohup)
set -uo pipefail
RUN=e55-rft-real-u5-gt-dw423; K=8
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; S04=wpk-serv-04.mechse.illinois.edu; SDV=/srv/scratch/bimrose2
B=$DV/train_v14/mech/benchmarks/data; LOG=$DV/logs/bo8/variant_bench.log; mkdir -p $DV/logs/bo8
say() { echo "$(date '+%m-%d %H:%M') $*" | tee -a $LOG; }
s4() { timeout ${T:-120} ssh -o BatchMode=yes $S04 "$@"; }
for b in "$@"; do
  while ! grep -q "STAGE1 DONE" $B/$b/logs/stage.log 2>/dev/null; do sleep 60; done
  s4 "mkdir -p $SDV/mech_benchmarks/$b"
  rsync -a --copy-links --exclude step_mm --exclude render/iso $B/$b/ $S04:$SDV/mech_benchmarks/$b/ || { say "rsync $b failed"; exit 2; }
done
say "benches shipped: $*"
if ! s4 "curl -s -m 5 http://127.0.0.1:8100/v1/models | grep -q '\"$RUN\"'"; then
  s4 "cd $SDV; MODEL=$SDV/runs/$RUN/final NAME=$RUN setsid nohup bash train_v14/serv19/run_vllm_run_serv04.sh > logs/vllm-$RUN-variant.log 2>&1 < /dev/null & sleep 2; echo started"
  for i in $(seq 1 240); do s4 "curl -s -m 5 http://127.0.0.1:8100/health >/dev/null" && break; sleep 15; done
  s4 "curl -s -m 5 http://127.0.0.1:8100/health >/dev/null" || { say "vLLM never ready"; s4 "tail -30 $SDV/logs/vllm-$RUN-variant.log" >> $LOG; exit 2; }
fi
say "vLLM up"
for b in "$@"; do
  TAG=bo8_$b; say "generating $TAG"
  T=10800 s4 "cd $SDV; for i in 0 1 2 3 4 5 6 7; do .venv/bin/python train_v14/geom/gen_openai_bo.py --bench mech_benchmarks/$b --base-url http://127.0.0.1:8100/v1 --model $RUN --k $K --temperature 0.7 --shard \$i --nshards 8 --workers 16 --out results/split/${TAG}_$RUN > logs/gen_${TAG}_\$i.log 2>&1 & done; wait; grep -h DONE logs/gen_${TAG}_*.log | head -8" >> $LOG 2>&1
done
T=60 s4 "pkill -f 'vllm serv[e]'"; say "generation done; vLLM stopped"
JOBS=""
for b in "$@"; do
  TAG=bo8_$b
  rsync -a "$S04:$SDV/results/split/${TAG}_$RUN.shard*.json.partial.json" $DV/results/ext/ || { say "no partials $TAG"; continue; }
  J=$(sbatch --parsable --job-name=score-$b --export=ALL,PARTIALS="$DV/results/ext/${TAG}_$RUN.shard*.json.partial.json",GT=$B/$b/gt_meshes_v15,OUT=$DV/results/ext/${TAG}_$RUN.json $DV/train_v14/sbatch/score_generic.sbatch)
  say "scoring $TAG job $J"; JOBS="$JOBS $J"
done
J=$(echo $JOBS | tr ' ' ','); while [ -n "$(squeue -j $J -h 2>/dev/null)" ]; do sleep 120; done
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
for b in "$@"; do C=$DV/results/ext/bo8_${b}_$RUN
  python $DV/train_v14/mech/benchmarks/analyze_ext.py ${C}_consistency.json --split $B/$b/split.json > ${C}_summary.txt 2>&1
  say "$b summary:"; grep -vE "^\s*$" ${C}_summary.txt | head -14 >> $LOG
done
say "VARIANT EVAL DONE"
