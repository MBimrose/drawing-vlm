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
# Stage the verifier's base weights to /dev/shm (Lustre loads took ~1 h with other jobs reading finals).
BASE=$(grep -E "^model_id:" $DV/train_v14/configs/${VRUN:-v3-verifier-real}.yaml | awk '{print $2}')
SHM=/dev/shm/bimrose2_$SLURM_JOB_ID; trap 'rm -rf $SHM' EXIT
mkdir -p $SHM && echo "$(date) staging $BASE -> $SHM" && cp -r $BASE $SHM/base && echo "$(date) staged" || { echo "staging failed, loading from Lustre"; SHM=""; }
BASE_ARG=${SHM:+--base $SHM/base}
python $DV/train_v14/geom/verifier_select_offline.py \
  --verifier $DV/${VER} --verifier-run ${VRUN:-v3-verifier-real} ${BASE_ARG:-} \
  --cands $DV/${CANDS} --consistency $DV/${CONS:-} \
  --cache ${CACHE:-$B/eval_cache_v14.pkl} $([ "${SPLIT:-$B/split.json}" != none ] && echo --split ${SPLIT:-$B/split.json}) \
  --k ${KS:-8 32} --prompt-mode ${MODE:-bin} --batch ${BATCH:-8} \
  --out $DV/${OUT} ${EXTRA:-}
