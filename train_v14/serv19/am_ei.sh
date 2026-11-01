#!/bin/bash
# American-VLM expert-iteration round for Muse Glimmer (2026-10-28; Flash-Next fn_ei.sh), serv-19 GPUs 0-3. After gl1
# has ended and its step is picked (amvlm/grpo/GL1_BEST, chosen on real-144 + synthetic only):
#   1. SFT am-glimmer-rft2 (configs/am-glimmer-rft2.yaml): gl1's adapter warm-started, cycle-2 mix, 955 x 16 rows, FSDP2 x4
#   2. RL glei = the 27B's rft2_rl: lr 1e-5, entropy floor pinned to gl1's auto target (0.1694), pool2 = the old hard pool
#      + realpool2_hard_4500, 60 steps, adapters every 10; rollouts vLLM TP2 (GPUs 0,1), trainer on GPUs 2,3 (am_grpo_arm.sh)
#   3. main-protocol evals of glei s20 / s40 / s60 on real / full / benchb (am_eval_grpo.sh, two TP2 servers, GPUs 0-3)
#   setsid nohup bash amvlm/train_v14/serv19/am_ei.sh > amvlm/grpo/logs/am_ei.log 2>&1 < /dev/null &
set -uo pipefail
cd /srv/scratch/bimrose2
say() { echo "$(date '+%m-%d %H:%M') $*"; }
fail() { say "FAILED: $*"; touch amvlm/grpo/EI_FAILED; exit 1; }
G=amvlm/grpo; T=amvlm/train_v14
say "waiting for the gl1 pick ($G/GL1_BEST)"
until [ -s $G/GL1_BEST ] && grep -q "trainer exit" $G/logs/arm_gl1.log 2>/dev/null; do sleep 120; done
BEST=$(tr -dc 0-9 < $G/GL1_BEST); AD=$(readlink -f $G/runs/gl1/adapter_step$BEST)
[ -f $AD/adapter_model.safetensors ] || fail "no adapter $AD"
for i in $(seq 1 60); do
  busy=0; for g in 0 1 2 3; do used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $g); lim=2000; [ $g = 0 ] && lim=3500; [ "$used" -lt $lim ] || busy=1; done
  [ $busy = 0 ] && break; sleep 30
done
[ $busy = 0 ] || fail "GPUs 0-3 busy: $(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader | tr '\n' ' ')"

# 1. SFT
R=amvlm/runs/am-glimmer-rft2
if [ ! -f $R/final/adapter_model.safetensors ]; then
  sed "s#GL1_BEST_ADAPTER#$AD#" $T/configs/am-glimmer-rft2.yaml > $T/configs/am-glimmer-rft2.run.yaml
  ( source $T/serv19/am_env.sh
    export DRAWING_VLM_RFT_SHARDS=/srv/scratch/bimrose2/cycle2/mix TRAIN_VENV=/srv/scratch/bimrose2/.venv
    export CUDA_VISIBLE_DEVICES=0,1,2,3 OMP_NUM_THREADS=8 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
    say "SFT am-glimmer-rft2 from gl1 s$BEST ($AD), RFT tier $(ls $DRAWING_VLM_RFT_SHARDS | wc -l) shards"
    exec taskset -c ${CORES:-0-95} bash $T/run.sh $T/configs/am-glimmer-rft2.run.yaml ) > $G/logs/train_am_rft2.log 2>&1
  say "SFT exit $?"
fi
[ -f $R/final/adapter_model.safetensors ] || fail "no SFT adapter: $(tail -3 $G/logs/train_am_rft2.log)"

# 2. RL
if ! grep -q "trainer exit" $G/logs/arm_glei.log 2>/dev/null; then
  say "RL glei from $R/final"
  VGPUS=0,1 TGPUS=2,3 PORT=8762 CORES=0-95 bash $T/serv19/am_grpo_arm.sh glei \
    --bench fp/h6/rft_corpus4,mech_benchmarks/rft_corpus2_dw423,fp/h6/train_bench,mech_benchmarks/rft_realpool_v2 \
    --keys fp/h6/real4_hard_keys.txt,fp/h6/c2_hard_keys.txt,fp/h6/fam_hard_keys.txt,fp/h6/realpool2_hard_4500.txt \
    --steps 60 --lr 1e-5 --ent-target 0.1694 --adapter $(readlink -f $R/final) --start-step 0 > $G/logs/arm_glei.log 2>&1
fi
say "RL: $(tail -1 $G/logs/arm_glei.log) | $(grep -c '^{' $G/runs/glei/round_log.jsonl 2>/dev/null) steps logged"

# 3. evals (each server waits on its adapters; no Gemma wait: the marker already exists)
RUN=glei STEPS="20 40" GPUS=0,1 PORT=8772 bash $T/serv19/am_eval_grpo.sh > $G/logs/eval_glei_a.log 2>&1 &
E1=$!
RUN=glei STEPS="60" GPUS=2,3 PORT=8773 bash $T/serv19/am_eval_grpo.sh > $G/logs/eval_glei_b.log 2>&1 &
E2=$!
wait $E1 $E2
touch $G/EI_DONE
say "EI DONE"
