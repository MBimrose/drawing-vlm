#!/bin/bash
# American-VLM GRPO for Gemma 4 31B on serv-19 (2026-10-28; am_grpo_arm.sh for the Gemma column). Same ent_t10 recipe as
# Glimmer's gl1 on a LoRA over the Gemma FT (final_vllm). The rollout server prefills the thought channel (gmftpf.jinja:
# "<|turn>model\n<|channel>thought\n1.") with no reasoning parser; grpo_round.py --raw-channels gemma splits the raw replies
# at <channel|> and its processor renders the same template, so the prefill is prompt and only sampled tokens are trained.
# Gate first: fn_parity.py on 6 training parts, stop if mean |dlogp| > PARITY_MAX (gl1 passed at 0.010). Trainer venv
# .venv_g4 (transformers 5.16, Gemma 4).
#   VGPUS=4,5 TGPUS=6,7 PORT=8780 setsid nohup bash amvlm/train_v14/serv19/am_grpo_gemma.sh gm1 > amvlm/grpo/logs/arm_gm1.log 2>&1 &
set -uo pipefail
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4
cd /srv/scratch/bimrose2
name=${1:?name}; shift
POLICY=${POLICY:-/srv/scratch/bimrose2/amvlm/runs/am-gemma4-31b-e55recipe/final_vllm}
TEMPLATE=${TEMPLATE:-/srv/scratch/bimrose2/american_vlm/templates/gmftpf.jinja}
RUN=${RUN:-am-gemma4-31b-e55recipe}; BASE=${BASE:-/srv/scratch/bimrose2/models/gemma-4-31B-it}
VGPUS=${VGPUS:-4,5}; TGPUS=${TGPUS:-6,7}; PORT=${PORT:-8780}
VTP=$(echo $VGPUS | tr , '\n' | grep -c .)
O=amvlm/grpo; mkdir -p $O/runs/$name $O/logs tmp
say() { echo "$(date '+%m-%d %H:%M') $*"; }
export VLLM_ALLOW_RUNTIME_LORA_UPDATING=True APPTAINERENV_VLLM_ALLOW_RUNTIME_LORA_UPDATING=True
MODEL=$POLICY NAME=gmpol GPUS=$VGPUS TP=$VTP PORT=$PORT RPARSER= SEQS=${SEQS:-256} GMU=${GMU:-0.85} \
  VLLM_EXTRA="--enable-lora --max-lora-rank 64 --max-loras 2 --disable-custom-all-reduce --chat-template $TEMPLATE --mm-processor-kwargs {\"max_soft_tokens\":1120}" \
  setsid nohup bash amvlm/train_v14/serv19/run_vllm_any_serv19.sh > $O/logs/vllm-$name.log 2>&1 < /dev/null &
VPID=$!; trap "kill -TERM -- -$VPID 2>/dev/null" EXIT
say "vLLM for $name on GPUs $VGPUS :$PORT (pid $VPID)"
ok=0; for i in $(seq 1 240); do curl -s -m 5 http://127.0.0.1:$PORT/health >/dev/null && { ok=1; break; }; sleep 15; done
[ $ok = 1 ] || { say "vLLM never ready"; tail -20 $O/logs/vllm-$name.log; exit 2; }
PY=/srv/scratch/bimrose2/.venv_g4/bin/python
if [ ! -f $O/runs/$name/PARITY_OK ]; then
  CUDA_VISIBLE_DEVICES=$TGPUS $PY amvlm/train_v14/geom/fn_parity.py --url http://127.0.0.1:$PORT/v1 --model gmpol --ckpt $POLICY \
    --model-base $BASE --run $RUN --bench fp/h6/train_bench --raw-channels gemma --think-prefill "1." --chat-template $TEMPLATE \
    --max-seq-len 6144 --out $O/runs/$name/parity.json > $O/logs/parity_$name.log 2>&1
  v=$(grep -h "\[parity\] SUMMARY" $O/logs/parity_$name.log | tail -1 | sed 's/.*SUMMARY //' | python3 -c "import json,sys; print(json.load(sys.stdin)['mean_abs'])" 2>/dev/null)
  say "parity mean_abs ${v:-none}: $(grep -h 'SUMMARY' $O/logs/parity_$name.log | tail -1 | cut -c1-300)"
  python3 -c "import sys; sys.exit(0 if '$v' and float('$v') <= ${PARITY_MAX:-0.05} else 1)" || { say "PARITY GATE FAILED"; tail -20 $O/logs/parity_$name.log; exit 3; }
  touch $O/runs/$name/PARITY_OK
fi
GM_LORA='model\.language_model\.layers\.\d+\.(self_attn\.(q|k|v|o)_proj|mlp\.(gate|up|down)_proj)'
COMMON=(--run $RUN --model-base $BASE --ckpt $POLICY --lora-targets "$GM_LORA"
  --raw-channels gemma --think-prefill "1." --chat-template $TEMPLATE --max-seq-len 6144 --train-raw
  --bench fp/h6/rft_corpus4,mech_benchmarks/rft_corpus2_dw423,fp/h6/train_bench
  --keys fp/h6/real4_hard_keys.txt,fp/h6/c2_hard_keys.txt,fp/h6/fam_hard_keys.txt
  --n-parts 16 --g 8 --steps 200 --lr 2e-5 --kl-beta 0 --minibatches 4 --scale-logits --adv batchstd
  --temperature 1.0 --top-p 1.0 --guard 0.6 --ent-coef 0.1 --ent-max 0.35
  --train-batch ${TB:-4} --score-workers 48 --score-timeouts --save-every 10 --rollout-url http://127.0.0.1:$PORT/v1)
CUDA_VISIBLE_DEVICES=$TGPUS PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
  taskset -c ${CORES:-96-191} $PY amvlm/train_v14/geom/grpo_round.py "${COMMON[@]}" "$@" --out $O/runs/$name \
  > $O/logs/grpo_$name.log 2>&1 < /dev/null
say "trainer exit $? for $name"
