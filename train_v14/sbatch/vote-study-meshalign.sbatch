#!/bin/bash
#SBATCH --job-name=vote-ma
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=120G
#SBATCH --time=6:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.e%j
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 IOU_MC_POINTS=0 WORKERS=16
/projects/illinois/eng/ece/wpk/bimrose2/venv_meshalign/bin/python $DV/train_v14/geom/vote_study_meshalign.py /scratch/bimrose2/mech_selfcheck/out/prestage $DV/results/vote_study_meshalign_96.json
