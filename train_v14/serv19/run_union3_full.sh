#!/usr/bin/env bash
# 3-model union (e24 ∪ e34 ∪ e37, 24 candidates/part) consistency on the full pool.
# CPU only; waits for the e37 rerank to finish.
cd /srv/scratch/bimrose2; source train_v14/env.sh
until [ -f results/bo8_full_e37_consistency.json ]; do sleep 120; done
.venv/bin/python train_v14/geom/union_bo.py results/bo24_union_full_e24e34e37.json results/bo8_full_e24.json results/bo8_full_e34.json results/bo8_full_e37.json > logs/union3_full.log 2>&1
.venv/bin/python train_v14/geom/consistency_rerank.py results/bo24_union_full_e24e34e37.json results/bo24_union_full_consistency.json >> logs/union3_full.log 2>&1
