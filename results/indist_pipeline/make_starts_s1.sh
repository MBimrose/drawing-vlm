#!/bin/bash
# In-dist pipeline (2026-10-14): tail of stage2_full_shm.sbatch (the job was OOM-killed after render/v3/vscore): full S1 starts
# (pg_make_starts.py, top-3 distinct by v3b-EV + v3) -> check vs part-A starts -> z blocks for the remaining keys -> serv-20.
set -euo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; P=$DV/results/indist_pipeline; NAME=rl2s60; O=$P/full_k16_$NAME
[ -s ${O}_consistency.json ] && [ -s $P/vpreds_k16_$NAME.json ] && [ -s ${O}_rc_v3.json ]
$DV/.venv/bin/python $DV/train_v14/geom/pg_make_starts.py --cands $O.json --cons ${O}_consistency.json --vpreds $P/vpreds_k16_$NAME.json \
  --rc ${O}_rc_v3.json --out-stem $P/starts_$NAME --k 16 | tee $P/logs/pg_make_starts_$NAME.log
python3 $P/make_z_blocks.py
rsync -a $P/blocks/ wpk-serv-20.mechse.illinois.edu:/srv/scratch/bimrose2/indist_pipeline/blocks/
echo "S1 z blocks queued $(date)"
