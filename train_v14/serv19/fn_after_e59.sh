#!/bin/bash
# Flash-Next pipeline stage 2 hand-off (2026-10-19, serv-19 only): when e59's eval lanes are done ->
#   gate A: vLLM serves e59/final with LoRA enabled (GPUs 0-3) and hot-loads a Flash-Next adapter (e26fl, same module set)
#   gate B: HF-vs-vLLM teacher-forced logprob parity (geom/fn_parity.py, HF on GPUs 4-7): base, then with the adapter
#   pass  -> stop the gate server, launch GRPO (fn_grpo_arm.sh fn1, POLICY=e59/final)
#   fail  -> stop, GPUs left free for debugging (marker fn55/GATE_FAILED)
#   setsid nohup bash train_v14/serv19/fn_after_e59.sh > fn55/logs/after_e59.log 2>&1 < /dev/null &
set -uo pipefail
cd /srv/scratch/bimrose2
say() { echo "$(date '+%m-%d %H:%M') $*"; }
P=runs/e59-flashnext-e55recipe/final; AD=abl/ckpt/e26fl; PORT=8749; L=fn55/logs
say "waiting for e59 eval lanes"
until grep -q "E59 EVAL LANES DONE\|no final model" fn55/logs/train_e59.log 2>/dev/null; do sleep 120; done
grep -q "no final model" fn55/logs/train_e59.log && { say "e59 has no final model - stop"; exit 1; }
sleep 60
export VLLM_ALLOW_RUNTIME_LORA_UPDATING=True APPTAINERENV_VLLM_ALLOW_RUNTIME_LORA_UPDATING=True
MODEL=$P NAME=fnpol GPUS=0,1,2,3 TP=4 PORT=$PORT VLLM_EXTRA="--enable-lora --max-lora-rank 64 --max-loras 2" \
  setsid nohup bash train_v14/serv19/run_vllm_qwen_serv19.sh > $L/vllm-gate.log 2>&1 < /dev/null &
VPID=$!
ok=0; for i in $(seq 1 240); do curl -s -m 5 http://127.0.0.1:$PORT/health >/dev/null && { ok=1; break; }; sleep 15; done
fail() { say "GATE FAILED: $*"; touch fn55/GATE_FAILED; kill -TERM -- -$VPID 2>/dev/null; exit 1; }
[ $ok = 1 ] || fail "vLLM (LoRA-enabled) never ready: $(tail -3 $L/vllm-gate.log)"
say "gate A: server up; hot-loading $AD"
r=$(curl -s -m 600 -X POST http://127.0.0.1:$PORT/v1/load_lora_adapter -H "Content-Type: application/json" \
     -d "{\"lora_name\": \"e26fl\", \"lora_path\": \"$(readlink -f $AD)\"}")
say "load_lora_adapter -> ${r:0:300}"
curl -s -m 30 http://127.0.0.1:$PORT/v1/models | grep -q '"e26fl"' || fail "adapter not listed after load"
PY=".venv/bin/python fn55/train_v14/geom/fn_parity.py --url http://127.0.0.1:$PORT/v1 --ckpt $P
    --model-base /srv/scratch/bimrose2/models/Qwen3.8-Flash-Next --run e59-flashnext-e55recipe --bench fp/h6/train_bench --n 6"
export CUDA_VISIBLE_DEVICES=4,5,6,7 FLASHNEXT_PLE_DIR=/dev/shm/flashnext_ple
say "gate B1: parity base"
taskset -c 0-95 $PY --model fnpol --out fn55/parity_base.json > $L/parity_base.log 2>&1
say "gate B2: parity with adapter"
taskset -c 0-95 $PY --model e26fl --adapter $(readlink -f $AD) --out fn55/parity_lora.json > $L/parity_lora.log 2>&1
unset CUDA_VISIBLE_DEVICES
for f in base lora; do
  s=$(grep "SUMMARY" $L/parity_$f.log | sed 's/.*SUMMARY //')
  say "parity $f: ${s:-none}"
  [ -n "$s" ] || fail "parity $f produced no summary: $(tail -3 $L/parity_$f.log)"
  python3 -c "import json,sys; s=json.loads(sys.argv[1]); sys.exit(0 if s['mean_abs'] < 0.06 and abs(s['mean_diff']) < 0.02 and s['id_match'] > 0.95 else 1)" "$s" \
    || fail "parity $f outside tolerance (mean_abs < 0.06, |mean_diff| < 0.02, id_match > 0.95)"
done
say "gates passed; stopping gate server"
kill -TERM -- -$VPID 2>/dev/null; sleep 60
touch fn55/GATES_PASSED
say "launching GRPO fn1 from $P"
POLICY=$P bash train_v14/serv19/fn_grpo_arm.sh fn1
say "fn1 finished"
