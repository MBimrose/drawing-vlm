#!/usr/bin/env bash
# Daily trace sync: pull newly generated traces from wpk-serv-09 and rebuild
# the training index. Safe while training runs: dataloader workers hold the
# old index in memory, and the JSON is replaced atomically — only runs that
# START after a sync see the new traces. The eval cache (eval_cache_v14.pkl)
# is deliberately NOT rebuilt so validation stays frozen and comparable.
set -uo pipefail

SRC=wpk-serv-09.mechse.illinois.edu:/srv/scratch/bimrose2/step_to_drw/wds_dataset/traces_v14/
DST=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/step_to_drw/wds_dataset/traces_v14/
VENV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/.venv
HERE="$(cd "$(dirname "$0")" && pwd)"
LOG=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/trace_sync.log

{
  echo "=== trace sync $(date -Is)"
  before=$(ls "$DST" | grep -c "_trace.txt$" || true)
  rsync -a --timeout=600 -e "ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new" "$SRC" "$DST"
  rc=$?
  after=$(ls "$DST" | grep -c "_trace.txt$" || true)
  echo "rsync rc=$rc  traces: $before -> $after (+$((after - before)))"
  if [ "$rc" -eq 0 ] && [ "$after" -gt "$before" ]; then
    "$VENV/bin/python" "$HERE/build_trace_index.py"
  else
    echo "index rebuild skipped (rc=$rc, no new traces)"
  fi
  echo "=== done $(date -Is)"
} >> "$LOG" 2>&1
