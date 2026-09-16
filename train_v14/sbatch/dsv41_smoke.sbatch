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
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV
export HF_HOME=$DV/.cache/huggingface PYTHONPATH=$DV/train_v14:$DV/train_v14/geom OPENBLAS_NUM_THREADS=1
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | head -2
echo "=== stage 1 ($SLURM_JOB_NODELIST, job $SLURM_JOB_ID) ==="
srun $DV/.venv_dsv41/bin/python $DV/train_v14/geom/dsv41_lora_smoke.py --model $DV/models/DeepSeek-V4.1-Flash \
  --png $DV/spike_dsv41/sheet.png --answer $DV/spike_dsv41/answer.py --rank ${RANK_R:-16} --max-len 4096 \
  --fit-steps ${FIT_STEPS:-6} --gen-tokens 48
echo "STAGE1 EXIT $?"
