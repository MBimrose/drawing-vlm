#!/usr/bin/env bash
# Render every not-yet-rendered STEP of a corpus in its own renderer process (a segfault in one
# part cannot break a shared pool), merge the per-part sidecars, build the eval cache.
#   render_isolated.sh <corpus_dir> [parallel]        (serv-19 paths)
C=$1; P=${2:-32}; M=/srv/scratch/bimrose2/mech_benchmarks
mkdir -p $C/render/png $C/render/iso $C/logs
export SCRIPT_DIR=$M/step_to_drw OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1
one() { f=$1; k=$(basename $f .step); C=$2; M=$3
  ls $C/render/png/${k}_v*.png >/dev/null 2>&1 && return 0
  d=$C/render/iso/$k; rm -rf $d; mkdir -p $d/src; ln -s $f $d/src/$k.step
  timeout 400 /software/python-3.11.1/bin/python3 $M/render_ext.py --src $d/src --out $d/out --workers 1 > $d/log 2>&1; rc=$?
  if ls $d/out/png/${k}_v*.png >/dev/null 2>&1; then mv $d/out/png/${k}_v*.png $C/render/png/; echo "$k ok" >> $C/logs/iso.log
  else echo "$k FAIL rc=$rc $(grep -m1 -i "error\|fault\|timeout\|brokenprocess" $d/log | cut -c1-100)" >> $C/logs/iso.log; fi; }
export -f one
ls $C/step_mm/*.step | xargs -P $P -I{} bash -c "one {} $C $M"
/srv/scratch/bimrose2/.venv/bin/python - "$C" <<'PY'
import json, glob, os, sys
C = sys.argv[1]; side = os.path.join(C, "render", "renderers.json")
s = json.load(open(side)) if os.path.exists(side) else {}
for f in glob.glob(f"{C}/render/iso/*/out/renderers.json"):
    s.update(json.load(open(f)))
json.dump(s, open(side, "w"), indent=1, sort_keys=True)
print("sidecar entries", len(s), "pngs", len(glob.glob(f"{C}/render/png/*.png")))
PY
echo "ISO RENDER DONE $(date) ok=$(grep -c " ok" $C/logs/iso.log) fail=$(grep -c FAIL $C/logs/iso.log)" >> $C/logs/stage.log
/srv/scratch/bimrose2/.venv/bin/python $M/build_ext_eval_cache.py --bench $C --png-dir $C/render/png > $C/logs/cache.log 2>&1; tail -3 $C/logs/cache.log >> $C/logs/stage.log
echo "STAGE1 DONE $(date)" >> $C/logs/stage.log
