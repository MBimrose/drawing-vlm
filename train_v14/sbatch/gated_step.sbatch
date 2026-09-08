#!/bin/bash
#SBATCH --job-name=gated
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
# Served-policy numbers for an EXISTING candidate file (verifier scoring + gated_select), one GPU:
#   sbatch --export=ALL,CANDS=results/ext/bo8_ext_<run>.json,K=8[,CONS=...,CACHE=...,SPLIT=...|none] gated_step.sbatch
# Defaults: CONS=<stem>_consistency.json, ext_bench cache + split. Re-runs analyze_ext.py for results/ext files.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
export OPENBLAS_NUM_THREADS=1
B=$DV/train_v14/mech/benchmarks/data/ext_bench
STEM=${CANDS%.json}
STAGE_SHM=1 CUDA_VISIBLE_DEVICES=0 bash $DV/train_v14/geom/gated_step.sh $DV/$CANDS $DV/${CONS:-${STEM}_consistency.json} \
  ${CACHE:-$B/eval_cache_v14.pkl} ${K:-8} ${SPLIT:-$B/split.json}
case $CANDS in results/ext/*) python $DV/train_v14/mech/benchmarks/analyze_ext.py $DV/${STEM}_consistency.json \
  --gated $DV/${STEM}_gated.json > $DV/${STEM}_summary.txt 2>&1 || true;; esac
