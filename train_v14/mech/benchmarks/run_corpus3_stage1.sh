#!/usr/bin/env bash
# Corpus 3 (CADBench F/A/E EASY tiers) stage 1 on serv-19, CPU + download only — identical to the stage-1
# half of run_corpus2_all.sh: download -> 40-way prep (--max-faces 120) -> merge -> render -> eval cache.
# No GPU generation here; that is launched separately.
set -u
DV=/srv/scratch/bimrose2; M=$DV/mech_benchmarks; C=$M/rft_corpus3; PY=$DV/.venv/bin/python
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
mkdir -p $C/logs $C/prep $C/step_mm $C/gt_meshes_v15 $C/results
echo "STAGE1 START $(date)" >> $C/logs/stage.log
$PY $M/build_corpus3.py --out $C --exclude $M/exclude_ids_corpus3.txt > $C/logs/download.log 2>&1
echo "DOWNLOAD DONE $(date) $(find $C/src -name '*.step' | wc -l) step" >> $C/logs/stage.log
ls -d $C/src/*/ | xargs -P 40 -I{} bash -c 'd={}; n=$(basename $d); '"$PY"' '"$M"'/prep_external_parts.py --src $d --out '"$C"'/prep/$n --max-faces 120 --timeout 60 > '"$C"'/logs/prep_$n.log 2>&1'
echo "PREP DONE $(date)" >> $C/logs/stage.log
$PY - <<'PYEOF'
import json, glob, os, shutil, collections
C="/srv/scratch/bimrose2/mech_benchmarks/rft_corpus3"; parts={}; rej=collections.Counter()
for mf in sorted(glob.glob(f"{C}/prep/*/manifest.json")):
    m=json.load(open(mf)); d=os.path.dirname(mf)
    for k,v in m["parts"].items():
        v["family"]=k.split("_",1)[0]; v["label"]=k.rsplit("_",1)[1]; parts[k]=v
        for sub in ("step_mm","gt_meshes_v15"):
            for f in glob.glob(f"{d}/{sub}/{k}.*"): shutil.move(f, f"{C}/{sub}/{os.path.basename(f)}")
    rej.update(m.get("rejected",{}))
json.dump({"target_mm":80,"max_faces":120,"parts":parts,"rejected":dict(rej)},open(f"{C}/manifest.json","w"),indent=1)
print("kept",len(parts),dict(collections.Counter((v["family"],v["label"]) for v in parts.values())),"rejected",dict(rej))
PYEOF
echo "MERGE1 DONE $(date)" >> $C/logs/stage.log
SCRIPT_DIR=$M/step_to_drw OMP_NUM_THREADS=2 /software/python-3.11.1/bin/python3 $M/render_ext.py --src $C/step_mm --out $C/render --workers 96 > $C/logs/render.log 2>&1
echo "RENDER DONE $(date) $(ls $C/render/png | wc -l) png" >> $C/logs/stage.log
$PY $M/build_ext_eval_cache.py --bench $C --png-dir $C/render/png > $C/logs/cache.log 2>&1; cat $C/logs/cache.log >> $C/logs/stage.log
echo "STAGE1 DONE $(date)" >> $C/logs/stage.log
