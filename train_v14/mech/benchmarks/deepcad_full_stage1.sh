#!/usr/bin/env bash
# DeepCAD full split, stage 1 on wpk-serv-20 (CPU only): verified STEPs -> chunked prep with the
# DeepCAD filters -> merged corpus -> draftwright 0.4.23 sheets -> eval cache.
# Mirrors run_corpus3_stage1.sh; differences: --min-faces 3 --max-aspect 40 (plain plates, rods
# and cylinders are real Onshape parts), family D / label deepcad, render_isolated.sh (one
# process per part, no shared pool to poison) at high parallelism on 344 idle cores.
#   deepcad_full_stage1.sh [corpus_dir=/srv/scratch/bimrose2/deepcad/corpus_full] [parallel_prep=60] [parallel_render=160]
set -u
DV=/srv/scratch/bimrose2; M=$DV/mech_benchmarks; PY=$DV/.venv/bin/python
C=${1:-$DV/deepcad/corpus_full}; PP=${2:-60}; PR=${3:-160}
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
mkdir -p $C/logs $C/prep $C/step_mm $C/gt_meshes_v15 $C/results $C/src_chunks
echo "STAGE1 START $(date) $(ls $C/src/000/*.step | wc -l) verified STEPs" >> $C/logs/stage.log
# chunk the flat src/000 into src_chunks/NNN of 1,000 symlinks (prep takes one dir at a time)
$PY - "$C" <<'PY'
import os, sys, glob
C = sys.argv[1]; files = sorted(glob.glob(f"{C}/src/000/*.step"))
for i in range(0, len(files), 1000):
    d = f"{C}/src_chunks/{i//1000:03d}"; os.makedirs(d, exist_ok=True)
    for f in files[i:i+1000]:
        dst = os.path.join(d, os.path.basename(f))
        if not os.path.lexists(dst): os.symlink(f, dst)
print("chunks", (len(files)+999)//1000)
PY
ls -d $C/src_chunks/*/ | xargs -P $PP -I{} bash -c 'd={}; n=$(basename $d); [ -f '"$C"'/prep/$n/manifest.json ] || '"$PY"' '"$M"'/prep_external_parts.py --src $d --out '"$C"'/prep/$n --max-faces 400 --min-faces 3 --max-aspect 40 --timeout 60 > '"$C"'/logs/prep_$n.log 2>&1'
echo "PREP DONE $(date)" >> $C/logs/stage.log
$PY - "$C" <<'PY'
import json, glob, os, shutil, collections, sys
C = sys.argv[1]; parts = {}; rej = collections.Counter()
for mf in sorted(glob.glob(f"{C}/prep/*/manifest.json")):
    m = json.load(open(mf)); d = os.path.dirname(mf)
    for k, v in m["parts"].items():
        v["family"] = "D"; v["label"] = "deepcad"; parts[k] = v
        for sub in ("step_mm", "gt_meshes_v15"):
            for f in glob.glob(f"{d}/{sub}/{k}.*"):
                dst = f"{C}/{sub}/{os.path.basename(f)}"
                if not os.path.exists(dst): shutil.move(f, dst)
    rej.update(m.get("rejected", {}))
json.dump({"target_mm": 80, "max_faces": 400, "min_faces": 3, "max_aspect": 40, "parts": parts,
           "rejected": dict(rej)}, open(f"{C}/manifest.json", "w"), indent=1)
print("kept", len(parts), "rejected", dict(rej))
PY
echo "MERGE DONE $(date) $(ls $C/step_mm | wc -l) step_mm" >> $C/logs/stage.log
bash $M/render_isolated.sh $C $PR >> $C/logs/stage.log 2>&1
echo "STAGE1 DONE $(date) sheets $(ls $C/render/png | wc -l)" >> $C/logs/stage.log
