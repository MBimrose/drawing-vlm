#!/usr/bin/env bash
# Usage: ./run_bo8_full_generic.sh <run_name>
# Full certified pool (1,030 parts) best-of-8 for runs/<run_name>/final: waits for
# the weight copy (10 files, no rsync temp files), 8 single-GPU workers, merge,
# consistency reranking. Needs train_v14/configs/<run_name>-serv19.yaml.
R=$1; cd /srv/scratch/bimrose2; source train_v14/env.sh
until [ "$(ls runs/$R/final 2>/dev/null | wc -l)" -ge 10 ] && [ -z "$(ls -A runs/$R/final | grep '^\.')" ]; do sleep 30; done
for i in 0 1 2 3 4 5 6 7; do
  CUDA_VISIBLE_DEVICES=$i nohup .venv/bin/python train_v14/geom/bestofn_verifier_eval.py \
    --ckpt runs/$R/final --kind hf --run $R-serv19 --verifier "" --n 1072 --k 8 \
    --temperature 0.7 --batch 16 --shard $i --nshards 8 \
    --out results/bo8_full_$R.shard$i.json > logs/bo8_full_$R.shard$i.log 2>&1 &
done
wait
.venv/bin/python train_v14/geom/merge_bo_shards.py results/bo8_full_$R.json results/bo8_full_$R.shard?.json > logs/bo8_full_${R}_merge.log 2>&1
[ -f results/bo8_full_$R.json ] && .venv/bin/python train_v14/geom/consistency_rerank.py \
  results/bo8_full_$R.json results/bo8_full_${R}_consistency.json > logs/bo8_full_${R}_consistency.log 2>&1
