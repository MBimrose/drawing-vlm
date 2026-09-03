#!/bin/bash
#SBATCH --job-name=m-benchmarks-bo8
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --gres=gpu:L40S:4
#SBATCH --mem=450G
#SBATCH --nodelist=ccc0442
#SBATCH --time=8:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/mech/benchmarks/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/mech/benchmarks/%x.e%j
# Champion e24 best-of-8 (greedy + 7 at T=0.7) on 146 EXTERNAL parts
# (CADBench benchF/benchA medium tier, real Fusion360/ABC geometry) rendered
# through our draftwright sheets; then consistency (medoid) reranking.
# The eval scripts are unchanged: cache + GT dir come from env overrides
# (must be exported AFTER env.sh, which sets DRAWING_VLM_TRACES_JSON itself).
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
M=$DV/train_v14/mech/benchmarks
B=$M/data/ext_bench
export OPENBLAS_NUM_THREADS=1
source $DV/train_v14/env.sh
source $DV/.venv/bin/activate
export DRAWING_VLM_TRACES_JSON=$B/traces_v14.json
export DRAWING_VLM_EVAL_CACHE=$B/eval_cache_v14.pkl
python $DV/train_v14/geom/bestofn_verifier_eval.py \
  --ckpt $DV/runs/e24-rft/final --kind hf --run e24-rft \
  --n 146 --k 8 --temperature 0.7 --batch 8 \
  --out $M/results/bo8_ext_e24.json
python $DV/train_v14/geom/consistency_rerank.py $M/results/bo8_ext_e24.json $M/results/bo8_ext_e24_consistency.json
python $M/analyze_ext.py $M/results/bo8_ext_e24_consistency.json > $M/results/summary.txt 2>&1 || true
cat $M/results/summary.txt || true
