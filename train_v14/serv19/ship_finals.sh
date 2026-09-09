#!/usr/bin/env bash
# Usage: ship_finals.sh <run> [<run> ...]
# For each run in order: wait until its SLURM job is gone and runs/<run>/final is
# complete, then submit the external real-part eval and the full-pool best-of-8 on the cluster.
# Launch detached:  setsid nohup train_v14/serv19/ship_finals.sh e46-rft-real > logs/ship_finals.log 2>&1 < /dev/null &
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
cd $DV
for R in "$@"; do
  until ! squeue -h -n $R -o %T | grep -q . && [ -f runs/$R/final/model.safetensors.index.json ] && [ "$(ls runs/$R/final | wc -l)" -ge 10 ]; do sleep 120; done
  sleep 60
  J=$(sbatch --parsable --export=ALL,RUN=$R --job-name=bo8-ext-$R train_v14/sbatch/bo8_ext_cluster.sbatch)
  echo "$(date) submitted external eval for $R: job $J"
  # Full pool on the CLUSTER (serv-19 GPUs are reserved by the user since 2026-09-09): same job as the
  # external bench pointed at the in-distribution cache dir; a <run>-serv19.env with a dw423 cache maps
  # to the cluster copy of that cache.
  CACHE_ENV=""
  if [ -f train_v14/configs/$R-serv19.env ] && grep -q "eval_cache_v15_dw423" train_v14/configs/$R-serv19.env; then
    CACHE_ENV=",DRAWING_VLM_EVAL_CACHE_V15=$DV/step_to_drw/wds_dataset/eval_cache_v15_dw423.pkl"
  fi
  JF=$(sbatch --parsable --export=ALL,RUN=$R,BENCH=$DV/step_to_drw/wds_dataset,TAG=bo8_full,N=1072$CACHE_ENV --job-name=bo8-full-$R train_v14/sbatch/bo8_ext_cluster.sbatch)
  echo "$(date) submitted cluster full-pool for $R: job $JF (results/ext/bo8_full_$R*)"
done
