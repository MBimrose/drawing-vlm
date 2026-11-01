#!/bin/bash
# Kimi-trace A/B (2026-10-29): sample an arm's round-0 Glimmer (am-glimmer-ab-<arm>0 final) for its own RFT tier.
# 8 single-GPU vLLM servers; each lane claims jobs from amvlm/ab/jobs.txt (mkdir claim) and runs gen_openai_bo.py on
# them as 4 shards x WORKERS requests (draw 0 greedy + K-1 at T 0.7 / top_p 0.95, 2,400 tokens, e55 prompt), writing
# amvlm/ab/gen_<arm>/<job>.shard<i>.json.partial.json + <job>.GEN_DONE. Scoring + packing: train_v14/sbatch/ab_score.sbatch.
#   arm a (Kimi traces): glftpf.jinja ("1." thought prefill) as every Glimmer FT eval, but no reasoning parser and raw
#                        replies split by the channel tokens (gen_openai_bo --raw-channels glimmer), so think is kept
#                        (with the parser the prefilled thought came back empty: 0 / 1,152 real_glftpf candidates)
#   arm b (no traces):   glft.jinja, no reasoning parser (the parser drops replies that open directly in to=user)
# Host-agnostic: HOST=s19 serves through run_vllm_any_serv19.sh; HOST=cc (a campus-cluster job) through srv_exec.sh.
#   serv-19: ARM=b HOST=s19 setsid nohup bash amvlm/train_v14/serv19/ab_sample.sh > amvlm/ab/logs/sample_b.log 2>&1 &
set -uo pipefail
R=/srv/scratch/bimrose2; ARM=${ARM:?}; HOST=${HOST:-s19}; GPUS=${GPUS:-0 1 2 3 4 5 6 7}; PB=${PB:-8930}
# host-side paths (files, claims, logs): $R on serv-19, the Lustre mirror on the cluster; the commands keep $R (container)
HR=$R; [ $HOST = cc ] && HR=/projects/illinois/eng/ece/wpk/bimrose2/srvmirror
# round 2 (2026-10-31): RND=1 samples am-glimmer-ab-<arm>1 into gen_<TAG> (TAG=a2) over JOBS=amvlm/ab/jobs_r2.txt
RND=${RND:-0}; TAG=${TAG:-$ARM}
CKPT=${CKPT:-$R/amvlm/runs/am-glimmer-ab-${ARM}${RND}/final}; A=$HR/amvlm/ab; O=$A/gen_$TAG; OI=$R/amvlm/ab/gen_$TAG; mkdir -p $O/claims $A/logs
JOBS=${JOBS:-$A/jobs.txt}
case $ARM in
  a) TPL=$R/american_vlm/templates/glftpf.jinja; RP=""; GX="--raw-channels glimmer --raw-prefill 1.";;
  b) TPL=$R/american_vlm/templates/glft.jinja; RP=""; GX="";;
esac
say() { echo "$(date '+%m-%d %H:%M') $*"; }
if [ $HOST = cc ]; then
  DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; SX=$DV/train_v14/sbatch/srv_exec.sh; RUN="bash $SX"
  export LOCAL_TMP=/tmp/bimrose2_srv_${SLURM_JOB_ID:-ab} APPTAINERENV_CUDA_HOME=/software/cuda-13.0 APPTAINERENV_PREPEND_PATH=/software/cuda-13.0/bin
else RUN="bash -c"; fi
SPIDS=(); LC=""; trap 'for p in "${SPIDS[@]}"; do kill -TERM -- -$p 2>/dev/null; done; [ -n "$LC" ] && rm -rf "$LC"' EXIT
# cc: copy the final to node-local storage once (10-30: eight servers reading 108 GB each from Lustre at night were still
# loading weights when the health wait expired, so arm A's first sampling job produced nothing)
if [ $HOST = cc ] && [ "${STAGE:-1}" = 1 ]; then
  HC=$HR/amvlm/runs/am-glimmer-ab-${ARM}${RND}/final; need=$(du -sk $HC | cut -f1)
  for d in /tmp /dev/shm; do [ $(df -k --output=avail $d | tail -1) -gt $((need + 50000000)) ] && { LC=$d/bimrose2_ab_${ARM}${RND}; break; }; done
  [ -n "$LC" ] || { say "no local space for $((need / 1048576)) GB"; exit 2; }
  say "staging $HC -> $LC"; rsync -a $HC/ $LC/ || { say "staging failed"; exit 2; }; CKPT=$LC; say "staged"
fi
for g in $GPUS; do
  port=$((PB + g))
  if [ $HOST = cc ]; then
    APPTAINERENV_VLLM_PORT=$((29800 + 50 * g)) CUDA_VISIBLE_DEVICES=$g setsid bash $SX "vllm serve $CKPT --served-model-name ab \
      --host 127.0.0.1 --port $port --tensor-parallel-size 1 --trust-remote-code ${RP:+--reasoning-parser $RP} \
      --gpu-memory-utilization 0.88 --max-model-len 16384 --max-num-seqs 128 --limit-mm-per-prompt '{\"image\": 1, \"video\": 0}' \
      --chat-template $TPL" > $A/logs/vllm_${TAG}_$port.log 2>&1 < /dev/null &
  else
    (cd $R; MODEL=$CKPT NAME=ab GPUS=$g TP=1 PORT=$port RPARSER=$RP SEQS=128 GMU=0.88 VLLM_EXTRA="--chat-template $TPL" \
      setsid bash amvlm/train_v14/serv19/run_vllm_any_serv19.sh) > $A/logs/vllm_${TAG}_$port.log 2>&1 < /dev/null &
  fi
  SPIDS+=($!); sleep 20
done
lane() {
  local g=$1 port=$(($PB + $1)) ok=0 name bench k keys i GP
  for t in $(seq 1 ${HW:-480}); do curl -s -m 5 http://127.0.0.1:$port/health >/dev/null && { ok=1; break; }; sleep 15; done
  [ $ok = 1 ] || { say "lane $g: server never ready: $(tail -3 $A/logs/vllm_${TAG}_$port.log)"; return 1; }
  say "lane $g up :$port"
  while read -r name bench k keys; do
    [ -z "$name" ] && continue
    [ -f $O/$name.GEN_DONE ] && continue
    mkdir $O/claims/$name 2>/dev/null || continue
    say "lane $g gen $name ($bench, K=$k)"
    GP=(); for i in 0 1 2 3; do
      $RUN "cd $R; OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 .venv/bin/python train_v14/geom/gen_openai_bo.py --bench $bench \
        --base-url http://127.0.0.1:$port/v1 --model ab --k $k --temperature 0.7 --max-tokens 2400 --shard $i --nshards 4 \
        --workers ${WORKERS:-16} --timeout 3600 $GX ${keys:+--keys $keys} --out $OI/$name" > $A/logs/gen_${TAG}_$name.$i.log 2>&1 < /dev/null &
      GP+=($!); done; wait "${GP[@]}"
    n=$(grep -h "DONE shard" $A/logs/gen_${TAG}_$name.*.log | wc -l)
    if [ $n = 4 ]; then touch $O/$name.GEN_DONE; say "lane $g done $name"; else say "lane $g $name: $n/4 shards"; rmdir $O/claims/$name; fi
  done < $JOBS
}
LP=(); for g in $GPUS; do lane $g & LP+=($!); done
wait "${LP[@]}"; say "AB SAMPLE DONE $TAG: $(ls $O/*.GEN_DONE 2>/dev/null | wc -l)/$(grep -c . $JOBS) jobs"
