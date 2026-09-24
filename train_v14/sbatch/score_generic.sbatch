#!/bin/bash
#SBATCH --job-name=score-gen
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=40
#SBATCH --mem=200G
#SBATCH --time=12:00:00
#SBATCH --nodelist=ccc0442
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/bo8/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/bo8/%x-%j.err
# CPU-only (L40S node, no GPU): execute + score best-of-N partials generated elsewhere (serv-04
# vLLM), then the candidate-agreement pass (consistency_rerank). Venv staged into node RAM.
#   sbatch --export=ALL,PARTIALS='<glob>',GT=<gt_meshes_v15 dir>,OUT=<merged.json>[,WORKERS=40] score_generic.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/train_v14/env.sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
LV=/dev/shm/bimrose2/venv_$SLURM_JOB_ID; mkdir -p /dev/shm/bimrose2
rsync -a --copy-links $DV/.venv/ $LV/ && PY=$LV/bin/python || PY=$DV/.venv/bin/python
$PY -c "import build123d, OCP" 2>/dev/null || PY=$DV/.venv/bin/python
trap 'rm -rf $LV' EXIT
echo "$(date) scoring $PARTIALS -> $OUT on $(hostname) with $PY (${WORKERS:-40} workers)"
$PY $DV/train_v14/geom/score_partials.py --partials "$PARTIALS" --gt-dir $GT --out $OUT \
  --workers ${WORKERS:-40} --exec-timeout ${EXEC_TIMEOUT:-60} --iou-timeout ${IOU_TIMEOUT:-90}
STEM=${OUT%.json}
[ -z "${NO_CONS:-}" ] && [ -f $OUT ] && $PY $DV/train_v14/geom/consistency_rerank.py $OUT ${STEM}_consistency.json > ${STEM}_consistency.log 2>&1
tail -3 ${STEM}_consistency.log
echo "SCORE GENERIC DONE $OUT $(date)"
