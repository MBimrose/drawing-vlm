#!/bin/bash
# Bench B full pipeline, stage 2 on serv-20 (2026-10-10). The commands of results/cycle2/pipeline/pg_score_rc_c2.sh (score_partials
# eval rule, consistency_rerank, render_compare --tol 3 --gt-check 5 + rc_metric2 v3) and vscore_s20.sh (v3b-EV verifier on the
# e51 base) with bench = mech_benchmarks/bench_b. CPU kept modest (score 24 workers, render 16, v3 16); verifier on GPU 7.
set -uo pipefail
cd /srv/scratch/bimrose2
NAME=rl2s60; O=bench_b/pipeline; STEM=$O/benchb_k16_$NAME; BENCH=/srv/scratch/bimrose2/mech_benchmarks/bench_b
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
PY=/srv/scratch/bimrose2/.venv/bin/python; RPY=/srv/scratch/bimrose2/dw_venv/bin/python; SD=/srv/scratch/bimrose2/mech_step_to_drw
say() { echo "$(date '+%m-%d %H:%M') $*"; }
until [ -f $O/GEN_DONE_$NAME ]; do sleep 60; done
[ -f $STEM.json ] || nice -n 10 $PY train_v14/geom/score_partials.py --partials "$STEM.shard*.json.partial.json" --gt-dir $BENCH/gt_meshes_v15 \
  --out $STEM.json --workers 24 --exec-timeout 60 --iou-timeout 90 > $STEM.score.log 2>&1 || { say "score failed"; exit 1; }
say "scored: $(tail -1 $STEM.score.log)"
# verifier (GPU 7 is free once generation is done)
( until ! nvidia-smi -i 7 --query-compute-apps=pid --format=csv,noheader | grep -q .; do sleep 30; done
  CUDA_VISIBLE_DEVICES=7 OMP_NUM_THREADS=4 PYTHONPATH=cycle2/train_v14:cycle2/train_v14/geom DRAWING_VLM_ROOT=/srv/scratch/bimrose2 \
  $PY cycle2/train_v14/geom/sel_vscore.py --cache $BENCH/eval_cache_v15.pkl --outdir $O --batch 8 \
    --verifier runs/v3b-verifier-real-reg/final --base /srv/scratch/bimrose2/runs/e51-rft-real-u3-strict90/final \
    k16_$NAME=$STEM.json > $O/logs/vscore_$NAME.log 2>&1; say "VSCORE DONE $?" ) &
VP=$!
[ -f ${STEM}_consistency.json ] || nice -n 10 $PY train_v14/geom/consistency_rerank.py $STEM.json ${STEM}_consistency.json > ${STEM}_consistency.log 2>&1 &
CP=$!
mkdir -p ${STEM}_rcpng
[ -f ${STEM}_rc.json ] || nice -n 10 $PY train_v14/geom/render_compare.py --bo $STEM.json --bench $BENCH --out ${STEM}_rc.json --py $PY --rpy $RPY \
  --script-dir $SD --workers 16 --tol 3 --gt-check 5 --save-png-dir ${STEM}_rcpng > ${STEM}_rc.log 2>&1
say "rendered: $(tail -1 ${STEM}_rc.log)"
nice -n 10 $PY train_v14/geom/rc_metric2.py --rc ${STEM}_rc.json --png-dir ${STEM}_rcpng --bench $BENCH --out ${STEM}_rc_v3.json --workers 16 > ${STEM}_rc_v3.log 2>&1
say "v3: $(tail -1 ${STEM}_rc_v3.log)"
wait $CP; say "consistency: $(grep -h re-executed ${STEM}_consistency.log)"
wait $VP
say "STAGE2 DONE"
