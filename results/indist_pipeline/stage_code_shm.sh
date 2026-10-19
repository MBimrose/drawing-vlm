#!/bin/bash
# In-dist pipeline (2026-10-14): node-RAM copy of the pipeline code and the pool on ccc0442. Running the scorers from
# Lustre left ~115 processes in D state (wait_woken: every python import stats train_v14/geom on Lustre first), so
# vr_serve / score_partials / render_compare run from a byte-identical copy in /dev/shm instead. Idempotent.
#   bash stage_code_shm.sh   -> /dev/shm/bimrose2/ipcode/{train_v14,fullpool}/ + READY
set -euo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; D=/dev/shm/bimrose2/ipcode
[ -f $D/READY ] && { echo "already staged"; exit 0; }
exec 8>/dev/shm/bimrose2/ipcode.lock; flock 8
[ -f $D/READY ] && { echo "already staged"; exit 0; }
mkdir -p $D/train_v14/mech/benchmarks $D/fullpool/gt_meshes_v15
rsync -a --exclude mech --exclude __pycache__ --exclude sbatch --exclude serv19 $DV/train_v14/ $D/train_v14/
rsync -a $DV/train_v14/mech/benchmarks/*.py $D/train_v14/mech/benchmarks/
for f in $DV/train_v14/mech/*.py $DV/train_v14/mech/benchmarks/__init__.py; do [ -f $f ] && cp $f ${f/$DV/$D} || true; done
cp -L $DV/train_v14/mech/benchmarks/data/fullpool_dw423/eval_cache_v15.pkl $D/fullpool/
python3 -c "import json; print('\n'.join(p['key'] + '.stl' for p in json.load(open('$DV/results/grpo_eval/full_e55ctl.json'))['candidates']))" > $D/gt.txt
rsync -a --files-from=$D/gt.txt -L $DV/train_v14/mech/benchmarks/data/fullpool_dw423/gt_meshes_v15/ $D/fullpool/gt_meshes_v15/
# check identical
(cd $DV/train_v14 && find . -path ./mech -prune -o -path ./sbatch -prune -o -path ./serv19 -prune -o -name '*.py' -print | grep -v __pycache__ | sort | xargs md5sum) > $D/src.md5
(cd $D/train_v14 && md5sum -c --quiet $D/src.md5)
(cd $DV/train_v14/mech/benchmarks/data/fullpool_dw423/gt_meshes_v15 && xargs md5sum < $D/gt.txt) > $D/gt.md5
(cd $D/fullpool/gt_meshes_v15 && md5sum -c --quiet $D/gt.md5)
[ "$(ls $D/fullpool/gt_meshes_v15 | wc -l)" = 1027 ]
touch $D/READY; echo "staged $(du -sh $D | cut -f1)"
