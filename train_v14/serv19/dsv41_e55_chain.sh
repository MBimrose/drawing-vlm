#!/bin/bash
# DeepSeek-V4.1-Flash on the e55 recipe (2026-10-21, user: "queue up deepseek to run after any other experiments with the
# improved training recipe"). serv-19 only; starts when the Flash-Next GRPO run and its checkpoint evals are done.
#   0. tier (CPU, now): build_dsv41_e55_tier.py -- e55's three streams at 60/20/20 with data_v14's filters + e55's aug
#   1. wait: the Flash-Next pipeline is done (fnpipe/FN_DONE; repairer, EI round and both repair systems)
#   2. gates, in parallel: (a) timing smoke, one replica on GPUs 0-3, 10 steps; (b) prompt check: the base model in vLLM
#      on GPUs 4-7, the eval payload's prompt_tokens == the trainer's prompt length (dse55_promptcheck.py)
#   3. train: two data-parallel replicas (GPUs 0-3 / 4-7), LoRA r64 on attention (layers >= 20), lr 1e-4, 16 rows per
#      step, every row in thinking mode (e55's untraced rows: empty reasoning), effort 25; STEPS = BUDGET_H hours at the
#      smoke's s/step, capped by the tier
#   4. BF16-attention merge -> two vLLM servers (TP4+EP: :8200 GPUs 0-3, :8201 GPUs 4-7)
#   5. eval, main-table protocol: gen_openai_bo.py K=8 (draw 0 greedy + 7 at T 0.7 / top_p 0.95), think, 2400 tokens, the
#      e55 prompt, effort 25 -> abl/results/{real,full,benchb}_$NAME (+ .GEN_DONE); scoring on ccc0442 (nemo_score.sbatch)
# Markers: $R/FAILED (stage in the log), $R/DONE. GPU 0 also holds the user's render_server.py: shared, never touched.
#   setsid nohup bash dsv41_e55/code/train_v14/serv19/dsv41_e55_chain.sh > dsv41_e55/logs/chain.log 2>&1 < /dev/null &
set -uo pipefail
S=/srv/scratch/bimrose2; cd $S
R=$S/dsv41_e55; C=$R/code/train_v14; L=$R/logs; mkdir -p $L
NAME=${NAME:-dse55}; BUDGET_H=${BUDGET_H:-48}; NROWS=${NROWS:-256000}; EFFORT=${EFFORT:-25}   # 256k rows = e55's 4000 x 64
M=/scratch/bimrose2/dsv41_ft/$NAME; BASE=$(ls -d /scratch/bimrose2/dsv41_flash/models/models--deepseek-ai--DeepSeek-V4.1-Flash/snapshots/*/ | head -1)
say() { echo "$(date '+%m-%d %H:%M') $*"; }
fail() { say "FAILED: $*"; touch $R/FAILED; exit 1; }
gpu_busy() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '$1 > 6000' | wc -l; }
export HF_HOME=$S/.cache/huggingface PYTHONPATH=$C:$C/geom OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=1 \
  TRITON_CACHE_DIR=$S/.cache/triton_dsv41 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
ARGS="--model models/DeepSeek-V4.1-Flash --think-all --reasoning-effort $EFFORT
 --rank 64 --lr 1e-4 --targets (self_attn\.(q_a_proj|q_b_proj|kv_proj|o_b_proj))\$ --min-layer 20 --max-len 6144 --grad-ckpt
 --last-gpu-headroom 60 --accum 8 --eval-n 0 --seed 43"
TEST=$R/tier_test   # 60-row build of the same streams (build_dsv41_e55_tier.py --n 60): the gates run on it

# 0. tier, in the background (CPU, nice) while the GPUs are still busy
TB=""
if [ ! -f $R/tier/manifest.json ]; then
  say "building tier ($NROWS rows) in the background"
  ( source nemotron/env_nemo19.sh; CUDA_VISIBLE_DEVICES= exec nice -n 19 .venv/bin/python $C/geom/build_dsv41_e55_tier.py \
      --n $NROWS --out $R/tier --workers 12 ) > $L/tier.log 2>&1 &
  TB=$!
fi

# 1. wait for the Flash-Next pipeline (2026-10-22, user: Flash-Next visual repair + GRPO first, then DeepSeek): fnpipe/FN_DONE
#    is written once the last Flash-Next repair chain has finished and its servers are stopped
say "waiting for the Flash-Next pipeline (fnpipe/FN_DONE)"
until [ -f $S/fnpipe/FN_DONE ]; do sleep 300; done
for i in $(seq 1 60); do [ "$(gpu_busy)" = 0 ] && break; sleep 30; done
[ "$(gpu_busy)" = 0 ] || fail "GPUs still busy after fn1: $(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader | tr '\n' ' ')"
say "GPUs free"

# 2. gates
if [ ! -f $R/GATES_PASSED ]; then
  rm -rf $R/smoke
  CUDA_VISIBLE_DEVICES=0,1,2,3 setsid nohup .venv_dsv41/bin/python $C/geom/dsv41_lora_train.py $ARGS --tier $TEST/tier \
    --prompts $TEST/prompts.json --steps 10 --out $R/smoke > $L/smoke.log 2>&1 < /dev/null &
  SM=$!
  MAXLEN=16384 setsid nohup bash $C/serv19/dsv41_ft_serve_serv19.sh $BASE base 8201 4,5,6,7 > $L/serve_base.log 2>&1 < /dev/null &
  VB=$!
  ok=0; for i in $(seq 1 240); do curl -sf -m 5 127.0.0.1:8201/health >/dev/null && { ok=1; break; }; sleep 15; done
  if [ $ok = 1 ]; then
    CUDA_VISIBLE_DEVICES= .venv_dsv41/bin/python $C/geom/dse55_promptcheck.py --tier $TEST/tier --prompts $TEST/prompts.json --effort $EFFORT \
      --url http://127.0.0.1:8201/v1 --model base --n 6 > $L/promptcheck.log 2>&1; pc=$?
  else pc=9; echo "base server never ready: $(tail -3 $L/serve_base.log)" > $L/promptcheck.log; fi
  kill -TERM -- -$VB 2>/dev/null
  wait $SM; sm=$?
  [ $pc = 0 ] || { kill -TERM -- -$SM 2>/dev/null; fail "prompt check: $(tail -3 $L/promptcheck.log)"; }
  [ $sm = 0 ] && grep -q "step 10/10" $L/smoke.log || fail "smoke: $(tail -3 $L/smoke.log)"
  touch $R/GATES_PASSED
  for i in $(seq 1 60); do [ "$(gpu_busy)" = 0 ] && break; sleep 10; done
fi
say "prompt check: $(tail -1 $L/promptcheck.log)"
if [ -n "$TB" ]; then say "waiting for the tier build"; wait $TB || fail "tier build: $(tail -3 $L/tier.log)"; fi
[ -f $R/tier/manifest.json ] || fail "no tier manifest: $(tail -3 $L/tier.log)"
cmp -s $R/prompts.json $TEST/prompts.json || fail "tier prompts.json differs from the gated one"
say "tier: $(tail -1 $L/tier.log)"
SPS=$(grep "step 10/10" $L/smoke.log | sed 's/.* \([0-9]*\) s\/step.*/\1/')
NT=$(python3 -c "import json; print(json.load(open('$R/tier/manifest.json'))['rows'])")
STEPS=$(python3 -c "print(max(50, min(int($BUDGET_H * 3600 / $SPS), $NT // 16)))")
say "smoke: $SPS s/step for 8 rows per replica ($(grep -c 'sample [1-4]:' $L/smoke.log) samples logged: $(grep 'sample 1:' $L/smoke.log | sed 's/.*sample 1: //')) -> STEPS $STEPS x 16 rows (~$((STEPS * SPS / 3600)) h; tier $NT rows)"

# 3. train
if [ ! -s $R/adapter/adapter_model.safetensors ]; then
  export MASTER_ADDR=127.0.0.1 MASTER_PORT=29613 WORLD_SIZE=2 NCCL_P2P_LEVEL=NVL
  P=()
  for r in 0 1; do
    G=$([ $r = 0 ] && echo 0,1,2,3 || echo 4,5,6,7)
    CUDA_VISIBLE_DEVICES=$G RANK=$r setsid nohup .venv_dsv41/bin/python $C/geom/dsv41_lora_train.py --dist $ARGS --tier $R/tier \
      --prompts $R/prompts.json --steps $STEPS --save-every 250 --out $R/adapter > $L/train.rank$r.log 2>&1 < /dev/null &
    P+=($!)
  done
  say "training: 2 replicas, pids ${P[*]} (logs $L/train.rank{0,1}.log)"
  wait "${P[@]}"
  [ -s $R/adapter/adapter_model.safetensors ] || fail "train: $(tail -3 $L/train.rank0.log)"
fi
say "train done: $(grep '\[train\] step' $L/train.rank0.log | tail -1)"
unset MASTER_ADDR MASTER_PORT WORLD_SIZE

# 4. merge + serve
if [ ! -f $M/MERGED ]; then
  bash $C/serv19/dsv41_grpo_s19.sh merge $R/adapter $M $L/merge.log
  until [ -f $M/MERGED ] || [ -f $M.FAILED ]; do sleep 30; done
  [ -f $M/MERGED ] || fail "merge: $(tail -3 $L/merge.log)"
fi
say "merged -> $M"
V=()
for pg in "8200 0,1,2,3" "8201 4,5,6,7"; do
  set -- $pg
  MAXLEN=16384 setsid nohup bash $C/serv19/dsv41_ft_serve_serv19.sh $M $NAME $1 $2 > $L/serve_$1.log 2>&1 < /dev/null &
  V+=($!)
done
for port in 8200 8201; do
  ok=0; for i in $(seq 1 240); do curl -sf -m 5 127.0.0.1:$port/health >/dev/null && { ok=1; break; }; sleep 15; done
  [ $ok = 1 ] || { for v in "${V[@]}"; do kill -TERM -- -$v 2>/dev/null; done; fail "server :$port never ready: $(tail -3 $L/serve_$port.log)"; }
done
say "servers up (:8200 GPUs 0-3, :8201 GPUs 4-7)"

# 5. eval (main-table protocol)
export REASONING_EFFORT=$EFFORT OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
for b in real full benchb; do
  case $b in real) BENCH=mech_benchmarks/ext_bench_dw423_perm;; benchb) BENCH=mech_benchmarks/bench_b;; full) BENCH=mech_benchmarks/fullpool_dw423;; esac
  STEM=abl/results/${b}_$NAME
  [ -f $STEM.GEN_DONE ] && continue
  say "gen $b -> $STEM"
  GP=(); for i in 0 1 2 3; do
    port=$([ $i -lt 2 ] && echo 8200 || echo 8201)
    .venv/bin/python $C/geom/gen_openai_bo.py --bench $BENCH --base-url http://127.0.0.1:$port/v1 --model $NAME --k 8 \
      --temperature 0.7 --max-tokens 2400 --shard $i --nshards 4 --workers 16 --timeout 3600 --out $STEM > $L/gen_${b}.$i.log 2>&1 &
    GP+=($!); done; wait "${GP[@]}"
  nd=$(grep -h "DONE shard" $L/gen_${b}.*.log | wc -l)
  say "$b: $nd/4 shards done"; [ $nd = 4 ] && touch $STEM.GEN_DONE
done
for v in "${V[@]}"; do kill -TERM -- -$v 2>/dev/null; done
touch $R/DONE
say "DSE55 DONE $NAME"
