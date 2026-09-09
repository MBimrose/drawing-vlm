#!/bin/bash
#SBATCH --job-name=bo8-ext
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=64
#SBATCH --gres=gpu:H200:8
#SBATCH --mem=1000G
#SBATCH --time=8:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.err
# External real-geometry bench (146 held-out CADBench parts, our sheets): best-of-8 +
# consistency + gated verifier selection for runs/$RUN/final on one H200 node.   sbatch --export=ALL,RUN=<run> ...
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
B=${BENCH:-$DV/train_v14/mech/benchmarks/data/ext_bench}   # BENCH=<dir> for another bench (e.g. ext_bench_dw423)
T=${TAG:-bo8_ext}   # output stem: results/ext/<TAG>_<run>*
export OPENBLAS_NUM_THREADS=1 DRAWING_VLM_TRACES_JSON=$B/traces_v14.json DRAWING_VLM_EVAL_CACHE=$B/eval_cache_v14.pkl
G=$DV/train_v14/geom; R=$RUN; mkdir -p $DV/logs/bo8 $DV/results/ext
for i in 0 1 2 3 4 5 6 7; do
  CUDA_VISIBLE_DEVICES=$i python $G/bestofn_verifier_eval.py --ckpt $DV/runs/$R/final --kind hf --run $R \
    --verifier "" --n ${N:-146} --k 8 ${EXTRA:-} --temperature 0.7 --batch 16 --shard $i --nshards 8 \
    --out $DV/results/ext/${T}_$R.shard$i.json > $DV/logs/bo8/${T}_$R.shard$i.log 2>&1 &
done
wait
python $G/merge_bo_shards.py $DV/results/ext/${T}_$R.json $DV/results/ext/${T}_$R.shard?.json > $DV/logs/bo8/${T}_${R}_merge.log 2>&1
[ -f $DV/results/ext/${T}_$R.json ] && python $G/consistency_rerank.py $DV/results/ext/${T}_$R.json $DV/results/ext/${T}_${R}_consistency.json > $DV/logs/bo8/${T}_${R}_consistency.log 2>&1
# Served policy: verifier scoring (one GPU, base staged in /dev/shm) + agreement-gated selection.
STAGE_SHM=1 CUDA_VISIBLE_DEVICES=0 bash $G/gated_step.sh $DV/results/ext/${T}_$R.json $DV/results/ext/${T}_${R}_consistency.json \
  $B/eval_cache_v14.pkl 8 $B/split.json > $DV/logs/bo8/${T}_${R}_gated.log 2>&1
python $DV/train_v14/mech/benchmarks/analyze_ext.py $DV/results/ext/${T}_${R}_consistency.json --gated $DV/results/ext/${T}_${R}_gated.json > $DV/results/ext/${T}_${R}_summary.txt 2>&1 || true
