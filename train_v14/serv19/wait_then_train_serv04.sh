#!/usr/bin/env bash
# Detached: wait for the tier/mix shipment and free GPUs on serv-04, then train <config> there and
# run the split evaluation chain when it finishes.
#   setsid nohup bash wait_then_train_serv04.sh <config> <mix dir name> <ship log marker file> &
CFG=${1:?config}; MIX=${2:?mix}; SHIPLOG=${3:?ship log}
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; S04=wpk-serv-04.mechse.illinois.edu
until grep -q "SHIP DONE" $SHIPLOG 2>/dev/null; do sleep 120; done
echo "$(date) shipment complete"
until timeout 30 ssh -o BatchMode=yes $S04 "[ \$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | sort -n | tail -1) -lt 5000 ]"; do
  echo "$(date) serv-04 GPUs busy; waiting"; sleep 600; done
echo "$(date) launching $CFG on serv-04 with mix $MIX"
timeout 300 ssh -o BatchMode=yes $S04 "cd /srv/scratch/bimrose2 && MIX=$MIX bash train_v14/serv19/launch_e58_serv04.sh $CFG"
sleep 120
timeout 60 ssh -o BatchMode=yes $S04 "grep -vE '^\s*$|W0[0-9]|_frames' /srv/scratch/bimrose2/logs/${CFG}_serv04.log | tail -5 | cut -c1-200"
until timeout 30 ssh -o BatchMode=yes $S04 "grep -q 'TRAIN EXIT' /srv/scratch/bimrose2/logs/${CFG}_serv04.log 2>/dev/null"; do sleep 900; done
echo "$(date) training ended: $(timeout 30 ssh -o BatchMode=yes $S04 "grep 'TRAIN EXIT' /srv/scratch/bimrose2/logs/${CFG}_serv04.log | tail -1")"
if timeout 30 ssh -o BatchMode=yes $S04 "[ -d /srv/scratch/bimrose2/runs/$CFG/final ]"; then
  bash $DV/train_v14/serv19/eval_run_split.sh $CFG 8
else
  echo "$(date) no final checkpoint for $CFG"
fi
echo "$(date) CHAIN EXIT"
