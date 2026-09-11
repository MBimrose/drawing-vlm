#!/bin/bash
#SBATCH --job-name=score-part
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=60
#SBATCH --exclusive
#SBATCH --mem=400G
#SBATCH --time=12:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.err
# CPU-only: execute + score a best-of-N run's checkpointed candidates (score_partials.py).
#   sbatch --export=ALL,CORPUS=rft_corpus_dw423[,WORKERS=24] score_partials.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
C=$DV/train_v14/mech/benchmarks/data/$CORPUS
R=${RUN:-e55-rft-real-u5-gt-dw423}
python $DV/train_v14/geom/score_partials.py \
  --partials "$C/results/bo32_${CORPUS}_${R}.shard?.json.partial.json" \
  --gt-dir $C/gt_meshes_v15 --out $C/results/bo32_${CORPUS}_${R}.json \
  --workers ${WORKERS:-24} --exec-timeout ${EXEC_TIMEOUT:-60} --iou-timeout ${IOU_TIMEOUT:-90}
python $DV/train_v14/mech/benchmarks/write_rft_real.py --bo8 $C/results/bo32_${CORPUS}_${R}.json \
  --png-dir $C/render/png --manifest $C/manifest.json --out $DV/rft_selfdistill_${CORPUS}
tail -5 $DV/rft_selfdistill_${CORPUS}/stats.json 2>/dev/null
echo "SCORE+TIER DONE $CORPUS"
