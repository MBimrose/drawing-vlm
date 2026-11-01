#!/bin/bash
#SBATCH --job-name=ab-score
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=100
#SBATCH --mem=300G
#SBATCH --time=24:00:00
#SBATCH --nodelist=ccc0442
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/ab/%x-%j.out
# Kimi-trace A/B (2026-10-29): score an arm's samples (train_v14/serv19/ab_sample.sh) and pack its own RFT tier + round-1
# mix (geom/ab_pack_tier.py). Per job of amvlm/ab/jobs.txt: wait for <job>.GEN_DONE (SRC=s19: on serv-19, partials pulled
# here; SRC=local: the mirror), score_partials.py with the bench settings (exec 60 s, IoU 90 s) against the job's
# gt_meshes_v15, NPAR jobs at a time x SW workers. Then pack into the mirror's amvlm/ab/tier_<arm> (SRC=s19: pushed to
# serv-19 too) and write tier_<arm>/TIER_READY.
#   sbatch --export=ALL,ARM=b,SRC=s19 ab_score.sbatch
# PUSH=1 pushes the tier to serv-19 for SRC=local too (2026-10-29: all training on serv-19, sampling on the cluster).
# Round 2 (2026-10-31): TAG=a2 JOBS=<ab>/jobs_r2.txt scores gen_a2 into scored_a2; jobs are claimed (mkdir), so extra
# scorers on other nodes can share them (PACK=0: score only); the packing job waits for every job, then packs the union
# of this round and PREV="<scored dir>:<jobs file> ..." into tier_<TAG>.
#   sbatch --export=ALL,ARM=a,TAG=a2,JOBS=$M/amvlm/ab/jobs_r2.txt,PREV=<DV>/results/american_vlm/ab/scored_a:$M/amvlm/ab/jobs.txt,PUSH=1 ab_score.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; M=/projects/illinois/eng/ece/wpk/bimrose2/srvmirror
H=wpk-serv-19.mechse.illinois.edu; R=/srv/scratch/bimrose2; ARM=${ARM:?}; SRC=${SRC:-local}
TAG=${TAG:-$ARM}; A=$M/amvlm/ab; G=$A/gen_$TAG; S=$DV/results/american_vlm/ab/scored_$TAG; JOBS=${JOBS:-$A/jobs.txt}
mkdir -p $G $S/claims
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
PY=/dev/shm/bimrose2/ipcode/venv/bin/python
[ -x $PY ] || bash $DV/results/indist_pipeline/stage_py_shm.sh
say() { echo "$(date '+%m-%d %H:%M') $*"; }
one() {   # one <job> <bench>
  local n=$1 b=$2
  if [ $SRC = s19 ]; then
    until ssh -o BatchMode=yes $H "test -f $R/amvlm/ab/gen_$TAG/$n.GEN_DONE"; do sleep 120; done
    rsync -a "$H:$R/amvlm/ab/gen_$TAG/$n.shard*.json.partial.json" $G/
  else
    until [ -f $G/$n.GEN_DONE ]; do sleep 120; done
  fi
  say "scoring $n"
  $PY $DV/train_v14/geom/score_partials.py --partials "$G/$n.shard*.json.partial.json" --gt-dir $M/$b/gt_meshes_v15 \
    --out $S/$n.json --workers ${SW:-32} --exec-timeout 60 --iou-timeout 90 > $S/$n.score.log 2>&1 \
    && say "scored $n: $(grep -h executed $S/$n.score.log | tail -1)" || { say "SCORE FAILED $n"; touch $S/$n.FAILED; }
}
cd $DV
JP=()
while read -r n b k keys; do
  [ -z "$n" ] && continue
  [ -s $S/$n.json ] && continue
  mkdir $S/claims/$n 2>/dev/null || continue
  while [ $(jobs -rp | wc -l) -ge ${NPAR:-3} ]; do sleep 30; done
  one $n $b & JP+=($!)
done < $JOBS
wait "${JP[@]}"
[ "${PACK:-1}" = 1 ] || { say "AB SCORE DONE (no pack)"; exit 0; }
left() { while read -r n b k keys; do [ -n "$n" ] && [ ! -s $S/$n.json ] && [ ! -f $S/$n.FAILED ] && echo $n; done < $JOBS; }
until [ -z "$(left)" ]; do sleep 120; done   # jobs claimed by the other scorers
miss=$(while read -r n b k keys; do [ -n "$n" ] && [ ! -s $S/$n.json ] && echo $n; done < $JOBS)
[ -z "$miss" ] || { say "unscored: $miss"; exit 1; }
rm -rf $A/tier_$TAG
SC=($S); JB=($JOBS); for p in ${PREV:-}; do SC+=(${p%%:*}); JB+=(${p#*:}); done
$PY $DV/train_v14/geom/ab_pack_tier.py --arm $TAG --scored "${SC[@]}" --jobs "${JB[@]}" --root $A --srv $M --abc $A/abc_gt \
  > $S/pack.log 2>&1 || { say "PACK FAILED: $(tail -3 $S/pack.log)"; exit 1; }
say "$(tail -1 $S/pack.log | cut -c1-600)"
if [ $SRC = s19 ] || [ "${PUSH:-0}" = 1 ]; then
  rsync -a $A/tier_$TAG $A/abc_gt $H:$R/amvlm/ab/ && ssh -o BatchMode=yes $H "touch $R/amvlm/ab/tier_$TAG/TIER_READY" \
    || { say "push to serv-19 failed"; exit 1; }
fi
touch $A/tier_$TAG/TIER_READY; say "AB TIER READY $TAG"
