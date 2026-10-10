#!/bin/bash
# Full pipeline on the GRPO generator (2026-10-08): v3b-EV verifier on the scored K=16 ent_t10 s120 candidates
# (executing ones), ccc0451 H200 GPU 6 (overlap step in grpo-fast job 11213000), same tool as the selection study.
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV; source train_v14/env.sh
export CUDA_VISIBLE_DEVICES=6 OMP_NUM_THREADS=4 PYTHONPATH=$DV/train_v14:$DV/train_v14/geom
PY=$(ls -d /dev/shm/bimrose2/gf_11213000/venv/bin/python 2>/dev/null || echo $DV/.venv/bin/python)
O=results/pipeline_grpo
until [ -f $O/real_k16_ent_t10s120.json ]; do sleep 30; done
$PY train_v14/geom/sel_vscore.py --cache train_v14/mech/benchmarks/data/ext_bench_dw423_perm/eval_cache_v15.pkl \
  --outdir $O --batch 8 k16_ent_t10s120=$O/real_k16_ent_t10s120.json > $O/logs/vscore_k16.log 2>&1
echo "VSCORE K16 DONE $?"
