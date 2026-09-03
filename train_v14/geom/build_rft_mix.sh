#!/usr/bin/env bash
# Build a mixed RFT shard directory: base tier shards + the real-geometry tier
# shards linked REPEAT times, so the shard-uniform mixer upweights the small
# real tier without code changes.   build_rft_mix.sh <out_dir> <base_shards> <real_shards> <repeat>
set -euo pipefail
OUT=$1; BASE=$2; REAL=$3; REP=${4:-8}
mkdir -p "$OUT"; rm -f "$OUT"/rft-*.tar
i=0
for f in "$BASE"/rft-*.tar; do ln -s "$(readlink -f "$f")" "$OUT/rft-$(printf %05d $i).tar"; i=$((i+1)); done
nb=$i
for r in $(seq 1 "$REP"); do for f in "$REAL"/rft-*.tar; do ln -s "$(readlink -f "$f")" "$OUT/rft-$(printf %05d $i).tar"; i=$((i+1)); done; done
echo "$OUT: $nb base shards + $((i-nb)) real-shard links (repeat=$REP) = $i"
