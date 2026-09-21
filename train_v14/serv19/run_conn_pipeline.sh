#!/usr/bin/env bash
# End-to-end pipeline for a single drawing: serve the model on serv-04, draw K candidates,
# execute + score them on the cluster CPUs, then render the served reconstruction's own sheet
# so the drawing and the rebuild can be shown side by side.
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; S04=wpk-serv-04.mechse.illinois.edu; SDV=/srv/scratch/bimrose2
BENCH=${1:-conn_bench}; K=${2:-8}; RUN=${3:-e55-rft-real-u5-gt-dw423}
C=$DV/train_v14/mech/benchmarks/data/$BENCH; STEM=bo${K}_${BENCH}_${RUN}
say(){ echo "$(date '+%m-%d %H:%M') $*"; }
until timeout 30 ssh -o BatchMode=yes $S04 "[ \$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | sort -n | tail -1) -lt 5000 ]"; do say "serv-04 GPUs busy; waiting"; sleep 600; done
say "GPUs free; running the pipeline for $BENCH"
bash $DV/train_v14/serv19/solve_corpus_split.sh $BENCH $K $RUN conn_tier_unused
say "PIPELINE DONE"
