#!/bin/bash
# In-dist full pipeline (2026-10-14): repair-chain block runner. Runs on serv-20 and ccc0442 alike.
# Work = blocks listed in blocks.txt (blocks/<chain>.bNN.json = 24 sorted keys of a start file). A block is claimed
# globally by an atomic mkdir in serv-20:/srv/scratch/bimrose2/indist_pipeline/claims/ (via ssh from the cluster),
# then run with vr_serve.py (the bench-B protocol, unchanged: K=16, 6 rounds, margin 0.1, max-tokens 6000, T 0.7)
# into out/<block>.jsonl. vr_serve skips keys already in its out file, so a killed runner's block is resumed by the next
# runner on the same host (claimed blocks are remembered in mine/, a flock in locks/ prevents two local runners on one block).
#   bash runner.sh <host.env> <base_url> <workers> <runner_id>
set -uo pipefail
ENVF=$1; URL=$2; W=$3; RID=$4
source $ENVF     # ROOT HT PY RPY SD BENCH VRS CLAIMS_SSH(empty on serv-20)
cd $ROOT; mkdir -p out done mine locks logs failed
CLAIMS=/srv/scratch/bimrose2/indist_pipeline/claims
say() { echo "$(date '+%m-%d %H:%M:%S') [$HT/$RID] $*"; }
remote() {   # run a command in the claims dir (locally on serv-20, by ssh from the cluster); retries on ssh failure
  local i; for i in 1 2 3 4 5; do
    if [ -z "$CLAIMS_SSH" ]; then (mkdir -p $CLAIMS; cd $CLAIMS && bash -c "$1"); return; fi
    out=$(timeout 60 ssh -o BatchMode=yes -o ConnectTimeout=20 $CLAIMS_SSH "mkdir -p $CLAIMS; cd $CLAIMS && $1"); rc=$?
    [ $rc != 255 ] && [ $rc != 124 ] && { echo "$out"; return 0; }
    sleep 20; done; return 1
}
run_block() {
  local b=$1 want n try
  want=$(python3 -c "import json,sys; print(len(json.load(open(sys.argv[1]))))" blocks/$b.json)
  for try in 1 2 3; do
    say "block $b try $try ($want keys)"
    l0=$(cat logs/blk_$b.log 2>/dev/null | wc -l)
    $PY $VRS --bench $BENCH --picks blocks/$b.json --base-url $URL --model rp3 --k 16 --rounds 6 --margin 0.1 \
      --max-tokens 6000 --workers $W --py $PY --rpy $RPY --script-dir $SD --out out/$b.jsonl >> logs/blk_$b.log 2>&1
    # an endpoint failure makes vr_serve write a record with an empty round (no repair proposals): drop such records, redo them
    if tail -n +$((l0 + 1)) logs/blk_$b.log | grep -q "endpoint .* failed"; then
      python3 $ROOT/drop_empty_rounds.py out/$b.jsonl | sed "s/^/[$b] /"; want=$((want + 0)); fi
    n=$(cat out/$b.jsonl 2>/dev/null | wc -l)
    [ "$n" -ge "$want" ] && break
    say "block $b incomplete $n/$want"; sleep 30
  done
  if [ "$n" -ge "$want" ]; then touch done/$b; remote "touch $b/DONE_$HT" >/dev/null; say "block $b DONE ($n)"
  else touch failed/$b; say "block $b FAILED $n/$want"; fi
}
while :; do
  ran=0; pending=0; cand=()
  for b in $(cat blocks.txt); do
    [ -f done/$b ] || [ -f failed/$b ] && continue
    pending=1
    [ -s blocks/$b.json ] || continue
    if [ -f mine/$b ]; then                       # resume an unfinished block of this host if no local runner holds it
      exec 9>locks/$b.lock
      if flock -n 9; then run_block $b; ran=1; exec 9>&-; break; fi
      exec 9>&-; continue
    fi
    cand+=($b)
  done
  [ $ran = 1 ] && continue
  [ $pending = 0 ] && { say "nothing left"; exit 0; }
  [ -f STOP_$HT ] && { say "STOP file: no new claims"; exit 0; }
  if [ ${#cand[@]} -gt 0 ]; then
    taken=" $(remote "ls" | tr '\n' ' ') "; free=()
    for x in "${cand[@]}"; do [[ "$taken" == *" $x "* ]] || free+=($x); done
    b=""; [ ${#free[@]} -gt 0 ] && b=$(remote "for x in ${free[*]}; do mkdir \$x 2>/dev/null && { echo $HT > \$x/host; echo \$x; break; }; done")
    if [ -n "$b" ] && [ -s blocks/$b.json ]; then
      touch mine/$b; exec 9>locks/$b.lock; flock -n 9 && run_block $b; exec 9>&-; continue
    fi
  fi
  sleep 120
done
