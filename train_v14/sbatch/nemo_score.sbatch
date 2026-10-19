#!/bin/bash
#SBATCH --job-name=nemo-score
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=200G
#SBATCH --time=24:00:00
#SBATCH --nodelist=ccc0442
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/bo8/%x-%j.out
# Nemotron port (2026-10-15): score + vote serv-19 generations on ccc0442 CPUs with the bench-B / grpo_eval settings
# (score_partials --workers 16 --exec-timeout 60 --iou-timeout 90, default --accept 0.8; consistency_rerank), python
# from the /dev/shm stage (stage_py_shm.sh). Waits for serv-19's <stem>.GEN_DONE, pulls the partials, scores here.
#   sbatch --export=ALL,NAMES="real_nemobase benchb_nemobase" nemo_score.sbatch
# 2026-10-17: RDIR (serv-19 partials dir) / ODIR (cluster results dir) / SW (score workers) overridable; results-table ablations:
#   sbatch --cpus-per-task=32 --export=ALL,NAMES="real_e24 ...",RDIR=/srv/scratch/bimrose2/abl/results,ODIR=$DV/results/ablations,SW=32 nemo_score.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; H=wpk-serv-19.mechse.illinois.edu; R=${RDIR:-/srv/scratch/bimrose2/nemotron/results}
O=${ODIR:-$DV/results/nemotron}; mkdir -p $O
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
PY=/dev/shm/bimrose2/ipcode/venv/bin/python
[ -x $PY ] || bash $DV/results/indist_pipeline/stage_py_shm.sh
[ -x $PY ] || { echo "no staged python"; exit 2; }
cd $DV
for n in $NAMES; do
  until ssh -o BatchMode=yes $H "test -f $R/$n.GEN_DONE"; do sleep 120; done
  rsync -a "$H:$R/$n.shard*.json.partial.json" $O/
  case $n in real_*) GT=$DV/train_v14/mech/benchmarks/data/ext_bench_dw423_perm/gt_meshes_v15;;
             benchb_*) GT=$DV/results/bench_b/bench/gt_meshes_v15;;
             full_*) GT=$DV/train_v14/mech/benchmarks/data/fullpool_dw423/gt_meshes_v15;; esac
  echo "$(date '+%m-%d %H:%M') scoring $n"
  $PY train_v14/geom/score_partials.py --partials "$O/$n.shard*.json.partial.json" --gt-dir $GT --out $O/$n.json \
    --workers ${SW:-16} --exec-timeout 60 --iou-timeout 90 > $O/$n.score.log 2>&1 || { echo "SCORE FAILED $n"; continue; }
  $PY train_v14/geom/consistency_rerank.py $O/$n.json $O/${n}_consistency.json > $O/${n}_consistency.log 2>&1 || echo "CONS FAILED $n"
  echo "SCORED+VOTED $n: $(grep -h 'executed' $O/$n.score.log | tail -1) | $(grep -h 're-executed' $O/${n}_consistency.log)"
done
echo "NEMO SCORE DONE $(date)"
