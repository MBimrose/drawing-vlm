#!/usr/bin/env bash
# DeepSeek-V4.1-Flash on-policy GRPO loop, LOW-RESOURCE (2026-10-06). Driver runs on serv-20 (CPU only: rollout HTTP
# client + execute/IoU scoring, <= 16 single-thread workers); every GPU stage runs on serv-19 GPUs 4-7 via
# dsv41_grpo_s19.sh (serve vLLM :8200 <-> LoRA update <-> FP8 merge, alternating on the same 4 GPUs).
# Round r (policy u_r = base + r updates):
#   serve u_r -> [eval: 1 draw x held-out real bench, every EVAL_EVERY rounds] + G draws x P hard real training parts
#   -> stop server -> score (exec 60 s / IoU 90 s) -> group advantages -> rows -> LoRA pass on serv-19 -> merge -> r+1
# Launch (on serv-20):  NAME=dsgrpo1 setsid nohup bash dsv41_grpo_loop.sh > /dev/null 2>&1 < /dev/null &
# Stop:  touch $RUN/STOP (exits at the next stage boundary and stops the server)   Monitor: $RUN/loop.log, $RUN/progress.tsv
set -uo pipefail
NAME=${NAME:-dsgrpo1}; ROUNDS=${ROUNDS:-8}; P=${P:-48}; K=${K:-4}; TEMP=${TEMP:-0.8}; MAXTOK=${MAXTOK:-16384}
EVAL_EVERY=${EVAL_EVERY:-2}; START=${START:-0}; WORKERS=${WORKERS:-16}; EVAL_N=${EVAL_N:-0}
SDV=/srv/scratch/bimrose2; S19=wpk-serv-19.mechse.illinois.edu; RUN=$SDV/grpo_ds/$NAME; G19=$SDV/grpo_ds/$NAME
PY=$SDV/.venv/bin/python; GEOM=$SDV/train_v14/geom; URL=http://$S19:8200/v1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=$SDV/train_v14:$GEOM
mkdir -p $RUN; LOG=$RUN/loop.log; echo $$ > $RUN/driver.pid
say() { echo "$(date '+%m-%d %H:%M:%S') $*" >> $LOG; }
on19() { timeout ${TMO:-300} ssh -o BatchMode=yes $S19 "bash $SDV/train_v14/serv19/dsv41_grpo_s19.sh $*"; }
die() { say "FATAL: $*"; TMO=600 on19 stop >> $LOG 2>&1; exit 1; }
chk_stop() { [ -e $RUN/STOP ] && { say "STOP file -> stopping server and exiting"; TMO=600 on19 stop >> $LOG 2>&1; exit 0; }; }
poll19() {  # poll19 <file that means done> <file that means failed> <max minutes>
  for i in $(seq 1 $(( $3 * 2 ))); do
    timeout 60 ssh -o BatchMode=yes $S19 "test -e $1" && return 0
    timeout 60 ssh -o BatchMode=yes $S19 "test -e $2" && return 1
    sleep 30
  done; return 2; }
serve() {  # serve <model dir|base> <tag>
  on19 serve $1 $G19/serve_$2.log >> $LOG 2>&1
  for i in $(seq 1 120); do on19 up && { say "server up ($2) after $((i/2)) min"; return 0; }; sleep 30; done
  return 1; }
score() {  # score <round dir> <prefix> <parts.tsv>
  for b in $(cut -f1 $3 | sort -u); do
    bn=$(basename $b)
    nice -n 10 $PY $GEOM/score_partials.py --partials "$1/${2}_$bn.partial.json" --gt-dir $b/gt_meshes_v15 \
      --out $1/scored_${2}_$bn.json --workers $WORKERS --exec-timeout 60 --iou-timeout 90 --accept 0 >> $1/score_$2.log 2>&1
  done; }

