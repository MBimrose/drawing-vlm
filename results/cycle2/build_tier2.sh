#!/bin/bash
# Cycle 2 tier (2026-10-09): geom/build_rft2_tier.py over the 4 training corpora, union with the round-1 tier.
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV; C=results/cycle2; BD=train_v14/mech/benchmarks/data
rm -rf $C/tier2
python3 train_v14/geom/build_rft2_tier.py --out $C/tier2 --tier1 results/guide/rft1/tier/accepted-000.jsonl \
  --part $BD/rft_corpus4:$C/gen/A_c4_c2pol.json,$C/gen/C_c4_c2pol.json:$C/search/bank_c4.json \
  --part $BD/rft_corpus2_dw423:$C/gen/A_c2_c2pol.json,$C/gen/C_c2_c2pol.json:$C/search/bank_c2.json \
  --part $BD/rft_corpus_dw423:$C/gen/A_c1_c2pol.json,$C/gen/C_c1_c2pol.json:$C/search/bank_c1.json \
  --part $BD/rft_realpool_v2:$C/gen/B_rp2_c2pol.json:$C/search/bank_rp2.json \
  --prior $BD/rft_corpus_dw423/results/bo32_rft_corpus_dw423_e55-rft-real-u5-gt-dw423.json \
  --prior $BD/rft_corpus2_dw423/results/bo32_rft_corpus2_dw423_e55-rft-real-u5-gt-dw423.json \
  --prior results/h6c/bo8_real4_e55.json --prior results/guide/v3/bo16_c2_t10.json --prior results/guide/v3/bo16_c4_t10.json \
  --prior results/h6c/bo8_realpool2_e55.json --prior results/realpool_v2/bo4_t10s120_a.json --prior results/realpool_v2/bo4_t10s120_b.json
