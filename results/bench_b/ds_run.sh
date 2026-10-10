#!/bin/bash
# Vanilla DeepSeek-V4.1-Flash best-of-8 on the 144-part real bench, T0 regime (lab hub, /v1/messages, effort low = 25,
# 30k tokens, T default 1.0, <= 3 calls: answer-now / exec-fix), x-hub-user bimrose2, 32 requests in flight.
cd /srv/scratch/bimrose2
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
nice -n 10 .venv/bin/python bench_b/code/dsv41_t0_rollout.py --parts ${PARTS:-bench_b/ds/parts_real144.tsv} \
  --base-url http://wpk-serv-07.mechse.illinois.edu:3456 --model "claude-deepseek-ai/DeepSeek-V4.1-Flash[1m]" \
  --hub-user bimrose2 --k 8 --workers ${W:-32} --score-workers 8 --py $PWD/.venv/bin/python --out ${OUT:-bench_b/ds/real144_dsv41_t0}
echo "DS RUN DONE $(date)"
