#!/usr/bin/env bash
# 2026-10-07: extend dsgrpo2 (serv-19 GPUs 4-7) from 8 to ROUNDS rounds without restarting it: wait for the running driver
# to finish its round 8 (u8 eval), then resume the same loop with START=8 (the u8 eval is already complete -> the
# resumable episode client skips it; u8's merged checkpoint is kept by the driver). Then run the follow-up (if given).
#   (serv-20) setsid nohup bash dsv41_grpo2_extend.sh [ROUNDS] [followup script] > /dev/null 2>&1 &
SDV=/srv/scratch/bimrose2; RUN=$SDV/grpo_ds/dsgrpo2; ROUNDS=${1:-16}; FOLLOW=${2:-}
PID=$(cat $RUN/driver.pid)
while kill -0 $PID 2>/dev/null; do sleep 120; done
if tail -n 3 $RUN/loop.log | grep -q "=== finished\|=== loop exit"; then
  echo "$(date '+%m-%d %H:%M:%S') EXTEND: resuming dsgrpo2 at round 8 -> $ROUNDS" >> $RUN/loop.log
  NAME=dsgrpo2 START=8 ROUNDS=$ROUNDS P=48 K=4 bash $SDV/train_v14/serv19/dsv41_grpo_loop2.sh
else
  echo "$(date '+%m-%d %H:%M:%S') EXTEND: driver did not finish cleanly -> not resuming" >> $RUN/loop.log; exit 1
fi
[ -n "$FOLLOW" ] && tail -n 3 $RUN/loop.log | grep -q "=== finished\|=== loop exit" && bash $FOLLOW
