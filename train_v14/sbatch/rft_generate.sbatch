#!/bin/bash
#SBATCH --job-name=rft-gen
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=96
#SBATCH --gres=gpu:H200:8
#SBATCH --mem=1400G
#SBATCH --time=24:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.e%j

# Rejection-sampling generation: 8 single-GPU workers, each streaming a
# stride-partitioned slice of tars_v14 through the champion checkpoint,
# executing + IoU-scoring inline, keeping iou>=0.8. NODE_IDX (0 or 1)
# offsets the stride so two nodes never overlap.
# NB: env.sh redefines ROOT — use DV for our tree and set paths BEFORE
# sourcing anything.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
TRAIN=$DV/train_v14
NODE_IDX=${NODE_IDX:-0}
CKPT=${RFT_CKPT:-$DV/runs/e16-full-execfilter/final}
RUN=${RFT_RUN:-e16-full-execfilter}
OUT=${RFT_OUT:-$DV/rft_v1}
LOGD=$DV/logs/slurm
mkdir -p "$OUT" "$LOGD"

source $DV/.venv/bin/activate
source $TRAIN/env.sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4

pids=()
for g in 0 1 2 3 4 5 6 7; do
  w=$((NODE_IDX * 8 + g))
  CUDA_VISIBLE_DEVICES=$g python $TRAIN/geom/rft_generate.py \
    --ckpt "$CKPT" --kind hf --run "$RUN" \
    --worker $w --stride 16 --out "$OUT" \
    --batch 8 --min-iou 0.8 ${RFT_EXTRA:---temperature 0.6} --max-accepted ${RFT_MAX_ACCEPTED:-4000} \
    > "$LOGD/rft-w${w}.log" 2>&1 &
  pids+=($!)
done
wait "${pids[@]}"
echo "RFT NODE $NODE_IDX COMPLETE"
