#!/bin/bash
# American-VLM GRPO on serv-19 (2026-10-27; fn_grpo_arm.sh for Muse Glimmer): the 27B's ent_t10 recipe on a LoRA over the
# e55-recipe full fine-tune. Rollouts come from a LoRA-enabled vLLM server (GPUs $VGPUS) that serves the thought-prefilled
# template (generation prompt "<|start|>assistant to=self<|message|>1.", as the eval's glftpf) with no reasoning parser;
# grpo_round.py --raw-channels glimmer splits the raw replies and its processor renders the same template, so the
# prefill is prompt and only sampled tokens are trained. Each step the trainer hot-loads its adapter (on-policy).
#   POLICY=<hf dir> TEMPLATE=<jinja> bash amvlm/train_v14/serv19/am_grpo_arm.sh <name> [grpo_round.py args; later win]
set -uo pipefail
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4
cd /srv/scratch/bimrose2
name=${1:?name}; shift
POLICY=${POLICY:-/srv/scratch/bimrose2/amvlm/runs/am-glimmer-30b-e55recipe/final}
TEMPLATE=${TEMPLATE:-/srv/scratch/bimrose2/american_vlm/templates/glftpf.jinja}
RUN=${RUN:-am-glimmer-30b-e55recipe}; BASE=${BASE:-/srv/scratch/bimrose2/models/Muse-Glimmer-30B}
VGPUS=${VGPUS:-0,1}; TGPUS=${TGPUS:-2,3}; PORT=${PORT:-8760}
VTP=$(echo $VGPUS | tr , '\n' | grep -c .)
O=amvlm/grpo; mkdir -p $O/runs/$name $O/logs tmp
export VLLM_ALLOW_RUNTIME_LORA_UPDATING=True APPTAINERENV_VLLM_ALLOW_RUNTIME_LORA_UPDATING=True
MODEL=$POLICY NAME=glpol GPUS=$VGPUS TP=$VTP PORT=$PORT RPARSER= SEQS=${SEQS:-256} GMU=${GMU:-0.85} \
  VLLM_EXTRA="--enable-lora --max-lora-rank 64 --max-loras 2 --disable-custom-all-reduce --chat-template $TEMPLATE" \
  setsid nohup bash amvlm/train_v14/serv19/run_vllm_any_serv19.sh > $O/logs/vllm-$name.log 2>&1 < /dev/null &
VPID=$!
echo "$(date '+%m-%d %H:%M') vLLM for $name on GPUs $VGPUS :$PORT (pid $VPID)"
ok=0; for i in $(seq 1 240); do curl -s -m 5 http://127.0.0.1:$PORT/health >/dev/null && { ok=1; break; }; sleep 15; done
[ $ok = 1 ] || { echo "vLLM never ready"; tail -20 $O/logs/vllm-$name.log; kill -- -$VPID; exit 2; }
# language-model attention + MLP only (vLLM packs q/k/v and gate/up; the attention output gate and the vision tower stay frozen)
GL_LORA='model\.language_model\.layers\.\d+\.(self_attn\.(q|k|v|o)_proj|mlp\.(gate|up|down)_proj)'
COMMON=(--run $RUN --model-base $BASE --ckpt $POLICY --lora-targets "$GL_LORA"
  --raw-channels glimmer --think-prefill "1." --chat-template $TEMPLATE --max-seq-len 8704 --train-raw
  --bench fp/h6/rft_corpus4,mech_benchmarks/rft_corpus2_dw423,fp/h6/train_bench
  --keys fp/h6/real4_hard_keys.txt,fp/h6/c2_hard_keys.txt,fp/h6/fam_hard_keys.txt
  --n-parts 16 --g 8 --steps 200 --lr 2e-5 --kl-beta 0 --minibatches 4 --scale-logits --adv batchstd
  --temperature 1.0 --top-p 1.0 --guard 0.6 --ent-coef 0.1 --ent-max 0.35
  --train-batch ${TB:-4} --score-workers 48 --score-timeouts --save-every 10 --rollout-url http://127.0.0.1:$PORT/v1)
CUDA_VISIBLE_DEVICES=$TGPUS PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
  taskset -c ${CORES:-0-95} .venv/bin/python amvlm/train_v14/geom/grpo_round.py "${COMMON[@]}" "$@" --out $O/runs/$name \
  > $O/logs/grpo_$name.log 2>&1 < /dev/null
echo "$(date '+%m-%d %H:%M') trainer exit $? for $name"
kill -TERM -- -$VPID 2>/dev/null
