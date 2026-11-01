#!/bin/bash
#SBATCH --job-name=align-cells
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=96
#SBATCH --mem=200G
#SBATCH --time=12:00:00
#SBATCH --nodelist=ccc0441
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/%x-%j.out
# Rigid-alignment column for every results-table cell (2026-10-29): geom/align_cells.py with the build123d python and
# venv_meshalign both staged in /dev/shm (a cold 1.6 GB meshalign import from Lustre takes ~1 min per subprocess).
# Rerun later to add the repair cells still running: only new programs are scored (cache).
#   sbatch [--export=ALL,ONLY="Gemma"] align_cells.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; S=/dev/shm/bimrose2
PY=$S/ipcode/venv/bin/python
[ -x $PY ] || bash $DV/results/indist_pipeline/stage_py_shm.sh
[ -x $PY ] || { echo "no staged python"; exit 2; }
( flock 8; [ -f $S/venv_meshalign/.STAGED ] || { rsync -a /projects/illinois/eng/ece/wpk/bimrose2/venv_meshalign/ $S/venv_meshalign/ && touch $S/venv_meshalign/.STAGED; }
) 8>$S/venv_meshalign.lock
echo "$(date) staged"
export MA_PY=$S/venv_meshalign/bin/python OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
$MA_PY -c "import meshalign" || { echo "staged meshalign broken"; exit 3; }
cd $DV
$PY train_v14/geom/align_cells.py --workers ${W:-90} ${ONLY:+--only "$ONLY"}
echo "ALIGN CELLS DONE $(date)"
