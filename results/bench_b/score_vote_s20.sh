#!/bin/bash
# Score + vote one eval on serv-20, identical settings to grpo_autoeval.sh / grpo_cons_loop.sbatch:
# score_partials.py --workers 16 --exec-timeout 60 --iou-timeout 90 (default --accept 0.8), then consistency_rerank.py.
#   bash bench_b/code/score_vote_s20.sh <stem without .json> <gt_meshes_v15 dir>
cd /srv/scratch/bimrose2
STEM=$1; GT=$2
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
nice -n 10 .venv/bin/python train_v14/geom/score_partials.py --partials "$STEM.shard*.json.partial.json" --gt-dir $GT \
  --out $STEM.json --workers ${W:-16} --exec-timeout 60 --iou-timeout 90 > $STEM.score.log 2>&1 || { echo "SCORE FAILED $STEM"; exit 1; }
nice -n 10 .venv/bin/python train_v14/geom/consistency_rerank.py $STEM.json ${STEM}_consistency.json > ${STEM}_consistency.log 2>&1 || { echo "CONS FAILED $STEM"; exit 1; }
echo "SCORED+VOTED $STEM: $(grep -h 'executed' $STEM.score.log | tail -1) | $(grep -h 're-executed' ${STEM}_consistency.log)"
