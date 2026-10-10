#!/bin/bash
# Cycle 2 (serv-20): STaR rationalization of the GT-search / teacher programs (cycle2/search/targets_<c>.json) by the
# SEARCH POLICY itself (rft1_rl2 s120 merged, served as c2pol on :8610, GPU 1) with geom/build_guide_bank.py
# (hint prompt, leak filter, think kept; plan later paired with the program under the normal prompt).
cd /srv/scratch/bimrose2
export OMP_NUM_THREADS=2
declare -A BENCH=( [c4]=fp/h6/rft_corpus4 [c2]=mech_benchmarks/rft_corpus2_dw423 [c1]=mech_benchmarks/rft_corpus_dw423
                   [rp2]=mech_benchmarks/rft_realpool_v2 )
curl -s -m 5 http://127.0.0.1:8610/health >/dev/null || { echo "c2pol server not up on :8610"; exit 1; }
for c in c4 c2 c1 rp2; do
  [ -f cycle2/search/targets_$c.json ] || continue
  .venv/bin/python cycle2/train_v14/geom/build_guide_bank.py --bench ${BENCH[$c]} --targets cycle2/search/targets_$c.json \
    --base-url http://127.0.0.1:8610/v1 --model c2pol --out cycle2/search/bank_$c.json --min-iou 0.75 --workers 24 \
    > cycle2/logs/rat_$c.log 2>&1 &
done
wait; tail -qn 1 cycle2/logs/rat_*.log; echo "RATIONALIZE DONE $(date)"
