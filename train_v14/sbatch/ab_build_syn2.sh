#!/bin/bash
# Kimi-trace A/B round 2 (2026-10-31): 42k synthetic parts disjoint from round 1's syn_s0..7 (cpu_run.sh on ccc0442).
PY=/dev/shm/bimrose2/ipcode/venv/bin/python
[ -x $PY ] || bash /projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/indist_pipeline/stage_py_shm.sh
cd /projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/train_v14/geom && $PY ab_build_benches.py --seed 31 --workers 36 --exclude /projects/illinois/eng/ece/wpk/bimrose2/srvmirror/amvlm/ab/syn_s{0..7} --out /projects/illinois/eng/ece/wpk/bimrose2/srvmirror/amvlm/ab/syn2
