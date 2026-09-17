#!/bin/bash
#SBATCH --job-name=render-cmp
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=100
#SBATCH --mem=300G
#SBATCH --time=12:00:00
#SBATCH --nodelist=ccc0442
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/real/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/real/%x-%j.err
# CPU-only (L40S node, no GPU): render every stored candidate as a sheet and score it against
# the input drawing (render_compare.py). Both venvs and the renderer scripts are staged into
# node RAM -- per-candidate interpreters importing OCP from Lustre are 5-10x slower.
#   sbatch --export=ALL,BO=<bo json>,BENCH=<bench dir>,OUT=<out json>[,WORKERS=90,TOL=3,GT=5] render_compare.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
S=/dev/shm/bimrose2/rc_$SLURM_JOB_ID; mkdir -p $S; trap 'rm -rf $S' EXIT
T0=$(date +%s)
rsync -a --copy-links $DV/.venv/ $S/venv/ & rsync -a --copy-links $DV/dw_venv/ $S/dw_venv/ & rsync -a $DV/mech_step_to_drw/ $S/step_to_drw/ & wait
echo "staged venvs in $(( $(date +%s)-T0 )) s"
PY=$S/venv/bin/python; RPY=$S/dw_venv/bin/python
$PY -c "import build123d, scipy, PIL" && $RPY -c "import draftwright, OCP" || { echo "staged env broken"; exit 1; }
$PY $DV/train_v14/geom/render_compare.py --bo $BO --bench $BENCH --out $OUT --py $PY --rpy $RPY \
  --script-dir $S/step_to_drw --workers ${WORKERS:-90} --tol ${TOL:-3} --gt-check ${GT:-5} ${PNGDIR:+--save-png-dir $PNGDIR}
echo "RENDER COMPARE DONE $OUT $(date)"
