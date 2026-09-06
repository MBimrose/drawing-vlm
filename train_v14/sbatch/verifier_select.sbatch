#!/bin/bash
#SBATCH --job-name=vsel
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --gres=gpu:H200:1
#SBATCH --mem=250G
#SBATCH --time=6:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.err
# Offline verifier selection study on stored candidates (one GPU).
#   sbatch --export=ALL,VER=runs/v3-verifier-real/best_adapter,VRUN=v3-verifier-real,\
#          CANDS=results/ext/bo32_ext_e51-rft-real-u3-strict90.json,\
#          CONS=results/ext/bo32_ext_e51-rft-real-u3-strict90_consistency.json,\
#          OUT=results/ext/vsel_v3_e51_bo32.json[,MODE=bin|legacy,EXTRA="..."] verifier_select.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
export OPENBLAS_NUM_THREADS=1
B=$DV/train_v14/mech/benchmarks/data/ext_bench
python $DV/train_v14/geom/verifier_select_offline.py \
  --verifier $DV/${VER} --verifier-run ${VRUN:-v3-verifier-real} \
  --cands $DV/${CANDS} --consistency $DV/${CONS:-} \
  --cache ${CACHE:-$B/eval_cache_v14.pkl} --split ${SPLIT:-$B/split.json} \
  --k ${KS:-8 32} --prompt-mode ${MODE:-bin} --batch ${BATCH:-8} \
  --out $DV/${OUT} ${EXTRA:-}
