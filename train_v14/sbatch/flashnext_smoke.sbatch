#!/bin/bash
#SBATCH --job-name=flashnext-smoke
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --gres=gpu:H200:4
#SBATCH --mem=800G
#SBATCH --time=02:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.e%j

set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
SELF=$DV/train_v14/sbatch/flashnext_smoke.sbatch
if [ ! -f $DV/models/Qwen3.8-Flash-Next/model.safetensors.index.json ] \
   || ! $DV/.venv_next/bin/python -c "
import json, os
M='$DV/models/Qwen3.8-Flash-Next'
s=set(json.load(open(os.path.join(M,'model.safetensors.index.json')))['weight_map'].values())
missing=[x for x in s if not os.path.exists(os.path.join(M,x))]
raise SystemExit(1 if missing else 0)" 2>/dev/null; then
  echo "[smoke] weights not fully staged — requeue +1h"
  sbatch --begin=now+1hour "$SELF"
  exit 0
fi
export HF_HUB_OFFLINE=1 OPENBLAS_NUM_THREADS=1
$DV/.venv_next/bin/python $DV/train_v14/geom/smoke_flashnext_cluster.py
