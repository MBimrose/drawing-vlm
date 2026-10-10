#!/bin/bash
# v4-verifier-e55-reg (e55 base) on 3 models' K=8 real candidates, GPU 7 (between the K=32 v3b pass and v5 training).
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV; source train_v14/env.sh
export CUDA_VISIBLE_DEVICES=7 OMP_NUM_THREADS=4 PYTHONPATH=$DV/train_v14:$DV/train_v14/geom
PY=/dev/shm/bimrose2/gf_11181389/venv/bin/python; G=results/grpo_eval
$PY train_v14/geom/sel_vscore.py --cache train_v14/mech/benchmarks/data/ext_bench_dw423_perm/eval_cache_v15.pkl \
  --outdir results/selection --prefix v4preds_ --verifier runs/v4-verifier-e55-reg/final --verifier-run v4-verifier-e55-reg --batch 8 \
  e55ctl=$G/real_e55ctl.json mix_t10_s120=$G/real_mix_t10_s120.json guide_mb8b_s60=$G/real_guide_mb8b_s60.json > results/selection/vscore_v4.log 2>&1
echo "VSCORE V4 DONE $?"
