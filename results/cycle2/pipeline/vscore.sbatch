#!/bin/bash
#SBATCH --job-name=c2-vsc
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodelist=ccc0442
#SBATCH --gres=gpu:L40S:2
#SBATCH --cpus-per-task=8
#SBATCH --mem=200G
#SBATCH --time=06:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/cycle2/pipeline/logs/%x-%j.out
# Cycle-2 pipeline: v3b-EV verifier (e51 base + v3b LoRA = the 0.716 pipeline's verifier) on the scored K=16 candidates,
# split over 2 L40S (device_map balanced). sbatch --export=ALL,NAME=<name> vscore.sbatch
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV; source train_v14/env.sh
export OMP_NUM_THREADS=4 PYTHONPATH=$DV/train_v14:$DV/train_v14/geom
P=results/cycle2/pipeline
until [ -f $P/real_k16_$NAME.json ]; do sleep 60; done
.venv/bin/python train_v14/geom/sel_vscore.py --cache train_v14/mech/benchmarks/data/ext_bench_dw423_perm/eval_cache_v15.pkl \
  --outdir $P --batch 8 k16_$NAME=$P/real_k16_$NAME.json
echo "VSCORE DONE $?"
