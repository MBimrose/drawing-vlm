#!/bin/bash
#SBATCH --job-name=m-selfcheck-gen
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --gres=gpu:L40S:4
#SBATCH --mem=450G
#SBATCH --nodelist=ccc0442
#SBATCH --time=4:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/mech/selfcheck/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/mech/selfcheck/%x.e%j
# Mechanism 1: visual self-check. One round of "compare the drawing of your own
# part against the original, then correct the script" on the 96-pool served
# (consistency-medoid) candidates of the e24 champion. Pre-stage (render) is
# CPU-only and runs first (idempotent).
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
export OPENBLAS_NUM_THREADS=1
M=$DV/train_v14/mech/selfcheck
python $M/prestage.py --workers 16 --out $M/out/prestage
python $M/selfcheck_gen.py --prestage $M/out/prestage --out $M/out/selfcheck_96.json --batch ${BATCH:-4}
python $M/analyze.py --out $M/out/selfcheck_96.json
