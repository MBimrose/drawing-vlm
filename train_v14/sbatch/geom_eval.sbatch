#!/bin/bash
#SBATCH --job-name=geom-eval
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --nodelist=ccc0442
#SBATCH --gres=gpu:L40S:4
#SBATCH --mem=500G
#SBATCH --time=24:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.e%j

# Geometric IoU eval worker (runs on the L40S node so it never competes with
# training). Self-resubmitting every 8h; kill the chain with:
#   scancel -n geom-eval -u $USER
set -uo pipefail
SCRIPT=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/train_v14/sbatch/geom_eval.sbatch
if ! squeue -u "$USER" -h -n geom-eval -t PD | grep -q .; then
  sbatch --begin=now+8hours "$SCRIPT"
fi

TRAIN=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/train_v14
bash "$TRAIN/geom/self_heal.sh" || true

source /projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/.venv/bin/activate
source "$TRAIN/env.sh"
export GEOM_EVAL_SKIP_DCP=1   # finals only; sharded checkpoints take 2-3 h to consolidate
python "$TRAIN/geom/geom_eval_worker.py" --n 96 --batch 8
bash /projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/scripts/snapshot_results.sh || true
