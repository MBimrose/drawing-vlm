#!/bin/bash
# Resume a running fast-path GRPO arm on serv-20 from its step-N checkpoint in a fresh trainer process
# (2026-10-06: picks up code/env fixes — thread caps, single-thread scoring — without losing the vLLM
# server). Waits for runs/grpo_v_<arm>/adapter_step<N>, SIGKILLs the arm's launcher (so it cannot pkill
# the vLLM server on trainer exit) and the trainer, then relaunches the trainer with the same argv +
# --adapter <ckpt> --start-step N (argparse: later flags win). Log is appended.
#   bash train_v14/serv19/grpo_resume.sh <arm> <N>
set -uo pipefail
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4
cd /srv/scratch/bimrose2
arm=${1:?arm}; N=${2:?step}; ck=runs/grpo_v_$arm/adapter_step$N
tp=$(pgrep -u bimrose2 -f "grpo_round.py .*--out runs/grpo_v_$arm\$" | head -1)
[ -n "$tp" ] || { echo "no trainer for $arm"; exit 1; }
until [ -f $ck/adapter_model.safetensors ]; do sleep 20; done; sleep 30   # let the save finish
lp=$(ps -o ppid= -p $tp | tr -d ' ')
gpu=$(tr '\0' '\n' < /proc/$tp/environ | sed -n 's/^CUDA_VISIBLE_DEVICES=//p')
mapfile -d '' argv < /proc/$tp/cmdline
kill -9 $lp 2>/dev/null; kill $tp; while kill -0 $tp 2>/dev/null; do sleep 2; done
echo "$(date '+%m-%d %H:%M') resuming $arm from $ck on GPU $gpu" >> logs/grpo_v_$arm.log
CUDA_VISIBLE_DEVICES=$gpu PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
  setsid nohup "${argv[@]}" --adapter $ck --start-step $N --save-every 10 >> logs/grpo_v_$arm.log 2>&1 < /dev/null &
echo "resumed $arm at step $N on GPU $gpu (pid $!)"
