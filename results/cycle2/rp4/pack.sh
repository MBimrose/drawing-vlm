#!/bin/bash
# rp4c2 repair tier: pack each corpus' rendered pairs (pack_repair_shards.py, rp3 format: target sheet + cand.png +
# REPAIR_PROMPT(start code) -> target code, no-think) into results/cycle2/rp4/tier_<c>/shards.
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV; O=results/cycle2/rp4; BD=train_v14/mech/benchmarks/data
declare -A B=([c4]=rft_corpus4 [c2]=rft_corpus2_dw423 [c1]=rft_corpus_dw423 [rp2]=rft_realpool_v2)
for c in c4 c2 c1 rp2; do
  rm -rf $O/tier_$c; .venv/bin/python train_v14/geom/pack_repair_shards.py --bo $O/${c}_inputs.json --png-dir $O/png_$c \
    --bench $BD/${B[$c]} --targets $O/${c}_targets.json --out $O/tier_$c --per-shard 500
done
