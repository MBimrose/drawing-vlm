#!/usr/bin/env bash
# solve_corpus_split.sh on serv-20 GPUs 4-7 ONLY (DP=4, 4 shards; GPUs 0-3 belong to someone else;
# serv-04 is off-limits since 2026-09-23). Scoring on the cluster CPU, then the
# accepted rows (IoU >= 0.8, think kept) are written as an RFT tier and packed into shards.
#   bash solve_corpus_2box.sh <corpus> [K=8] [tier=rft_<corpus>]      (cluster login node, setsid nohup)
set -uo pipefail
CORPUS=${1:?corpus}; K=${2:-8}; TIER=${3:-rft_$CORPUS}; RUN=e55-rft-real-u5-gt-dw423
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; SDV=/srv/scratch/bimrose2
S20=wpk-serv-20.mechse.illinois.edu
C=$DV/train_v14/mech/benchmarks/data/$CORPUS; STEM=bo${K}_${CORPUS}_${RUN}
LOG=$DV/logs/real/solve20_$CORPUS.log; mkdir -p $DV/logs/real $C/results
say() { echo "$(date '+%m-%d %H:%M') $*" | tee -a $LOG; }
on() { local h=$1; shift; timeout ${T:-180} ssh -o BatchMode=yes $h "$@"; }
for H in $S20; do
  rsync -a --exclude 'mech/benchmarks/data' --exclude '__pycache__' $DV/train_v14/ $H:$SDV/train_v14/ || { say "sync $H failed"; exit 2; }
  on $H "mkdir -p $SDV/mech_benchmarks/$CORPUS $SDV/results/split"
  rsync -a $C/eval_cache_v15.pkl $C/manifest.json $C/gt_meshes_v15 $H:$SDV/mech_benchmarks/$CORPUS/ || exit 2
done
say "corpus shipped to both boxes"
# serv-04: 8-way DP via its native venv runner; serv-20: apptainer runner pinned to GPUs 4-7
if ! on $S20 "curl -s -m 5 http://127.0.0.1:8100/v1/models | grep -q '\"e55\"'"; then
  on $S20 "cd $SDV; CUDA_VISIBLE_DEVICES=4,5,6,7 DP=4 SEQS=96 setsid nohup bash train_v14/serv19/run_vllm_e55_serv20.sh > logs/vllm-e55-g4567.log 2>&1 < /dev/null & sleep 1; echo ok"
fi
for H in $S20; do
  for i in $(seq 1 240); do on $H "curl -s -m 5 http://127.0.0.1:8100/health >/dev/null" && break; sleep 15; done
  on $H "curl -s -m 5 http://127.0.0.1:8100/health >/dev/null" || { say "vLLM never ready on $H"; exit 2; }
done
say "server up; generating K=$K (4 shards on serv-20)"
GEN=".venv/bin/python train_v14/geom/gen_openai_bo.py --bench mech_benchmarks/$CORPUS --base-url http://127.0.0.1:8100/v1 --k $K --temperature 0.7 --nshards 4 --workers 16 --out results/split/$STEM"
T=172800 on $S20 "cd $SDV; for i in 0 1 2 3; do $GEN --model e55 --shard \$i > logs/gen_${STEM}_\$i.log 2>&1 & done; wait"
say "generation done: $(on $S20 "cd $SDV; grep -h DONE logs/gen_${STEM}_*.log | wc -l") shards DONE"
on $S20 "pkill -u bimrose2 -f 'vllm serv[e]'"; say "server stopped"
rsync -a "$S20:$SDV/results/split/$STEM.shard*.json.partial.json" $C/results/ || { say "no serv-20 partials"; }
NP=$(ls $C/results/$STEM.shard*.json.partial.json 2>/dev/null | wc -l); say "partials: $NP"
[ "$NP" -eq 4 ] || { say "expected 4 partials, got $NP; abort before scoring"; exit 2; }
J=$(sbatch --parsable --job-name=score-$CORPUS --time=24:00:00 --cpus-per-task=110 --export=ALL,PARTIALS="$C/results/$STEM.shard*.json.partial.json",GT=$C/gt_meshes_v15,OUT=$C/results/$STEM.json,WORKERS=100 $DV/train_v14/sbatch/score_generic.sbatch)
say "scoring job $J"
while [ -n "$(squeue -j $J -h 2>/dev/null)" ]; do sleep 300; done
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
mkdir -p $C/render/png_v; for f in $C/render/png/*.png; do b=$(basename $f .png); ln -sf $f $C/render/png_v/${b}_v0.png; done
python $DV/train_v14/mech/benchmarks/write_rft_real.py --bo8 $C/results/$STEM.json --png-dir $C/render/png_v --manifest $C/manifest.json --out $DV/$TIER 2>&1 | tail -3 | tee -a $LOG
python - $DV/$TIER <<'PY' | tee -a $LOG
# strict tier (as rft_strict90): IoU >= 0.9, at most 2 draws per part (highest IoU first)
import json, sys, os, collections
d = sys.argv[1]; src = os.path.join(d, "accepted-000.jsonl"); os.replace(src, os.path.join(d, "accepted_all.jsonl"))
rows = [json.loads(l) for l in open(os.path.join(d, "accepted_all.jsonl"))]
by = collections.defaultdict(list)
for r in rows:
    if r["iou"] >= 0.9: by[r["key"]].append(r)
out = [r for k, v in by.items() for r in sorted(v, key=lambda r: -r["iou"])[:2]]
with open(src, "w") as f:
    for r in out: f.write(json.dumps(r) + "\n")
print(f"[tier] {len(rows)} rows >= 0.8 -> {len(out)} rows >= 0.9 over {len(by)} parts")
PY
python $DV/train_v14/geom/pack_rft_shards_dir.py $DV/$TIER $DV/$TIER/png   # write_rft_real copies <key>.png here 2>&1 | tail -2 | tee -a $LOG
say "SOLVE20 DONE $CORPUS -> $TIER"
