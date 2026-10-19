#!/bin/bash
#SBATCH --job-name=ip-s2b
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --nodelist=ccc0442
#SBATCH --time=12:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/indist_pipeline/logs/%x-%j.out
# v2 (code + pool from node RAM, stage_code_shm.sh; score_partials resumes from its .scored.jsonl). In-dist full pipeline (2026-10-14), S1 stage 2 = the bench-B/e2e recipe (pg_score_rc_c2.sh + vscore_s20.sh + pg_make_starts.py)
# with bench = fullpool_dw423: pull K=16 partials from serv-20 -> score_partials (exec 60 s / IoU 90 s, default accept) ->
# consistency_rerank || render_compare --tol 3 --gt-check 5 + rc_metric2 v3 (ccc0442 CPU); v3b-EV verifier (sel_vscore.py,
# e51 base) on serv-20 GPU $VGPU; pg_make_starts.py top-3 distinct -> starts_rl2s60_r{1,2,3}.json -> blocks (runner queue).
#   sbatch --cpus-per-task=40 --mem=300G --export=ALL,VGPU=5 stage2_full.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV; S20=wpk-serv-20.mechse.illinois.edu; SDV=/srv/scratch/bimrose2
P=results/indist_pipeline; NAME=rl2s60; O=$DV/$P/full_k16_$NAME
bash $DV/$P/stage_code_shm.sh || { echo "code staging failed"; exit 1; }
CODE=/dev/shm/bimrose2/ipcode/train_v14; BENCH=/dev/shm/bimrose2/ipcode/fullpool   # node-RAM copies (stage_code_shm.sh): Lustre imports were I/O-bound
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
say() { echo "$(date '+%m-%d %H:%M') $*"; }
on() { timeout 600 ssh -o BatchMode=yes $S20 "$@"; }
S=/dev/shm/bimrose2/ips2_$SLURM_JOB_ID; mkdir -p $S; trap 'rm -rf $S' EXIT
C2=/dev/shm/bimrose2/c2stage
if [ -f $C2/READY ]; then ln -s $C2/venv $S/venv; ln -s $C2/dw_venv $S/dw_venv; ln -s $C2/step_to_drw $S/step_to_drw
else rsync -a --copy-links $DV/.venv/ $S/venv/ & rsync -a --copy-links $DV/dw_venv/ $S/dw_venv/ & rsync -a $DV/mech_step_to_drw/ $S/step_to_drw/ & wait; fi
bash $DV/$P/stage_py_shm.sh || { echo "python staging failed"; exit 1; }
PY=/dev/shm/bimrose2/ipcode/venv/bin/python; RPY=/dev/shm/bimrose2/ipcode/dw_venv/bin/python   # node-RAM Python homes (stage_py_shm.sh)
$PY -c "import build123d, scipy, PIL" && $RPY -c "import draftwright, OCP" || { echo "staged env broken"; exit 1; }
until on test -f $SDV/indist_pipeline/GEN_DONE_$NAME; do sleep 60; done
rsync -a "$S20:$SDV/indist_pipeline/full_k16_$NAME.shard*.json.partial.json" $P/
say "partials pulled: $(ls $P/full_k16_$NAME.shard*.partial.json | wc -l)"
if [ ! -f $O.json ]; then
  $PY $CODE/geom/score_partials.py --partials "$O.shard*.json.partial.json" --gt-dir $BENCH/gt_meshes_v15 --out $O.json \
    --workers ${SW:-40} --exec-timeout 60 --iou-timeout 90 > $O.score.log 2>&1 || { say "score failed"; exit 1; }
fi
say "scored: $(tail -1 $O.score.log)"
# verifier on serv-20 (vscore_s20.sh recipe; cache = fullpool)
rsync -a $O.json $S20:$SDV/indist_pipeline/
on "cd $SDV; nvidia-smi -i $VGPU --query-compute-apps=pid --format=csv,noheader | grep -q . && echo GPU_BUSY || (CUDA_VISIBLE_DEVICES=$VGPU OMP_NUM_THREADS=4 PYTHONPATH=cycle2/train_v14:cycle2/train_v14/geom DRAWING_VLM_ROOT=$SDV \
  setsid nohup .venv/bin/python cycle2/train_v14/geom/sel_vscore.py --cache mech_benchmarks/fullpool_dw423/eval_cache_v15.pkl --outdir indist_pipeline --batch 8 \
  --verifier runs/v3b-verifier-real-reg/final --base $SDV/runs/e51-rft-real-u3-strict90/final k16_$NAME=indist_pipeline/full_k16_$NAME.json \
  > indist_pipeline/logs/vscore_$NAME.log 2>&1 < /dev/null & echo vscore pid \$!)"
[ -f ${O}_consistency.json ] || $PY $CODE/geom/consistency_rerank.py $O.json ${O}_consistency.json > ${O}_consistency.log 2>&1 &
CPID=$!
mkdir -p ${O}_rcpng
[ -f ${O}_rc.json ] || $PY $CODE/geom/render_compare.py --bo $O.json --bench $BENCH --out ${O}_rc.json --py $PY --rpy $RPY \
  --script-dir $S/step_to_drw --workers ${RW:-32} --tol 3 --gt-check 5 --save-png-dir ${O}_rcpng > ${O}_rc.log 2>&1
say "rendered: $(tail -1 ${O}_rc.log)"
$PY $CODE/geom/rc_metric2.py --rc ${O}_rc.json --png-dir ${O}_rcpng --bench $BENCH --out ${O}_rc_v3.json --workers 32 > ${O}_rc_v3.log 2>&1
say "v3: $(tail -1 ${O}_rc_v3.log)"
wait $CPID; say "consistency: $(grep -h re-executed ${O}_consistency.log)"
until on "grep -q 'wrote' $SDV/indist_pipeline/logs/vscore_$NAME.log"; do sleep 60; done
rsync -a $S20:$SDV/indist_pipeline/vpreds_k16_$NAME.json $P/
say "vpreds pulled"
$PY $CODE/geom/pg_make_starts.py --cands $O.json --cons ${O}_consistency.json --vpreds $P/vpreds_k16_$NAME.json \
  --rc ${O}_rc_v3.json --out-stem $P/starts_$NAME --k 16 || { say "starts failed"; exit 1; }
for c in 1 2 3; do python3 $P/make_blocks.py $P/starts_${NAME}_r$c.json ${NAME}_c$c; done
rsync -a $P/blocks/ $S20:$SDV/indist_pipeline/blocks/
say "STAGE2 DONE: S1 blocks queued on both hosts"
