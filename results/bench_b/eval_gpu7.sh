#!/bin/bash
# Bench B + baseline generation on serv-20 GPU 7 (2026-10-10). Copy of grpo_eval.sh's per-model path (vLLM DP=1,
# gen_openai_bo.py K=8: draw 0 greedy + 7 at T 0.7 / top_p 0.95, think mode, 4 client shards x 12 workers), with
#   - a wait for ent_s2's trainer (TRAINER_PID) to exit before touching the GPU,
#   - bench tags: real = mech_benchmarks/ext_bench_dw423_perm (144), benchb = mech_benchmarks/bench_b (waits for FROZEN),
#   - per-model max tokens / model-len (the un-fine-tuned Qwen3.8-27B thinks far longer than e55's 2400-token budget).
# Jobs: "<name>|<model dir or merged name>|<bench tags>|<max_tokens>|<max_model_len>[|eager]" (one vLLM per job).
# 2026-10-10 01:10: serv-20 at load ~340 made CUDA-graph capture take >30 min (e55ctl never became ready in the old
# 30-min window) -> health wait 90 min and --enforce-eager for the short-output (2,400-token) bench-B jobs.
#   setsid nohup bash bench_b/code/eval_gpu7.sh > bench_b/logs/eval_gpu7.log 2>&1 &
set -uo pipefail
cd /srv/scratch/bimrose2
GPU=7; PORT=${PORT:-8460}; O=bench_b/eval; mkdir -p $O logs
E55=/srv/scratch/bimrose2/runs/e55-rft-real-u5-gt-dw423/final; QB=/srv/scratch/bimrose2/models/Qwen3.8-27B
say() { echo "$(date '+%m-%d %H:%M') $*"; }
if [ -n "${TRAINER_PID:-}" ]; then
  say "waiting for trainer pid $TRAINER_PID to exit"
  while kill -0 $TRAINER_PID 2>/dev/null; do sleep 60; done
  say "trainer exited; waiting for GPU $GPU to drain"
  for i in $(seq 1 60); do
    u=$(nvidia-smi -i $GPU --query-gpu=memory.used --format=csv,noheader,nounits | tr -d ' ')
    [ "$u" -lt 2000 ] && break; sleep 30
  done
  say "GPU $GPU memory used ${u} MiB"; [ "$u" -lt 2000 ] || { say "GPU $GPU still busy -- abort"; exit 1; }
fi
JOBS=${JOBS:-"qwenbase|$QB|real benchb|16000|24576
e55ctl|$E55|benchb|2400|16384
rft2_rl_s60|runs/merged_bb_rft2_rl_s60|benchb|2400|16384
rft1_rl2_s120|runs/merged_bb_rft1_rl2_s120|benchb|2400|16384
ent_t10_s120|runs/merged_bb_ent_t10_s120|benchb|2400|16384"}
while IFS='|' read -r name model benches mtok mlen eager; do
  [ -n "$name" ] || continue
  case $model in /*) ;; *) model=/srv/scratch/bimrose2/$model;; esac
  todo=""; for b in $benches; do [ -f $O/GEN_DONE_${b}_$name ] || todo="$todo $b"; done
  [ -n "$todo" ] || continue
  [ -f $model/config.json ] || { say "no model $model for $name"; continue; }
  say "serving $name ($model) on GPU $GPU :$PORT, max_tokens $mtok, model-len $mlen"
  CUDA_VISIBLE_DEVICES=$GPU DP=1 SEQS=128 PORT=$PORT MODEL=$model NAME=$name VLLM_EXTRA="--max-model-len $mlen${eager:+ --enforce-eager}" \
    setsid bash train_v14/serv19/run_vllm_e55_serv20.sh > logs/vllm-bb-$name.log 2>&1 < /dev/null &
  VPID=$!
  ok=0; for i in $(seq 1 ${HEALTH_TRIES:-360}); do curl -s -m 5 http://127.0.0.1:$PORT/health >/dev/null && { ok=1; break; }; sleep 15; done
  [ $ok = 1 ] || { say "vLLM never ready for $name"; tail -20 logs/vllm-bb-$name.log; kill -- -$VPID 2>/dev/null; continue; }
  for b in $todo; do
    case $b in
      real)   BENCH=mech_benchmarks/ext_bench_dw423_perm ;;
      benchb) BENCH=mech_benchmarks/bench_b
              until [ -f $BENCH/FROZEN ]; do say "waiting for bench B to be frozen"; sleep 300; done ;;
    esac
    GP=()
    for i in 0 1 2 3; do
      .venv/bin/python train_v14/geom/gen_openai_bo.py --bench $BENCH --base-url http://127.0.0.1:$PORT/v1 \
        --model $name --k 8 --temperature 0.7 --max-tokens $mtok --shard $i --nshards 4 --workers 12 --timeout 3600 \
        --out $O/${b}_$name > logs/bbgen_${b}_$name.$i.log 2>&1 &
      GP+=($!)
    done; wait "${GP[@]}"
    say "$name $b: $(grep -h DONE logs/bbgen_${b}_$name.*.log | wc -l)/4 shards done"
    touch $O/GEN_DONE_${b}_$name
  done
  kill -- -$VPID 2>/dev/null; sleep 20
  for i in $(seq 1 30); do curl -s -m 3 http://127.0.0.1:$PORT/health >/dev/null || break; sleep 5; done
  say "GEN DONE $name"
done <<< "$JOBS"
say "BENCH B GPU7 ALL DONE"
