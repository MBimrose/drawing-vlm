#!/bin/bash
# Gemma 4 31B FT -> eval (2026-10-27): runs on serv-05. Waits for the run's TRAIN_DONE and final/ (HF dir), copies it
# to serv-19, marks it done there, then starts am_eval_ft.sh on serv-19 (tags gmft / gmftpf) once serv-19's GPUs are
# free (GPU 0 holds the user's ~2.5 GB render server).
#   setsid nohup bash amvlm/train_v14/serv19/am_gemma_after_train.sh > amvlm/logs/gemma_after_train.log 2>&1 < /dev/null &
set -uo pipefail
cd /srv/scratch/bimrose2
say() { echo "$(date '+%m-%d %H:%M') $*"; }
RUN=am-gemma4-31b-e55recipe; F=amvlm/runs/$RUN/final; H=wpk-serv-19.mechse.illinois.edu
until [ -f amvlm/logs/$RUN.TRAIN_DONE ] && [ -f $F/config.json ]; do sleep 120; done
say "train done; copying $F ($(du -sh $F | cut -f1)) to serv-19"
ssh -o BatchMode=yes $H "mkdir -p /srv/scratch/bimrose2/amvlm/runs/$RUN /srv/scratch/bimrose2/amvlm/logs"
rsync -a $F/ $H:/srv/scratch/bimrose2/$F/ || { say "rsync failed"; exit 1; }
ssh -o BatchMode=yes $H "touch /srv/scratch/bimrose2/amvlm/logs/$RUN.TRAIN_DONE"
say "copied"
# 2026-10-27: GPUs 0-3 run Glimmer GRPO -> the Gemma eval takes GPUs 4-7 (two servers, PAIRS)
until ssh -o BatchMode=yes $H "nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits" |
      awk -F', ' '$1 >= 4 && $2 > 2000 {busy = 1} END {exit busy}'; do sleep 300; done
say "serv-19 GPUs 4-7 free -> Gemma eval"
ssh -o BatchMode=yes $H "cd /srv/scratch/bimrose2; RUN=$RUN TAG=gmft KIND=gemma PAIRS='4,5 6,7' setsid nohup bash amvlm/train_v14/serv19/am_eval_ft.sh > american_vlm/logs/eval_gmft.log 2>&1 < /dev/null & echo started \$!"
