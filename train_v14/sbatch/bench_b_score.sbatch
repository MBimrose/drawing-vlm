#!/bin/bash
#SBATCH --job-name=bb-score
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=200G
#SBATCH --time=08:00:00
#SBATCH --nodelist=ccc0442
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/bo8/%x-%j.out
# Bench B (2026-10-10): score + vote GPU-7 evals on ccc0442 in parallel with serv-20's loop (same settings:
# score_partials --workers 16 --exec-timeout 60 --iou-timeout 90, default --accept 0.8; consistency_rerank).
# Waits for serv-20's GEN_DONE marker, pulls the partials, scores here, pushes nothing back.
#   sbatch --export=ALL,NAMES="benchb_rft2_rl_s60 benchb_ent_t10_s120" bench_b_score.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; S20=wpk-serv-20.mechse.illinois.edu; O=$DV/results/bench_b/eval
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
PY=/dev/shm/bimrose2/c2stage/venv/bin/python; [ -x $PY ] || PY=$DV/.venv/bin/python
cd $DV
for n in $NAMES; do
  until ssh -o BatchMode=yes $S20 "test -f /srv/scratch/bimrose2/bench_b/eval/GEN_DONE_$n"; do sleep 120; done
  rsync -a "$S20:/srv/scratch/bimrose2/bench_b/eval/$n.shard*.json.partial.json" $O/
  case $n in real_*) GT=$DV/train_v14/mech/benchmarks/data/ext_bench_dw423_perm/gt_meshes_v15;; *) GT=$DV/results/bench_b/bench/gt_meshes_v15;; esac
  echo "$(date '+%m-%d %H:%M') scoring $n"
  $PY train_v14/geom/score_partials.py --partials "$O/$n.shard*.json.partial.json" --gt-dir $GT --out $O/$n.json \
    --workers 16 --exec-timeout 60 --iou-timeout 90 > $O/$n.score.log 2>&1 || { echo "SCORE FAILED $n"; continue; }
  $PY train_v14/geom/consistency_rerank.py $O/$n.json $O/${n}_consistency.json > $O/${n}_consistency.log 2>&1 || echo "CONS FAILED $n"
  echo "SCORED+VOTED $n: $(grep -h 'executed' $O/$n.score.log | tail -1) | $(grep -h 're-executed' $O/${n}_consistency.log)"
done
echo "BB SCORE DONE $(date)"
