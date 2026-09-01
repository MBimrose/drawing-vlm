#!/bin/bash
#SBATCH --job-name=e39-soup-union
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --nodelist=ccc0442
#SBATCH --gres=gpu:L40S:4
#SBATCH --mem=600G
#SBATCH --time=24:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.e%j
# 1. soup e24+e34 -> runs/e39-soup-e24e34/final (geom-eval chain scores it)
# 2. best-of-8 for e34 on the 96-pool  3. consistency on e34 alone and on the
#    e24+e34 16-candidate union (does model diversity lift the medoid?)
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
G=$DV/train_v14/geom
if [ ! -f $DV/runs/e39-soup-e24e34/final/model.safetensors.index.json ]; then
  python $G/soup.py $DV/runs/e39-soup-e24e34/final $DV/runs/e24-rft/final $DV/runs/e34-rft-seed43/final || exit 1
fi
[ -f $DV/results/bo8_e34.json ] || python $G/bestofn_verifier_eval.py --ckpt $DV/runs/e34-rft-seed43/final --kind hf \
  --run e34-rft-seed43 --verifier "" --n 96 --k 8 --temperature 0.7 --batch 8 --out $DV/results/bo8_e34.json
python $G/consistency_rerank.py $DV/results/bo8_e34.json $DV/results/bo8_e34_consistency.json
python $G/union_bo.py $DV/results/bo16_union_e24e34.json $DV/results/bo8_verifier2_e24.json $DV/results/bo8_e34.json
python $G/consistency_rerank.py $DV/results/bo16_union_e24e34.json $DV/results/bo16_union_e24e34_consistency.json
bash $DV/scripts/snapshot_results.sh || true
