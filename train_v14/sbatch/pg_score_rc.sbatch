#!/bin/bash
#SBATCH --job-name=pg-score
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --nodelist=ccc0442
#SBATCH --cpus-per-task=56
#SBATCH --mem=360G
#SBATCH --time=12:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/pipeline_grpo/logs/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/pipeline_grpo/logs/%x-%j.err
# Full pipeline on the GRPO generator (2026-10-08), stage 2 (CPU, ccc0442): score the K=16 partials (exec + IoU vs GT,
# reporting only), then in parallel the consistency vote matrix (consistency_rerank) and render-compare of every
# candidate (render_compare.py, sheets kept) followed by the v3 metric (rc_metric2.py). Venvs staged in node RAM.
#   sbatch --export=ALL,STEM=results/pipeline_grpo/real_k16_ent_t10s120 pg_score_rc.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV; source train_v14/env.sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
S=/dev/shm/bimrose2/pgs_$SLURM_JOB_ID; mkdir -p $S; trap 'rm -rf $S' EXIT
BENCH=$DV/train_v14/mech/benchmarks/data/ext_bench_dw423_perm; O=$DV/$STEM
T0=$(date +%s)
rsync -a --copy-links $DV/.venv/ $S/venv/ & rsync -a --copy-links $DV/dw_venv/ $S/dw_venv/ & rsync -a $DV/mech_step_to_drw/ $S/step_to_drw/ & wait
PY=$S/venv/bin/python; RPY=$S/dw_venv/bin/python
$PY -c "import build123d, scipy, PIL" && $RPY -c "import draftwright, OCP" || { echo "staged env broken"; exit 1; }
echo "$(date) staged in $(( $(date +%s)-T0 )) s"
if [ ! -f $O.json ]; then
  $PY train_v14/geom/score_partials.py --partials "$O.shard*.json.partial.json" --gt-dir $BENCH/gt_meshes_v15 --out $O.json \
    --workers 48 --exec-timeout 60 --iou-timeout 90 || { echo "score failed"; exit 1; }
fi
echo "$(date) scored"
[ -f ${O}_consistency.json ] || $PY train_v14/geom/consistency_rerank.py $O.json ${O}_consistency.json > ${O}_consistency.log 2>&1 &
CPID=$!
mkdir -p ${O}_rcpng
[ -f ${O}_rc.json ] || $PY train_v14/geom/render_compare.py --bo $O.json --bench $BENCH --out ${O}_rc.json --py $PY --rpy $RPY \
  --script-dir $S/step_to_drw --workers 30 --tol 3 --gt-check 5 --save-png-dir ${O}_rcpng > ${O}_rc.log 2>&1
echo "$(date) rendered: $(tail -1 ${O}_rc.log)"
$PY train_v14/geom/rc_metric2.py --rc ${O}_rc.json --png-dir ${O}_rcpng --bench $BENCH --out ${O}_rc_v3.json --workers 24 > ${O}_rc_v3.log 2>&1
echo "$(date) v3: $(tail -1 ${O}_rc_v3.log)"
wait $CPID; tail -6 ${O}_consistency.log
echo "PG SCORE DONE $(date) ($(( $(date +%s)-T0 )) s)"
