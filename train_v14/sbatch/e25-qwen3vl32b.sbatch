#!/bin/bash
#SBATCH --job-name=e25-qwen3vl32b
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=96
#SBATCH --gres=gpu:H200:8
#SBATCH --mem=1400G
#SBATCH --time=48:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.e%j

set -uo pipefail
# Guard: weights must be fully downloaded (index + all shards present).
# Not ready -> requeue ourselves for +1h instead of dying.
M=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/models/Qwen3-VL-32B-Instruct
if ! python3 - <<'PYEOF'
import json, os, sys
M = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/models/Qwen3-VL-32B-Instruct"
idx = os.path.join(M, "model.safetensors.index.json")
if not os.path.exists(idx):
    sys.exit("weights not ready: no index")
shards = set(json.load(open(idx))["weight_map"].values())
missing = [s for s in shards if not os.path.exists(os.path.join(M, s))]
sys.exit(f"weights not ready: {len(missing)} shards missing" if missing else 0)
PYEOF
then
  echo "[e25] weights not ready — requeueing +1h"
  sbatch --begin=now+1hour /projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/train_v14/sbatch/e25-qwen3vl32b.sbatch
  exit 0
fi
set -e

TRAIN=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/train_v14
bash "$TRAIN/run.sh" "$TRAIN/configs/e25-qwen3vl32b.yaml"
