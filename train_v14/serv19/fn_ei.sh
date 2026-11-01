#!/bin/bash
# Flash-Next expert-iteration round (2026-10-22, results/flashnext/PLAN.md stage 3), serv-19 GPUs 0-3 only -- GPUs 4-7 serve
# the Flash-Next repairer to the repair chains meanwhile. After the repairer training (fn55/FNRP_DONE) and the fn1 step pick
# (fn55/FN1_BEST, chosen on real-144 + synthetic):
#   1. SFT fn_rft2 = the 27B's rft2 (configs/fn-rft2.yaml): fn1's adapter warm-started, cycle-2 mix, 955 x 16 rows, FSDP2 x4
#   2. RL fnei = the 27B's rft2_rl (results/cycle2/after_sft.sh): lr 1e-5, T 1.0 scaled logits, top_p 1, batch-std adv,
#      4 minibatches, KL 0, guard 0.6, entropy floor 0.1 pinned to fn1's auto target (0.1536; the 27B pinned rft1_rl2's
#      0.1829), ceiling 0.35, pool2 = the old hard pool + realpool2_hard_4500, 60 steps (the 27B picked s60), adapters every 10;
#      rollouts vLLM TP2 (GPUs 0,1), trainer on GPUs 2,3
#   3. main-protocol evals of fnei s20 / s40 / s60 on real / full / benchb (fn_eval_grpo.sh, two TP2 servers)
#   setsid nohup bash fn55/fn_ei.sh > fn55/logs/fn_ei.log 2>&1 < /dev/null &
set -uo pipefail
cd /srv/scratch/bimrose2
say() { echo "$(date '+%m-%d %H:%M') $*"; }
fail() { say "FAILED: $*"; touch fn55/EI_FAILED; exit 1; }
say "waiting for the repairer (FNRP_DONE) and the fn1 pick (FN1_BEST)"
until [ -f fn55/FNRP_DONE ] && [ -s fn55/FN1_BEST ]; do sleep 120; done
BEST=$(tr -dc 0-9 < fn55/FN1_BEST); AD=$(readlink -f runs/fn_grpo_fn1/adapter_step$BEST)
[ -f $AD/adapter_model.safetensors ] || fail "no adapter $AD"
for i in $(seq 1 60); do
  busy=0; for g in 0 1 2 3; do used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $g); lim=2000; [ $g = 0 ] && lim=3500; [ "$used" -lt $lim ] || busy=1; done
  [ $busy = 0 ] && break; sleep 30
done
[ $busy = 0 ] || fail "GPUs 0-3 busy: $(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader | tr '\n' ' ')"

# 1. SFT
if [ ! -f runs/fn_rft2/final/adapter_model.safetensors ]; then
  sed "s#FN1_BEST_ADAPTER#$AD#" fn55/train_v14/configs/fn-rft2.yaml > fn55/train_v14/configs/fn-rft2.run.yaml
  ( source nemotron/env_nemo19.sh
    export DRAWING_VLM_RFT_SHARDS=/srv/scratch/bimrose2/cycle2/mix TRAIN_VENV=/srv/scratch/bimrose2/.venv FLASHNEXT_PLE_DIR=/dev/shm/flashnext_ple
    bash fn55/train_v14/stage_ple_shm.sh models/Qwen3.8-Flash-Next
    export CUDA_VISIBLE_DEVICES=0,1,2,3 OMP_NUM_THREADS=8 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True; mkdir -p $TRITON_CACHE_DIR
    say "SFT fn_rft2 from fn1 s$BEST ($AD), RFT tier $(ls $DRAWING_VLM_RFT_SHARDS | wc -l) shards"
    exec taskset -c ${CORES:-0-95} bash fn55/train_v14/run.sh fn55/train_v14/configs/fn-rft2.run.yaml ) > fn55/logs/train_fn_rft2.log 2>&1
  say "SFT exit $?"
fi
[ -f runs/fn_rft2/final/adapter_model.safetensors ] || fail "no SFT adapter: $(tail -3 fn55/logs/train_fn_rft2.log)"

# 2. RL
if ! grep -q "trainer exit" fn55/logs/fn_ei_rl.log 2>/dev/null; then
  say "RL fnei from runs/fn_rft2/final"
  VGPUS=0,1 TGPUS=2,3 PORT=8752 CORES=0-95 POLICY=runs/e59-flashnext-e55recipe/final bash train_v14/serv19/fn_grpo_arm.sh fnei \
    --bench fp/h6/rft_corpus4,mech_benchmarks/rft_corpus2_dw423,fp/h6/train_bench,mech_benchmarks/rft_realpool_v2 \
    --keys fp/h6/real4_hard_keys.txt,fp/h6/c2_hard_keys.txt,fp/h6/fam_hard_keys.txt,fp/h6/realpool2_hard_4500.txt \
    --steps 60 --lr 1e-5 --ent-target 0.1536 --adapter $(readlink -f runs/fn_rft2/final) --start-step 0 > fn55/logs/fn_ei_rl.log 2>&1
fi
say "RL: $(tail -1 fn55/logs/fn_ei_rl.log) | $(grep -c '^{' fn55/logs/fn_grpo_fnei.log) steps logged"

# 3. evals (both servers wait on the adapters themselves)
RUN=fnei STEPS="20 40" GPUS=0,1 PORT=8761 bash train_v14/serv19/fn_eval_grpo.sh > fn55/logs/eval_grpo_fnei_a.log 2>&1 &
E1=$!
RUN=fnei STEPS="60" GPUS=2,3 PORT=8762 bash train_v14/serv19/fn_eval_grpo.sh > fn55/logs/eval_grpo_fnei_b.log 2>&1 &
E2=$!
wait $E1 $E2
touch fn55/EI_DONE
say "EI DONE"
