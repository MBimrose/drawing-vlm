#!/usr/bin/env bash
# Verifier scoring + agreement-gated selection on a merged best-of-N candidate
# file (the served policy; RECIPE.md "Serving policy"). One GPU, idempotent:
# the verifier pass is skipped when <stem>_vsel.json.preds.json already exists.
#
#   gated_step.sh <cands.json> <consistency.json> <cache.pkl> <K> [<split.json>|none]
#
# Env: DV     repo root (default: the campus-cluster checkout)
#      PY     python (default: $DV/.venv/bin/python)
#      VRUN   verifier run / config name (default v3b-verifier-real-reg)
#      VER    verifier LoRA dir (default $DV/runs/$VRUN/final)
#      VBASE  verifier base weights (default: model_id in configs/$VRUN.yaml = e51 final)
#      STAGE_SHM=1  copy the base to /dev/shm first (Lustre loads take up to 1 h under contention)
#      CUDA_VISIBLE_DEVICES  one GPU (default 0)
# Outputs next to <cands.json>: <stem>_vsel.json (+ .preds.json, _summary.txt) and
# <stem>_gated.json / <stem>_gated_summary.txt (gated_select.py).
set -uo pipefail
CANDS=$1; CONS=$2; CACHE=$3; K=$4; SPLIT=${5:-none}
DV=${DV:-/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm}
PY=${PY:-$DV/.venv/bin/python}
VRUN=${VRUN:-v3b-verifier-real-reg}
VER=${VER:-$DV/runs/$VRUN/final}
VBASE=${VBASE:-$(grep -E "^model_id:" $DV/train_v14/configs/$VRUN.yaml | awk '{print $2}')}
export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0}
G=$DV/train_v14/geom
STEM=${CANDS%.json}
VSEL=${STEM}_vsel.json
SPLIT_ARG=$([ "$SPLIT" != none ] && echo "--split $SPLIT")
[ -f "$CANDS" ] && [ -f "$CONS" ] || { echo "[gated] missing $CANDS or $CONS"; exit 1; }

if [ -f "$VSEL.preds.json" ]; then
  echo "$(date) [gated] reusing $VSEL.preds.json"
  $PY $G/verifier_select_offline.py --no-model --cands $CANDS --consistency $CONS --cache $CACHE \
    $SPLIT_ARG --k $K --prompt-mode reg_ev --out $VSEL
else
  BASE=$VBASE; SHM=""
  if [ "${STAGE_SHM:-0}" = 1 ]; then
    SHM=/dev/shm/bimrose2_gated_${SLURM_JOB_ID:-$$}; trap 'rm -rf $SHM' EXIT
    echo "$(date) [gated] staging $VBASE -> $SHM"
    if mkdir -p $SHM && cp -r $VBASE $SHM/base; then BASE=$SHM/base; echo "$(date) [gated] staged";
    else echo "[gated] staging failed, loading from $VBASE"; rm -rf $SHM; fi
  fi
  echo "$(date) [gated] verifier $VER (base $BASE) scoring $CANDS"
  $PY $G/verifier_select_offline.py --verifier $VER --verifier-run $VRUN --base $BASE \
    --cands $CANDS --consistency $CONS --cache $CACHE $SPLIT_ARG \
    --k $K --prompt-mode reg_ev --batch ${BATCH:-8} --out $VSEL
  [ -n "$SHM" ] && rm -rf $SHM
fi
[ -f "$VSEL.preds.json" ] || { echo "[gated] verifier scoring failed (no $VSEL.preds.json)"; exit 1; }
echo "$(date) [gated] gated_select"
$PY $G/gated_select.py --cands $CANDS --consistency $CONS --preds $VSEL.preds.json $SPLIT_ARG \
  --k $K --out ${STEM}_gated.json
echo "$(date) [gated] done -> ${STEM}_gated.json"
