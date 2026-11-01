#!/bin/bash
# Flash-Next full pipeline (2026-10-22), serv-19 side of the repair chains. After the Flash-Next repairer is trained
# (fn55/FNRP_DONE): two vLLM servers for it (TP2: GPUs 4,5 :8801 and 6,7 :8802; two images per prompt, no-think requests),
# then NR local block runners (fn_runner.sh, nice 10, cores 96-223). The blocks are S2-FN first: e59 K=8 vote -> top-3
# distinct starts (make_vote_picks.py, the bench-B S2 recipe) -> 3 chains, bench B blocks before synthetic. ccc0442 runners join
# through ssh tunnels (fn_chains_c442.sbatch); S1-FN blocks are appended to blocks.txt later. GPUs 0-3 belong to the EI round.
#   setsid nohup bash /srv/scratch/bimrose2/fnpipe/fn_s2_launch.sh > /srv/scratch/bimrose2/fnpipe/logs/s2_launch.log 2>&1 < /dev/null &
set -uo pipefail
S=/srv/scratch/bimrose2; R=$S/fnpipe; cd $R; mkdir -p logs out done mine locks failed claims
NR=${NR:-6}; W=${W:-12}
say() { echo "$(date '+%m-%d %H:%M') $*"; }
say "waiting for the repairer (fn55/FNRP_DONE)"
until [ -f $S/fn55/FNRP_DONE ]; do sleep 120; done
M=$S/runs/fnrp-flashnext-rp3recipe/final
[ -f $M/config.json ] || { say "no repairer model $M"; exit 1; }
for spec in "4,5 8801" "6,7 8802"; do
  set -- $spec
  ( cd $S; MODEL=$M NAME=fnrp GPUS=$1 TP=2 PORT=$2 SEQS=256 GMU=0.88 \
      VLLM_EXTRA='--limit-mm-per-prompt {"image":2,"video":0} --disable-custom-all-reduce' \
      exec setsid nohup bash train_v14/serv19/run_vllm_qwen_serv19.sh > $R/logs/vllm_fnrp_$2.log 2>&1 < /dev/null ) &
  echo $! > $R/vllm_$2.pgid
done
for port in 8801 8802; do
  ok=0; for i in $(seq 1 240); do curl -sf -m 5 127.0.0.1:$port/health >/dev/null && { ok=1; break; }; sleep 15; done
  [ $ok = 1 ] || { say "server :$port never ready: $(tail -3 $R/logs/vllm_fnrp_$port.log)"; exit 1; }
done
printf 'http://127.0.0.1:8801/v1\nhttp://127.0.0.1:8802/v1\n' > $R/urls_s19.txt   # runners pick a server per block
touch $R/SERVERS_UP
say "repairer servers up (:8801 GPUs 4,5; :8802 GPUs 6,7)"
for r in $(seq 1 $NR); do
  port=$([ $((r % 2)) = 1 ] && echo 8801 || echo 8802)
  setsid nohup nice -n 10 taskset -c ${CORES:-96-223} bash $R/fn_runner.sh $R/host_s19.env http://127.0.0.1:$port/v1 $W s19r$r \
    > $R/logs/runner_s19_r$r.log 2>&1 < /dev/null &
  say "runner $r pid $! -> :$port"; sleep 20
done
say "S2 LAUNCHED"
