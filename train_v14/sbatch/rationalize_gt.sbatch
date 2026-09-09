#!/bin/bash
#SBATCH --job-name=rationalize
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --gres=gpu:H200:1
#SBATCH --mem=200G
#SBATCH --time=4:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.err
# Rationalize a ground-truth tier: sbatch --export=ALL,TIER=<tier_dir>,OUT=<out_dir>[,RUN=e51-rft-real-u3-strict90,CKPT=<hf dir, default runs/$RUN/final>,BATCH=3] rationalize_gt.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
R=${RUN:-e51-rft-real-u3-strict90}
SHM=/dev/shm/bimrose2_$SLURM_JOB_ID; trap 'rm -rf $SHM' EXIT
SRC=${CKPT:-$DV/runs/$R/final}
mkdir -p $SHM && cp -r $SRC $SHM/final && CK=$SHM/final || CK=$SRC
python $DV/train_v14/geom/rationalize_gt.py --tier $DV/$TIER --ckpt $CK --run $R --out $DV/$OUT --batch ${BATCH:-3}
