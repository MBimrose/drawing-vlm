#!/bin/bash
# Results-table ablations on serv-19 (2026-10-17): one model per lane.
#   NAME=e24 GPUS=1 TP=1 PORT=8701 MODEL=<dir> [ADAPTER=<lora dir> (merged into MODEL first)] [WAIT=<marker file>]
#   [WAIT2="<more markers>"] [WAIT_SERVE="<markers checked after the merge, before serving>"] [BENCHES="real benchb full"] setsid bash abl/abl_lane.sh > abl/logs/lane_<name>.log 2>&1 &
# Serve (run_vllm_qwen_serv19.sh) -> nemotron/eval_nemo.sh (K=8: draw 0 greedy + 7 at T 0.7, think, 2400 tok; = grpo_eval)
# into abl/results/<bench>_<name> -> stop the server. Scoring: nemo_score.sbatch on ccc0442 (RDIR=abl/results).
set -uo pipefail
cd /srv/scratch/bimrose2
NAME=${NAME:?}; A=abl; mkdir -p $A/logs $A/results $A/merged
say() { echo "$(date '+%m-%d %H:%M') $*"; }
[ -n "${WAIT:-}" ] && { say "waiting for $WAIT"; until [ -f $WAIT ]; do sleep 60; done; }
for w in ${WAIT2:-}; do say "waiting for $w"; until [ -f $w ]; do sleep 60; done; done
M=$MODEL
if [ -n "${ADAPTER:-}" ]; then
  M=$A/merged/$NAME
  if [ ! -f $M/config.json ]; then
    say "merging $ADAPTER into $MODEL -> $M"
    CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=16 taskset -c ${MCORES:-100-131} .venv/bin/python train_v14/geom/merge_grpo_lora.py \
      --ckpt $MODEL --adapter $ADAPTER --out $M --model-base $MODEL > $A/logs/merge_$NAME.log 2>&1 \
      || { say "MERGE FAILED"; tail -5 $A/logs/merge_$NAME.log; exit 1; }
  fi
fi
M=$(readlink -f $M)
for w in ${WAIT_SERVE:-}; do say "merged; waiting for $w before serving"; until [ -f $w ]; do sleep 60; done; done
say "serving $NAME ($M) on GPUs $GPUS TP ${TP:-1} :$PORT"
MODEL=$M NAME=$NAME GPUS=$GPUS TP=${TP:-1} PORT=$PORT setsid bash train_v14/serv19/run_vllm_qwen_serv19.sh > $A/logs/vllm_$NAME.log 2>&1 < /dev/null &
VPID=$!
ok=0; for i in $(seq 240); do curl -s -m 5 http://127.0.0.1:$PORT/health >/dev/null && { ok=1; break; }; sleep 15; done
[ $ok = 1 ] || { say "vLLM never ready"; tail -20 $A/logs/vllm_$NAME.log; kill -- -$VPID; exit 1; }
say "server up"
NAME=$NAME TAG=$NAME PORT=$PORT MTOK=2400 WORKERS=${WORKERS:-16} OUT=$A/results BENCHES="${BENCHES:-real benchb full}" \
  bash nemotron/eval_nemo.sh > $A/logs/eval_$NAME.log 2>&1
say "$(tail -1 $A/logs/eval_$NAME.log)"
kill -TERM -- -$VPID 2>/dev/null; sleep 30
touch $A/LANE_DONE_$NAME; say "LANE DONE $NAME"
