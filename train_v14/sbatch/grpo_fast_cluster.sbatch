#!/bin/bash
#SBATCH --job-name=grpo-fast
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=120
#SBATCH --gres=gpu:H200:8
#SBATCH --mem=1400G
#SBATCH --time=48:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.err
# Fast-path GRPO on one H200 node (2026-10-06): 4 arms, each = vLLM rollout server (LoRA hot-load)
# on an even GPU + HF/peft trainer on the next odd GPU (H200 141 GB cannot hold both, a B300 can).
#   sbatch --nodelist=<node> --export=ALL,ARMS_FILE=<file: one "name|args" per line> grpo_fast_cluster.sbatch
# (a file, not an env list: sbatch --export splits values on commas, which --bench a,b needs)
# --cleanenv drops CUDA_VISIBLE_DEVICES: it must be passed as APPTAINERENV_CUDA_VISIBLE_DEVICES.
# Outputs runs/grpo_v_<name>, logs logs/grpo_v_<name>.log (same layout as serv19/grpo_vllm_arm.sh).
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
S=/dev/shm/bimrose2/gf_$SLURM_JOB_ID; mkdir -p $S/tmp $S/cfg $S/home
trap 'pkill -f "vllm serv[e]"; rm -rf $S' EXIT
source $DV/train_v14/env.sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
rsync -a --copy-links $DV/.venv/ $S/venv/ & cp $DV/containers/vllm-dsv41.from-serv20.sif $S/vllm.sif & wait
PY=$S/venv/bin/python; $PY -c "import build123d, OCP" 2>/dev/null || PY=$DV/.venv/bin/python
E55=$DV/runs/e55-rft-real-u5-gt-dw423/final
mapfile -t SPECS < <(grep -v '^\s*$' "$ARMS_FILE")
i=0; TPIDS=()
for spec in "${SPECS[@]}"; do
  name=${spec%%|*}; extra=${spec#*|}
  vg=$((2 * i)); tg=$((2 * i + 1)); port=$((8500 + i))
  mkdir -p $DV/runs/grpo_v_$name
  CUDA_VISIBLE_DEVICES=$vg APPTAINERENV_CUDA_VISIBLE_DEVICES=$vg APPTAINERENV_VLLM_ALLOW_RUNTIME_LORA_UPDATING=True APPTAINERENV_VLLM_ENGINE_READY_TIMEOUT_S=3600 \
    APPTAINERENV_PYTHONNOUSERSITE=1 APPTAINERENV_VLLM_CONFIG_ROOT=$S/cfg APPTAINERENV_XDG_CACHE_HOME=$S/home/.cache \
    apptainer exec --nv --cleanenv --home $S/home --bind $DV:$DV --bind /dev/shm:/dev/shm --bind $S/tmp:/tmp $S/vllm.sif \
    vllm serve $E55 --served-model-name e55 --host 127.0.0.1 --port $port --reasoning-parser qwen3 \
      --gpu-memory-utilization 0.88 --max-model-len 16384 --max-num-seqs 256 --limit-mm-per-prompt '{"image": 1}' \
      --trust-remote-code --enable-lora --max-lora-rank 64 --max-loras 2 > $DV/logs/vllm-grpo_v_$name.log 2>&1 &
  (
    for j in $(seq 1 360); do curl -s -m 5 http://127.0.0.1:$port/health >/dev/null && break; sleep 10; done
    curl -s -m 5 http://127.0.0.1:$port/health >/dev/null || { echo "vLLM never ready $name"; exit 1; }
    cd $DV
    CUDA_VISIBLE_DEVICES=$tg $PY train_v14/geom/grpo_round.py --run e55-rft-real-u5-gt-dw423 \
      --model-base $DV/models/Qwen3.8-27B --ckpt $E55 --n-parts 16 --g 8 --steps 300 --lr 2e-5 --kl-beta 0 \
      --train-batch 4 --score-workers 24 --score-timeouts --save-every 20 \
      --rollout-url http://127.0.0.1:$port/v1 $extra --out $DV/runs/grpo_v_$name
    echo "trainer exit $? $name"
  ) > $DV/logs/grpo_v_$name.log 2>&1 &
  TPIDS+=($!)
  echo "arm $name: vLLM GPU $vg :$port, trainer GPU $tg :: $extra"
  i=$((i + 1))
done
wait "${TPIDS[@]}"   # trainers only; the vLLM servers die with the trap
echo "GRPO FAST DONE $(date)"
