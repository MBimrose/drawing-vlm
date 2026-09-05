#!/bin/bash
#SBATCH --job-name=boK-ext
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=64
#SBATCH --gres=gpu:H200:8
#SBATCH --mem=1000G
#SBATCH --time=16:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.err
# External bench at arbitrary K: sbatch --export=ALL,RUN=<run>,K=32 (outputs results/ext/bo<K>_ext_<run>*)
# consistency for runs/$RUN/final on one H200 node.   sbatch --export=ALL,RUN=<run> ...
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
B=$DV/train_v14/mech/benchmarks/data/ext_bench
export OPENBLAS_NUM_THREADS=1 DRAWING_VLM_TRACES_JSON=$B/traces_v14.json DRAWING_VLM_EVAL_CACHE=$B/eval_cache_v14.pkl
G=$DV/train_v14/geom; R=$RUN; mkdir -p $DV/logs/bo8 $DV/results/ext
for i in 0 1 2 3 4 5 6 7; do
  CUDA_VISIBLE_DEVICES=$i python $G/bestofn_verifier_eval.py --ckpt $DV/runs/$R/final --kind hf --run $R \
    --verifier "" --n 146 --k ${K:-8} --temperature 0.7 --batch 16 --shard $i --nshards 8 \
    --out $DV/results/ext/bo${K:-8}_ext_$R.shard$i.json > $DV/logs/bo8/bo${K:-8}_ext_$R.shard$i.log 2>&1 &
done
wait
python $G/merge_bo_shards.py $DV/results/ext/bo${K:-8}_ext_$R.json $DV/results/ext/bo${K:-8}_ext_$R.shard?.json > $DV/logs/bo8/bo${K:-8}_ext_${R}_merge.log 2>&1
[ -f $DV/results/ext/bo${K:-8}_ext_$R.json ] && python $G/consistency_rerank.py $DV/results/ext/bo${K:-8}_ext_$R.json $DV/results/ext/bo${K:-8}_ext_${R}_consistency.json > $DV/logs/bo8/bo${K:-8}_ext_${R}_consistency.log 2>&1
python $DV/train_v14/mech/benchmarks/analyze_ext.py $DV/results/ext/bo${K:-8}_ext_${R}_consistency.json > $DV/results/ext/bo${K:-8}_ext_${R}_summary.txt 2>&1 || true
