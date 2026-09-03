#!/bin/bash
#SBATCH --job-name=m-ambiguity-gen
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --gres=gpu:L40S:4
#SBATCH --mem=300G
#SBATCH --nodelist=ccc0442
#SBATCH --time=5:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/mech/ambiguity/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/mech/ambiguity/%x.e%j
# Best-of-8 (greedy + 7 at T=0.7) with the ambiguity-convention system prompt
# on the 242 underdetermined eval parts; then consistency (medoid) reranking.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
export OPENBLAS_NUM_THREADS=1
source $DV/train_v14/env.sh
source $DV/.venv/bin/activate
M=$DV/train_v14/mech/ambiguity
VARIANT=${VARIANT:-convention}
python $M/gen_underdet.py --ckpt $DV/runs/e24-rft/final --kind hf --run e24-rft \
  --keys $M/keys_underdet.txt --variant $VARIANT --k 8 --temperature 0.7 --batch 8 \
  --out $M/out/bo8_underdet_$VARIANT.json
python $DV/train_v14/geom/consistency_rerank.py $M/out/bo8_underdet_$VARIANT.json $M/out/bo8_underdet_${VARIANT}_consistency.json
