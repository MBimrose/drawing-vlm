#!/bin/bash
#SBATCH --job-name=am-grpo-h200
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=128
#SBATCH --gres=gpu:8
#SBATCH --mem=1400G
#SBATCH --time=48:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/%x-%j.out
# American-VLM GRPO on a campus-cluster H200 node (2026-10-28): serv19/am_grpo_arm.sh's recipe (the 27B's ent_t10: LoRA r64 on
# LM attention + MLP over the SFT policy, 16 parts x G 8, 200 steps, lr 2e-5, T 1, batchstd, 4 minibatches, KL 0, guard 0.6,
# entropy coef 0.1 / ceiling 0.35, train-raw, save every 10) for any model with a thought-prefilled template. The rollout
# server (vLLM image) and the trainer (mirrored venv) run in separate srv_exec.sh containers on the host network.
# Gate first: fn_parity.py on 6 training parts (vLLM vs trainer per-token logprobs of the same sampled tokens); the run
# stops if mean |dlogp| > PARITY_MAX (Glimmer passed at 0.010).
#   Gemma 4:  sbatch --nodelist=ccc0451 --export=ALL,ARM=gm1,MODEL=gemma am_grpo_cluster.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; M=/projects/illinois/eng/ece/wpk/bimrose2/srvmirror
SX=$DV/train_v14/sbatch/srv_exec.sh; R=/srv/scratch/bimrose2
ARM=${ARM:?}; MODEL=${MODEL:-gemma}
case $MODEL in
  gemma) POLICY=$R/amvlm/runs/am-gemma4-31b-e55recipe/final_vllm; RUN=am-gemma4-31b-e55recipe; BASE=$R/models/gemma-4-31B-it
         TEMPLATE=$R/american_vlm/templates/gmftpf.jinja; VENV=.venv_g4; SEQ=6144
         VX="--mm-processor-kwargs {\\\"max_soft_tokens\\\":1120}"; NEED="g4 finals grpo";;
  glimmer) POLICY=$R/amvlm/runs/am-glimmer-30b-e55recipe/final; RUN=am-glimmer-30b-e55recipe; BASE=$R/models/Muse-Glimmer-30B
         TEMPLATE=$R/american_vlm/templates/glftpf.jinja; VENV=.venv_g4; SEQ=8704; VX=""; NEED="g4 finals grpo";;
  # Nemotron (2026-10-28): the FT's gathered best_model (served as nemoft, here without MTP speculation: LoRA hot-loading),
  # TP4 rollouts, the 120B trainer on 4 GPUs; LoRA on the dense LLM projections as configs/am-nemo-lora-e55recipe.yaml
  nemotron) POLICY=$R/nemotron/runs/nemo-fullft-r2/best_model; RUN=nemo-fullft-r2; BASE=$R/models/Nemotron-3.5-Super-VL-120B-A12B-BF16
         TEMPLATE=$R/american_vlm/templates/nemopf.jinja; VENV=.venv_nemo; SEQ=6144; VX=""; NEED="nemo nemoft grpo"
         VGPUS=${VGPUS:-0,1,2,3}; TGPUS=${TGPUS:-4,5,6,7}
         LORA='(.*\.)?language_model\.model\.layers\.\d+\.mixer\.((q|k|v|o)_proj|in_proj|out_proj|shared_experts\.(up|down)_proj|fc(1|2)_latent_proj)';;
  *) echo "unknown MODEL $MODEL"; exit 2;;
