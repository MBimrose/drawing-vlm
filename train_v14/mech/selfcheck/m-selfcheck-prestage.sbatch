#!/bin/bash
#SBATCH --job-name=m-selfcheck-prestage
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=2:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/mech/selfcheck/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/mech/selfcheck/%x.e%j
# CPU-only pre-stage: execute the 96x8 stored champion candidates (keep STLs +
# served STEP) and render the served part back into a drawing. Idempotent.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
M=$DV/train_v14/mech/selfcheck
python $M/prestage.py --workers 12 --out $M/out/prestage
