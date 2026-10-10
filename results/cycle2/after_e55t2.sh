#!/bin/bash
# serv-20: data-vs-compounding arm. When the fresh-LoRA tier-2 SFT (e55_tier2_fresh) ends: copy the adapter to
# runs/grpo_v_e55_t2/adapter_step20 (daemon naming) + ARMS, then RL it to s60+ with the stabilised recipe = rft2_raw's args.
cd /srv/scratch/bimrose2; F=runs/e55_tier2_fresh/final
until [ -f $F/adapter_model.safetensors ] && grep -q "TRAIN DONE" cycle2/logs/sft_e55t2.driver; do sleep 60; done
grep -q "TRAIN DONE 0" cycle2/logs/sft_e55t2.driver || { echo "SFT failed"; exit 1; }
mkdir -p runs/grpo_v_e55_t2/adapter_step20 && cp $F/adapter_model.safetensors $F/adapter_config.json runs/grpo_v_e55_t2/adapter_step20/
O=results/grpo_eval; cp $O/ARMS $O/ARMS.bak_e55t2; echo "e55_t2 e55_t2_rl $(cat $O/ARMS.bak_e55t2)" > $O/ARMS
echo "$(date) e55_t2 registered"
for i in $(seq 1 30); do n=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i 2); [ $n -lt 2000 ] && break; sleep 30; done
P2B=fp/h6/rft_corpus4,mech_benchmarks/rft_corpus2_dw423,fp/h6/train_bench,mech_benchmarks/rft_realpool_v2
P2K=fp/h6/real4_hard_keys.txt,fp/h6/c2_hard_keys.txt,fp/h6/fam_hard_keys.txt,fp/h6/realpool2_hard_4500.txt
taskset -c 96-119 bash train_v14/serv19/grpo_vllm_arm.sh e55_t2_rl 2 8444 --bench $P2B --keys $P2K --minibatches 4 --scale-logits \
  --adv batchstd --temperature 1.0 --top-p 1.0 --ent-coef 0.1 --ent-target 0.1829 --ent-max 0.35 --lr 1e-5 --guard 0.85 --guard-abs 0.9 \
  --save-every 10 --steps 130 --kl-beta 0 --train-raw --adapter $F --start-step 0
echo "$(date) e55_t2_rl exited"
