#!/bin/bash
#SBATCH --job-name=grpo-ovl
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodelist=ccc0442
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=48:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.out
# Run ONE extra fast-path trainer inside an already-running grpo-fast job (2026-10-07), on a GPU that job left
# idle, against one of its vLLM servers. This tiny CPU job only keeps the overlapping srun step alive (the login
# node kills long-lived processes).
#   sbatch --export=ALL,HOSTJOB=<grpo-fast jobid>,TGPU=<idle gpu>,PORT=<that job's vLLM port>,NAME=<arm>,ARGS_FILE=<file> grpo_overlap_arm.sbatch
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
ARGS=$(cat $ARGS_FILE)
for v in $(env | grep -oE "^SLURM_[A-Z_]+"); do unset $v; done
srun --jobid=$HOSTJOB --overlap -N1 -n1 --gres=gpu:H200:8 bash -c "
  source $DV/train_v14/env.sh; cd $DV
  export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True CUDA_VISIBLE_DEVICES=$TGPU
  PY=\$(ls -d /dev/shm/bimrose2/gf_$HOSTJOB/venv/bin/python 2>/dev/null || echo $DV/.venv/bin/python)
  \$PY train_v14/geom/grpo_round.py --run e55-rft-real-u5-gt-dw423 --model-base $DV/models/Qwen3.8-27B \
    --ckpt $DV/runs/e55-rft-real-u5-gt-dw423/final --n-parts 16 --g 8 --steps 300 --train-batch 4 \
    --score-workers 24 --score-timeouts --save-every 10 --rollout-url http://127.0.0.1:$PORT/v1 $ARGS \
    --out $DV/runs/grpo_v_$NAME >> $DV/logs/grpo_v_$NAME.log 2>&1"
echo "overlap arm $NAME exit $?"
