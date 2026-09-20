#!/bin/bash
#SBATCH --job-name=build-repair
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=110
#SBATCH --mem=400G
#SBATCH --time=24:00:00
#SBATCH --nodelist=ccc0442
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/real/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/real/%x-%j.err
# CPU-only (L40S node, no GPU): render failed candidates, overlay them on their drawings and
# write the repair tier (build_repair_tier.py). Venvs + renderer staged in node RAM.
#   sbatch --export=ALL,BO=<bo json>,BENCH=<corpus dir>,OUT=<tier dir>[,MAXPP=2,WORKERS=100] build_repair.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
S=/dev/shm/bimrose2/rep_$SLURM_JOB_ID; mkdir -p $S; trap 'rm -rf $S' EXIT
T0=$(date +%s)
rsync -a --copy-links $DV/.venv/ $S/venv/ & rsync -a --copy-links $DV/dw_venv/ $S/dw_venv/ & rsync -a $DV/mech_step_to_drw/ $S/step_to_drw/ & wait
echo "staged in $(( $(date +%s)-T0 )) s"
PY=$S/venv/bin/python; RPY=$S/dw_venv/bin/python
$PY -c "import build123d, scipy, PIL" && $RPY -c "import draftwright, OCP" || { echo "staged env broken"; exit 1; }
cd $DV/train_v14/geom
$PY build_repair_tier.py --bo $BO --bench $BENCH --out $OUT --py $PY --rpy $RPY --script-dir $S/step_to_drw \
  --workers ${WORKERS:-100} --max-per-part ${MAXPP:-2} --good-min ${GOODMIN:-0.8} --bad-max ${BADMAX:-0.5} ${LIMIT:+--limit $LIMIT}
echo "BUILD REPAIR DONE $OUT $(date)"
