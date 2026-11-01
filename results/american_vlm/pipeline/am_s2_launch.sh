#!/bin/bash
# American-VLM visual repair (2026-10-28), serv-19 side of the S2 repair chains for Muse Glimmer (fn_s2_launch.sh with the
# repairer on serv-05). Starts = glftpf main-protocol K=8 vote -> top-3 distinct (make_vote_picks.py) -> 3 chains, bench B
# blocks before synthetic; vr_serve protocol unchanged (K=16, 6 rounds, margin 0.1, 6000 tok, T 0.7). No verifier (user
# 2026-10-27). Waits for serv-05's RP_SERVERS_UP (am_rp_serve05.sh), holds ssh tunnels serv-19:8851/8852 -> serv-05,
# probes 2 bench-B parts x 1 round (stops if no repair executes), then NR block runners (am_runner.sh, nice 10, cores
# 96-343; GPUs and cores 0-95 belong to Glimmer GRPO and its evals). ccc0442 runners join via am_chains_c442.sbatch.
#   setsid nohup bash /srv/scratch/bimrose2/glpipe/am_s2_launch.sh > /srv/scratch/bimrose2/glpipe/logs/s2_launch.log 2>&1 < /dev/null &
set -uo pipefail
S=/srv/scratch/bimrose2; R=$S/glpipe; cd $R; mkdir -p logs out done mine locks failed claims
NR=${NR:-10}; W=${W:-12}; H5=wpk-serv-05.mechse.illinois.edu; PORTS="8851 8852"
say() { echo "$(date '+%m-%d %H:%M') $*"; }
say "waiting for the Glimmer repairer servers on serv-05"
until timeout 60 ssh -o BatchMode=yes $H5 "test -f $S/amvlm/logs/RP_SERVERS_UP"; do sleep 120; done
tunnel() { ssh -o BatchMode=yes -o ServerAliveInterval=30 -o ExitOnForwardFailure=yes -N -L $1:127.0.0.1:$1 $H5 \
  > /dev/null 2>> logs/tunnel.log < /dev/null & echo $!; }
declare -A TP
keep() { local p; for p in $PORTS; do
  if [ -z "${TP[$p]:-}" ] || ! kill -0 ${TP[$p]} 2>/dev/null; then TP[$p]=$(tunnel $p); say "tunnel :$p (pid ${TP[$p]})"; fi; done; }
keep; sleep 15
for p in $PORTS; do curl -sf -m 10 127.0.0.1:$p/health >/dev/null || { say "tunnel :$p unhealthy"; exit 1; }; done
printf 'http://127.0.0.1:8851/v1\nhttp://127.0.0.1:8852/v1\n' > urls_s19.txt   # runners pick a server per block
source host_s19.env
$PY $VRS --bench $BENCH_B --picks blocks/glS2_benchb_c1.b00.json --base-url http://127.0.0.1:8851/v1 --model $MODEL --k 4 \
  --rounds 1 --margin 0.1 --max-tokens 6000 --workers 2 --limit 2 --py $PY --rpy $RPY --script-dir $SD --out logs/probe.jsonl \
  > logs/probe.log 2>&1
python3 - <<'EOF' || { say "probe: no executing repair -> stop"; exit 1; }
import json, sys
rs = [json.loads(l) for l in open("/srv/scratch/bimrose2/glpipe/logs/probe.jsonl")]
d = [x for r in rs for x in r["draws"]]
print("probe:", len(rs), "parts,", len(d), "distinct draws,", sum(x["exec"] for x in d), "exec; start iou",
      [round(r["hist"][0]["iou"], 3) for r in rs], "draw iou", [round(x["iou"], 3) for x in d])
sys.exit(0 if any(x["exec"] for x in d) else 1)
EOF
touch SERVERS_UP
for r in $(seq 1 $NR); do
  port=$([ $((r % 2)) = 1 ] && echo 8851 || echo 8852)
  setsid nohup nice -n 10 taskset -c ${CORES:-96-343} bash $R/am_runner.sh $R/host_s19.env http://127.0.0.1:$port/v1 $W s19r$r \
    > logs/runner_s19_r$r.log 2>&1 < /dev/null &
  say "runner $r pid $! -> :$port"; sleep 20
done
say "S2 LAUNCHED"
while pgrep -u $USER -f "am_runner.sh $R/host_s19.env" >/dev/null; do keep; sleep 30; done   # tunnels live while runners do
say "S2 RUNNERS DONE (done $(ls done | wc -l), failed $(ls failed | wc -l))"
