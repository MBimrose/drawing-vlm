#!/bin/bash
# Flash-Next pipeline wrap-up on serv-19 (2026-10-22): once the S1 blocks are queued (S1_READY) and every block of blocks.txt
# (S2 + S1) is DONE on some host (claims/<b>/DONE_*), stop the serv-19 runners (STOP_s19; they exit between blocks) and the
# Flash-Next repairer servers (:8801-:8804, by their pgid files), then write FN_DONE -- the DeepSeek chain
# (dsv41_e55_chain.sh) waits for it. The ccc0442 runners are stopped from the cluster side (STOP_c442).
#   setsid nohup bash /srv/scratch/bimrose2/fnpipe/fn_finish.sh > /srv/scratch/bimrose2/fnpipe/logs/finish.log 2>&1 < /dev/null &
set -uo pipefail
R=/srv/scratch/bimrose2/fnpipe; cd $R
say() { echo "$(date '+%m-%d %H:%M') $*"; }
say "waiting for S1_READY"
until [ -f S1_READY ]; do sleep 300; done
while :; do
  n=0; d=0
  for b in $(cat blocks.txt); do n=$((n + 1)); ls claims/$b/DONE_* > /dev/null 2>&1 && d=$((d + 1)); done
  [ $d = $n ] && break
  sleep 600
done
say "all $n blocks done"
touch STOP_s19
for i in $(seq 1 120); do [ "$(pgrep -u bimrose2 -fc "fn_runner.sh $R/host_s19.env")" = 0 ] && break; sleep 30; done
say "serv-19 runners left: $(pgrep -u bimrose2 -fc "fn_runner.sh $R/host_s19.env")"
for port in 8801 8802 8803 8804; do [ -s vllm_$port.pgid ] && kill -TERM -- -$(cat vllm_$port.pgid) 2>/dev/null; done
for i in $(seq 1 60); do
  busy=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '$1 > 6000' | wc -l); [ "$busy" = 0 ] && break; sleep 10
done
touch FN_DONE
say "FN DONE (GPUs busy: $busy)"
