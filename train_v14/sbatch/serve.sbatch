#!/bin/bash
#SBATCH --job-name=serve
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --gres=gpu:H200:1
#SBATCH --mem=250G
#SBATCH --time=4:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.err
# End-to-end serving (serve.py: e55 best-of-8 + agreement-gated verifier) on one GPU.
# Sheets must come from draftwright 0.4.23 (render_isolated.sh default since 2026-09-10).
#   sbatch --export=ALL,IN=<png or dir>,OUT=<out dir>[,K=8,KMAX=16,GATE=0.85,EXTRA="--keep-candidates"] serve.sbatch
# KMAX=8 disables escalation (fixed budget).
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
export OPENBLAS_NUM_THREADS=1
RUN=${RUN:-e55-rft-real-u5-gt-dw423}
# Stage the generator weights to /dev/shm (Lustre loads took ~1 h with other jobs reading finals).
SHM=/dev/shm/bimrose2_$SLURM_JOB_ID; trap 'rm -rf $SHM' EXIT
mkdir -p $SHM && echo "$(date) staging runs/$RUN/final -> $SHM" && cp -r $DV/runs/$RUN/final $SHM/base && echo "$(date) staged" || { echo "staging failed, loading from Lustre"; rm -rf $SHM; SHM=""; }
python $DV/train_v14/geom/serve.py $IN --out $OUT --run $RUN ${SHM:+--ckpt $SHM/base} \
  --k ${K:-8} --k-max ${KMAX:-16} --gate ${GATE:-0.85} ${EXTRA:-}
