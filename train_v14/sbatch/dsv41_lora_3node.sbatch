#!/bin/bash
#SBATCH --job-name=dsv41-lora-3node
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=3
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=96
#SBATCH --gres=gpu:H200:8
#SBATCH --mem=1400G
#SBATCH --nodelist=ccc0451,ccc0474,ccc0475
#SBATCH --time=24:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/dsv41/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/dsv41/%x.e%j
# DeepSeek-V4.1-Flash LoRA across three H200 nodes: one process per node holding a full
# pipeline-split replica (device_map="auto" over its 8 GPUs, FP8/FP4 kept quantized), adapter
# gradients averaged across the nodes over NCCL / InfiniBand (the connector-folder recipe:
# MASTER_ADDR from the first node, a free MASTER_PORT, NCCL over mlx5).
#   STEPS=600 ACCUM=4 LR=1e-4 RANK_R=16 TIER=rft_real_union5_dw423/shards \
#     sbatch train_v14/sbatch/dsv41_lora_3node.sbatch
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; export DV; cd $DV
export HF_HOME=$DV/.cache/huggingface PYTHONPATH=$DV/train_v14:$DV/train_v14/geom OPENBLAS_NUM_THREADS=1
# Triton JIT cache: the NFS home dir is slow for the hundreds of specializations this model compiles;
# seed a node-local copy from it and sync new entries back at the end.
export TRITON_CACHE_DIR=/dev/shm/bimrose2/triton; mkdir -p $TRITON_CACHE_DIR
[ -d $HOME/.triton/cache ] && rsync -a $HOME/.triton/cache/ $TRITON_CACHE_DIR/ 2>/dev/null
trap 'rsync -a $TRITON_CACHE_DIR/ $HOME/.triton/cache/ 2>/dev/null; rm -rf /dev/shm/bimrose2' EXIT
export NCCL_IB_DISABLE=0 NCCL_P2P_LEVEL=NVL NCCL_NET_GDR_LEVEL=5
export MASTER_ADDR=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -n 1)
export MASTER_PORT=$(python3 -c "import socket; s=socket.socket(); s.bind(('', 0)); print(s.getsockname()[1]); s.close()")
echo "nodes $SLURM_JOB_NODELIST master $MASTER_ADDR:$MASTER_PORT job $SLURM_JOB_ID"
STEPS=${STEPS:-600}; ACCUM=${ACCUM:-4}; LR=${LR:-1e-4}; R=${RANK_R:-16}; TIER=${TIER:-rft_real_union5_dw423/shards}
OUT=${OUT:-$DV/runs/dsv41_lora_r${R}_s${STEPS}}
srun --ntasks=$SLURM_NNODES --ntasks-per-node=1 bash -c 'mkdir -p $TRITON_CACHE_DIR; rsync -a $HOME/.triton/cache/ $TRITON_CACHE_DIR/ 2>/dev/null; LV=/dev/shm/bimrose2/venv_dsv41; T0=$(date +%s); rsync -a --copy-links $DV/.venv_dsv41/ $LV/ && echo "$(hostname): venv staged in $(( $(date +%s)-T0 )) s" && PY=$LV/bin/python || PY=$DV/.venv_dsv41/bin/python; exec $PY "$@"' _ $DV/train_v14/geom/dsv41_lora_train.py --dist \
  --model $DV/models/DeepSeek-V4.1-Flash --tier $DV/$TIER --steps $STEPS --accum $ACCUM --lr $LR --rank $R \
  --max-len ${MAX_LEN:-4096} --out $OUT --exec-python $DV/.venv/bin/python --eval-bench ${EVAL_BENCH:-$DV/train_v14/mech/benchmarks/data/ext_bench} --eval-n ${EVAL_N:-96}
echo "TRAIN EXIT $?"
