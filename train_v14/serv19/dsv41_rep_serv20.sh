#!/usr/bin/env bash
# DeepSeek-V4.1-Flash visual-REPAIR LoRA on serv-20 GPUs 0-7 (all 8 B300 since 2026-09-30; 4 GPUs OOMed, one pipeline-split replica), after rp4 frees them.
# Rows = the rp2/rp3 repair tiers ([target sheet, candidate sheet] + REPAIR_PROMPT(code) -> better program), chat mode.
# Step 1: 2-step smoke (Blackwell has never run this training path); step 2: the run.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; SDV=/srv/scratch/bimrose2; S20=wpk-serv-20.mechse.illinois.edu; LOG=$DV/logs/real/dsv41_rep.log
say() { echo "$(date '+%m-%d %H:%M') $*" | tee -a $LOG; }
on() { timeout ${TMO:-180} ssh -o BatchMode=yes $S20 "$@"; }
cd $DV
# (2026-09-29: user paused the rp4 chain -- start immediately)
rsync -a --exclude 'mech/benchmarks/data' --exclude __pycache__ train_v14/ $S20:$SDV/train_v14/
on "pkill -u bimrose2 -f 'vllm serv[e]'"; sleep 20
RUN="cd $SDV; export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 HF_HOME=$SDV/.cache/huggingface PYTHONPATH=$SDV/train_v14:$SDV/train_v14/geom OPENBLAS_NUM_THREADS=1 TRITON_CACHE_DIR=$SDV/.cache/triton_dsv41; .venv_dsv41/bin/python train_v14/geom/dsv41_lora_train.py --model models/DeepSeek-V4.1-Flash --tier dsv41_repair_tier --prompts spike_dsv41/prompts.json --rank 32 --lr 1e-4 --targets '(self_attn\.(q_a_proj|q_b_proj|kv_proj|o_b_proj)|shared_experts\.(gate_proj|up_proj|down_proj))\$' --max-len 4096 --eval-n 0 --last-gpu-headroom 40"
say "smoke"
TMO=10800 on "$RUN --steps 2 --accum 2 --min-layer 20 --out runs/dsv41_rep_smoke > logs/dsv41_rep_smoke.log 2>&1; tail -n 6 logs/dsv41_rep_smoke.log" | tee -a $LOG
on "grep -q 'adapter saved' $SDV/logs/dsv41_rep_smoke.log" || { say "SMOKE FAILED"; exit 1; }
say "training dsv41_rep"
on "setsid nohup bash -c \"$RUN --steps ${STEPS:-500} --accum 8 --min-layer 20 --save-every 100 --out runs/dsv41_rep_r32 > logs/dsv41_rep.log 2>&1; echo TRAIN EXIT \\\$? >> logs/dsv41_rep.log\" > /dev/null 2>&1 < /dev/null & echo started" | tee -a $LOG
