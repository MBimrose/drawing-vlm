#!/bin/bash
# serv-19 (2026-10-26): start the Muse-Glimmer-30B e55-recipe fine-tune once the zero-shot gates are done and GPUs are
# free (GPU 0 keeps the user's ~2.5 GB render server; leave it running).
#   setsid nohup bash amvlm/train_v14/serv19/am_glimmer_after_gates.sh > amvlm/logs/glimmer_chain.log 2>&1 < /dev/null &
cd /srv/scratch/bimrose2
say() { echo "$(date '+%m-%d %H:%M') $*"; }
say "waiting for ZS GATES DONE"
until grep -q "ZS GATES DONE" american_vlm/logs/zs_gates.log 2>/dev/null; do sleep 120; done
for i in $(seq 1 60); do
  busy=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits | awk -F', ' '($1 == 0 && $2 > 4000) || ($1 != 0 && $2 > 2000)' | wc -l)
  [ "$busy" = 0 ] && break; sleep 30
done
[ "$busy" = 0 ] || { say "GPUs still busy: $(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader | tr '\n' ' ')"; exit 1; }
say "GPUs free -> Glimmer smoke + full run"
CFG=am-glimmer-30b-e55recipe bash amvlm/train_v14/serv19/am_train.sh > amvlm/logs/am-glimmer-30b-e55recipe.log 2>&1
say "chain exit $?"
