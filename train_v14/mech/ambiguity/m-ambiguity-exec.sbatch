#!/bin/bash
#SBATCH --job-name=m-ambiguity-exec
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=24
#SBATCH --mem=80G
#SBATCH --exclude=ccc0451,ccc0474,ccc0475
#SBATCH --time=3:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/mech/ambiguity/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/mech/ambiguity/%x.e%j
# CPU-only: execute the stored e24 best-of-8 candidates for the 242
# underdetermined eval parts + 120 determinate controls into an STL cache.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
M=$DV/train_v14/mech/ambiguity
mkdir -p $M/out
python $M/exec_cands.py --bo8 $DV/results/bo8_full_e24.json --keys $M/keys_exec_all.txt \
  --stl-dir $M/out/stl_e24 --out $M/out/cand_geom_e24.jsonl --workers 22
