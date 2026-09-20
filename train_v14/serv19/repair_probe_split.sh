#!/usr/bin/env bash
# Zero-shot repair turn: hand the model the overlay of the candidate the policy served, with the
# repair prompt carrying that candidate's code, and let it draw K corrections. Generation on
# serv-04's GPUs, execution + IoU on the cluster's CPUs, then the comparison that decides whether
# a repair turn is worth adding to serving: repaired IoU vs the original pick and vs the K=8 ceiling.
#   bash repair_probe_split.sh <repair bench name> [K=8] [run=e55-...]
set -uo pipefail
BENCH=${1:?repair bench dir name under mech/benchmarks/data}; K=${2:-8}; RUN=${3:-e55-rft-real-u5-gt-dw423}
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; S04=wpk-serv-04.mechse.illinois.edu; SDV=/srv/scratch/bimrose2
C=$DV/train_v14/mech/benchmarks/data/$BENCH; STEM=bo${K}_${BENCH}_${RUN}
LOG=$DV/logs/real/repair_probe_$BENCH.log; mkdir -p $DV/logs/real $C/results
say() { echo "$(date '+%m-%d %H:%M') $*" | tee -a $LOG; }
s4() { timeout ${T:-180} ssh -o BatchMode=yes $S04 "$@"; }

say "syncing train_v14 code to serv-04"
rsync -a --exclude 'mech/benchmarks/data' --exclude '__pycache__' $DV/train_v14/ $S04:$SDV/train_v14/ || exit 2
say "shipping $BENCH (overlay sheets + prompts) to serv-04"
s4 "mkdir -p $SDV/mech_benchmarks/$BENCH"
rsync -aL $C/eval_cache_v15.pkl $C/user_prompts.json $C/picks.json $S04:$SDV/mech_benchmarks/$BENCH/ || exit 2
rsync -aL $C/gt_meshes_v15 $S04:$SDV/mech_benchmarks/$BENCH/ || exit 2

if ! s4 "curl -s -m 5 http://127.0.0.1:8100/v1/models | grep -q '\"$RUN\"'"; then
  say "serving $RUN on serv-04"
  s4 "cd $SDV; pkill -f 'vllm serv[e]' 2>/dev/null; sleep 5; \
      MODEL=$SDV/runs/$RUN/final NAME=$RUN setsid nohup bash train_v14/serv19/run_vllm_run_serv04.sh > logs/vllm-$RUN.log 2>&1 < /dev/null & sleep 2; echo started" || exit 2
  for i in $(seq 1 240); do s4 "curl -s -m 5 http://127.0.0.1:8100/health >/dev/null" && break; sleep 15; done
  s4 "curl -s -m 5 http://127.0.0.1:8100/health >/dev/null" || { say "vLLM never ready"; exit 2; }
fi
say "generating K=$K repairs over $BENCH"
T=86400 s4 "cd $SDV; for i in 0 1 2 3 4 5 6 7; do .venv/bin/python train_v14/geom/gen_openai_bo.py --bench mech_benchmarks/$BENCH \
  --base-url http://127.0.0.1:8100/v1 --model $RUN --k $K --temperature 0.7 --shard \$i --nshards 8 --workers 16 \
  --user-prompts mech_benchmarks/$BENCH/user_prompts.json --out results/split/$STEM > logs/gen_${STEM}_\$i.log 2>&1 & done; wait; grep -h DONE logs/gen_${STEM}_*.log | head -3"
s4 "pkill -f 'vllm serv[e]'"; say "generation done, server stopped"

rsync -a "$S04:$SDV/results/split/$STEM.shard*.json.partial.json" $C/results/ || { say "no partials"; exit 2; }
J=$(sbatch --parsable --job-name=score-$BENCH --export=ALL,PARTIALS="$C/results/$STEM.shard*.json.partial.json",GT=$C/gt_meshes_v15,OUT=$C/results/$STEM.json,WORKERS=100 $DV/train_v14/sbatch/score_generic.sbatch)
say "scoring on the L40S node: job $J"
while [ -n "$(squeue -j $J -h 2>/dev/null)" ]; do sleep 120; done

source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
python - "$C/results/$STEM.json" "$C/picks.json" <<'PY' | tee -a $LOG
import json, sys
import numpy as np
res = {p["key"]: p["cands"] for p in json.load(open(sys.argv[1]))["candidates"]}
picks = {r["key"]: r for r in json.load(open(sys.argv[2]))}
keys = [k for k in picks if k in res]; n = max(1, len(keys))
pick = np.array([picks[k]["pick_iou"] for k in keys])
base_best = np.array([picks[k]["best_iou"] for k in keys])
first = np.array([next((c.get("iou", 0.0) for c in res[k] if c.get("draw", 0) == 0), 0.0) for k in keys])
rbest = np.array([max((c.get("iou", 0.0) for c in res[k]), default=0.0) for k in keys])
keep = np.maximum(pick, first)                       # a repair turn you accept only when it executes
both = np.maximum(pick, rbest)
def row(name, x): print(f"  {name:34s} mean {x.mean():.3f}   >=0.85 {(x >= 0.85).mean():5.1%}   median {np.median(x):.3f}")
print(f"[repair probe] {len(keys)} parts")
row("served pick (baseline)", pick)
row("repair, first draw", first)
row("repair, best of K", rbest)
row("max(pick, repair first)", keep)
row("max(pick, repair best)", both)
row("original best-of-8 ceiling", base_best)
imp = first > pick + 0.02; wor = first < pick - 0.02
print(f"  repair first draw improved {imp.sum()}/{len(keys)} parts (mean +{(first-pick)[imp].mean() if imp.any() else 0:.3f}), "
      f"hurt {wor.sum()} (mean {(first-pick)[wor].mean() if wor.any() else 0:.3f}), net {(first-pick).mean():+.3f}")
PY
say "REPAIR PROBE DONE $BENCH"
