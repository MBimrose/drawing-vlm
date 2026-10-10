#!/bin/bash
# Auto held-out eval of fast-path GRPO generator checkpoints on serv-20 (2026-10-06).
# Polls runs/grpo_v_<arm>/adapter_step<N> for N in $STEPS; each new one goes through grpo_eval.sh
# (merge -> vLLM on $GPU -> K=8 on real/famheld/indh) and is scored HERE with score_partials.py at
# 16 workers (no cluster round-trip). Results: results/grpo_eval/<bench>_<arm>_s<N>.json.
#   setsid nohup bash train_v14/serv19/grpo_autoeval.sh > logs/grpo_autoeval.log 2>&1 &
set -uo pipefail
# serv-20 has no thread caps in the login env: unset, every python child spawns ~core-count threads (load ~900, 2026-10-06)
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4
cd /srv/scratch/bimrose2
GPU=${GPU:-3}; PORT=${PORT:-8300}
ARMS=${ARMS:-"mix_lr2e5 mix_lr4e5 mix_pkpo real_lr2e5"}
STEPS=${STEPS:-"20 60 120 200 300"}
export BENCHES=${BENCHES:-"real"}   # 2026-10-07: real only (family trend clear); newest checkpoint per arm first   # indh dropped from rolling evals (2026-10-06): trend clear, costs 40%
O=results/grpo_eval
declare -A GT=( [real]=mech_benchmarks/ext_bench_dw423_perm/gt_meshes_v15 [famheld]=fp/h6/bench_held2/gt_meshes_v15
                [indh]=mech_benchmarks/fullpool_dw423/gt_meshes_v15 )
say() { echo "$(date '+%m-%d %H:%M') $*"; }
# Repairer arms: rp3 + adapter, in-house loop protocol on the real bench (e55 vote-pick start, K=8 x 3 rounds,
# v3-gated adoption at margin 0.1) -> results/repair/loop_real_<arm>_s<N>.jsonl; baseline rp3 = 0.631.
# vr_serve workers each spawn several draftwright renderers: 24 workers -> ~110 procs, load 600 (2026-10-06)
REP_ARMS=${REP_ARMS:-"rep_rp3 rep_lr4e5"}; REP_STEPS=${REP_STEPS:-"120 300"}
RP3=/srv/scratch/bimrose2/runs/rp3-delta-e55/final
port_free() {  # a leftover eval server on $PORT would answer the health check with the OLD model: kill it
  local p
  for p in $(pgrep -u bimrose2 -f "vllm serve .*--port $PORT( |\$)"); do kill $p 2>/dev/null; done
  for i in $(seq 1 30); do curl -s -m 3 http://127.0.0.1:$PORT/health >/dev/null || return 0; sleep 5; done
  for p in $(pgrep -u bimrose2 -f "vllm serve .*--port $PORT( |\$)"); do kill -9 $p 2>/dev/null; done; sleep 20
  curl -s -m 3 http://127.0.0.1:$PORT/health >/dev/null && say "port $PORT still busy after kill -9"; return 0; }
rep_eval() {  # name adapter
  local name=$1 ad=$2 M=runs/merged_$1
  [ -f $M/config.json ] || CUDA_VISIBLE_DEVICES= .venv/bin/python train_v14/geom/merge_grpo_lora.py --ckpt $RP3 --adapter $ad \
      --out $M --model-base /srv/scratch/bimrose2/models/Qwen3.8-27B > logs/merge_$name.log 2>&1 || { say "merge failed $name"; return; }
  port_free
  CUDA_VISIBLE_DEVICES=$GPU DP=1 SEQS=128 PORT=$PORT MODEL=/srv/scratch/bimrose2/$M NAME=$name MM_LIMIT=2 \
    setsid bash train_v14/serv19/run_vllm_e55_serv20.sh > logs/vllm-geval-$name.log 2>&1 < /dev/null &
  local VPID=$! ok=0
  for i in $(seq 1 120); do curl -s -m 5 http://127.0.0.1:$PORT/health >/dev/null && { ok=1; break; }; sleep 15; done
  if [ $ok = 1 ]; then
    .venv/bin/python train_v14/geom/vr_serve.py --bench mech_benchmarks/ext_bench_dw423_perm --picks results/visrepair/e55_vote_picks.json \
      --base-url http://127.0.0.1:$PORT/v1 --model $name --k 8 --rounds 3 --margin 0.1 --workers ${REP_WORKERS:-8} --py $PWD/.venv/bin/python \
      --rpy $PWD/dw_venv/bin/python --script-dir $PWD/mech_step_to_drw --out results/repair/loop_real_$name.jsonl > logs/loop_real_$name.log 2>&1
  else say "vLLM never ready $name"; fi
  kill -- -$VPID 2>/dev/null; sleep 20; rm -rf $M
}
while true; do
  did=0
  # arm lists are re-read every pass from results/grpo_eval/{ARMS,REP_ARMS} when present (edit without restart)
  [ -s $O/ARMS ] && ARMS=$(cat $O/ARMS); [ -s $O/REP_ARMS ] && REP_ARMS=$(cat $O/REP_ARMS); [ -s $O/STEPS ] && STEPS=$(cat $O/STEPS)
  for arm in $ARMS; do   # newest not-yet-evaluated checkpoint in $STEPS per arm, arms in priority order
    n=""; for m in $STEPS; do [ -f runs/grpo_v_$arm/adapter_step$m/adapter_model.safetensors ] && n=$m; done
    [ -n "$n" ] || continue
    ad=runs/grpo_v_$arm/adapter_step$n; name=${arm}_s$n
    [ -f $O/GEN_DONE_$name ] && continue   # generated (scoring may still run in the background)
    mkdir $O/lock_$name 2>/dev/null || continue   # several daemons (one per eval GPU) share the queue
    say "eval $name"; port_free
    bash train_v14/serv19/grpo_eval.sh $GPU $PORT $name=$ad
    rm -rf runs/merged_$name   # 54 GB each; the adapter is kept
    (  # score on CPU in the background while the GPU moves on to the next checkpoint; real last = done marker
      for b in $(echo $BENCHES | tr ' ' '\n' | grep -v '^real$') real; do
        .venv/bin/python train_v14/geom/score_partials.py --partials "$O/${b}_$name.shard*.json.partial.json" \
          --gt-dir ${GT[$b]} --out $O/${b}_$name.json --workers 16 --exec-timeout 60 --iou-timeout 90 \
          > logs/gscore_${b}_$name.log 2>&1 || say "score failed $b $name"
      done; say "SCORED $name" ) &
    did=1; break   # re-scan from the top-priority arm after every eval
  done
  [ -n "${GEN_ONLY:-}" ] && { [ $did = 1 ] || sleep 300; continue; }
  for n in $REP_STEPS; do for arm in $REP_ARMS; do
    ad=runs/grpo_v_$arm/adapter_step$n; name=${arm}_s$n
    [ -f $ad/adapter_model.safetensors ] || continue
    [ -f results/repair/LOOP_DONE_$name ] && continue
    say "repair-loop eval $name"; rep_eval $name $ad
    if [ "$(wc -l < results/repair/loop_real_$name.jsonl 2>/dev/null || echo 0)" -ge 140 ]; then
      touch results/repair/LOOP_DONE_$name; say "LOOP DONE $name"
    else say "LOOP INCOMPLETE $name (see logs/loop_real_$name.log)"; fi
    did=1
  done; done
  [ $did = 1 ] || sleep 600
done
