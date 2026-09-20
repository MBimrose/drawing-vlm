#!/usr/bin/env bash
# Detached: wait for the corpus-4 solve to release serv-04's GPUs, then run the zero-shot repair probe.
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV
until grep -q "SOLVE CORPUS DONE" logs/real/solve_rft_corpus4.log 2>/dev/null; do sleep 300; done
echo "$(date) corpus4 solve done; starting the repair probe"
bash train_v14/serv19/repair_probe_split.sh repair_bench_e55 8 e55-rft-real-u5-gt-dw423
echo "$(date) CHAIN EXIT"
