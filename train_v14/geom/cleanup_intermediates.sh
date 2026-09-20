#!/usr/bin/env bash
# Remove regenerable intermediates from the repo. Nothing here is an input to training, serving
# or evaluation; each category is either scratch the pipeline already harvested, or a checkpoint
# superseded by the merged file it was written for.
#
#   cleanup_intermediates.sh [--apply]      (default: report only)
#
# Removed:
#   <corpus>/render/iso/<key>/   per-part renderer scratch (the sheet was moved to render/png and
#                                the sidecar merged into render/renderers.json)
#   *.json.partial.json          best-of-N generation checkpoints, only when the merged <stem>.json
#                                exists (that file carries code/think/exec/iou for every candidate)
#   *.json.scored.jsonl          score_partials resume files, same condition
#   results/**/*.shard?.json     per-GPU shards, only when the merged file exists
# Kept: render/png, gt_meshes_v15, step_mm, eval caches, manifests, merged results, tiers, shards.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV
APPLY=0; [ "${1:-}" = "--apply" ] && APPLY=1
LOG=$DV/logs/real/cleanup_$(date +%Y%m%d_%H%M).log; mkdir -p $DV/logs/real
say() { echo "$*" | tee -a $LOG; }
say "=== cleanup $( [ $APPLY = 1 ] && echo APPLY || echo 'REPORT ONLY' ) $(date)"

tot=0
# --- 1. per-part renderer scratch directories
for iso in $(find . -maxdepth 7 -type d -name iso -path "*/render/*" -not -path "./.git/*" 2>/dev/null); do
  n=$(ls $iso 2>/dev/null | wc -l); [ "$n" -eq 0 ] && continue
  sz=$(du -sm $iso 2>/dev/null | cut -f1); tot=$((tot + sz))
  say "  render scratch $iso: $n part dirs, ${sz} MB"
  [ $APPLY = 1 ] && { mv $iso $iso.rm_$$ && rm -rf $iso.rm_$$ & }
done

# --- 2/3/4. checkpoints whose merged file exists
for pat in "*.json.partial.json" "*.json.scored.jsonl"; do
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    merged="${f%.json.partial.json}.json"; [ "${f##*.}" = jsonl ] && merged="${f%.scored.jsonl}"
    # a per-GPU checkpoint <stem>.shardN.json.partial.json is superseded by the run's merged <stem>.json
    nosh=$(echo "$merged" | sed -E 's/\.shard[0-9]+\.json$/.json/')
    [ -s "$merged" ] || merged="$nosh"
    if [ -s "$merged" ]; then
      sz=$(du -sm "$f" 2>/dev/null | cut -f1); tot=$((tot + sz))
      [ $APPLY = 1 ] && rm -f "$f"
      echo "  checkpoint $f (${sz} MB, merged exists)" >> $LOG
    fi
  done < <(find . -name "$pat" -not -path "./.git/*" 2>/dev/null)
done
while IFS= read -r f; do
  [ -n "$f" ] || continue
  merged=$(echo "$f" | sed -E 's/\.shard[0-9]+\.json$/.json/')
  if [ "$merged" != "$f" ] && [ -s "$merged" ]; then
    sz=$(du -sm "$f" 2>/dev/null | cut -f1); tot=$((tot + sz))
    [ $APPLY = 1 ] && rm -f "$f"
    echo "  shard $f (${sz} MB, merged exists)" >> $LOG
  fi
done < <(find ./results ./train_v14/mech/benchmarks/data ./deepcad -name "*.shard[0-9].json" -not -path "./.git/*" 2>/dev/null)
say "  (per-file checkpoint lines in $LOG)"
wait
say "=== total reclaimed: ${tot} MB $( [ $APPLY = 1 ] && echo '(removed)' || echo '(would remove)' )"
say "CLEANUP DONE $(date)"
