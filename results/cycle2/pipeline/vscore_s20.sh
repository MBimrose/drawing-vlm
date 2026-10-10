#!/bin/bash
# Cycle-2 pipeline: v3b-EV verifier on serv-20 GPU $GPU (default 4): e51 base (copied from the cluster) + v3b LoRA, the same
# weights as the 0.716 pipeline's verifier (there: H200; here: B300). Needs cycle2/pipeline/real_k16_<name>.json (scored).
cd /srv/scratch/bimrose2; NAME=${1:?name}; P=cycle2/pipeline
until [ -f $P/real_k16_$NAME.json ]; do sleep 30; done
CUDA_VISIBLE_DEVICES=${GPU:-4} OMP_NUM_THREADS=4 PYTHONPATH=cycle2/train_v14:cycle2/train_v14/geom DRAWING_VLM_ROOT=/srv/scratch/bimrose2 \
  .venv/bin/python cycle2/train_v14/geom/sel_vscore.py --cache mech_benchmarks/ext_bench_dw423_perm/eval_cache_v15.pkl \
  --outdir $P --batch 8 --verifier runs/v3b-verifier-real-reg/final --base /srv/scratch/bimrose2/runs/e51-rft-real-u3-strict90/final \
  k16_$NAME=$P/real_k16_$NAME.json > $P/logs/vscore_$NAME.log 2>&1
echo "VSCORE DONE $? $(date)"
