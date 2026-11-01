#!/bin/bash
# American-VLM visual repair (2026-10-28), serv-05 side: once the Glimmer repairer (configs/am-glimmer-rp3recipe.yaml) has
# trained, serve it on GPUs 0-3 as two TP2 servers (:8851 GPUs 0,1; :8852 GPUs 2,3), two images per prompt. Served with
# the BASE chat template (generation prompt "<|start|>assistant", as the collator rendered the untraced repair rows, whose
# target is " to=user<|message|>code") and NO reasoning parser: muse_glimmer drops replies that open in to=user, and
# vr_serve takes the last fenced python block of the raw content. GPUs 4-7 stay free (Glimmer LoRA). The chain runners
# live on serv-19 (am_s2_launch.sh) and reach these servers through an ssh tunnel.
#   setsid nohup bash amvlm/train_v14/serv19/am_rp_serve05.sh > amvlm/logs/rp_serve05.log 2>&1 < /dev/null &
set -uo pipefail
cd /srv/scratch/bimrose2
say() { echo "$(date '+%m-%d %H:%M') $*"; }
RUN=${RUN:-am-glimmer-rp3recipe}; M=amvlm/runs/$RUN/final; NAME=${NAME:-glrp}
TEMPLATE=$PWD/models/Muse-Glimmer-30B/chat_template.jinja
until [ -f amvlm/logs/$RUN.TRAIN_DONE ] && [ -f $M/config.json ]; do sleep 120; done
say "repairer trained: $M"
rm -f amvlm/logs/RP_SERVERS_UP
for spec in "0,1 8851" "2,3 8852"; do
  set -- $spec
  MODEL=$PWD/$M NAME=$NAME GPUS=$1 TP=2 PORT=$2 RPARSER= NIMG=2 SEQS=256 GMU=0.88 \
    VLLM_EXTRA="--chat-template $TEMPLATE --disable-custom-all-reduce" \
    setsid nohup bash amvlm/train_v14/serv19/run_vllm_any_serv19.sh > amvlm/logs/vllm_${NAME}_$2.log 2>&1 < /dev/null &
  echo $! > amvlm/logs/vllm_${NAME}_$2.pgid
done
for port in 8851 8852; do
  ok=0; for i in $(seq 1 240); do curl -sf -m 5 127.0.0.1:$port/health >/dev/null && { ok=1; break; }; sleep 15; done
  [ $ok = 1 ] || { say "server :$port never ready: $(tail -3 amvlm/logs/vllm_${NAME}_$port.log)"; exit 1; }
done
touch amvlm/logs/RP_SERVERS_UP
say "repairer servers up (:8851 GPUs 0,1; :8852 GPUs 2,3)"
