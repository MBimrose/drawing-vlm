#!/usr/bin/env bash
# Stage the 33 safetensors files holding Flash-Next's 102 GB n-gram table into
# /dev/shm (RAM, shared by all ranks on the node). Idempotent; ~1 min.
set -euo pipefail
M=${1:-/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/models/Qwen3.8-Flash-Next}
DST=${FLASHNEXT_PLE_DIR:-/dev/shm/flashnext_ple}
mkdir -p "$DST"
files=$(python3 -c "
import json,sys; d=json.load(open('$M/model.safetensors.index.json'))['weight_map']
print(' '.join(sorted({v for k,v in d.items() if 'ngram_embedding.shard_' in k})))")
n=0
for f in $files; do
  if [ ! -f "$DST/$f" ] || [ "$(stat -c %s "$DST/$f")" != "$(stat -c %s "$M/$f")" ]; then
    cp "$M/$f" "$DST/$f.tmp" && mv "$DST/$f.tmp" "$DST/$f"; n=$((n+1))
  fi
done
echo "[stage_ple] $DST: $(ls "$DST" | wc -l) files, $n copied, $(du -sh "$DST" | cut -f1)"
