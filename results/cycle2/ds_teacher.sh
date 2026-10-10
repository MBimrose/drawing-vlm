#!/bin/bash
# Cycle 2 teacher on serv-20 (2026-10-09): DeepSeek-V4.1-Flash (lab hub, x-hub-user bimrose2) GT-selected vis-repair
# (geom/vis_repair_gt.py --arm vis --adopt gt, 3 rounds) of the hardest training parts (best known program < 0.3).
# 4 corpora x DS_CAP 8 = <= 32 hub requests in flight (cap 48 total). Single-thread scoring subprocesses.
cd /srv/scratch/bimrose2
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 DS_CAP=${DS_CAP:-8} HUB_USER=bimrose2
declare -A BENCH=( [c4]=fp/h6/rft_corpus4 [c2]=mech_benchmarks/rft_corpus2_dw423 [c1]=mech_benchmarks/rft_corpus_dw423
                   [rp2]=mech_benchmarks/rft_realpool_v2 )
P=()
for c in ${CORPORA:-c4 c2 c1 rp2}; do
  [ -f cycle2/teacher/picks_$c.json ] || continue
  nice -n 10 .venv/bin/python cycle2/train_v14/geom/vis_repair_gt.py --bench ${BENCH[$c]} --picks cycle2/teacher/picks_$c.json \
    --arm vis --adopt gt --rounds 3 --workers ${W:-8} --py $PWD/.venv/bin/python --rpy $PWD/dw_venv/bin/python \
    --script-dir $PWD/mech_step_to_drw --out cycle2/teacher/ds_$c.jsonl > cycle2/logs/ds_teacher_$c.log 2>&1 &
  P+=($!)
done
wait "${P[@]}"; echo "DS TEACHER DONE $(date)"
