#!/bin/bash
# 2026-10-28 (user-approved relay): once an H200 repair job's servers are healthy, add chain runners on ccc0442 (via
# tcp_relay.py on the node's cluster-internal address) and on serv-19 (via rtunnel_keep.sh: reverse ssh forward
# serv-19:1885x -> node:885x). Same claims dir as the node's own runners.
#   bash am_relay_launch.sh <repair jobid> <node> <model: gemma> <serv-19 pipe dir: gmpipe>
set -uo pipefail
J=$1; N=$2; MODEL=$3; SP=$4; P=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/american_vlm/pipeline
H=wpk-serv-19.mechse.illinois.edu; say() { echo "$(date '+%m-%d %H:%M') $*"; }
until grep -q "servers healthy: 8/8" $P/logs/am-rp-h200-$J.out 2>/dev/null; do
  squeue -h -j $J | grep -q . || { say "job $J gone before its servers came up"; exit 1; }; sleep 120; done
say "job $J servers healthy"
IPN=$(ssh -o BatchMode=yes $N "ip -4 addr | grep -oE 'inet 172\.[0-9.]+' | head -1 | cut -d' ' -f2")
SPEC=""; for i in 1 2 3 4 5 6 7 8; do SPEC="$SPEC 3885$i:127.0.0.1:885$i"; done
ssh -o BatchMode=yes $N "setsid nohup python3 $P/tcp_relay.py $J $IPN $SPEC > $P/logs/relay_${N}_$J.log 2>&1 < /dev/null &
  setsid nohup bash $P/rtunnel_keep.sh $J > $P/logs/rtunnel_${N}_$J.log 2>&1 < /dev/null &"
sleep 20; say "relay: $(cat $P/logs/relay_${N}_$J.log)"
ok=$(ssh -o BatchMode=yes ccc0442 "curl -s -m 10 -o /dev/null -w '%{http_code}' http://$IPN:38851/health"); say "ccc0442 -> relay health $ok"
[ "$ok" = 200 ] && say "ccc0442 runners: job $(sbatch --parsable --nodelist=ccc0442 --export=ALL,MODEL=$MODEL,RELAY_HOST=$IPN,NR=${NR442:-5},W=12 $P/am_chains_relay.sbatch)"
ok=$(timeout 60 ssh -o BatchMode=yes $H "for i in 1 2 3 4 5 6 7 8; do curl -s -m 10 -o /dev/null -w '%{http_code} ' http://127.0.0.1:1885\$i/health; done; uptime | sed 's/.*load average: //'")
say "serv-19 -> tunnel health / load: $ok"
load=$(echo "$ok" | awk '{print int($9)}')
if [ "$(echo "$ok" | grep -o 200 | wc -l)" -ge 4 ] && [ "${load:-999}" -lt 150 ]; then
  timeout 120 ssh -o BatchMode=yes $H "cd /srv/scratch/bimrose2/$SP; for r in \$(seq 1 ${NR19:-8}); do setsid nohup bash am_runner.sh host_s19.env http://127.0.0.1:18851/v1 12 s19r\$r > logs/runner_s19_r\$r.log 2>&1 < /dev/null & sleep 10; done; ps -u bimrose2 -o args | grep -c '[a]m_runner.sh host_s19.env'"
  say "serv-19 runners launched"
else say "serv-19 runners NOT launched (tunnel or load)"; fi
