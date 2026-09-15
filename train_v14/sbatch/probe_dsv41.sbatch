#!/bin/bash
#SBATCH --job-name=probe-dsv41
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=64
#SBATCH --gres=gpu:H200:8
#SBATCH --mem=1000G
#SBATCH --time=12:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.err
# Zero-shot DeepSeek-V4.1-Flash on the 146-part real bench: vLLM (Docker image via apptainer,
# the only distribution that serves this architecture -- recipes.vllm.ai) on 8xH200, then
# probe_openai_vlm.py with the fine-tuned model's exact prompt. The checkpoint is FP8 with FP4
# experts (510 GB); the recipe's stated minimum is 614 GB VRAM, one 8-GPU H200 node fits.
#   sbatch --export=ALL[,BENCH=<dir>,N=146,K=1,TAG=probe_dsv41_ext] probe_dsv41.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
MODEL=$DV/models/DeepSeek-V4.1-Flash
SIF=$DV/containers/vllm-dsv41.sif
B=${BENCH:-$DV/train_v14/mech/benchmarks/data/ext_bench}
T=${TAG:-probe_dsv41_ext}
[ -f $MODEL/config.json ] && [ -f $SIF ] || { echo "missing model or image"; exit 1; }
export VLLM_ENGINE_READY_TIMEOUT_S=3600
# serve (vision on: no --language-model-only). Weights are read straight from Lustre; the
# first load is the slow part, so the ready timeout is an hour.
apptainer exec --nv --bind $DV:$DV --bind /tmp:/tmp $SIF \
  vllm serve $MODEL --served-model-name deepseek-ai/DeepSeek-V4.1-Flash \
    --host 127.0.0.1 --port 8000 --tensor-parallel-size 8 \
    --tokenizer-mode deepseek_v41 --reasoning-parser deepseek_v41 \
    --gpu-memory-utilization 0.90 --max-model-len 32768 --max-num-seqs 16 \
    --max-num-batched-tokens 16384 --limit-mm-per-prompt '{"image": 1}' \
    > $DV/logs/slurm/vllm-dsv41-$SLURM_JOB_ID.log 2>&1 &
VPID=$!
for i in $(seq 1 360); do
  curl -s -m 5 http://127.0.0.1:8000/health >/dev/null 2>&1 && { echo "$(date) vllm ready after $((i*10)) s"; break; }
  kill -0 $VPID 2>/dev/null || { echo "vllm died; tail:"; tail -30 $DV/logs/slurm/vllm-dsv41-$SLURM_JOB_ID.log; exit 1; }
  sleep 10
done
curl -s -m 5 http://127.0.0.1:8000/health >/dev/null || { echo "vllm never became ready"; tail -30 $DV/logs/slurm/vllm-dsv41-$SLURM_JOB_ID.log; kill $VPID; exit 1; }
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
export OPENBLAS_NUM_THREADS=1
python $DV/train_v14/geom/probe_openai_vlm.py --bench $B --base-url http://127.0.0.1:8000/v1 \
  --model deepseek-ai/DeepSeek-V4.1-Flash --out $DV/results/ext/$T.json --n ${N:-146} --k ${K:-1} \
  --temperature ${TEMP:-0} --workers ${WORKERS:-4}
kill $VPID 2>/dev/null; wait $VPID 2>/dev/null
echo "PROBE DONE $T"
