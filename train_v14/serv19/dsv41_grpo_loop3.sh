#!/usr/bin/env bash
# DeepSeek-V4.1-Flash GUIDED GRPO, run dsgrpo3 (2026-10-07): everything on serv-20 (GPUs 0,1,2,7 via
# serv19/hcfg_serv20.sh + serv19/dsv41_grpo_host.sh; NEVER GPUs 3-6), starting from dsgrpo2's adapter (INIT_ADAPTER),
# fixed trainer, T0 regime (effort 25, 30k tokens, <= 3 calls). Guidance: the guide banks (bankv2_c4/bankv2_c2/bank_c1,
# GT-verified best-known programs on hard real training parts) are rationalized ONCE in DeepSeek's own voice
# (dsv41_t0_rationalize.py, run with the round-0 server); training parts = rationalized bank parts; a part's bank program
# joins its group as an extra member (true IoU) when it beats all G draws by >= 0.05 (dsv41_t0_rows.py --bank).
# Held-out evals every 2 rounds, paired vs dsgrpo2's vanilla u0 (BASE_EVAL). Guard: exec or code rate < 0.85 -> stop.
# Launch (serv-20): NAME=dsgrpo3 INIT_ADAPTER=<adapter dir on serv-20> setsid nohup bash dsv41_grpo_loop3.sh > /dev/null 2>&1 &
set -uo pipefail
NAME=${NAME:-dsgrpo3}; ROUNDS=${ROUNDS:-8}; P=${P:-48}; K=${K:-4}; MAXTOK=${MAXTOK:-30000}
EVAL_EVERY=${EVAL_EVERY:-2}; START=${START:-0}; EVAL_N=${EVAL_N:-0}; GATE=${GATE:-0.22}
LR=${LR:-1.5e-5}; N_BANK=${N_BANK:-1000}; MIN_RATE=${MIN_RATE:-0.85}
INIT_ADAPTER=${INIT_ADAPTER:?set INIT_ADAPTER}; BASE_EVAL=${BASE_EVAL:-/srv/scratch/bimrose2/grpo_ds/dsgrpo2/eval_u00/ep.jsonl}
GHOST=wpk-serv-20.mechse.illinois.edu; HCFG=/srv/scratch/bimrose2/train_v14/serv19/hcfg_serv20.sh; TRAIN_MAXLEN=${TRAIN_MAXLEN:-34000}
SDV=/srv/scratch/bimrose2; S19=$GHOST; RUN=$SDV/grpo_ds/$NAME; G19=$SDV/grpo_ds/$NAME
PY=$SDV/.venv/bin/python; GEOM=$SDV/train_v14/geom; URL=http://127.0.0.1:8500
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=$SDV/train_v14:$GEOM
mkdir -p $RUN; LOG=$RUN/loop.log; echo $$ > $RUN/driver.pid
say() { echo "$(date '+%m-%d %H:%M:%S') $*" >> $LOG; }
on19() { timeout ${TMO:-300} ssh -o BatchMode=yes $S19 "HCFG=$HCFG bash $SDV/train_v14/serv19/dsv41_grpo_host.sh $*"; }
die() { say "FATAL: $*"; TMO=600 on19 stop >> $LOG 2>&1; exit 1; }
chk_stop() { [ -e $RUN/STOP ] && { say "STOP file -> stopping server and exiting"; TMO=600 on19 stop >> $LOG 2>&1; exit 0; }; }
poll19() {
  for i in $(seq 1 $(( $3 * 2 ))); do
    timeout 60 ssh -o BatchMode=yes $S19 "test -e $1" && return 0
    timeout 60 ssh -o BatchMode=yes $S19 "test -e $2" && return 1
    sleep 30
  done; return 2; }
serve() {
  # idempotent: a server already answering on our port (left by an interrupted driver) must hold THIS model
  if on19 up; then
    if [ "$(cat $RUN/served_model 2>/dev/null)" = "$1" ]; then say "server already up with $1"; return 0; fi
    TMO=900 on19 stop >> $LOG 2>&1 || return 1
  fi
  echo "$1" > $RUN/served_model
  MAXLEN=65536 on19 serve $1 $G19/serve_$2.log >> $LOG 2>&1
  for i in $(seq 1 120); do on19 up && { say "server up ($2) after $((i/2)) min"; return 0; }; sleep 30; done
  return 1; }

