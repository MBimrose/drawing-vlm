#!/bin/bash
# Glimmer visual repairer on serv-19 GPUs 4-7 (2026-10-28): the 8-H200 run on serv-05 OOMed at step ~155, so the rp3
# recipe trains here on 4 B300 (configs/am-glimmer-rp3recipe-s19.yaml, same effective batch). Then: copy the final to
# serv-05 (am_rp_serve05.sh serves it there on GPUs 0-3 for the S2 chains) and give GPUs 4-7 back to the gl1 checkpoint
# evals (am_eval_grpo.sh lanes, stopped for this run).
#   setsid nohup bash amvlm/train_v14/serv19/am_rp_s19.sh > amvlm/logs/rp_s19.log 2>&1 < /dev/null &
set -uo pipefail
cd /srv/scratch/bimrose2
say() { echo "$(date '+%m-%d %H:%M') $*"; }
H5=wpk-serv-05.mechse.illinois.edu; CFG=am-glimmer-rp3recipe-s19; F=amvlm/runs/am-glimmer-rp3recipe/final
CFG=$CFG GPUS=4,5,6,7 DRAWING_VLM_RFT_SHARDS=/srv/scratch/bimrose2/rft_mix_rp3 bash amvlm/train_v14/serv19/am_train.sh
if [ -f amvlm/logs/$CFG.TRAIN_DONE ] && [ -f $F/config.json ]; then
  ssh -o BatchMode=yes $H5 "mkdir -p /srv/scratch/bimrose2/$F"
  rsync -a $F/ $H5:/srv/scratch/bimrose2/$F/ && ssh -o BatchMode=yes $H5 "touch /srv/scratch/bimrose2/amvlm/logs/am-glimmer-rp3recipe.TRAIN_DONE" \
    && say "repairer copied to serv-05 ($(du -sh $F | cut -f1))" || say "COPY TO SERV-05 FAILED"
else
  say "REPAIRER TRAINING FAILED"
fi
for spec in "40 120 200|4,5|8770|a" "80 160|6,7|8771|b"; do
  IFS='|' read -r st g p x <<< "$spec"
  RUN=gl1 STEPS="$st" GPUS=$g PORT=$p setsid nohup bash amvlm/train_v14/serv19/am_eval_grpo.sh \
    >> amvlm/grpo/logs/eval_gl1_$x.log 2>&1 < /dev/null &
  say "gl1 eval lane $x (steps $st) on GPUs $g: pid $!"
done
