#!/bin/bash
# Cycle 2: score one set's K=16 partials on serv-20 (local NVMe venv; used for B_rp2 while the cluster scores CADBench sets).
#   setsid nohup bash cycle2/score_s20.sh <set> <gt dir> [workers] > cycle2/logs/score_s20_<set>.log 2>&1 &
cd /srv/scratch/bimrose2
S=$1; GT=$2; W=${3:-32}; TAG=${TAG:-c2pol}; O=cycle2/gen
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
while true; do
  gd=0; [ -f $O/GEN_DONE_${S}_$TAG ] && gd=1
  nice -n 10 .venv/bin/python train_v14/geom/score_partials.py --partials "$O/${S}_$TAG.shard0.json.partial.json" --gt-dir $GT \
    --out $O/${S}_$TAG.json --workers $W --exec-timeout 60 --iou-timeout 90 --accept 0
  [ $gd = 1 ] && { touch $O/SCORED_${S}_$TAG; echo "SCORED $S $(date)"; break; }
  sleep 120
done
