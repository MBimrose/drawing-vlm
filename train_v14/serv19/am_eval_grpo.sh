#!/bin/bash
# American-VLM GRPO checkpoint evals on serv-19 (2026-10-27; fn_eval_grpo.sh for Muse Glimmer). One LoRA-enabled vLLM server
# (TP2) on the stage-1 policy with the thought-prefilled template (as glftpf) and the muse_glimmer parser (code comes back
# in content); each GRPO adapter is hot-loaded under its own name, evaluated with the main-table protocol (eval_nemo.sh:
# K=8, draw 0 greedy + 7 at T 0.7, 2400 tok) on real-144, bench B and synthetic, then unloaded. Starts after the Gemma FT
# eval has released GPUs 4-7. Scoring: nemo_score.sbatch on ccc0442. Select steps on real-144 / synthetic only.
#   RUN=gl1 STEPS="40 120 200" GPUS=4,5 PORT=8770 setsid nohup bash amvlm/train_v14/serv19/am_eval_grpo.sh > amvlm/grpo/logs/eval_gl1_a.log 2>&1 &
set -uo pipefail
cd /srv/scratch/bimrose2
say() { echo "$(date '+%m-%d %H:%M') $*"; }
RUN=${RUN:-gl1}; STEPS=${STEPS:-40 80 120 160 200}; PORT=${PORT:-8770}; GPUS=${GPUS:-4,5}; TP=${TP:-2}
BASE=${BASE:-amvlm/runs/am-glimmer-30b-e55recipe/final}; TEMPLATE=${TEMPLATE:-american_vlm/templates/glftpf.jinja}
D=amvlm/grpo/runs/$RUN; L=amvlm/grpo/logs; OUT=american_vlm/results
until grep -q "FT EVAL DONE gmft" american_vlm/logs/eval_gmft.log 2>/dev/null; do sleep 300; done
say "Gemma FT eval done -> GPUs $GPUS"
export VLLM_ALLOW_RUNTIME_LORA_UPDATING=True APPTAINERENV_VLLM_ALLOW_RUNTIME_LORA_UPDATING=True
MODEL=$BASE NAME=glpol GPUS=$GPUS TP=$TP PORT=$PORT RPARSER=muse_glimmer SEQS=${SEQS:-128} GMU=${GMU:-0.85} \
  VLLM_EXTRA="--enable-lora --max-lora-rank 64 --max-loras 1 --disable-custom-all-reduce --chat-template $PWD/$TEMPLATE" \
  setsid nohup bash amvlm/train_v14/serv19/run_vllm_any_serv19.sh > $L/vllm-eval_${RUN}_$PORT.log 2>&1 < /dev/null &
VPID=$!
ok=0; for i in $(seq 1 240); do curl -s -m 5 http://127.0.0.1:$PORT/health >/dev/null && { ok=1; break; }; sleep 15; done
[ $ok = 1 ] || { say "vLLM never ready: $(tail -3 $L/vllm-eval_${RUN}_$PORT.log)"; kill -TERM -- -$VPID 2>/dev/null; exit 1; }
say "eval server up on GPUs $GPUS :$PORT"
api() { curl -s -m 600 -X POST http://127.0.0.1:$PORT/v1/$1 -H "Content-Type: application/json" -d "$2"; }
for s in $STEPS; do
  A=$D/adapter_step$s; N=${RUN}s$s
  until [ -f $A/adapter_model.safetensors ] || grep -q "ROUND DONE\|trainer exit" $L/grpo_$RUN.log 2>/dev/null; do sleep 300; done
  [ -f $A/adapter_model.safetensors ] || { say "no $A (run ended) - stop"; break; }
  sleep 30   # let the trainer finish writing the adapter
  say "load $N: $(api load_lora_adapter "{\"lora_name\": \"$N\", \"lora_path\": \"$(readlink -f $A)\"}" | head -c 200)"
  NAME=$N TAG=$N PORT=$PORT MTOK=2400 WORKERS=${WORKERS:-12} OUT=$OUT BENCHES="real full benchb" \
    bash nemotron/eval_nemo.sh > $L/eval_$N.log 2>&1
  say "$(tail -1 $L/eval_$N.log)"
  say "unload $N: $(api unload_lora_adapter "{\"lora_name\": \"$N\"}" | head -c 200)"
done
kill -TERM -- -$VPID 2>/dev/null
say "GRPO EVALS DONE $RUN $STEPS"
