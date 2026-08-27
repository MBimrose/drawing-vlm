#!/usr/bin/env bash
# Lab-notebook snapshot: copy every run's eval state + best-of-N results into
# results/, then commit configs/code/results. Pushes if a remote is reachable
# (needs the cluster SSH key authorized on GitHub); otherwise the commit waits
# locally. Idempotent — no changes, no commit. Called from the geom-eval chain.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
cd "$DV" || exit 0
for d in runs/*/; do
  r=$(basename "$d")
  [ -f "$d/geom_eval_state.json" ] && cp "$d/geom_eval_state.json" "results/${r}.json"
  for b in "$d"/geom_eval/bestof*.json; do
    [ -f "$b" ] && python3 -c "
import json,sys; d=json.load(open('$b')); json.dump(d['metrics'], open('results/${r}.'+'$(basename "$b" .json)'+'.json','w'), indent=1)" 2>/dev/null
  done
done
git add -A results train_v14 lab_pipeline scripts DATA_SOURCES.md 2>/dev/null
if git diff --cached --quiet; then
  echo "[snapshot] nothing new"; exit 0
fi
n=$(git diff --cached --name-only | wc -l)
git -c user.name="bimrose2" -c user.email="bimrose2@illinois.edu" commit -q \
  -m "notebook: eval snapshot $(date +%Y-%m-%d\ %H:%M) (${n} files)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" && echo "[snapshot] committed ${n} files"
timeout 60 git push -q origin main 2>/dev/null && echo "[snapshot] pushed" || echo "[snapshot] push deferred (no credentials on this host)"
