#!/bin/bash
#SBATCH --job-name=bo8-tsweep
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --nodelist=ccc0442
#SBATCH --gres=gpu:L40S:4
#SBATCH --mem=350G
#SBATCH --time=24:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.e%j
# Sampling-temperature sweep for the deployed best-of-8 + consistency policy on
# the champion (T=0.7 measured: oracle 0.936 / consistency 0.919). Lower T →
# tighter candidates (less diversity, higher agreement); higher T → more
# diversity (higher oracle, noisier medoid). Which way does the medoid move?
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
G=$DV/train_v14/geom
for T in 0.5 1.0; do
  tag=${T/./p}
  [ -f $DV/results/bo8_e24_T$tag.json ] || python $G/bestofn_verifier_eval.py --ckpt $DV/runs/e24-rft/final --kind hf \
    --run e24-rft --verifier "" --n 96 --k 8 --temperature $T --batch 8 --out $DV/results/bo8_e24_T$tag.json
  python $G/consistency_rerank.py $DV/results/bo8_e24_T$tag.json $DV/results/bo8_e24_T${tag}_consistency.json
done
bash $DV/scripts/snapshot_results.sh || true
