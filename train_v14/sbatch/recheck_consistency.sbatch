#!/bin/bash
#SBATCH --job-name=recheck
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=60
#SBATCH --exclusive
#SBATCH --mem=400G
#SBATCH --time=10:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.err
# CPU-only repair of a consistency matrix degraded by re-execution timeouts. Must run on an
# IDLE node: the loss is exec_to_stl hitting its 120 s timeout under CPU contention.
#   sbatch --export=ALL,STEM=bo32_esc_<run>,CACHE=<pkl>,K=32[,SPLIT=none] recheck_consistency.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
bash $DV/train_v14/geom/recheck_consistency.sh "$STEM" "$CACHE" "${K:-32}" "${SPLIT:-none}"
