#!/bin/bash
#SBATCH --job-name=grpo-r1e
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodelist=ccc0475
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=64
#SBATCH --gres=gpu:H200:8
#SBATCH --mem=1000G
#SBATCH --time=16:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.err
# GRPO round-1 node E (2026-10-05): classic-GRPO and optimisation axes.
#   c2    — REAL corpus 2 (1684 parts, dw423 sheets)
#   std0  — std-normalised advantage + NO KL (pure GRPO)
#   lr2e5 — aggressive learning rate 2e-5
#   g16t09 — group 16 at T=0.9 (max exploration)
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OPENBLAS_NUM_THREADS=1
COMMON="--run e55-rft-real-u5-gt-dw423 --model-base $DV/models/Qwen3.8-27B \
  --ckpt $DV/runs/e55-rft-real-u5-gt-dw423/final --steps 72 \
  --gen-batch 16 --train-batch 4 --score-workers 12 --save-every 24 --n-parts 16 --g 8"
arm() {
  name=$1; gpu=$2; shift 2
  mkdir -p $DV/runs/grpo_e_$name
  CUDA_VISIBLE_DEVICES=$gpu python $DV/train_v14/geom/grpo_round.py $COMMON "$@" \
    --out $DV/runs/grpo_e_$name > $DV/logs/grpo_r1e_$name.log 2>&1 &
  echo "arm $name on GPU $gpu (pid $!)"
}
arm c2     0 --lr 1e-5 --kl-beta 0.02 --bench $DV/train_v14/mech/benchmarks/data/rft_corpus2_dw423
arm std0   1 --lr 1e-5 --kl-beta 0 --adv std --bench $DV/results/h6c/train_bench
arm lr2e5  2 --lr 2e-5 --kl-beta 0.02 --bench $DV/results/h6c/train_bench
arm g16t09 3 --lr 1e-5 --kl-beta 0.02 --temperature 0.9 --n-parts 8 --g 16 --bench $DV/results/h6c/train_bench
wait
echo "GRPO R1E DONE"
