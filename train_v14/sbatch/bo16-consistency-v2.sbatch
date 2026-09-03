#!/bin/bash
#SBATCH --job-name=bo16-cons-v2
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=120G
#SBATCH --time=6:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.e%j
# CPU-only: re-rank the stored K=16 champion candidates (96-pool) with the
# matrix-persisting reranker, to simulate adaptive-K (extra draws only for
# low-agreement parts) offline.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
cp -n /tmp/claude-1147665/-projects-illinois-eng-ece-wpk-bimrose2-drawing-vlm/6be5ca02-2ca6-4600-b19d-5c6fdf323cd6/scratchpad/bo16_oracle_e24.json $DV/results/bo16_oracle_e24.json 2>/dev/null || true
python $DV/train_v14/geom/consistency_rerank.py $DV/results/bo16_oracle_e24.json $DV/results/bo16_e24_consistency_v2.json
