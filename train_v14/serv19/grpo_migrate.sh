#!/bin/bash
# Move a cluster GRPO arm onto serv-20 (2026-10-08: the H200 nodes ccc0451/0474/0475 go back to another user on Oct 9).
# Stops a finished/low-value serv-20 arm (its trainer exits -> its launcher kills its vLLM server), then resumes <name>
# from its newest mirrored adapter on the freed GPU/port with grpo_vllm_arm.sh (fresh vLLM + trainer).
#   bash train_v14/serv19/grpo_migrate.sh <name> <stop_arm|-> <gpu> <port> [grpo_round.py args, serv-20 paths]
set -uo pipefail
cd /srv/scratch/bimrose2
name=${1:?name}; stop=${2:?stop arm or -}; gpu=${3:?gpu}; port=${4:?port}; shift 4
log=logs/grpo_v_$name.migrate.log
echo "$(date '+%m-%d %H:%M') migrate $name -> GPU $gpu :$port (stopping $stop)" >> $log
if [ "$stop" != "-" ]; then
  tp=$(pgrep -u bimrose2 -f "grpo_round[.]py .*--out runs/grpo_v_$stop( |$)" | head -1)
  if [ -n "$tp" ]; then
    kill $tp; while kill -0 $tp 2>/dev/null; do sleep 2; done
    echo "$(date '+%m-%d %H:%M') stopped by hand for $name (H200 nodes returned)" >> logs/grpo_v_$stop.log
  fi
fi
for i in $(seq 1 60); do curl -s -m 3 http://127.0.0.1:$port/health >/dev/null || break; sleep 10; done   # old vLLM gone
N=$(ls -d runs/grpo_v_$name/adapter_step* 2>/dev/null | sed 's/.*adapter_step//' | sort -n | tail -1)
[ -n "$N" ] || { echo "no adapter for $name" >> $log; exit 1; }
echo "$(date '+%m-%d %H:%M') resuming $name from step $N" >> $log
OMP_NUM_THREADS=4 setsid nohup bash train_v14/serv19/grpo_vllm_arm.sh $name $gpu $port --steps 300 "$@" \
  --adapter runs/grpo_v_$name/adapter_step$N --start-step $N --save-every 10 \
  > logs/grpo_v_$name.launch.log 2>&1 < /dev/null &
echo "$(date '+%m-%d %H:%M') launched (pid $!)" >> $log
