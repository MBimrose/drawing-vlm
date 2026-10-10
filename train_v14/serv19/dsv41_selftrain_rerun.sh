#!/usr/bin/env bash
# 2026-10-07: re-run of the DeepSeek self-training fine-tune (dsv41_selftrain_r32, 2026-10-01) that the indexer bug
# invalidated -- same tier (dsv41_selftrain_tier: 492 rows of DeepSeek's own IoU >= 0.8 samples, <= 32k tokens), FIXED
# trainer (indexer hooks + PIL images), T0 regime prompt (vis_repair SYS + SCRATCH, Reasoning Effort 25), activation
# checkpointing, LoRA r32 on ATTENTION ONLY (q_a/q_b/kv/o_b, layers >= 24; shared experts dropped: the BF16 merge serves
# attention only), lr 1e-4, 125 steps x 8 rows (2 epochs) -- on serv-19 GPUs 4-7 after dsgrpo2. Then BF16 merge ->
# serve -> T0 eval on the 144 held-out parts, paired vs dsgrpo2's u0.
# Runs on serv-20 (driver; HTTP client + scoring), GPU work on serv-19 via dsv41_grpo_s19.sh.
set -uo pipefail
SDV=/srv/scratch/bimrose2; S19=wpk-serv-19.mechse.illinois.edu; RUN=$SDV/grpo_ds/selftrain_rerun; mkdir -p $RUN
LOG=$RUN/run.log; PY=$SDV/.venv/bin/python; GEOM=$SDV/train_v14/geom
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=$SDV/train_v14:$GEOM
say() { echo "$(date '+%m-%d %H:%M:%S') $*" >> $LOG; }
on19() { timeout ${TMO:-300} ssh -o BatchMode=yes $S19 "bash $SDV/train_v14/serv19/dsv41_grpo_s19.sh $*"; }
say "selftrain rerun: syncing tier"
rsync -a $SDV/dsv41_selftrain_tier/ $S19:$SDV/dsv41_selftrain_tier/
TMO=900 on19 stop >> $LOG 2>&1
OUT=$SDV/grpo_ds/selftrain_rerun/adapter
ssh -o BatchMode=yes $S19 "mkdir -p $OUT; cd $SDV; setsid nohup bash -c \"CUDA_VISIBLE_DEVICES=4,5,6,7 HF_HOME=$SDV/.cache/huggingface PYTHONPATH=$SDV/train_v14:$SDV/train_v14/geom OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=1 TRITON_CACHE_DIR=$SDV/.cache/triton_dsv41 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True .venv_dsv41/bin/python train_v14/geom/dsv41_lora_train.py --model models/DeepSeek-V4.1-Flash --tier dsv41_selftrain_tier/shards --prompts train_v14/geom/dsv41_grpo_prompts.json --reasoning-effort 25 --rank 32 --lr 1e-4 --targets '(self_attn\\\\.(q_a_proj|q_b_proj|kv_proj|o_b_proj))\\$' --think --chunked-attn 256 --grad-ckpt --min-layer 24 --max-len 34000 --last-gpu-headroom 60 --steps 125 --accum 8 --save-every 25 --eval-n 0 --out $OUT > $RUN/train.log 2>&1 && touch $OUT/DONE || touch $OUT/FAILED\" > /dev/null 2>&1 < /dev/null &"
say "training started on serv-19 GPUs 4-7 (log serv-19 $RUN/train.log)"
until ssh -o BatchMode=yes $S19 "test -e $OUT/DONE -o -e $OUT/FAILED"; do sleep 300; done
ssh -o BatchMode=yes $S19 "test -e $OUT/DONE" || { say "TRAIN FAILED"; exit 1; }
say "train done: $(ssh -o BatchMode=yes $S19 "grep 'step 125/\|adapter saved' $RUN/train.log | tail -n 2")"
M=/scratch/bimrose2/dsv41_ft/selftrain_rerun
on19 merge $OUT $M $RUN/merge.log >> $LOG 2>&1
until ssh -o BatchMode=yes $S19 "test -e $M/MERGED -o -e $M.FAILED"; do sleep 30; done
MAXLEN=65536 on19 serve $M $RUN/serve.log >> $LOG 2>&1
for i in $(seq 1 120); do on19 up && break; sleep 30; done
say "serving merged self-train adapter; T0 eval"
$PY $GEOM/dsv41_t0_rollout.py --parts $SDV/grpo_ds/dsgrpo2/parts_eval.tsv --base-url http://$S19:8200 --k 1 --max-tokens 30000 \
  --workers 48 --score-workers 12 --out $RUN/eval_u01_selftrain > $RUN/eval.log 2>&1
mkdir -p $RUN/eval_u01; cp $RUN/eval_u01_selftrain.jsonl $RUN/eval_u01/ep.jsonl
$PY $GEOM/dsv41_t0_eval_summary.py --evals "$RUN/eval_u01/ep.jsonl" --base $SDV/grpo_ds/dsgrpo2/eval_u00/ep.jsonl > $RUN/eval_summary.txt 2>&1
say "self-train rerun held-out (vs dsgrpo2 u0): $(cat $RUN/eval_summary.txt)"
TMO=900 on19 stop >> $LOG 2>&1
