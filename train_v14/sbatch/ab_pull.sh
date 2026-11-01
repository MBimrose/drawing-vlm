#!/bin/bash
# Kimi-trace A/B (2026-10-29): wait for a serv-19 training run (serv19/ab_serial_s19.sh) to finish and copy its final into
# the cluster mirror at the same path, so srv_exec jobs see it as /srv/scratch/bimrose2/amvlm/runs/<cfg>/final.
#   bash ab_pull.sh am-glimmer-ab-b0
set -uo pipefail
H=wpk-serv-19.mechse.illinois.edu; R=/srv/scratch/bimrose2; M=/projects/illinois/eng/ece/wpk/bimrose2/srvmirror; C=${1:?}
say() { echo "$(date '+%m-%d %H:%M') $*"; }
say "waiting for $C on serv-19"
until timeout 60 ssh -o BatchMode=yes $H "test -f $R/amvlm/logs/$C.TRAIN_DONE"; do
  timeout 60 ssh -o BatchMode=yes $H "grep -q 'train exit [1-9]\|SMOKE FAILED' $R/amvlm/logs/$C.log" 2>/dev/null && { say "$C FAILED on serv-19"; exit 1; }
  sleep 300; done
mkdir -p $M/amvlm/runs/$C
rsync -a $H:$R/amvlm/runs/$C/final $M/amvlm/runs/$C/ || { say "rsync failed"; exit 1; }
[ -f $M/amvlm/runs/$C/final/model.safetensors.index.json ] || { say "no final index"; exit 1; }
say "pulled $C ($(du -sh $M/amvlm/runs/$C/final | cut -f1))"