ssh -o BatchMode=yes $S19 "mkdir -p $G19"
if [ ! -s $RUN/parts_all.tsv ]; then
  $PY $GEOM/dsv41_grpo_parts.py train $RUN/parts_all.tsv $SDV/fp/h6/rft_corpus4:$SDV/fp/h6/real4_hard_keys.txt \
    $SDV/mech_benchmarks/rft_corpus2_dw423:$SDV/fp/h6/c2_hard_keys.txt >> $LOG 2>&1
  $PY $GEOM/dsv41_grpo_parts.py eval $RUN/parts_eval.tsv $SDV/mech_benchmarks/ext_bench_dw423_perm >> $LOG 2>&1
  [ "$EVAL_N" -gt 0 ] && { head -n $EVAL_N $RUN/parts_eval.tsv > $RUN/e.tsv; mv $RUN/e.tsv $RUN/parts_eval.tsv; }
fi
[ -s $RUN/progress.tsv ] || echo -e "round\tmean_reward\tbest_of_g\tfirst_draw\texec\ttrunc\tmed_tokens\tfrontier\trows\tminutes" > $RUN/progress.tsv
say "=== $NAME: rounds $START..$ROUNDS P=$P K=$K T=$TEMP max_tokens=$MAXTOK eval every $EVAL_EVERY ==="
EVPID=""
for r in $(seq $START $ROUNDS); do
  T0=$(date +%s); RD=$RUN/r$(printf %02d $r); mkdir -p $RD
  MODEL=/scratch/bimrose2/dsv41_ft/${NAME}_u$r
  if [ $r = 0 ] && ! ssh -o BatchMode=yes $S19 "test -e $MODEL/MERGED"; then
    # round-0 control = the base in the SAME layout as every later policy (adapted attention tensors in BF16, listed in
    # ignored_layers) -- an FP8 requant would round an RL-sized delta away (see merge_dsv41_lora.py --bf16)
    on19 merge $SDV/grpo_ds/zero_template $MODEL $G19/merge_u0.log 0 >> $LOG 2>&1
    poll19 $MODEL/MERGED $MODEL.FAILED 60 || die "round-0 control merge failed"
  fi
  chk_stop
  say "round $r: serving u$r ($MODEL)"
  serve $MODEL u$r || die "server for u$r never came up (see serv-19 $G19/serve_u$r.log)"
  EVR=""
  if [ $((r % EVAL_EVERY)) = 0 ] || [ $r = $ROUNDS ]; then
    EVR=$RUN/eval_u$(printf %02d $r); mkdir -p $EVR
    $PY $GEOM/dsv41_grpo_rollout.py --parts $RUN/parts_eval.tsv --base-url $URL --model pol --k 1 --temperature $TEMP \
      --max-tokens $MAXTOK --workers 48 --out $EVR/roll > $EVR/roll.log 2>&1 &
    EGEN=$!
    say "round $r: eval rollouts started (pid $EGEN)"
  fi
  if [ $r -lt $ROUNDS ]; then
    $PY $GEOM/dsv41_grpo_parts.py slice $RUN/parts_all.tsv $r $P $RD/parts.tsv >> $LOG 2>&1
    $PY $GEOM/dsv41_grpo_rollout.py --parts $RD/parts.tsv --base-url $URL --model pol --k $K --temperature $TEMP \
      --max-tokens $MAXTOK --workers 48 --out $RD/roll > $RD/roll.log 2>&1 || say "round $r: rollout exit $?"
    say "round $r: rollouts done ($(tail -n 1 $RD/roll.log))"
  fi
  [ -n "$EVR" ] && { wait $EGEN; say "round $r: eval rollouts done ($(tail -n 1 $EVR/roll.log))"; }
  TMO=900 on19 stop >> $LOG 2>&1 || die "could not free GPUs 4-7"
  [ -n "$EVPID" ] && wait $EVPID
  if [ -n "$EVR" ]; then   # held-out scoring + summary in the background (overlaps the GPU update on serv-19)
    ( score $EVR roll $RUN/parts_eval.tsv
      B0=$RUN/eval_u00/scored_roll_ext_bench_dw423_perm.json
      [ -s $B0 ] && $PY $GEOM/dsv41_grpo_eval_summary.py --evals "$RUN/eval_u*/scored_roll_ext_bench_dw423_perm.json" --base $B0 \
        --out $RUN/eval_summary.json > $RUN/eval_summary.txt 2>&1 ) &
    EVPID=$!
  fi
  [ $r = $ROUNDS ] && { [ -n "$EVPID" ] && wait $EVPID; say "=== finished: eval summary"; cat $RUN/eval_summary.txt >> $LOG; break; }
  score $RD roll $RD/parts.tsv
  $PY $GEOM/dsv41_grpo_rows.py --roll $RD/roll.jsonl --scored "$RD/scored_roll_*.json" --tier $RD/tier --stats $RD/stats.json \
    --adv batchstd > $RD/rows.log 2>&1 || die "rows failed"
  say "round $r: $(cat $RD/rows.log)"
  # degeneration guard: exec collapse or reasoning blow-up vs round 0
  BAD=$($PY -c "
import json; s=json.load(open('$RD/stats.json')); b=json.load(open('$RUN/r00/stats.json'))
print(int(s['exec_rate'] < 0.5*b['exec_rate'] or (s['trunc_rate'] > 0.5 and s['trunc_rate'] > 2*b['trunc_rate']+0.1)))")
  ROWS=$($PY -c "import json; print(json.load(open('$RD/stats.json'))['rows'])")
  $PY -c "
import json; s=json.load(open('$RD/stats.json'))
print('\t'.join(['$r']+['%.3f'%s[k] for k in ('mean_reward','best_of_g','first_draw','exec_rate','trunc_rate')]+[str(s['median_completion_tokens']),'%.2f'%s['frontier_frac'],str(s['rows'])]), end='\t')" >> $RUN/progress.tsv
  [ "$BAD" = 1 ] && { echo "DEGENERATE" >> $RUN/progress.tsv; say "round $r: policy degenerated (exec collapse / truncation blow-up) -> stopping"; exit 0; }
  chk_stop
  PREV=-; [ $r -gt 0 ] && PREV=$G19/adapter_u$r
  if [ "$ROWS" -gt 0 ]; then
    rsync -a $RD/tier/ $S19:$G19/tier_u$r/
    on19 train $G19/tier_u$r $G19/adapter_u$((r+1)) $PREV $G19/train_u$((r+1)).log >> $LOG 2>&1
    poll19 $G19/adapter_u$((r+1))/DONE $G19/adapter_u$((r+1))/FAILED 240; rc=$?
    [ $rc = 0 ] || die "update u$((r+1)) failed/timed out (rc $rc; serv-19 $G19/train_u$((r+1)).log)"
    say "round $r: update done ($(ssh -o BatchMode=yes $S19 "tail -n 1 $G19/train_u$((r+1)).log" | cut -c1-300))"
    M=/scratch/bimrose2/dsv41_ft/${NAME}_u$((r+1))
    on19 merge $G19/adapter_u$((r+1)) $M $G19/merge_u$((r+1)).log >> $LOG 2>&1
    poll19 $M/MERGED $M.FAILED 120; rc=$?
    [ $rc = 0 ] || die "merge u$((r+1)) failed/timed out (rc $rc)"
    say "round $r: merged -> $M"
    ssh -o BatchMode=yes $S19 "rm -rf /scratch/bimrose2/dsv41_ft/${NAME}_u$r"
  else
    say "round $r: no trainable rows -> policy unchanged"
    [ $r = 0 ] && die "round 0 produced no rows"
    ssh -o BatchMode=yes $S19 "ln -sfn /scratch/bimrose2/dsv41_ft/${NAME}_u$r /scratch/bimrose2/dsv41_ft/${NAME}_u$((r+1)); ln -sfn $G19/adapter_u$r $G19/adapter_u$((r+1))"
  fi
  echo "$(( ($(date +%s) - T0) / 60 ))" >> $RUN/progress.tsv
  say "round $r done in $(( ($(date +%s) - T0) / 60 )) min"
done
say "=== loop exit"
