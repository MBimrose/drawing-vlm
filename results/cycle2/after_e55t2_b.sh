#!/bin/bash
# serv-20: when the e55_t2 SFT frees GPUs 2/0, launch g2_guided_raw on GPU 0 (shares afm8's ~18 GB): identical to g2_guided
# (guided GRPO from rft1_rl2 s120, round-2 banks) + --train-raw -> separates the format blind spot from off-policy injection.
cd /srv/scratch/bimrose2
until grep -q "TRAIN DONE" cycle2/logs/sft_e55t2.driver; do sleep 60; done
sleep 120
for i in $(seq 1 30); do n=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i 0); [ $n -lt 25000 ] && break; sleep 30; done
O=results/grpo_eval; cp $O/ARMS $O/ARMS.bak_g2raw; echo "g2_guided_raw $(cat $O/ARMS.bak_g2raw)" > $O/ARMS
P2B=fp/h6/rft_corpus4,mech_benchmarks/rft_corpus2_dw423,fp/h6/train_bench,mech_benchmarks/rft_realpool_v2; G=cycle2/guided
taskset -c 168-199 bash train_v14/serv19/grpo_vllm_arm.sh g2_guided_raw 0 8445 --bench $P2B,mech_benchmarks/rft_corpus_dw423 \
  --keys $G/keys_c4.txt,$G/keys_c2.txt,fp/h6/fam_hard_keys.txt,$G/keys_rp2.txt,$G/keys_c1.txt \
  --guide-bank $G/bank_c4.json,$G/bank_c2.json,,$G/bank_rp2.json,$G/bank_c1.json --minibatches 4 --scale-logits --adv batchstd \
  --temperature 1.0 --top-p 1.0 --ent-coef 0.1 --ent-target 0.1829 --ent-max 0.35 --lr 1e-5 --guard 0.85 --guard-abs 0.9 \
  --save-every 10 --steps 130 --kl-beta 0 --train-raw --adapter runs/grpo_v_rft1_rl2/adapter_step120 --start-step 0
echo "$(date) g2_guided_raw exited"
