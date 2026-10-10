#!/bin/bash
# Expert iteration round 2 (2026-10-09), stage 1 on serv-20: K=16 samples of the search policy on TRAINING parts.
#   setsid nohup bash cycle2/gen_driver.sh <adapter dir> <tag> > cycle2/logs/gen_driver.log 2>&1 < /dev/null &
# Policy = e55 + LoRA adapter merged (same merge path as grpo_eval.sh), vLLM DP=3 on GPUs $GPUS (default 1,2,5;
# GPU 1 carries another user's ~18 GB -> GMU 0.85). Draw 0 greedy + 15 draws at T=1.0 / top_p 0.95, 2400 tokens
# (= round 1, results/guide/v3/gen_v3.sh). Two client streams of 24 workers keep the replicas busy.
# Scoring is NOT done here (serv-20 CPUs carry the RL arms): the cluster job cycle2/score_loop.sbatch pulls the partials.
set -uo pipefail
cd /srv/scratch/bimrose2
AD=${1:?adapter}; TAG=${2:?tag}
GPUS=${GPUS:-1,2,5}; NDP=$(echo $GPUS | tr ',' '\n' | wc -l); PORT=${PORT:-8610}
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
E55=/srv/scratch/bimrose2/runs/e55-rft-real-u5-gt-dw423/final
M=runs/merged_cyc2_$TAG
say() { echo "$(date '+%m-%d %H:%M') $*"; }
if [ ! -f $M/config.json ]; then
  say "merging $AD -> $M"
  CUDA_VISIBLE_DEVICES= .venv/bin/python train_v14/geom/merge_grpo_lora.py --ckpt $E55 --adapter $AD --out $M \
    --model-base /srv/scratch/bimrose2/models/Qwen3.8-27B > cycle2/logs/merge_$TAG.log 2>&1 || { say "merge failed"; exit 1; }
fi
say "serving $M on GPUs $GPUS (DP $NDP) :$PORT"
CUDA_VISIBLE_DEVICES=$GPUS DP=$NDP SEQS=256 GMU=0.85 PORT=$PORT MODEL=/srv/scratch/bimrose2/$M NAME=$TAG \
  setsid bash train_v14/serv19/run_vllm_e55_serv20.sh > cycle2/logs/vllm-gen-$TAG.log 2>&1 < /dev/null &
VPID=$!; echo $VPID > cycle2/logs/vllm-gen-$TAG.pgid
ok=0; for i in $(seq 1 160); do curl -s -m 5 http://127.0.0.1:$PORT/health >/dev/null && { ok=1; break; }; sleep 15; done
[ $ok = 1 ] || { say "vLLM never ready"; tail -30 cycle2/logs/vllm-gen-$TAG.log; kill -- -$VPID; exit 1; }
say "vLLM up"
declare -A BENCH=( [c4]=fp/h6/rft_corpus4 [c2]=mech_benchmarks/rft_corpus2_dw423 [c1]=mech_benchmarks/rft_corpus_dw423
                   [rp2]=mech_benchmarks/rft_realpool_v2 )
gen() {  # set (A_c4 ...) -> cycle2/gen/<set>_<tag>.shard0.json.partial.json
  local s=$1 c=${1#*_}
  .venv/bin/python train_v14/geom/gen_openai_bo.py --bench ${BENCH[$c]} --keys cycle2/keys/$s.txt \
    --base-url http://127.0.0.1:$PORT/v1 --model $TAG --k 16 --temperature 1.0 --workers ${WORKERS:-24} \
    --out cycle2/gen/${s}_$TAG > cycle2/logs/gen_${s}_$TAG.log 2>&1
  say "gen $s: $(tail -1 cycle2/logs/gen_${s}_$TAG.log)"; touch cycle2/gen/GEN_DONE_${s}_$TAG
}
( gen A_c4; gen A_c1; gen C_c4; gen C_c1 ) &
P1=$!
( gen A_c2; gen B_rp2; gen C_c2 ) &
P2=$!
wait $P1 $P2
touch cycle2/gen/GEN_ALL_DONE_$TAG
say "GEN ALL DONE (vLLM left up for rationalization unless KEEP=0)"
[ "${KEEP:-1}" = 0 ] && kill -- -$VPID
