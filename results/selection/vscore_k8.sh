#!/bin/bash
# v3b-EV verifier on the stored K=8 real-bench candidates of 10 models, ccc0451 GPU 7 (idle), one model load.
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV; source train_v14/env.sh
export CUDA_VISIBLE_DEVICES=7 OMP_NUM_THREADS=4 PYTHONPATH=$DV/train_v14:$DV/train_v14/geom
PY=$(ls -d /dev/shm/bimrose2/gf_11181389/venv/bin/python 2>/dev/null || echo $DV/.venv/bin/python)
nvidia-smi --query-gpu=index,memory.used --format=csv | sed -n '1p;9p'
G=results/grpo_eval; S=""
for m in e55ctl mix_t10_s120 guide_mb8b_s60 soup1_s20 mix_b32_s200 gt10_mb8_s60 mix_t10_s200 mix_b32_s120 mix_cont_s200 guide2b_s120; do S="$S $m=$G/real_$m.json"; done
$PY train_v14/geom/sel_vscore.py --cache train_v14/mech/benchmarks/data/ext_bench_dw423_perm/eval_cache_v15.pkl \
  --outdir results/selection --batch 8 $S > results/selection/vscore_k8.log 2>&1
echo "VSCORE K8 DONE $?"
