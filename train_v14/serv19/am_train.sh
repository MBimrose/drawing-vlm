#!/bin/bash
# American-VLM screen (2026-10-26): full fine-tune of a new base on the e55 recipe. 20-step smoke first (s/step, memory,
# loss), then the 4,000-step run if the smoke passed. Code = amvlm/train_v14 (synced from the cluster).
#   CFG=am-gemma4-31b-e55recipe GPUS=0,1,2,3,4,5,6,7 setsid nohup bash amvlm/train_v14/serv19/am_train.sh > amvlm/logs/<cfg>.log 2>&1 &
set -uo pipefail
cd /srv/scratch/bimrose2
say() { echo "$(date '+%m-%d %H:%M') $*"; }
CFG=${CFG:?}; C=amvlm/train_v14/configs/$CFG.yaml; L=amvlm/logs; mkdir -p $L amvlm/runs
source amvlm/train_v14/serv19/am_env.sh
export CUDA_VISIBLE_DEVICES=${GPUS:-0,1,2,3,4,5,6,7} TRAIN_VENV
if [ ! -f $L/$CFG.SMOKE_OK ]; then
  say "smoke: 20 steps"
  bash amvlm/train_v14/run.sh $C --max_steps=20 --eval_every=0 --save_final=false --save_best=false \
    --output_dir=/srv/scratch/bimrose2/amvlm/runs/$CFG-smoke > $L/$CFG.smoke.log 2>&1
  rc=$?; say "smoke exit $rc: $(grep -o "'loss': '[0-9.]*'" $L/$CFG.smoke.log | tail -2 | tr '\n' ' ') $(tr '\r' '\n' < $L/$CFG.smoke.log | grep -oE '[0-9.]+s/it' | tail -1)"
  [ $rc = 0 ] || { say "SMOKE FAILED: $(grep -E 'Error|error' $L/$CFG.smoke.log | grep -v errors.html | tail -3)"; exit 1; }
  touch $L/$CFG.SMOKE_OK
fi
[ "${SMOKE_ONLY:-0}" = 1 ] && { say "smoke only"; exit 0; }
say "full run"
bash amvlm/train_v14/run.sh $C > $L/$CFG.train.log 2>&1
rc=$?; say "train exit $rc"; [ $rc = 0 ] && touch $L/$CFG.TRAIN_DONE
