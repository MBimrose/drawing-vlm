#!/bin/bash
#SBATCH --job-name=m-ambiguity-score
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=18
#SBATCH --mem=160G
#SBATCH --exclude=ccc0451,ccc0474,ccc0475
#SBATCH --time=4:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/mech/ambiguity/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/mech/ambiguity/%x.e%j
# CPU-only: score the first K draws of the convention run and the stored baseline
# restricted to the same K draws, then run the unchanged consistency reranker on both.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
M=$DV/train_v14/mech/ambiguity
K=${K:-4}
cp $M/out/bo8_underdet_convention.json.partial.json $M/out/partial_k${K}_snapshot.json
python $M/score_partial.py --partial $M/out/partial_k${K}_snapshot.json --k $K \
  --out $M/out/bo${K}_underdet_convention.json --baseline-out $M/out/bo${K}_underdet_baseline.json --workers 16
python $DV/train_v14/geom/consistency_rerank.py $M/out/bo${K}_underdet_convention.json $M/out/bo${K}_underdet_convention_consistency.json
python $DV/train_v14/geom/consistency_rerank.py $M/out/bo${K}_underdet_baseline.json $M/out/bo${K}_underdet_baseline_consistency.json
