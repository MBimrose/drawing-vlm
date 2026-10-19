#!/bin/bash
# Nemotron-3.5 eval on serv-19 (was serv-20) against an ALREADY RUNNING vLLM server (run_vllm_nemotron_serv20.sh, GPUs 4-7):
# gen_openai_bo.py K=8 (draw 0 greedy + 7 at T 0.7 / top_p 0.95, think mode, the e55 system/user prompt), then
# score_partials.py (16 workers, exec 60 s, IoU 90 s, default --accept 0.8) + consistency_rerank.py
# = results/bench_b/score_vote_s20.sh.  Benches: real = ext_bench_dw423_perm (144), benchb = bench_b (280),
# full = fullpool_dw423 (1,027).
#   NAME=nemobase PORT=8600 MTOK=16000 BENCHES="real benchb" setsid bash eval_nemo.sh > log 2>&1 &
# PREFILL="<think>\n1." (2026-10-17): assistant prefill forcing the numbered plan (nemoft skipped thinking on 22% of draws)
set -uo pipefail
cd /srv/scratch/bimrose2
NAME=${NAME:?}; PORT=${PORT:-8600}; MTOK=${MTOK:-2400}; O=${OUT:-nemotron/results}; TAG=${TAG:-$NAME}
mkdir -p $O nemotron/logs
say() { echo "$(date '+%m-%d %H:%M') $*"; }
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
curl -s -m 5 http://127.0.0.1:$PORT/health >/dev/null || { say "no server on :$PORT"; exit 2; }
for b in ${BENCHES:-real benchb}; do
  case $b in
    real)   BENCH=mech_benchmarks/ext_bench_dw423_perm ;;
    benchb) BENCH=mech_benchmarks/bench_b ;;
    full)   BENCH=mech_benchmarks/fullpool_dw423 ;;
  esac
  STEM=$O/${b}_$TAG
  if [ ! -f $STEM.GEN_DONE ]; then
    say "gen $b -> $STEM (max_tokens $MTOK)"
    GP=(); for i in 0 1 2 3; do
      .venv/bin/python train_v14/geom/gen_openai_bo.py --bench $BENCH --base-url http://127.0.0.1:$PORT/v1 \
        --model $NAME --k 8 --temperature 0.7 --max-tokens $MTOK --shard $i --nshards 4 --workers ${WORKERS:-12} \
        --timeout 3600 ${PREFILL:+--prefill "$PREFILL"} --out $STEM > nemotron/logs/gen_${b}_$TAG.$i.log 2>&1 &
      GP+=($!); done; wait "${GP[@]}"
    nd=$(grep -h "DONE shard" nemotron/logs/gen_${b}_$TAG.*.log | wc -l)
    say "$b: $nd/4 shards done"; [ $nd = 4 ] && touch $STEM.GEN_DONE
  fi
  # serv-19 (2026-10-15): scoring runs on ccc0442 (train_v14/sbatch/nemo_score.sbatch waits for <stem>.GEN_DONE)
  if [ "${SCORE_LOCAL:-0}" = 1 ]; then
    ( W=${SW:-16} bash bench_b/code/score_vote_s20.sh $STEM $BENCH/gt_meshes_v15 > $STEM.scorevote.log 2>&1; say "scored $b: $(tail -1 $STEM.scorevote.log)" ) &
  fi
done
wait
say "EVAL DONE $TAG"
