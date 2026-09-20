#!/usr/bin/env bash
# Solve a real-STEP corpus with a trained model: generate K draws per part on serv-04's GPUs
# (native vLLM), execute + score on the cluster's CPUs (serv-04's glibc cannot load OCP), then
# write the accepted rows as an RFT tier. This is the union5 recipe, split across the two boxes.
#   bash solve_corpus_split.sh <corpus name under mech/benchmarks/data> [K=8] [run=e55-...] [tier=rft_real_<corpus>]
# Resumable: generation skips keys already drawn, scoring resumes from <out>.scored.jsonl.
set -uo pipefail
CORPUS=${1:?corpus name}; K=${2:-8}; RUN=${3:-e55-rft-real-u5-gt-dw423}; TIER=${4:-rft_real_$CORPUS}
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; S04=wpk-serv-04.mechse.illinois.edu; SDV=/srv/scratch/bimrose2
C=$DV/train_v14/mech/benchmarks/data/$CORPUS; STEM=bo${K}_${CORPUS}_${RUN}
LOG=$DV/logs/real/solve_$CORPUS.log; mkdir -p $DV/logs/real $C/results
say() { echo "$(date '+%m-%d %H:%M') $*" | tee -a $LOG; }
s4() { timeout ${T:-180} ssh -o BatchMode=yes $S04 "$@"; }

say "syncing train_v14 code to serv-04"
rsync -a --exclude 'mech/benchmarks/data' --exclude '__pycache__' $DV/train_v14/ $S04:$SDV/train_v14/ || exit 2
say "shipping $CORPUS to serv-04 (eval cache + gt meshes + manifest)"
s4 "mkdir -p $SDV/mech_benchmarks/$CORPUS"
rsync -a $C/eval_cache_v15.pkl $C/manifest.json $S04:$SDV/mech_benchmarks/$CORPUS/ || exit 2
rsync -a $C/gt_meshes_v15 $S04:$SDV/mech_benchmarks/$CORPUS/ || exit 2

say "serving $RUN on serv-04"
if ! s4 "curl -s -m 5 http://127.0.0.1:8100/v1/models | grep -q '\"$RUN\"'"; then
  s4 "cd $SDV; pkill -f 'vllm serv[e]' 2>/dev/null; sleep 5; [ -d runs/$RUN/final ] || { echo 'no final'; exit 2; }; \
      MODEL=$SDV/runs/$RUN/final NAME=$RUN setsid nohup bash train_v14/serv19/run_vllm_run_serv04.sh > logs/vllm-$RUN.log 2>&1 < /dev/null & sleep 2; echo started" || exit 2
  for i in $(seq 1 240); do s4 "curl -s -m 5 http://127.0.0.1:8100/health >/dev/null" && break; sleep 15; done
  s4 "curl -s -m 5 http://127.0.0.1:8100/health >/dev/null" || { say "vLLM never ready"; s4 "tail -20 $SDV/logs/vllm-$RUN.log"; exit 2; }
fi
say "vLLM up; generating K=$K over $CORPUS (8 shards x 16 threads)"
T=86400 s4 "cd $SDV; for i in 0 1 2 3 4 5 6 7; do .venv/bin/python train_v14/geom/gen_openai_bo.py --bench mech_benchmarks/$CORPUS \
  --base-url http://127.0.0.1:8100/v1 --model $RUN --k $K --temperature 0.7 --shard \$i --nshards 8 --workers 16 \
  --out results/split/$STEM > logs/gen_${STEM}_\$i.log 2>&1 & done; wait; grep -h DONE logs/gen_${STEM}_*.log | head -8"
s4 "pkill -f 'vllm serv[e]'"; say "generation done, server stopped"

rsync -a "$S04:$SDV/results/split/$STEM.shard*.json.partial.json" $C/results/ || { say "no partials"; exit 2; }
J=$(sbatch --parsable --job-name=score-$CORPUS --export=ALL,PARTIALS="$C/results/$STEM.shard*.json.partial.json",GT=$C/gt_meshes_v15,OUT=$C/results/$STEM.json,WORKERS=100 $DV/train_v14/sbatch/score_generic.sbatch)
say "scoring on the L40S node: job $J"
while [ -n "$(squeue -j $J -h 2>/dev/null)" ]; do sleep 300; done
say "scoring done: $(grep -E '^\[score\] executed' $DV/logs/bo8/score-$CORPUS-$J.out | tail -1)"

source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
python $DV/train_v14/mech/benchmarks/write_rft_real.py --bo8 $C/results/$STEM.json --png-dir $C/render/png \
  --manifest $C/manifest.json --out $DV/$TIER 2>&1 | tail -3 | tee -a $LOG
python - "$C/results/$STEM.json" <<'PY' | tee -a $LOG
import json, sys
d = json.load(open(sys.argv[1])); parts = d["candidates"]; n = max(1, len(parts))
first = [next((c.get("iou", 0.0) for c in p["cands"] if c.get("draw", 0) == 0), 0.0) for p in parts]
best = [max((c.get("iou", 0.0) for c in p["cands"]), default=0.0) for p in parts]
print(f"[solve] {len(parts)} parts | first draw {sum(first)/n:.3f} ({sum(x>=0.85 for x in first)/n:.1%} >=0.85) "
      f"| best-of-N {sum(best)/n:.3f} ({sum(x>=0.85 for x in best)/n:.1%} >=0.85, {sum(x>=0.8 for x in best)/n:.1%} >=0.80)")
PY
say "SOLVE CORPUS DONE $CORPUS -> $TIER"