ssh -o BatchMode=yes $S19 "mkdir -p $G19"
# trainer overrides for this run: the server renders effort "low" as "Reasoning Effort: 25"; T0 samples at T=1.0
printf 'CUDA_VISIBLE_DEVICES=0,1,2,7\nEFFORT=25\nLOGIT_TEMP=1.0\nMAXLEN=%s\nLR=%s\n' $TRAIN_MAXLEN $LR > $RUN/train.env
if [ ! -s $RUN/parts_eval.tsv ]; then
  $PY $GEOM/dsv41_grpo_parts.py eval $RUN/parts_eval.tsv $SDV/mech_benchmarks/ext_bench_dw423_perm >> $LOG 2>&1
  [ "$EVAL_N" -gt 0 ] && { head -n $EVAL_N $RUN/parts_eval.tsv > $RUN/e.tsv; mv $RUN/e.tsv $RUN/parts_eval.tsv; }
fi
[ -s $RUN/progress.tsv ] || echo -e "round\tmean_reward\tbest_of_g\tfirst_draw\texec\ttrunc\tcalls\tmed_tokens\tfrontier\trows\tminutes" > $RUN/progress.tsv
say "=== $NAME (guided GRPO from $INIT_ADAPTER, serv-20 GPUs 0,1,2,7): rounds $START..$ROUNDS P=$P K=$K max_tokens=$MAXTOK lr $LR eval every $EVAL_EVERY ==="
for r in $(seq $START $ROUNDS); do
  T0=$(date +%s); RD=$RUN/r$(printf %02d $r); mkdir -p $RD
  MODEL=/scratch/bimrose2/dsv41_ft/${NAME}_u$r
  if [ $r = 0 ] && ! ssh -o BatchMode=yes $S19 "test -e $MODEL/MERGED"; then
    on19 merge $INIT_ADAPTER $MODEL $G19/merge_u0.log 1 >> $LOG 2>&1
    poll19 $MODEL/MERGED $MODEL.FAILED 60 || die "round-0 control merge failed"
  fi
  chk_stop
  # resume shortcut: no server needed when this round's episodes (and its eval, if due) are already complete
  NEED=1; NE=$(cat $RD/ep.jsonl 2>/dev/null | wc -l); NV=$(cat $RUN/eval_u$(printf %02d $r)/ep.jsonl 2>/dev/null | wc -l)
  if [ -e $RUN/bank_ds.DONE ] && [ $NE -ge $((P*K)) ] && { [ $((r % EVAL_EVERY)) != 0 ] && [ $r != $ROUNDS ] || [ $NV -ge $(wc -l < $RUN/parts_eval.tsv) ]; }; then
    NEED=0; say "round $r: episodes/eval already complete -> no server"
  fi
  if [ $NEED = 1 ]; then
    say "round $r: serving u$r ($MODEL)"
    serve $MODEL u$r || die "server for u$r never came up (see serv-19 $G19/serve_u$r.log)"
  fi
  if [ ! -e $RUN/bank_ds.DONE ]; then
    say "round $r: rationalizing $N_BANK bank programs in DeepSeek's voice"
    $PY $GEOM/dsv41_t0_rationalize.py --mode write --n $N_BANK --base-url $URL --workers 48 --out $RUN/bank_ds.json \
      --banks c4:$SDV/fp/guide/bankv2_c4.json:$SDV/fp/h6/rft_corpus4,c2:$SDV/fp/guide/bankv2_c2.json:$SDV/mech_benchmarks/rft_corpus2_dw423,c1:$SDV/fp/guide/bank_c1.json:$SDV/mech_benchmarks/rft_corpus_dw423 \
      > $RUN/rationalize.log 2>&1 && touch $RUN/bank_ds.DONE || die "rationalization failed"
    say "round $r: $(tail -n 1 $RUN/rationalize.log)"
    $PY -c "
