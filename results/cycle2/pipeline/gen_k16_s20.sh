#!/bin/bash
# Cycle-2 end-to-end pipeline, stage 1 on serv-20 (2026-10-09): K=16 real-bench draws of a generator checkpoint, same recipe
# as results/pipeline_grpo/gen_k16.sh (draw 0 greedy, T 0.7 / top_p 0.95, 2400 tokens, think kept) but the LoRA merged into
# e55 (grpo_eval.sh path) and served on GPU $GPU (default 1, shared with afm8's 18 GB -> GMU 0.85).
#   setsid nohup bash cycle2/pipeline/gen_k16_s20.sh <adapter dir> <name> > cycle2/pipeline/logs/gen_<name>.log 2>&1 &
set -uo pipefail
cd /srv/scratch/bimrose2
AD=${1:?adapter}; NAME=${2:?name}; GPU=${GPU:-1}; PORT=${PORT:-8460}
E55=/srv/scratch/bimrose2/runs/e55-rft-real-u5-gt-dw423/final; M=runs/merged_pg_$NAME; O=cycle2/pipeline
export OMP_NUM_THREADS=2
[ -f $M/config.json ] || CUDA_VISIBLE_DEVICES= .venv/bin/python train_v14/geom/merge_grpo_lora.py --ckpt $E55 --adapter $AD --out $M \
  --model-base /srv/scratch/bimrose2/models/Qwen3.8-27B > $O/logs/merge_$NAME.log 2>&1 || { echo "merge failed"; exit 1; }
CUDA_VISIBLE_DEVICES=$GPU DP=1 SEQS=256 GMU=0.85 PORT=$PORT MODEL=/srv/scratch/bimrose2/$M NAME=$NAME \
  setsid bash train_v14/serv19/run_vllm_e55_serv20.sh > $O/logs/vllm_gen_$NAME.log 2>&1 < /dev/null &
VPID=$!
ok=0; for i in $(seq 1 160); do curl -s -m 5 http://127.0.0.1:$PORT/health >/dev/null && { ok=1; break; }; sleep 15; done
[ $ok = 1 ] || { echo "vLLM never ready"; kill -- -$VPID; exit 1; }
echo "$(date) vLLM up"
.venv/bin/python train_v14/geom/gen_openai_bo.py --bench mech_benchmarks/ext_bench_dw423_perm --base-url http://127.0.0.1:$PORT/v1 \
  --model $NAME --k 16 --temperature 0.7 --workers 16 --out $O/real_k16_$NAME
echo "$(date) gen exit $?"
kill -- -$VPID 2>/dev/null; sleep 20; kill -9 -- -$VPID 2>/dev/null
touch $O/GEN_DONE_$NAME; echo "GEN K16 DONE $NAME $(date)"
