#!/bin/bash
#SBATCH --job-name=grpo-r1c
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=64
#SBATCH --gres=gpu:H200:8
#SBATCH --mem=1000G
#SBATCH --time=20:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.err
# GRPO round-1 cluster arms (2026-10-05): one process per H200 GPU, same trainer as
# the serv-20 arms. Arms here probe the axes NOT covered on serv-20:
#   std   — classic GRPO std-normalized advantage
#   g16   — group size 16 (more exploration, better baseline), 8 parts/step
#   lr5e6 — conservative learning rate
#   real4 — REAL-part training bench (corpus 4, 2108 parts, e55-best < 0.9)
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OPENBLAS_NUM_THREADS=1
COMMON="--run e55-rft-real-u5-gt-dw423 --model-base $DV/models/Qwen3.8-27B \
  --ckpt $DV/runs/e55-rft-real-u5-gt-dw423/final --steps 60 --lr 1e-5 \
  --gen-batch 16 --train-batch 4 --score-workers 12 --save-every 20"
arm() {
  name=$1; gpu=$2; shift 2
  mkdir -p $DV/runs/grpo_c_$name
  CUDA_VISIBLE_DEVICES=$gpu python $DV/train_v14/geom/grpo_round.py $COMMON "$@" \
    --out $DV/runs/grpo_c_$name > $DV/logs/grpo_r1c_$name.log 2>&1 &
  echo "arm $name on GPU $gpu (pid $!)"
}
arm std   0 --adv std --bench $DV/results/h6c/train_bench --n-parts 16 --g 8
arm g16   1 --bench $DV/results/h6c/train_bench --n-parts 8 --g 16
arm lr5e6 2 --lr 5e-6 --bench $DV/results/h6c/train_bench --n-parts 16 --g 8
arm real4 3 --bench $DV/train_v14/mech/benchmarks/data/rft_corpus4 --n-parts 16 --g 8
wait
echo "GRPO R1 CLUSTER DONE"
