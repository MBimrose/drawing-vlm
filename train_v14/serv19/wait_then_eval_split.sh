#!/usr/bin/env bash
# Detached watcher (login node): when <run> finishes training on serv-04 and its final exists,
# run the split evaluation chain. Survives a lost interactive session.
#   setsid nohup bash wait_then_eval_split.sh <run> > logs/bo8/<run>_chain.log 2>&1 &
RUN=${1:?run}; DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; S04=wpk-serv-04.mechse.illinois.edu
until timeout 30 ssh -o BatchMode=yes $S04 "grep -q 'TRAIN EXIT' /srv/scratch/bimrose2/logs/${RUN}_serv04.log 2>/dev/null"; do sleep 900; done
echo "$(date) training ended: $(timeout 30 ssh -o BatchMode=yes $S04 "grep 'TRAIN EXIT' /srv/scratch/bimrose2/logs/${RUN}_serv04.log | tail -1")"
if timeout 30 ssh -o BatchMode=yes $S04 "[ -d /srv/scratch/bimrose2/runs/$RUN/final ]"; then
  bash $DV/train_v14/serv19/eval_run_split.sh $RUN 8
else
  echo "$(date) no final checkpoint for $RUN; chain not run"
fi
echo "$(date) CHAIN EXIT"
