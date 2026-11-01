#!/bin/bash
# Kimi-trace A/B round 2 (2026-10-31, user: "do 1 then 2"): train am-glimmer-ab-a2 on serv-19 once the cluster has pushed
# the pooled round-1 + round-2 own tier (ab_score.sbatch TAG=a2 PUSH=1 -> amvlm/ab/tier_a2/TIER_READY). The cluster pulls
# the final after amvlm/logs/am-glimmer-ab-a2.TRAIN_DONE (sbatch/ab_pull.sh) for the main-protocol eval.
#   setsid nohup bash amvlm/train_v14/serv19/ab_r2_s19.sh > amvlm/ab/logs/r2.log 2>&1 < /dev/null &
set -uo pipefail
cd /srv/scratch/bimrose2
R=/srv/scratch/bimrose2; L=amvlm/logs; A=amvlm/ab; C=am-glimmer-ab-a2
say() { echo "$(date '+%m-%d %H:%M') $*"; }
say "waiting for $A/tier_a2/TIER_READY"
until [ -f $A/tier_a2/TIER_READY ]; do sleep 300; done
say "tier a2: $(tr -d '\n ' < $A/tier_a2/summary.json | cut -c1-600)"
say "train $C"
DRAWING_VLM_RFT_SHARDS=$R/$A/tier_a2/mix CFG=$C GPUS=0,1,2,3,4,5,6,7 bash amvlm/train_v14/serv19/am_train.sh > $L/$C.log 2>&1
until [ -f $L/$C.TRAIN_DONE ]; do
  grep -q "train exit [1-9]\|SMOKE FAILED" $L/$C.log 2>/dev/null && { say "$C failed: $(tail -2 $L/$C.log)"; exit 1; }
  sleep 300; done
[ -f amvlm/runs/$C/final/model.safetensors.index.json ] || { say "$C: no final"; exit 1; }
say "AB R2 DONE"
