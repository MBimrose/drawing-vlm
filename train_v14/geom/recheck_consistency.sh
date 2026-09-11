#!/usr/bin/env bash
# Re-run the consistency step + gated selection for a candidate file whose pairwise matrix was
# degraded by re-execution timeouts (RECIPE "Never read exec/iou out of a _consistency.json").
# The verifier predictions are reused from <stem>_vsel.json.preds.json, so this is CPU only.
#   recheck_consistency.sh <stem> <cache.pkl> <K> [split.json|none]
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
PY=$DV/.venv/bin/python
STEM=$1; CACHE=$2; K=$3; SPLIT=${4:-none}
C=$DV/results/ext/$STEM.json
[ -f "$C" ] || { echo "no $C"; exit 1; }
gen=$(grep -oE '"n_exec": [0-9]+' $DV/logs/bo8/${STEM}_merge.log | head -1 | grep -oE '[0-9]+')
echo "$(date) [recheck] $STEM: generation executed $gen candidates; re-running consistency"
$PY $DV/train_v14/geom/consistency_rerank.py $C $DV/results/ext/${STEM}_consistency.json \
  > $DV/logs/bo8/${STEM}_consistency.log 2>&1
new=$(grep -oE "re-executed [0-9]+" $DV/logs/bo8/${STEM}_consistency.log | grep -oE '[0-9]+')
echo "$(date) [recheck] re-executed $new of $gen"
[ -n "$gen" ] && [ -n "$new" ] && [ "$new" -lt "$((gen * 98 / 100))" ] && \
  echo "[recheck] WARNING: still losing $((gen - new)) candidates -- run this on an idle node"
SPLIT_ARG=$([ "$SPLIT" != none ] && echo "--split $SPLIT")
$PY $DV/train_v14/geom/gated_select.py --cands $C \
  --consistency $DV/results/ext/${STEM}_consistency.json \
  --preds $DV/results/ext/${STEM}_vsel.json.preds.json $SPLIT_ARG \
  --k $K --out $DV/results/ext/${STEM}_gated.json
echo "$(date) [recheck] done"
