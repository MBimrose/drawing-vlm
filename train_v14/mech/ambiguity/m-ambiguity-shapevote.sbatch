#!/bin/bash
#SBATCH --job-name=m-ambiguity-shapevote
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=18
#SBATCH --mem=240G
#SBATCH --exclude=ccc0451,ccc0474,ccc0475
#SBATCH --time=3:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/mech/ambiguity/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/mech/ambiguity/%x.e%j
# CPU-only: extent-invariant (shape-only) agreement selectors on the cached candidate meshes.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
M=$DV/train_v14/mech/ambiguity
python $M/shape_vote.py --geom $M/out/cand_geom_e24.jsonl --workers 16 --keys $M/keys_shapevote.txt --out $M/out/shape_vote_e24.json
