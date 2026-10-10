#!/bin/bash
# Held-out eval of GRPO adapters on serv-20 (2026-10-06), one GPU, sequential over models.
#   bash train_v14/serv19/grpo_eval.sh <gpu> <port> <name>=<adapter dir|base> [<name>=<adapter> ...]
# Per model: merge the LoRA into e55 (CPU) -> vLLM on <gpu> -> K=8 (draw 0 greedy, T=0.7) think-mode
# draws on three held-out benches -> partials under results/grpo_eval/<bench>_<name>.shard*.
#   real    mech_benchmarks/ext_bench_dw423_perm   (144 real human-designed parts; the target)
#   famheld fp/h6/bench_held2                       (200 held-out family parts)
#   indh    mech_benchmarks/fullpool_dw423 + fp/h6/indist_held_keys_s48.txt
#           (259 in-dist parts the indist arm never samples through step 48)
# Scoring runs on the cluster CPU node (score_generic.sbatch), not here: serv-20 CPUs carry the arms.
# "base" = e55 itself through the identical path (the control).
set -uo pipefail
cd /srv/scratch/bimrose2
GPU=${1:?gpu}; PORT=${2:?port}; shift 2
E55=/srv/scratch/bimrose2/runs/e55-rft-real-u5-gt-dw423/final
O=results/grpo_eval; mkdir -p $O logs tmp
say() { echo "$(date '+%m-%d %H:%M') $*"; }
for spec in "$@"; do
  name=${spec%%=*}; ad=${spec#*=}
  if [ "$ad" = base ]; then MODEL=$E55
  else
    MODEL=runs/merged_$name
    if [ ! -f $MODEL/config.json ]; then
      say "merging $ad -> $MODEL"
      CUDA_VISIBLE_DEVICES= .venv/bin/python train_v14/geom/merge_grpo_lora.py --ckpt $E55 --adapter $ad \
        --out $MODEL --model-base /srv/scratch/bimrose2/models/Qwen3.8-27B > logs/merge_$name.log 2>&1 \
        || { say "merge failed $name"; tail -5 logs/merge_$name.log; continue; }
    fi
    MODEL=/srv/scratch/bimrose2/$MODEL
  fi
  say "serving $name on GPU $GPU :$PORT"
  CUDA_VISIBLE_DEVICES=$GPU DP=1 SEQS=128 PORT=$PORT MODEL=$MODEL NAME=$name \
    setsid bash train_v14/serv19/run_vllm_e55_serv20.sh > logs/vllm-geval-$name.log 2>&1 < /dev/null &
  VPID=$!
  ok=0; for i in $(seq 1 120); do curl -s -m 5 http://127.0.0.1:$PORT/health >/dev/null && { ok=1; break; }; sleep 15; done
  [ $ok = 1 ] || { say "vLLM never ready for $name"; tail -20 logs/vllm-geval-$name.log; kill -- -$VPID 2>/dev/null; continue; }
  for b in ${BENCHES:-real famheld indh}; do
    case $b in
      real)    BENCH=mech_benchmarks/ext_bench_dw423_perm; KEYS=() ;;
      famheld) BENCH=fp/h6/bench_held2; KEYS=() ;;
      indh)    BENCH=mech_benchmarks/fullpool_dw423; KEYS=(--keys fp/h6/indist_held_keys_s48.txt) ;;
    esac
    GP=()
    for i in 0 1 2 3; do
      .venv/bin/python train_v14/geom/gen_openai_bo.py --bench $BENCH "${KEYS[@]}" --base-url http://127.0.0.1:$PORT/v1 \
        --model $name --k 8 --temperature 0.7 --shard $i --nshards 4 --workers 12 \
        --out $O/${b}_$name > logs/geval_${b}_$name.$i.log 2>&1 &
      GP+=($!)
    done; wait "${GP[@]}"
    say "$name $b: $(grep -h DONE logs/geval_${b}_$name.*.log | wc -l)/4 shards done"
  done
  kill -- -$VPID 2>/dev/null; sleep 20; pkill -u bimrose2 -f "served-model-name $name[ ]" 2>/dev/null; sleep 10
  touch $O/GEN_DONE_$name; say "GEN DONE $name"
done
say "GRPO EVAL ALL DONE"
