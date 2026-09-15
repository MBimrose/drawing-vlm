#!/usr/bin/env bash
# DeepCAD gate, serv-19 side: verified STEPs -> corpus (step_mm / gt_meshes_v15 / manifest) ->
# draftwright 0.4.23 sheets -> eval cache. Then rsync the corpus to the cluster and score e55 at
# K=8 with bo8_ext_cluster.sbatch (BENCH=<corpus>, TAG=bo8_deepcad, N=0).
#
#   deepcad_gate.sh <corpus_dir under /srv/scratch/bimrose2/deepcad>   e.g. corpus_gate
#
# The corpus's src/000/<key>.step files were written by deepcad_verify.py (only parts whose
# rebuilt solid matches Onshape's bounding box). prep_external_parts.py rescales to 80 mm
# (a no-op here: the converter already emitted 80 mm parts), meshes the GT and writes the
# manifest; render_isolated.sh renders one process per part with the 0.4.23 engine.
set -uo pipefail
cd /srv/scratch/bimrose2/deepcad
C=${1:-corpus_gate}; M=/srv/scratch/bimrose2/mech_benchmarks; PY=/srv/scratch/bimrose2/.venv/bin/python
mkdir -p $C/logs
echo "$(date) [gate] prep $(ls $C/src/000/*.step | wc -l) STEPs" | tee -a $C/logs/stage.log
$PY $M/prep_external_parts.py --src $C/src/000 --out $C --max-faces 400 --timeout 60 > $C/logs/prep.log 2>&1
tail -1 $C/logs/prep.log | tee -a $C/logs/stage.log
# manifest: tag the family so analyze_ext slices work
$PY - "$C" <<'PY'
import json, sys
p = f"{sys.argv[1]}/manifest.json"; m = json.load(open(p))
for k, v in m["parts"].items():
    v.setdefault("family", "D"); v.setdefault("label", "deepcad")
json.dump(m, open(p, "w"), indent=1); print("[gate] manifest parts", len(m["parts"]))
PY
echo "$(date) [gate] render" | tee -a $C/logs/stage.log
bash $M/render_isolated.sh $PWD/$C 32 >> $C/logs/stage.log 2>&1
tail -3 $C/logs/stage.log
echo "$(date) [gate] DONE $C: sheets $(ls $C/render/png | wc -l)" | tee -a $C/logs/stage.log
