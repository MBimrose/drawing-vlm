#!/bin/bash
#SBATCH --job-name=e13-production
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodelist=ccc0451,ccc0474,ccc0475
#SBATCH --nodes=3
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=96
#SBATCH --gres=gpu:H200:8
#SBATCH --mem=1400G
#SBATCH --time=48:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.e%j

set -euo pipefail
TRAIN=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/train_v14
CFG=${E13_CFG:-$TRAIN/configs/e13-production.yaml}
MASTER=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -1)
PORT=$((20000 + SLURM_JOB_ID % 20000))

# One srun task per node; each launches its 8 local ranks via accelerate
# with the right machine_rank. EXTRA_ARGS lets the smoke test shrink the run.
srun bash -c '
  source /projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/.venv/bin/activate
  source '"$TRAIN"'/env.sh
  export NCCL_DEBUG=WARN
  MODEL_DIR=$(grep -E "^model_id:" '"$CFG"' | awk "{print \$2}")
  if [ -d "$MODEL_DIR" ]; then
    ls "$MODEL_DIR"/*.safetensors | xargs -P 16 -I{} cat {} > /dev/null || true
  fi
  accelerate launch \
    --config_file '"$TRAIN"'/configs/accelerate_hsdp_24gpu.yaml \
    --machine_rank "$SLURM_NODEID" \
    --main_process_ip '"$MASTER"' \
    --main_process_port '"$PORT"' \
    --num_machines 3 \
    --num_processes 24 \
    '"$TRAIN"'/train_sft_v14.py '"$CFG"' '"${E13_EXTRA:-}"'
'
