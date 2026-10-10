#!/bin/bash
# Run gt_search.py streams concurrently against an rp3 server. Usage: gts_streams.sh <spec file> <port> <py> <rpy> <script dir>
# spec line: "<corpus> <workers> <keys file> <out jsonl>" (paths relative to results/cycle2/search); '#' lines ignored.
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; O=$DV/results/cycle2/search; L=$DV/results/cycle2/logs
SPEC=$1; PORT=$2; PY=$3; RPY=$4; SD=$5
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
BD=$DV/train_v14/mech/benchmarks/data
declare -A BENCH=( [c4]=$BD/rft_corpus4 [c2]=$BD/rft_corpus2_dw423 [c1]=$BD/rft_corpus_dw423 [rp2]=$BD/rft_realpool_v2 )
PIDS=()
while read -r c w k o; do
  [ -z "$c" ] || [ "${c:0:1}" = "#" ] && continue
  $PY $DV/train_v14/geom/gt_search.py --bench ${BENCH[$c]} --starts $O/starts_$c.json --keys $O/$k \
    --base-url http://127.0.0.1:$PORT/v1 --model rp3 --k 8 --rounds 4 --workers $w --py $PY --rpy $RPY \
    --script-dir $SD --out $O/$o > $L/gts_${o%.jsonl}.log 2>&1 &
  PIDS+=($!); echo "$(date) stream $c $w $k -> $o (pid $!)"
done < $SPEC
wait "${PIDS[@]}"
echo "$(date) streams of $SPEC done"
