#!/bin/bash
# Selection study (2026-10-07): K=32 draws (draw 0 greedy, T=0.7 top_p 0.95 = the grpo_eval recipe) from mix_t10 s120
# (LoRA "t10s120" on the shared :8503 server of job 11181389) on the 144-part real bench. K=8/16 = first 8/16 draws.
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV; source train_v14/env.sh
export OMP_NUM_THREADS=2 PYTHONPATH=$DV/train_v14:$DV/train_v14/geom
PY=$(ls -d /dev/shm/bimrose2/gf_11181389/venv/bin/python 2>/dev/null || echo $DV/.venv/bin/python)
curl -s http://127.0.0.1:8503/v1/models | head -c 600; echo
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv
$PY train_v14/geom/gen_openai_bo.py --bench train_v14/mech/benchmarks/data/ext_bench_dw423_perm --base-url http://127.0.0.1:8503/v1 \
  --model t10s120 --k 32 --temperature 0.7 --workers 12 --out results/selection/real_k32_t10s120 > results/selection/gen_k32.log 2>&1
echo "GEN K32 DONE"