import json, random
b = json.load(open('$RUN/bank_ds.json')); rows = sorted((v['bench'], k) for k, v in b.items() if v['status'] == 'ok')
random.Random(0).shuffle(rows); open('$RUN/parts_all.tsv', 'w').write(''.join(f'{x}\\t{y}\\n' for x, y in rows)); print(len(rows), 'bank parts')" >> $LOG 2>&1
  fi
  EVR=""
  if [ $((r % EVAL_EVERY)) = 0 ] || [ $r = $ROUNDS ]; then
    EVR=$RUN/eval_u$(printf %02d $r); mkdir -p $EVR
    $PY $GEOM/dsv41_t0_rollout.py --parts $RUN/parts_eval.tsv --base-url $URL --k 1 --max-tokens $MAXTOK \
      --workers 48 --score-workers 8 --out $EVR/ep > $EVR/ep.log 2>&1 &
    EGEN=$!
    say "round $r: eval episodes started (pid $EGEN)"
  fi
  if [ $r -lt $ROUNDS ]; then
    $PY $GEOM/dsv41_grpo_parts.py slice $RUN/parts_all.tsv $r $P $RD/parts.tsv >> $LOG 2>&1
    $PY $GEOM/dsv41_t0_rollout.py --parts $RD/parts.tsv --base-url $URL --k $K --max-tokens $MAXTOK \
      --workers 48 --score-workers 8 --out $RD/ep > $RD/ep.log 2>&1 || say "round $r: rollout exit $?"
    say "round $r: episodes done ($(tail -n 1 $RD/ep.log))"
  fi
  if [ -n "$EVR" ]; then
    wait $EGEN; say "round $r: eval done ($(tail -n 1 $EVR/ep.log))"
    $PY $GEOM/dsv41_t0_eval_summary.py --evals "$RUN/eval_u*/ep.jsonl" --base $BASE_EVAL \
      --out $RUN/eval_summary.json > $RUN/eval_summary.txt 2>&1
    say "held-out: $(tail -n 1 $RUN/eval_summary.txt)"
  fi
  [ $NEED = 1 ] && { TMO=900 on19 stop >> $LOG 2>&1 || die "could not free GPUs"; rm -f $RUN/served_model; }
  if [ $r = 0 ]; then
    OK=$($PY -c "import json; print(int([x for x in json.load(open('$RUN/eval_summary.json')) if x['policy'] == 0][0]['mean'] >= $GATE))")
    [ "$OK" = 1 ] || { say "GATE: u0 held-out mean below $GATE -> regime not reproduced, stopping before any update"; exit 0; }
  fi
  [ $r = $ROUNDS ] && { say "=== finished"; cat $RUN/eval_summary.txt >> $LOG; break; }
  $PY $GEOM/dsv41_t0_rows.py --eps $RD/ep.jsonl --tier $RD/tier --stats $RD/stats.json --max-row-tokens $TRAIN_MAXLEN --bank $RUN/bank_ds.json \
    > $RD/rows.log 2>&1 || die "rows failed"
  say "round $r: $(cat $RD/rows.log)"
  BAD=$($PY -c "
import json; s=json.load(open('$RD/stats.json')); b=json.load(open('$RUN/r00/stats.json'))
print(int(s['exec_rate'] < $MIN_RATE or s['code_rate'] < $MIN_RATE or (s['trunc_rate'] > 0.6 and s['trunc_rate'] > 2*b['trunc_rate']+0.1)))")
  ROWS=$($PY -c "import json; print(json.load(open('$RD/stats.json'))['rows'])")
  $PY -c "
import json; s=json.load(open('$RD/stats.json'))
print('\t'.join(['$r']+['%.3f'%s[k] for k in ('mean_reward','best_of_g','first_draw','exec_rate','trunc_rate','calls_per_episode')]+[str(s['median_completion_tokens']),'%.2f'%s['frontier_frac'],str(s['rows'])]), end='\t')" >> $RUN/progress.tsv
  [ "$BAD" = 1 ] && { echo "DEGENERATE" >> $RUN/progress.tsv; say "round $r: policy degenerated -> stopping"; exit 0; }
  chk_stop
  PREV=$INIT_ADAPTER; [ $r -gt 0 ] && PREV=$G19/adapter_u$r
  if [ "$ROWS" -gt 0 ]; then
    rsync -a $RD/tier/ $S19:$G19/tier_u$r/
    on19 train $G19/tier_u$r $G19/adapter_u$((r+1)) $PREV $G19/train_u$((r+1)).log >> $LOG 2>&1
    poll19 $G19/adapter_u$((r+1))/DONE $G19/adapter_u$((r+1))/FAILED 300; rc=$?
    [ $rc = 0 ] || die "update u$((r+1)) failed/timed out (rc $rc; serv-19 $G19/train_u$((r+1)).log)"
    say "round $r: update done ($(ssh -o BatchMode=yes $S19 "grep '\[grpo\] {' $G19/train_u$((r+1)).log" | cut -c1-300))"
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
