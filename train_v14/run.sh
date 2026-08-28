#!/usr/bin/env bash
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"

# shellcheck disable=SC1091
source "${TRAIN_VENV:-$here/../.venv}/bin/activate"   # TRAIN_VENV overrides (e.g. .venv_next for Qwen4Exp)
# shellcheck disable=SC1091
source "$here/env.sh"

CFG=${1:?usage: run.sh configs/<experiment>.yaml [--key=value ...]}
shift

# Accelerate config comes from the experiment YAML's `accel_config` key
# (relative to train_v14/configs/). Default: FSDP2 8-GPU.
ACCEL=$(grep -E "^accel_config:" "$CFG" | awk '{print $2}' || true)
ACCEL=${ACCEL:-accelerate_fsdp2_8gpu.yaml}
ACCEL_CFG="$here/configs/$ACCEL"
echo "[run.sh] accelerate config: $ACCEL_CFG"

# Warm the model weights into the node page cache so rank 0's real load is
# fast (cold Lustre reads of 54 GB otherwise stall NCCL bootstrap).
MODEL_DIR=$(grep -E "^model_id:" "$CFG" | awk '{print $2}')
if [ -d "$MODEL_DIR" ]; then
  echo "[run.sh] warming page cache for $MODEL_DIR"
  ls "$MODEL_DIR"/*.safetensors | xargs -P 16 -I{} cat {} > /dev/null || true
fi

# Unique rendezvous port so two jobs can share a node.
PORT=$((20000 + ${SLURM_JOB_ID:-$$} % 20000))

accelerate launch \
  --config_file "$ACCEL_CFG" \
  --main_process_port "$PORT" \
  "$here/train_sft_v14.py" "$CFG" "$@"
