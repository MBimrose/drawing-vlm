#!/bin/bash
#SBATCH --job-name=align-study
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=120G
#SBATCH --time=4:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.e%j
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate
export OPENBLAS_NUM_THREADS=1 IOU_MC_POINTS=0 WORKERS=24
python $DV/train_v14/geom/align_study.py /scratch/bimrose2/mech_selfcheck/out/prestage $DV/results/align_study_96.json
