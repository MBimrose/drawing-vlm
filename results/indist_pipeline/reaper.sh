#!/bin/bash
# In-dist pipeline (2026-10-14): kill orphaned scorer/renderer children of this run (ppid 1; a vr_serve subprocess.run
# timeout kills render_ext.py but not its pool worker, which then keeps a core busy). Only processes started after
# SINCE (epoch, default 2026-10-14 12:29 = first runner) whose command is render_ext.py / exec_harness.py / iou_once.py.
#   bash reaper.sh [since_epoch]
SINCE=${1:-$(date +%s -d "2026-10-14 12:29")}
while :; do
  now=$(date +%s)
  ps -u $(id -u) -o pid=,ppid=,etimes=,args= | awk '$2==1' | grep -E "render_ext.py|exec_harness.py|iou_once.py" | while read -r pid ppid et rest; do
    st=$((now - et)); [ $st -ge $SINCE ] && [ $et -gt 30 ] && { echo "$(date '+%m-%d %H:%M') reap $pid (age ${et}s) ${rest:0:100}"; kill $pid 2>/dev/null; }
  done
  sleep 60
done
