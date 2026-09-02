#!/bin/bash
#SBATCH --job-name=union-cons
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=120G
#SBATCH --time=12:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.e%j
# CPU-only: consistency on the e24+e34 16-candidate union (96-pool), and the
# e34 8-candidate file re-scored with per-part output.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
G=$DV/train_v14/geom
python $G/consistency_rerank.py $DV/results/bo16_union_e24e34.json $DV/results/bo16_union_e24e34_consistency.json
python $G/consistency_rerank.py $DV/results/bo8_e34.json $DV/results/bo8_e34_consistency.json
bash $DV/scripts/snapshot_results.sh || true
