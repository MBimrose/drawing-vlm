#!/bin/bash
# Real-part verifier pool: corpus best-of-N passes (serv-19 merged JSONs copied
# to mech/benchmarks/data/<corpus>/results) + gt_feedback_gen scored passes.
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; D=$DV/train_v14/mech/benchmarks/data
python3 $DV/train_v14/geom/pack_scored_real.py --out $DV/rft_scored_real/shards \
  --heldout $D/heldout_file_ids.txt \
  --png $D/rft_corpus/render/png --png $D/rft_corpus2/render/png --png $D/rft_corpus3/render/png \
  --src $D/rft_corpus/results/bo8_corpus_e40-rft-strict-all-6k.json \
  --src $D/rft_corpus/results/bo16_corpus_e40-rft-strict-all-6k.json \
  --src $D/rft_corpus/results/bo8_corpus_e45-rft-strict90-all-s43.json \
  --src $D/rft_corpus2/results/bo8_corpus2_e40-rft-strict-all-6k.json \
  --src $D/rft_corpus3/results/bo8_rft_corpus3_e51-rft-real-u3-strict90.json \
  --src $DV/rft_gtfb_c2 --src $DV/rft_plain_c2 --src $DV/rft_gtfb_c1 --src $DV/rft_plain_c1 "$@"
