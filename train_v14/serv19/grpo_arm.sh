#!/bin/bash
# Launch ONE GRPO arm on serv-20 from e55 (2026-10-06). Avoids the inline-quoting trap that killed
# frontkl0 (\$COMMON not expanded over ssh): everything lives in this file, ssh only passes words.
#   bash train_v14/serv19/grpo_arm.sh <name> <gpu> [extra grpo_round.py args, later ones win]
# e.g. bash train_v14/serv19/grpo_arm.sh lr5e5 0 --lr 5e-5
# Output runs/grpo_s_<name>, log logs/grpo_s_<name>.log. Defaults = round-1 kl002 config on the
# 1,655-part family train bench; override --bench/--keys/--steps/--lr/... as needed.
set -uo pipefail
# serv-20 has no thread caps in the login env: unset, every python child spawns ~core-count threads (load ~900, 2026-10-06)
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4
cd /srv/scratch/bimrose2
name=${1:?name}; gpu=${2:?gpu}; shift 2
COMMON=(--run e55-rft-real-u5-gt-dw423 --model-base /srv/scratch/bimrose2/models/Qwen3.8-27B
  --ckpt /srv/scratch/bimrose2/runs/e55-rft-real-u5-gt-dw423/final --bench fp/h6/train_bench
  --n-parts 16 --g 8 --steps 60 --lr 1e-5 --kl-beta 0.02 --gen-batch 16 --train-batch 4
  --score-workers 12 --save-every 8)
mkdir -p runs/grpo_s_$name logs
CUDA_VISIBLE_DEVICES=$gpu PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
  setsid nohup .venv/bin/python train_v14/geom/grpo_round.py "${COMMON[@]}" "$@" \
  --out runs/grpo_s_$name > logs/grpo_s_$name.log 2>&1 < /dev/null &
echo "arm $name on GPU $gpu (pid $!): $*"
