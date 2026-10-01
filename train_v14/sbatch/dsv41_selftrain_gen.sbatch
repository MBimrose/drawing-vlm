#!/bin/bash
#SBATCH --job-name=dsv41-stgen
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodes=1
#SBATCH --cpus-per-task=96
#SBATCH --gres=gpu:H200:8
#SBATCH --mem=1400G
#SBATCH --time=24:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/dsv41/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/dsv41/%x-%j.err
# DeepSeek self-training data (2026-09-30): vanilla DeepSeek-V4.1-Flash served by vLLM (TP8, native context) samples
# K drafts per part at T=0.7 with up to 100k tokens, reasoning saved; drafts executed + scored vs GT in-job.
#   sbatch --nodelist=<node> --export=ALL,SHARD=<i>,NSHARDS=<n> dsv41_selftrain_gen.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; B=$DV/dsv41_selftrain_bench
S=/dev/shm/bimrose2/stg_$SLURM_JOB_ID; mkdir -p $S/tmp $S/cfg $S/home; trap 'pkill -f "vllm serv[e]"; rm -rf $S' EXIT
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
rsync -a --copy-links $DV/.venv/ $S/venv/ & cp $DV/containers/vllm-dsv41.from-serv20.sif $S/vllm.sif & wait
APPTAINERENV_VLLM_ENGINE_READY_TIMEOUT_S=3600 APPTAINERENV_PYTHONNOUSERSITE=1 APPTAINERENV_VLLM_CONFIG_ROOT=$S/cfg APPTAINERENV_XDG_CACHE_HOME=$S/home/.cache \
apptainer exec --nv --cleanenv --home $S/home --bind $DV:$DV --bind /dev/shm:/dev/shm --bind $S/tmp:/tmp $S/vllm.sif \
  vllm serve $DV/models/DeepSeek-V4.1-Flash --served-model-name ds --host 127.0.0.1 --port 8000 --tensor-parallel-size 8 --enable-expert-parallel \
  --tokenizer-mode deepseek_v41 --reasoning-parser deepseek_v41 --gpu-memory-utilization 0.90 --max-num-seqs 64 --max-num-batched-tokens 32768 \
  --limit-mm-per-prompt '{"image": 1}' > $DV/logs/dsv41/vllm-stgen-$SLURM_JOB_ID.log 2>&1 &
for i in $(seq 1 360); do curl -s -m 5 http://127.0.0.1:8000/health >/dev/null && break; sleep 10; done
curl -s -m 5 http://127.0.0.1:8000/health >/dev/null || { echo "vLLM never ready"; tail -30 $DV/logs/dsv41/vllm-stgen-$SLURM_JOB_ID.log; exit 1; }
echo "vLLM up $(date)"
cd $DV; export REASONING_EFFORT=75 PYTHONPATH=$DV/train_v14:$DV/train_v14/geom
$S/venv/bin/python train_v14/geom/probe_openai_vlm.py --bench $B --keys $B/keys.txt --shard ${SHARD} --nshards ${NSHARDS} --base-url http://127.0.0.1:8000/v1 --model ds \
  --out $DV/results/dsv41_selftrain/gen_s${SHARD}.json --k ${K:-2} --temperature 0.7 --workers ${WORKERS:-64} --max-tokens ${MAXTOK:-100000} --timeout 14400 --save-reasoning
echo "STGEN DONE $(date)"
