#!/bin/bash
#SBATCH --job-name=bo8-full
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=64
#SBATCH --gres=gpu:H200:8
#SBATCH --mem=1000G
#SBATCH --time=24:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.err
# Full certified pool (1,030 parts) best-of-8 + consistency for runs/$RUN/final on one
# H200 node: 8 single-GPU workers, merge, rerank.  Usage: sbatch --export=RUN=<run> ...
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
G=$DV/train_v14/geom; R=$RUN; mkdir -p $DV/logs/bo8
for i in 0 1 2 3 4 5 6 7; do
  CUDA_VISIBLE_DEVICES=$i python $G/bestofn_verifier_eval.py --ckpt $DV/runs/$R/final --kind hf --run $R \
    --verifier "" --n 1072 --k 8 --temperature 0.7 --batch 16 --shard $i --nshards 8 \
    --out $DV/results/bo8_full_$R.shard$i.json > $DV/logs/bo8/bo8_full_$R.shard$i.log 2>&1 &
done
wait
python $G/merge_bo_shards.py $DV/results/bo8_full_$R.json $DV/results/bo8_full_$R.shard?.json > $DV/logs/bo8/bo8_full_${R}_merge.log 2>&1
[ -f $DV/results/bo8_full_$R.json ] && python $G/consistency_rerank.py $DV/results/bo8_full_$R.json $DV/results/bo8_full_${R}_consistency.json > $DV/logs/bo8/bo8_full_${R}_consistency.log 2>&1
bash $DV/scripts/snapshot_results.sh || true
