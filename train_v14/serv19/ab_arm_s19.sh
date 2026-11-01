#!/bin/bash
# Kimi-trace A/B (2026-10-29): arm ARM end to end on serv-19 after its round 0 (am_train.sh am-glimmer-ab-<arm>0):
#   1. sample the round-0 final (ab_sample.sh, 8 GPUs)          -> amvlm/ab/gen_<arm>
#   2. wait for the own tier (cluster ab_score.sbatch SRC=s19 scores + packs it and pushes amvlm/ab/tier_<arm>)
#   3. round 1: am_train.sh am-glimmer-ab-<arm>1 on the mix     -> amvlm/runs/am-glimmer-ab-<arm>1/final
#   4. main-protocol eval of the round-1 final (eval_nemo.sh: real-144 / synthetic / bench B, K=8, 2,400 tokens) on 3
#      single-GPU servers, one bench each -> amvlm/ab/eval/<bench>_ab<arm>1; scored on ccc0442 by nemo_score.sbatch
#   ARM=b setsid nohup bash amvlm/train_v14/serv19/ab_arm_s19.sh > amvlm/ab/logs/arm_b.log 2>&1 < /dev/null &
set -uo pipefail
cd /srv/scratch/bimrose2
R=/srv/scratch/bimrose2; ARM=${ARM:?}; L=amvlm/logs; A=amvlm/ab; mkdir -p $A/logs $A/eval
say() { echo "$(date '+%m-%d %H:%M') $*"; }
say "waiting for round 0 (am-glimmer-ab-${ARM}0)"
until [ -f $L/am-glimmer-ab-${ARM}0.TRAIN_DONE ]; do
  grep -q "train exit [1-9]\|SMOKE FAILED" $L/am-glimmer-ab-${ARM}0.log 2>/dev/null && { say "round 0 failed: $(tail -2 $L/am-glimmer-ab-${ARM}0.log)"; exit 1; }
  sleep 300; done
[ -f amvlm/runs/am-glimmer-ab-${ARM}0/final/model.safetensors.index.json ] || { say "no round-0 final"; exit 1; }
say "1. sampling"
ARM=$ARM HOST=s19 bash amvlm/train_v14/serv19/ab_sample.sh > $A/logs/sample_$ARM.log 2>&1
say "sampling: $(tail -1 $A/logs/sample_$ARM.log)"
say "2. waiting for $A/tier_$ARM/TIER_READY"
until [ -f $A/tier_$ARM/TIER_READY ]; do sleep 300; done
say "tier: $(cat $A/tier_$ARM/summary.json | tr -d '\n ' | cut -c1-400)"
say "3. round 1"
DRAWING_VLM_RFT_SHARDS=$R/$A/tier_$ARM/mix CFG=am-glimmer-ab-${ARM}1 GPUS=0,1,2,3,4,5,6,7 bash amvlm/train_v14/serv19/am_train.sh \
  > $L/am-glimmer-ab-${ARM}1.log 2>&1
[ -f $L/am-glimmer-ab-${ARM}1.TRAIN_DONE ] || { say "round 1 failed: $(tail -2 $L/am-glimmer-ab-${ARM}1.log)"; exit 1; }
say "4. eval"
case $ARM in a) TPL=$R/american_vlm/templates/glftpf.jinja;; b) TPL=$R/american_vlm/templates/glft.jinja;; esac
SP=(); i=0
for b in real full benchb; do
  port=$((8960 + i))
  MODEL=$R/amvlm/runs/am-glimmer-ab-${ARM}1/final NAME=ab GPUS=$i TP=1 PORT=$port RPARSER=$([ $ARM = a ] && echo muse_glimmer) SEQS=128 GMU=0.88 \
    VLLM_EXTRA="--chat-template $TPL" setsid bash amvlm/train_v14/serv19/run_vllm_any_serv19.sh > $A/logs/vllm_eval_$port.log 2>&1 < /dev/null &
  SP+=($!); i=$((i + 1)); sleep 20
done
trap 'for p in "${SP[@]}"; do kill -TERM -- -$p 2>/dev/null; done' EXIT
EP=(); i=0
for b in real full benchb; do
  port=$((8960 + i)); i=$((i + 1))
  ( for t in $(seq 1 240); do curl -s -m 5 http://127.0.0.1:$port/health >/dev/null && break; sleep 15; done
    NAME=ab TAG=ab${ARM}1 PORT=$port MTOK=2400 WORKERS=16 OUT=$A/eval BENCHES=$b bash nemotron/eval_nemo.sh ) > $A/logs/eval_${b}_ab${ARM}1.log 2>&1 &
  EP+=($!)
done
wait "${EP[@]}"
say "AB ARM DONE $ARM: $(ls $A/eval/*_ab${ARM}1.GEN_DONE 2>/dev/null | wc -l)/3 benches generated"
