#!/bin/bash
#SBATCH --job-name=c2-gtsw
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --nodelist=ccc0442
#SBATCH --time=24:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/cycle2/logs/%x-%j.out
# CPU-only GT-search streams (cycle 2) attached to the rp3 server of a running gts_l40s.sbatch job on this node.
#   sbatch --cpus-per-task=N --mem=M --export=ALL,SPEC_FILE=<file>[,PORT=8620] results/cycle2/gts_worker.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV
S=/dev/shm/bimrose2/c2gtsw_$SLURM_JOB_ID; mkdir -p $S; trap "rm -rf $S" EXIT
rsync -a --copy-links $DV/.venv/ $S/venv/ & rsync -a --copy-links $DV/dw_venv/ $S/dw_venv/ & rsync -a $DV/mech_step_to_drw/ $S/step_to_drw/ & wait
PY=$S/venv/bin/python; RPY=$S/dw_venv/bin/python
$PY -c "import build123d, scipy, PIL" && $RPY -c "import draftwright, OCP" || { echo "staged env broken"; exit 1; }
curl -s -m 5 http://127.0.0.1:${PORT:-8620}/health >/dev/null || { echo "no rp3 server on :${PORT:-8620}"; exit 1; }
bash $DV/results/cycle2/gts_streams.sh $SPEC_FILE ${PORT:-8620} $PY $RPY $S/step_to_drw
echo "C2 GTS WORKER DONE $(date)"
