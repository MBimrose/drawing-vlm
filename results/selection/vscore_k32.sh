#!/bin/bash
# v3b-EV verifier on the K=32 mix_t10 s120 real-bench draws (every candidate with code; exec filter applied later), GPU 7.
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV; source train_v14/env.sh
export CUDA_VISIBLE_DEVICES=7 OMP_NUM_THREADS=4 PYTHONPATH=$DV/train_v14:$DV/train_v14/geom
PY=$(ls -d /dev/shm/bimrose2/gf_11181389/venv/bin/python 2>/dev/null || echo $DV/.venv/bin/python)
until grep -q "VSCORE K8 DONE" logs/slurm/sel-vscore-11209265.out 2>/dev/null; do sleep 30; done
$PY train_v14/geom/sel_vscore.py --cache train_v14/mech/benchmarks/data/ext_bench_dw423_perm/eval_cache_v15.pkl \
  --outdir results/selection --batch 8 k32_t10s120=results/selection/vin_k32.json > results/selection/vscore_k32.log 2>&1
echo "VSCORE K32 DONE $?"
