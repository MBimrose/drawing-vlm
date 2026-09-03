#!/bin/bash
#SBATCH --job-name=m-constraints-2stage
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --gres=gpu:L40S:4
#SBATCH --mem=450G
#SBATCH --nodelist=ccc0442
#SBATCH --time=6:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/mech/constraints/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/mech/constraints/%x.e%j
# Constraints-before-code on the 96-pool: base greedy+repair vs
# stage A (constraint JSON) -> stage B (drawing + constraints) -> verify/repair.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
export OPENBLAS_NUM_THREADS=1
M=$DV/train_v14/mech/constraints
nvidia-smi -L
python $M/two_stage.py --ckpt $DV/runs/e24-rft/final --kind hf --run e24-rft \
  --n 96 --batch 8 --repair-rounds 2 --out $M/out/two_stage_e24_96.json