esac
VGPUS=${VGPUS:-0,1}; TGPUS=${TGPUS:-2,3,4,5}; PORT=${PORT:-8760}; VTP=$(echo $VGPUS | tr , '\n' | grep -c .)
for g in $NEED; do until [ -f $M/MIRROR_$g ]; do sleep 60; done; done
cp $DV/train_v14/geom/grpo_round.py $DV/train_v14/geom/fn_parity.py $M/amvlm/train_v14/geom/
O=$M/amvlm/grpo; mkdir -p $O/runs/$ARM $O/logs
say() { echo "$(date '+%m-%d %H:%M') $*"; }
export LOCAL_TMP=/tmp/bimrose2_srv_$SLURM_JOB_ID
export APPTAINERENV_VLLM_ALLOW_RUNTIME_LORA_UPDATING=True APPTAINERENV_VLLM_ENGINE_READY_TIMEOUT_S=3600
export APPTAINERENV_CUDA_HOME=/software/cuda-13.0 APPTAINERENV_PREPEND_PATH=/software/cuda-13.0/bin
CUDA_VISIBLE_DEVICES=$VGPUS setsid bash $SX "vllm serve $POLICY --served-model-name pol --host 127.0.0.1 --port $PORT \
  --tensor-parallel-size $VTP --trust-remote-code --gpu-memory-utilization 0.85 --max-model-len 16384 --max-num-seqs 256 \
  --limit-mm-per-prompt '{\"image\": 1, \"video\": 0}' --enable-lora --max-lora-rank 64 --max-loras 2 \
  --disable-custom-all-reduce --chat-template $TEMPLATE $VX" > $O/logs/vllm-$ARM.log 2>&1 < /dev/null &
VPID=$!; trap "kill -- -$VPID 2>/dev/null" EXIT
ok=0; for i in $(seq 1 240); do curl -s -m 5 http://127.0.0.1:$PORT/health >/dev/null && { ok=1; break; }; sleep 15; done
[ $ok = 1 ] || { say "vLLM never ready"; tail -30 $O/logs/vllm-$ARM.log; exit 2; }
say "vLLM $ARM up on GPUs $VGPUS :$PORT"
LORA=${LORA:-'model\.language_model\.layers\.\d+\.(self_attn\.(q|k|v|o)_proj|mlp\.(gate|up|down)_proj)'}
TR="cd $R; export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
  HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_HOME=$R/.cache/huggingface DRAWING_VLM_ROOT=$R; $R/$VENV/bin/python"
if [ "${SKIP_PARITY:-0}" != 1 ]; then
  CUDA_VISIBLE_DEVICES=$TGPUS bash $SX "$TR amvlm/train_v14/geom/fn_parity.py --url http://127.0.0.1:$PORT/v1 --model pol \
    --ckpt $POLICY --model-base $BASE --run $RUN --bench fp/h6/train_bench --raw-channels $MODEL --think-prefill 1. \
    --chat-template $TEMPLATE --max-seq-len $SEQ --out $O/runs/$ARM/parity.json" > $O/logs/parity_$ARM.log 2>&1
  say "parity exit $?: $(tail -3 $O/logs/parity_$ARM.log | tr '\n' ' ' | cut -c1-400)"
  python3 - "$O/logs/parity_$ARM.log" "${PARITY_MAX:-0.05}" <<'EOF' || { say "PARITY GATE FAILED"; exit 3; }
import json, sys
s = [l.split("SUMMARY", 1)[1] for l in open(sys.argv[1]) if "[parity] SUMMARY" in l]
v = json.loads(s[-1])["mean_abs"] if s else None
print("parity mean_abs", v); sys.exit(0 if v is not None and v <= float(sys.argv[2]) else 1)
EOF
fi
CUDA_VISIBLE_DEVICES=$TGPUS bash $SX "$TR amvlm/train_v14/geom/grpo_round.py --run $RUN --model-base $BASE --ckpt $POLICY \
  --lora-targets '$LORA' --raw-channels $MODEL --think-prefill 1. --chat-template $TEMPLATE --max-seq-len $SEQ --train-raw \
  --bench fp/h6/rft_corpus4,mech_benchmarks/rft_corpus2_dw423,fp/h6/train_bench \
  --keys fp/h6/real4_hard_keys.txt,fp/h6/c2_hard_keys.txt,fp/h6/fam_hard_keys.txt \
  --n-parts 16 --g 8 --steps ${STEPS:-200} --lr 2e-5 --kl-beta 0 --minibatches 4 --scale-logits --adv batchstd \
  --temperature 1.0 --top-p 1.0 --guard 0.6 --ent-coef 0.1 --ent-max 0.35 \
  --train-batch ${TB:-4} --score-workers 48 --score-timeouts --save-every 10 --rollout-url http://127.0.0.1:$PORT/v1 \
  ${EXTRA:-} --out amvlm/grpo/runs/$ARM" > $O/logs/grpo_$ARM.log 2>&1
say "trainer exit $? for $ARM"
