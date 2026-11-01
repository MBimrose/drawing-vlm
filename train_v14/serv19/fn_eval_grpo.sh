#!/bin/bash
# Flash-Next GRPO checkpoint evals on the two GPUs the fn1 trainer leaves idle (2026-10-21, serv-19 only).
# One LoRA-enabled vLLM server (TP2) on the stage-1 policy; each GRPO adapter is hot-loaded under its own name
# (gates A/B: vLLM LoRA serving matches HF to mean_abs 0.023), evaluated with the main-table protocol (eval_nemo.sh:
# K=8, draw 0 greedy + 7 at T 0.7, think, 2400 tok) on real-144, bench B and synthetic, then unloaded.
# Scoring runs on ccc0442 (nemo_score.sbatch waits for <stem>.GEN_DONE). Select steps on real-144 / synthetic only.
#   RUN=fn1 STEPS="40 80 120 160 200" setsid nohup bash train_v14/serv19/fn_eval_grpo.sh > fn55/logs/eval_grpo_fn1.log 2>&1 &
set -uo pipefail
cd /srv/scratch/bimrose2
say() { echo "$(date '+%m-%d %H:%M') $*"; }
RUN=${RUN:-fn1}; STEPS=${STEPS:-40 80 120 160 200}; PORT=${PORT:-8760}; GPUS=${GPUS:-6,7}; TP=${TP:-2}
BASE=runs/e59-flashnext-e55recipe/final; D=runs/fn_grpo_$RUN; L=fn55/logs
export VLLM_ALLOW_RUNTIME_LORA_UPDATING=True APPTAINERENV_VLLM_ALLOW_RUNTIME_LORA_UPDATING=True
MODEL=$BASE NAME=fnpol GPUS=$GPUS TP=$TP PORT=$PORT SEQS=${SEQS:-128} GMU=${GMU:-0.88} \
  VLLM_EXTRA="--enable-lora --max-lora-rank 64 --max-loras 1 --disable-custom-all-reduce" \
  setsid nohup bash train_v14/serv19/run_vllm_qwen_serv19.sh > $L/vllm-eval_grpo_$RUN.log 2>&1 < /dev/null &
VPID=$!
ok=0; for i in $(seq 1 240); do curl -s -m 5 http://127.0.0.1:$PORT/health >/dev/null && { ok=1; break; }; sleep 15; done
[ $ok = 1 ] || { say "vLLM never ready: $(tail -3 $L/vllm-eval_grpo_$RUN.log)"; kill -TERM -- -$VPID 2>/dev/null; exit 1; }
say "eval server up on GPUs $GPUS :$PORT"
api() { curl -s -m 600 -X POST http://127.0.0.1:$PORT/v1/$1 -H "Content-Type: application/json" -d "$2"; }
for s in $STEPS; do
  A=$D/adapter_step$s; N=${RUN}s$s
  until [ -f $A/adapter_model.safetensors ] || grep -q "ROUND DONE\|trainer exit" $L/fn_grpo_$RUN.log 2>/dev/null; do sleep 300; done
  [ -f $A/adapter_model.safetensors ] || { say "no $A (run ended) - stop"; break; }
  sleep 30   # let the trainer finish writing the adapter
  say "load $N: $(api load_lora_adapter "{\"lora_name\": \"$N\", \"lora_path\": \"$(readlink -f $A)\"}" | head -c 200)"
  NAME=$N TAG=$N PORT=$PORT MTOK=2400 WORKERS=${WORKERS:-12} OUT=abl/results BENCHES="real full benchb" \
    bash nemotron/eval_nemo.sh > $L/eval_$N.log 2>&1
  say "$(tail -1 $L/eval_$N.log)"
  say "unload $N: $(api unload_lora_adapter "{\"lora_name\": \"$N\"}" | head -c 200)"
done
kill -TERM -- -$VPID 2>/dev/null
say "GRPO EVALS DONE $RUN"
