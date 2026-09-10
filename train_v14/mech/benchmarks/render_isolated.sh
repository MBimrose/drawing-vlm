#!/usr/bin/env bash
# Render every not-yet-rendered STEP of a corpus in its own renderer process (a segfault in one
# part cannot break a shared pool), merge the per-part sidecars, build the eval cache.
#   render_isolated.sh <corpus_dir> [parallel]        (serv-19 paths)
# RPY selects the renderer interpreter: default /srv/scratch/bimrose2/dw_venv/bin/python
# (draftwright 0.4.23 + _FONT_SIZE 5.25 patch) -- the engine the training sheets, the serving
# policy and e55 use since 2026-09-10. RPY=/software/python-3.11.1/bin/python3 renders with the
# retired 0.4.0 + patch (corpora 1-3 / ext_bench were built that way); there is NO legacy SVG
# fallback in either -- a part that will not draw is recorded as a verbose failure.
C=$1; P=${2:-32}; M=/srv/scratch/bimrose2/mech_benchmarks; export RPY=${RPY:-/srv/scratch/bimrose2/dw_venv/bin/python}
mkdir -p $C/render/png $C/render/iso $C/logs
export SCRIPT_DIR=$M/step_to_drw OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1
one() { f=$1; k=$(basename $f .step); C=$2; M=$3
  ls $C/render/png/${k}_v*.png >/dev/null 2>&1 && return 0
  d=$C/render/iso/$k; rm -rf $d; mkdir -p $d/src; ln -s $f $d/src/$k.step
  timeout 400 $RPY $M/render_ext.py --src $d/src --out $d/out --workers 1 > $d/log 2>&1; rc=$?
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
# record the renderer build in the corpus manifest
import subprocess
rpy = os.environ.get("RPY", "/software/python-3.11.1/bin/python3")
info = subprocess.run([rpy, "-c", "import draftwright, re, os; p=os.path.join(os.path.dirname(draftwright.__file__), '_core.py'); "
                       "m=re.search(r'^_FONT_SIZE = ([0-9.]+)', open(p).read(), re.M); "
                       "from importlib.metadata import version; print(version('draftwright'), m.group(1) if m else '?')"], capture_output=True, text=True).stdout.split()
mp = os.path.join(C, "manifest.json")
if os.path.exists(mp) and len(info) == 2:
    man = json.load(open(mp)); man["renderer"] = {"engine": "draftwright", "version": info[0], "font_size_patch": float(info[1]),
                                                   "python": rpy, "driver": "render_ext.py/worker_v11 VLM_MODE=1 via render_isolated.sh"}
    json.dump(man, open(mp, "w"), indent=1); print("manifest renderer", man["renderer"])
PY
echo "ISO RENDER DONE $(date) ok=$(grep -c " ok" $C/logs/iso.log) fail=$(grep -c FAIL $C/logs/iso.log)" >> $C/logs/stage.log
/srv/scratch/bimrose2/.venv/bin/python $M/build_ext_eval_cache.py --bench $C --png-dir $C/render/png > $C/logs/cache.log 2>&1; tail -3 $C/logs/cache.log >> $C/logs/stage.log
echo "STAGE1 DONE $(date)" >> $C/logs/stage.log
