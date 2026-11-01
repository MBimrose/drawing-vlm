#!/bin/bash
# Kimi-trace A/B (2026-10-29): all four training rounds on serv-19, one after another (replaces ab_arm_s19.sh). Arm A's
# round 0 smoke OOMed on the H200s (Glimmer full FT at seq 6144 takes ~145 GB/GPU on the B300s, an H200 has 140), so both
# arms train here on the same hardware and the campus-cluster H200 node does the sampling, scoring and evals:
#   B0 (already running) -> A0 -> B1 (after tier_b) -> A1 (after tier_a)
# The cluster pulls each final once amvlm/logs/<cfg>.TRAIN_DONE exists (sbatch/ab_pull.sh) and pushes the tiers back
# (ab_score.sbatch PUSH=1 -> amvlm/ab/tier_<arm>/TIER_READY).
#   setsid nohup bash amvlm/train_v14/serv19/ab_serial_s19.sh > amvlm/ab/logs/serial.log 2>&1 < /dev/null &
set -uo pipefail
cd /srv/scratch/bimrose2
R=/srv/scratch/bimrose2; L=amvlm/logs; A=amvlm/ab; mkdir -p $A/logs
say() { echo "$(date '+%m-%d %H:%M') $*"; }
wait_done() {   # wait_done <cfg>: until its TRAIN_DONE, failing on a failed run
  until [ -f $L/$1.TRAIN_DONE ]; do
    grep -q "train exit [1-9]\|SMOKE FAILED" $L/$1.log 2>/dev/null && { say "$1 failed: $(tail -2 $L/$1.log)"; exit 1; }
    sleep 300; done
  [ -f amvlm/runs/$1/final/model.safetensors.index.json ] || { say "$1: no final"; exit 1; }
  say "$1 done"
}
train() {   # train <cfg> [rft mix dir]
  say "train $1"
  DRAWING_VLM_RFT_SHARDS=${2:-} CFG=$1 GPUS=0,1,2,3,4,5,6,7 bash amvlm/train_v14/serv19/am_train.sh > $L/$1.log 2>&1
  wait_done $1
}
say "waiting for am-glimmer-ab-b0"; wait_done am-glimmer-ab-b0
train am-glimmer-ab-a0
for arm in b a; do
  say "waiting for $A/tier_$arm/TIER_READY"
  until [ -f $A/tier_$arm/TIER_READY ]; do sleep 300; done
  say "tier $arm: $(tr -d '\n ' < $A/tier_$arm/summary.json | cut -c1-400)"
  train am-glimmer-ab-${arm}1 $R/$A/tier_$arm/mix
done
say "AB SERIAL DONE"
