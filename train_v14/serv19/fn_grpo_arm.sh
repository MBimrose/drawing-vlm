#!/bin/bash
# Flash-Next 180B GRPO on serv-19 (2026-10-19; the 27B's grpo_vllm_arm.sh scaled to two 4-GPU halves): a LoRA-enabled
# vLLM rollout server (TP4, GPUs $VGPUS) + the HF/peft trainer (geom/grpo_round.py, model spread over GPUs $TGPUS by
# load_model's balanced device map, n-gram table on CPU). Each step the trainer saves its adapter and hot-loads it
# (load_lora_adapter), so rollouts stay on-policy. Code = fn55/train_v14 (cluster snapshot incl. geom/).
#   POLICY=<hf dir> bash train_v14/serv19/fn_grpo_arm.sh <name> [grpo_round.py args; later ones win]
set -uo pipefail
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4
cd /srv/scratch/bimrose2
name=${1:?name}; shift
POLICY=${POLICY:?hf dir of the SFT policy}; VGPUS=${VGPUS:-0,1,2,3}; TGPUS=${TGPUS:-4,5,6,7}; PORT=${PORT:-8750}
mkdir -p runs/fn_grpo_$name fn55/logs tmp
export VLLM_ALLOW_RUNTIME_LORA_UPDATING=True APPTAINERENV_VLLM_ALLOW_RUNTIME_LORA_UPDATING=True
MODEL=$POLICY NAME=fnpol GPUS=$VGPUS TP=4 PORT=$PORT SEQS=${SEQS:-256} GMU=${GMU:-0.85} \
  VLLM_EXTRA="--enable-lora --max-lora-rank 64 --max-loras 2" \
  setsid nohup bash train_v14/serv19/run_vllm_qwen_serv19.sh > fn55/logs/vllm-fn_grpo_$name.log 2>&1 < /dev/null &
VPID=$!
echo "$(date '+%m-%d %H:%M') vLLM for $name on GPUs $VGPUS :$PORT (pid $VPID)"
ok=0; for i in $(seq 1 240); do curl -s -m 5 http://127.0.0.1:$PORT/health >/dev/null && { ok=1; break; }; sleep 15; done
[ $ok = 1 ] || { echo "vLLM never ready"; tail -20 fn55/logs/vllm-fn_grpo_$name.log; kill -- -$VPID; exit 2; }
FN_LORA='model\.language_model\.layers\.\d+\.(self_attn\.(q|k|v|o)_proj|linear_attn\.(in_proj_qkv|in_proj_z|in_proj_a|in_proj_b|out_proj)|mlp\.shared_expert\.(gate|up|down)_proj)'
COMMON=(--run e59-flashnext-e55recipe --model-base /srv/scratch/bimrose2/models/Qwen3.8-Flash-Next --ckpt $POLICY
  --lora-targets "$FN_LORA"
  --bench fp/h6/rft_corpus4,mech_benchmarks/rft_corpus2_dw423,fp/h6/train_bench
  --keys fp/h6/real4_hard_keys.txt,fp/h6/c2_hard_keys.txt,fp/h6/fam_hard_keys.txt
  --n-parts 16 --g 8 --steps 200 --lr 2e-5 --kl-beta 0 --minibatches 4 --scale-logits --adv batchstd
  --temperature 1.0 --top-p 1.0 --guard 0.6 --ent-coef 0.1 --ent-max 0.35
  --train-batch ${TB:-4} --score-workers 48 --score-timeouts --save-every 10 --rollout-url http://127.0.0.1:$PORT/v1)
CUDA_VISIBLE_DEVICES=$TGPUS PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True FLASHNEXT_PLE_DIR=/dev/shm/flashnext_ple \
  taskset -c ${CORES:-0-95} .venv/bin/python fn55/train_v14/geom/grpo_round.py "${COMMON[@]}" "$@" --out runs/fn_grpo_$name \
  > fn55/logs/fn_grpo_$name.log 2>&1 < /dev/null
echo "$(date '+%m-%d %H:%M') trainer exit $? for $name"
kill -TERM -- -$VPID 2>/dev/null
