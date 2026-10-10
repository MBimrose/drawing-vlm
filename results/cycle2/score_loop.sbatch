#!/bin/bash
#SBATCH --job-name=c2-score
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodelist=ccc0442
#SBATCH --cpus-per-task=72
#SBATCH --mem=200G
#SBATCH --time=24:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/cycle2/logs/%x-%j.out
# Expert iteration round 2 (2026-10-09): pull the K=16 partials from serv-20 (cycle2/gen_driver.sh) and execute + score
# them against GT here (serv-20 CPUs carry the RL arms). score_partials.py is resumable (<out>.scored.jsonl); exec 60 s /
# IoU 90 s subprocess timeouts (= eval rule); --accept 0 = exact IoU for every candidate (no volume-bound shortcut).
#   sbatch --export=ALL,TAG=<tag> results/cycle2/score_loop.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV; source train_v14/env.sh
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=$DV/train_v14:$DV/train_v14/geom
S20=wpk-serv-20.mechse.illinois.edu; O=results/cycle2/gen; mkdir -p $O
BD=train_v14/mech/benchmarks/data
declare -A GT=( [c4]=$BD/rft_corpus4/gt_meshes_v15 [c2]=$BD/rft_corpus2_dw423/gt_meshes_v15 [c1]=$BD/rft_corpus_dw423/gt_meshes_v15
                [rp2]=$BD/rft_realpool_v2/gt_meshes_v15 )
SETS=${SETS:-"A_c4 A_c2 A_c1 B_rp2 C_c4 C_c2 C_c1"}; NSETS=$(echo $SETS | wc -w)
# venv staged in /dev/shm: scoring subprocesses importing build123d/OCP from Lustre ran at ~30% CPU (2 cands/s at 64 workers)
SH=/dev/shm/bimrose2/c2score_$SLURM_JOB_ID; mkdir -p $SH; trap "rm -rf $SH" EXIT
rsync -a --copy-links $DV/.venv/ $SH/venv/; PY=$SH/venv/bin/python; $PY -c "import build123d, trimesh" || PY=$DV/.venv/bin/python
echo "python: $PY"
hostname; uptime
while true; do
  # markers first: a set counts as final only if its GEN_DONE marker existed BEFORE its partial was copied
  rsync -a --include 'GEN_*' --exclude '*' "$S20:/srv/scratch/bimrose2/cycle2/gen/" $O/ 2>/dev/null
  MK=$(ls $O/ | grep '^GEN_' | tr '\n' ' ')
  rsync -a --exclude '*.scored.jsonl' "$S20:/srv/scratch/bimrose2/cycle2/gen/" $O/ 2>/dev/null
  alldone=0; [[ " $MK " == *" GEN_ALL_DONE_$TAG "* ]] && alldone=1
  for s in $SETS; do
    f=$O/${s}_$TAG.shard0.json.partial.json; [ -f $f ] || continue
    [ -f $O/SCORED_${s}_$TAG ] && continue
    gd=0; [[ " $MK " == *" GEN_DONE_${s}_$TAG "* ]] && gd=1
    $PY train_v14/geom/score_partials.py --partials "$f" --gt-dir ${GT[${s#*_}]} --out $O/${s}_$TAG.json \
      --workers ${WORKERS:-64} --exec-timeout 60 --iou-timeout 90 --accept 0 >> results/cycle2/logs/score_${s}.log 2>&1
    [ $gd = 1 ] && { touch $O/SCORED_${s}_$TAG; echo "$(date '+%m-%d %H:%M') SCORED $s"; }
    rsync -a $O/${s}_$TAG.json.scored.jsonl "$S20:/srv/scratch/bimrose2/cycle2/gen/" 2>/dev/null
  done
  n=0; for s in $SETS; do [ -f $O/SCORED_${s}_$TAG ] && n=$((n+1)); done
  [ $alldone = 1 ] && [ $n -ge $NSETS ] && break
  sleep 120
done
echo "SCORE LOOP DONE $(date)"
