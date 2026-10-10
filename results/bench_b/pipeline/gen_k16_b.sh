#!/bin/bash
# Bench B full pipeline, stage 1 (serv-20 GPU 7, 2026-10-10): K=16 draws of rft2_rl_s60 on bench B. Same recipe as
# results/cycle2/pipeline/gen_k16_s20.sh (draw 0 greedy + 15 at T 0.7 / top_p 0.95, 2400 tokens, think kept; LoRA merged
# into e55 = runs/merged_bb_rft2_rl_s60, made by premerge.sh exactly as grpo_eval.sh does).
set -uo pipefail
cd /srv/scratch/bimrose2
NAME=rl2s60; GPU=7; PORT=8460; M=/srv/scratch/bimrose2/runs/merged_bb_rft2_rl_s60; O=bench_b/pipeline; mkdir -p $O/logs
export OMP_NUM_THREADS=2
CUDA_VISIBLE_DEVICES=$GPU DP=1 SEQS=256 PORT=$PORT MODEL=$M NAME=$NAME \
  setsid bash train_v14/serv19/run_vllm_e55_serv20.sh > $O/logs/vllm_gen_$NAME.log 2>&1 < /dev/null &
VPID=$!
ok=0; for i in $(seq 1 360); do curl -s -m 5 http://127.0.0.1:$PORT/health >/dev/null && { ok=1; break; }; sleep 15; done
[ $ok = 1 ] || { echo "vLLM never ready"; kill -- -$VPID; exit 1; }
echo "$(date) vLLM up"
.venv/bin/python train_v14/geom/gen_openai_bo.py --bench mech_benchmarks/bench_b --base-url http://127.0.0.1:$PORT/v1 \
  --model $NAME --k 16 --temperature 0.7 --workers 16 --out $O/benchb_k16_$NAME
echo "$(date) gen exit $?"
kill -- -$VPID 2>/dev/null; sleep 20; kill -9 -- -$VPID 2>/dev/null
touch $O/GEN_DONE_$NAME; echo "GEN K16 DONE $NAME $(date)"
