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
#SBATCH --output=/scratch/bimrose2/mech_selfcheck/logs/%x.o%j
#SBATCH --error=/scratch/bimrose2/mech_selfcheck/logs/%x.e%j
# Visual self-check, draftwright renders, working tree on /scratch (the /projects
# group quota is hard-full). Pre-stage already done; do not rerun it here.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
export OPENBLAS_NUM_THREADS=1
M=$DV/train_v14/mech/selfcheck; W=/scratch/bimrose2/mech_selfcheck
python $M/selfcheck_gen.py --prestage $W/out/prestage --out $W/out/selfcheck_96.json --batch ${BATCH:-4}
python $M/analyze.py --out $W/out/selfcheck_96.json --md $W/out/analysis.md
