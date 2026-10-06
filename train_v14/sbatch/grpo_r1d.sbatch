#!/bin/bash
#SBATCH --job-name=grpo-r1d
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodelist=ccc0474
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=64
#SBATCH --gres=gpu:H200:8
#SBATCH --mem=1000G
#SBATCH --time=16:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.err
# GRPO round-1 node D (2026-10-05): benches + reward shaping axes.
#   c1     — REAL corpus 1 (1527 parts)          kl002 default
#   indist — in-distribution full pool (1067)      guards/improves single-shot in-dist
#   execp  — family bench + exec penalty 0.1        reward shaping for the non-exec cliff
#   t09    — family bench at T=0.9                  exploration
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OPENBLAS_NUM_THREADS=1
COMMON="--run e55-rft-real-u5-gt-dw423 --model-base $DV/models/Qwen3.8-27B \
  --ckpt $DV/runs/e55-rft-real-u5-gt-dw423/final --steps 72 --lr 1e-5 --kl-beta 0.02 \
  --gen-batch 16 --train-batch 4 --score-workers 12 --save-every 24 --n-parts 16 --g 8"
arm() {
  name=$1; gpu=$2; shift 2
  mkdir -p $DV/runs/grpo_d_$name
  CUDA_VISIBLE_DEVICES=$gpu python $DV/train_v14/geom/grpo_round.py $COMMON "$@" \
    --out $DV/runs/grpo_d_$name > $DV/logs/grpo_r1d_$name.log 2>&1 &
  echo "arm $name on GPU $gpu (pid $!)"
}
arm c1     0 --bench $DV/train_v14/mech/benchmarks/data/rft_corpus
arm indist 1 --bench $DV/train_v14/mech/benchmarks/data/fullpool_dw423
arm execp  2 --bench $DV/results/h6c/train_bench --exec-penalty 0.1
arm t09    3 --bench $DV/results/h6c/train_bench --temperature 0.9
wait
echo "GRPO R1D DONE"
