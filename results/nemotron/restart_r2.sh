#!/bin/bash
# Warm restart of the Nemotron full SFT (2026-10-16, serv-19). The run slowed from 18 to 35-55 s/step; restart it
# from its newest best_model with the lean_sync + StepTimer build (configs/nemo-fullft-r2.yaml).
# Waits for the first val eval after launch that is a NEW BEST (its gather-save has finished when the
# "[eval] ... new best" line prints); a non-improving eval leaves the run alone and waits for the next one.
# Then: stop post_sft.sh + the training process group, finalize best_model (base MTP head + router buffers),
# install the staged code, launch r2 from that step, and start the r2 post-training driver.
#   setsid nohup bash nemotron/restart_r2.sh > nemotron/logs/restart_r2.log 2>&1 < /dev/null &
set -uo pipefail
cd /srv/scratch/bimrose2
L=nemotron/logs/nemo-fullft.log; R=nemotron/runs/nemo-fullft; B=models/Nemotron-3.5-Super-VL-120B-A12B-BF16
TRAIN_PGID=3828982; POST_PID=3904697; STAGE=nemotron/train_v14_r2_stage
say() { echo "$(date '+%m-%d %H:%M') $*"; }
# only an eval that lands after this script starts counts (best_model always holds the newest best)
LAST=$(grep -E "^\[eval\] step [0-9]+ " $L | tail -1 | awk '{print $3}'); LAST=${LAST:-0}
say "waiting for the first new-best eval after step $LAST"
S=""
while [ -z "$S" ]; do
  grep -q "TRAIN DONE" $L && { say "old run ended on its own - nothing to restart"; exit 1; }
  S=$(grep -E "^\[eval\] step [0-9]+ val/loss=.*new best" $L | awk '{print $3}' | awk -v l=$LAST '$1>l' | head -1)
  [ -z "$S" ] && sleep 60
done
say "new best at step $S: $(grep -E "^\[eval\] step $S " $L)"
kill $POST_PID 2>/dev/null && say "stopped post_sft.sh ($POST_PID)"
kill -TERM -- -$TRAIN_PGID && say "sent TERM to training pgid $TRAIN_PGID"
for i in $(seq 60); do pgrep -g $TRAIN_PGID >/dev/null || break; sleep 10; done
pgrep -g $TRAIN_PGID >/dev/null && { say "training still alive after 10 min - KILL"; kill -KILL -- -$TRAIN_PGID; sleep 30; }
for i in $(seq 60); do
  busy=0; for g in 0 1 2 3 4 5 6 7; do
    u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $g); lim=2000; [ $g = 0 ] && lim=3500
    [ "$u" -lt $lim ] || busy=1; done
  [ $busy = 0 ] && break; sleep 10
done
[ $busy = 0 ] || { say "GPUs not free after 10 min - stop"; nvidia-smi; exit 1; }
say "GPUs free"
OMP_NUM_THREADS=8 taskset -c 0-15 .venv_nemo/bin/python nemotron/train_v14/geom/nemotron_finalize_ckpt.py --base $B --ckpt $R/best_model \
  > nemotron/logs/finalize_best_s$S.log 2>&1 || { say "finalize FAILED"; tail -5 nemotron/logs/finalize_best_s$S.log; exit 1; }
say "finalized best_model (step $S): $(tail -1 nemotron/logs/finalize_best_s$S.log)"
cp $STAGE/train_sft_v14.py nemotron/train_v14/train_sft_v14.py && cp $STAGE/nemo-fullft-r2.yaml nemotron/train_v14/configs/
cp $STAGE/post_sft_r2.sh nemotron/post_sft_r2.sh
say "installed staged code ($(md5sum nemotron/train_v14/train_sft_v14.py | cut -c1-8))"
DRAWING_VLM_DATA_SEED=44 CORES=0-191 setsid nohup bash nemotron/train_nemo.sh nemotron/train_v14/configs/nemo-fullft-r2.yaml \
  --lr_resume_from_step=$S --max_steps=$((4000 - S)) > nemotron/logs/nemo-fullft-r2.log 2>&1 < /dev/null &
say "launched r2 (pid $!) from step $S, max_steps $((4000 - S)); log nemotron/logs/nemo-fullft-r2.log"
sleep 5
RESUME_STEP=$S setsid nohup bash nemotron/post_sft_r2.sh > nemotron/logs/post_sft_r2.log 2>&1 < /dev/null &
say "post_sft_r2.sh pid $!"
say "RESTART DONE"
