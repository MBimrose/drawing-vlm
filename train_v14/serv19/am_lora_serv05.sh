#!/bin/bash
# American-VLM paper table, Glimmer LoRA row (2026-10-28): serv-05 GPUs 4-7 train configs/am-glimmer-lora-e55recipe.yaml
# (smoke + 2,500 steps, am_train.sh) once the Glimmer repairer has trained and its servers hold GPUs 0-3
# (am_rp_serve05.sh -> RP_SERVERS_UP). Copies the Glimmer base from serv-19 first.
#   setsid nohup bash amvlm/train_v14/serv19/am_lora_serv05.sh > amvlm/logs/lora_serv05.log 2>&1 < /dev/null &
set -uo pipefail
cd /srv/scratch/bimrose2
say() { echo "$(date '+%m-%d %H:%M') $*"; }
H=wpk-serv-19.mechse.illinois.edu; B=models/Muse-Glimmer-30B
rsync -a $H:/srv/scratch/bimrose2/$B/ $B/ || { say "base copy failed"; exit 1; }
say "base copied ($(du -sh $B | cut -f1))"
until [ -f amvlm/logs/RP_SERVERS_UP ]; do sleep 120; done
until nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits |
      awk -F', ' '$1 >= 4 && $2 > 2000 {busy = 1} END {exit busy}'; do sleep 60; done
say "GPUs 4-7 free -> Glimmer LoRA"
CFG=am-glimmer-lora-e55recipe GPUS=4,5,6,7 TRAIN_VENV=/srv/scratch/bimrose2/.venv_g4 bash amvlm/train_v14/serv19/am_train.sh
say "GLIMMER LORA DONE"
