#!/bin/bash
# bank v3 stage 1 (2026-10-07): best RL generator (mix_t10 s120) draws K=16 at T=1.0 on the hard real training parts
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV; source train_v14/env.sh
export OMP_NUM_THREADS=2 PYTHONPATH=$DV/train_v14:$DV/train_v14/geom
PY=$(ls -d /dev/shm/bimrose2/gf_11181389/venv/bin/python 2>/dev/null || echo $DV/.venv/bin/python)
curl -s -X POST http://127.0.0.1:8503/v1/load_lora_adapter -H "Content-Type: application/json" \
  -d "{\"lora_name\": \"t10s120\", \"lora_path\": \"$DV/runs/grpo_v_mix_t10/adapter_step120\"}"; echo
B=train_v14/mech/benchmarks/data
$PY train_v14/geom/gen_openai_bo.py --bench $B/rft_corpus2_dw423 --keys results/h6c/c2_hard_keys.txt --base-url http://127.0.0.1:8503/v1 \
  --model t10s120 --k 16 --temperature 1.0 --workers 24 --out results/guide/v3/bo16_c2_t10 > results/guide/v3/gen_c2.log 2>&1
$PY train_v14/geom/gen_openai_bo.py --bench $B/rft_corpus4 --keys results/h6c/real4_hard_keys.txt --base-url http://127.0.0.1:8503/v1 \
  --model t10s120 --k 16 --temperature 1.0 --workers 24 --out results/guide/v3/bo16_c4_t10 > results/guide/v3/gen_c4.log 2>&1
echo "GEN V3 DONE"
