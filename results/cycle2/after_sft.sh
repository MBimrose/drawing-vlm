#!/bin/bash
# Cycle 2 (serv-20): when the round-2 SFT final adapter exists -> (1) copy it to runs/grpo_v_rft2/adapter_step20 (the eval
# daemon's naming, as rft1 did) and put rft2 + rft2_rl at the front of results/grpo_eval/ARMS (backup ARMS.bak_c2);
# (2) launch RL round 2 = rft2_rl on GPU $RLGPU: best recipe at the mature-adapter lr 1e-5, T 1.0 scaled logits, top_p 1,
# batch-std adv, 4 minibatches, KL 0, guard 0.6, entropy floor coef 0.1 with target pinned 0.1829 (= rft1_rl2) + ceiling
# 0.35, pool2 (old hard pool + realpool2_hard_4500), 300 steps, adapters every 10.
cd /srv/scratch/bimrose2
RLGPU=${RLGPU:-2}; PORT=${PORT:-8440}; F=runs/rft2_from_rl2/final
say() { echo "$(date '+%m-%d %H:%M') $*"; }
until [ -f $F/adapter_model.safetensors ] && grep -q "TRAIN DONE" cycle2/logs/sft_rft2.driver; do sleep 60; done
grep -q "TRAIN DONE 0" cycle2/logs/sft_rft2.driver || { say "SFT failed"; exit 1; }
mkdir -p runs/grpo_v_rft2/adapter_step20 && cp $F/adapter_model.safetensors $F/adapter_config.json runs/grpo_v_rft2/adapter_step20/
O=results/grpo_eval; cp $O/ARMS $O/ARMS.bak_c2
echo "rft2 rft2_rl $(tr ' ' '\n' < $O/ARMS.bak_c2 | grep -vxE 'rft2|rft2_rl' | tr '\n' ' ')" > $O/ARMS
say "rft2 adapter in place; ARMS: $(cat $O/ARMS | cut -c1-80)"
for i in $(seq 1 20); do n=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $RLGPU); [ $n -lt 2000 ] && break; sleep 30; done
say "launching rft2_rl on GPU $RLGPU :$PORT"
taskset -c 264-295 bash train_v14/serv19/grpo_vllm_arm.sh rft2_rl $RLGPU $PORT \
  --bench fp/h6/rft_corpus4,mech_benchmarks/rft_corpus2_dw423,fp/h6/train_bench,mech_benchmarks/rft_realpool_v2 \
  --keys fp/h6/real4_hard_keys.txt,fp/h6/c2_hard_keys.txt,fp/h6/fam_hard_keys.txt,fp/h6/realpool2_hard_4500.txt \
  --steps 300 --minibatches 4 --scale-logits --adv batchstd --temperature 1.0 --top-p 1.0 --kl-beta 0 --guard 0.6 \
  --ent-coef 0.1 --ent-target 0.1829 --ent-max 0.35 --lr 1e-5 --adapter $F --start-step 0
say "rft2_rl trainer exited"
