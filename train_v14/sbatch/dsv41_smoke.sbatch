#!/bin/bash
#SBATCH --job-name=dsv41-smoke
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --gres=gpu:H200:8
#SBATCH --mem=1000G
#SBATCH --time=03:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/dsv41/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/dsv41/%x.e%j
# Stage 1 of the DeepSeek-V4.1-Flash fine-tune spike on one H200 node: load the released FP8
# checkpoint pipeline-split over 8 GPUs, LoRA on the attention projections, forward/backward,
# a six-step one-sample fit (answer loss must fall) and a greedy continuation.
#   sbatch [--nodelist=ccc0451] train_v14/sbatch/dsv41_smoke.sbatch
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; export DV; cd $DV
export HF_HOME=$DV/.cache/huggingface PYTHONPATH=$DV/train_v14:$DV/train_v14/geom OPENBLAS_NUM_THREADS=1
# Triton JIT cache: the NFS home dir is slow for the hundreds of specializations this model compiles;
# seed a node-local copy from it and sync new entries back at the end.
export TRITON_CACHE_DIR=/dev/shm/bimrose2/triton; mkdir -p $TRITON_CACHE_DIR
[ -d $HOME/.triton/cache ] && rsync -a $HOME/.triton/cache/ $TRITON_CACHE_DIR/ 2>/dev/null
trap 'rsync -a $TRITON_CACHE_DIR/ $HOME/.triton/cache/ 2>/dev/null; rm -rf /dev/shm/bimrose2' EXIT
# The Triton compiler (and its bundled ptxas) run for hundreds of kernel variants per new shape; from the
# Lustre-hosted venv a forward took 150-430 s vs 12 s from local disk. Stage the venv into node RAM.
stage_venv() { local LV=/dev/shm/bimrose2/venv_dsv41; mkdir -p /dev/shm/bimrose2; local T0=$(date +%s);
  rsync -a --copy-links $DV/.venv_dsv41/ $LV/ && echo "$(hostname): venv staged in $(( $(date +%s)-T0 )) s" >&2 && echo $LV/bin/python || echo $DV/.venv_dsv41/bin/python; }
PY=$(stage_venv)
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | head -2
echo "=== stage 1 ($SLURM_JOB_NODELIST, job $SLURM_JOB_ID) ==="
srun $PY $DV/train_v14/geom/dsv41_lora_smoke.py --model $DV/models/DeepSeek-V4.1-Flash \
  --png $DV/spike_dsv41/sheet.png --answer $DV/spike_dsv41/answer.py --rank ${RANK_R:-16} --max-len 4096 \
  --fit-steps ${FIT_STEPS:-6} --gen-tokens 48
echo "STAGE1 EXIT $?"
