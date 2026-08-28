#!/bin/bash
#SBATCH --job-name=geom-eval-next
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --gres=gpu:H200:8
#SBATCH --mem=1400G
#SBATCH --time=12:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.e%j

# Geometric IoU eval for Qwen3.8-Flash-Next (e26) adapters: needs a full H200
# node (336 GB base). One-shot (no self-resubmission); evaluates whatever
# best_adapter/ and final/ exist for the run at launch time.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
export FLASHNEXT_PLE_DIR=/dev/shm/flashnext_ple
source "$DV/train_v14/env.sh"
M=$DV/models/Qwen3.8-Flash-Next
echo "[warm] page cache for $M"; ls "$M"/*.safetensors | xargs -P 16 -I{} cat {} > /dev/null || true
source "$DV/.venv/bin/activate"
python "$DV/train_v14/geom/geom_eval_worker.py" --runs ${RUNS:-e26-flashnext-lora} --n 96 --batch 8
bash "$DV/scripts/snapshot_results.sh" || true
