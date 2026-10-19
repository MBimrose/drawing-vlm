#!/bin/bash
# r2 copy (2026-10-16): the same driver for the warm-restarted run nemo-fullft-r2 (global step = RESUME_STEP + r2 step).
# After the Nemotron full SFT (2026-10-15/16, serv-19): wait for TRAIN DONE, finalize best_model + final for vLLM
# (nemotron_finalize_ckpt.py), then in parallel
#   GPUs 0-3: fine-tune (best_model) TP4 :8601 -> standard fine-tuned eval, K=8 (draw 0 greedy + 7 at T 0.7/top_p 0.95),
#             think, 2,400 tokens, on real-144, bench B, synthetic pool (TAG nemoft)
#   GPUs 4-7: base TP4 :8600 -> finish the zero-shot synthetic pool (16k tokens, resumes from partials, TAG nemobase)
# Scoring/vote: ccc0442 (nemo_score.sbatch), submitted from the cluster.
#   setsid nohup bash nemotron/post_sft.sh > nemotron/logs/post_sft.log 2>&1 &
set -uo pipefail
cd /srv/scratch/bimrose2
L=nemotron/logs/nemo-fullft-r2.log; R=nemotron/runs/nemo-fullft-r2; B=models/Nemotron-3.5-Super-VL-120B-A12B-BF16
V=nemotron/train_v14/serv19/run_vllm_nemotron_serv19.sh
say() { echo "$(date '+%m-%d %H:%M') $*"; }
until grep -q "TRAIN DONE" $L; do sleep 120; done
grep -q "TRAIN DONE 0" $L || { say "training did not exit 0 - stop"; exit 1; }
say "training done; finalizing"
for c in best_model final; do
  [ -d $R/$c ] || { say "no $R/$c"; continue; }
  [ -f $R/$c/FINALIZED_FROM_BASE ] && continue
  OMP_NUM_THREADS=8 taskset -c 0-15 .venv_nemo/bin/python nemotron/train_v14/geom/nemotron_finalize_ckpt.py --base $B --ckpt $R/$c \
    > nemotron/logs/finalize_$c.log 2>&1 || { say "finalize FAILED for $c"; tail -5 nemotron/logs/finalize_$c.log; exit 1; }
  say "finalized $c: $(tail -1 nemotron/logs/finalize_$c.log)"
done
grep -hE "^\[eval\] step" nemotron/logs/nemo-fullft.log | tail -20; echo "r2 (global = ${RESUME_STEP:-?} + r2 step):"; grep -hE "^\[eval\] step" $L | tail -20
say "serving"
MODEL=/srv/scratch/bimrose2/$R/best_model NAME=nemoft PORT=8601 GPUS=0,1,2,3 TP=4 MLEN=16384 SEQS=256 GMU=0.85 \
  setsid bash $V > nemotron/logs/vllm-nemoft.log 2>&1 < /dev/null &
FT=$!
NAME=nemobase PORT=8600 GPUS=4,5,6,7 TP=4 MLEN=24576 SEQS=256 GMU=0.88 setsid bash $V > nemotron/logs/vllm-nemobase-b.log 2>&1 < /dev/null &
BS=$!
for p in 8601 8600; do
  ok=0; for i in $(seq 1 180); do curl -s -m 5 http://127.0.0.1:$p/health >/dev/null && { ok=1; break; }; sleep 20; done
  [ $ok = 1 ] || { say "server :$p never ready"; }
done
say "servers up (ft pgid $FT, base pgid $BS)"
NAME=nemoft PORT=8601 MTOK=2400 BENCHES="real benchb full" WORKERS=16 bash nemotron/eval_nemo.sh > nemotron/logs/eval_nemoft.log 2>&1 &
E1=$!
NAME=nemobase PORT=8600 MTOK=16000 BENCHES=full WORKERS=24 bash nemotron/eval_nemo.sh > nemotron/logs/eval_nemobase_full3.log 2>&1 &
E2=$!
wait $E1; say "fine-tune eval generation done"; kill -- -$FT 2>/dev/null
wait $E2; say "zero-shot synthetic generation done"; kill -- -$BS 2>/dev/null
say "POST_SFT DONE"
