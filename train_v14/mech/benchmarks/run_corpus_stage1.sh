#!/usr/bin/env bash
# Stage 1 on serv-19: download -> parallel prep (filter/rescale/GT STL) -> merge manifests.
set -u
M=/srv/scratch/bimrose2/mech_benchmarks; C=$M/rft_corpus; PY=/srv/scratch/bimrose2/.venv/bin/python
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
mkdir -p $C/logs $C/prep $C/step_mm $C/gt_meshes_v15
echo "STAGE1 START $(date)" >> $C/logs/stage1.log
$PY $M/build_corpus.py --out $C --exclude $M/heldout_file_ids.txt > $C/logs/download.log 2>&1
echo "DOWNLOAD DONE $(date)" >> $C/logs/stage1.log
ls -d $C/src/*/ | xargs -P 40 -I{} bash -c 'd={}; n=$(basename $d); '"$PY"' '"$M"'/prep_external_parts.py --src $d --out '"$C"'/prep/$n --timeout 60 > '"$C"'/logs/prep_$n.log 2>&1'
echo "PREP DONE $(date)" >> $C/logs/stage1.log
$PY - <<'PYEOF'
import json, glob, os, shutil, collections
C="/srv/scratch/bimrose2/mech_benchmarks/rft_corpus"; parts={}; rej=collections.Counter()
for mf in sorted(glob.glob(f"{C}/prep/*/manifest.json")):
    m=json.load(open(mf)); d=os.path.dirname(mf)
    for k,v in m["parts"].items():
        v["family"]=k.split("_",1)[0]; v["label"]=k.rsplit("_",1)[1]; parts[k]=v
        for sub in ("step_mm","gt_meshes_v15"):
            for f in glob.glob(f"{d}/{sub}/{k}.*"): shutil.move(f, f"{C}/{sub}/{os.path.basename(f)}")
    rej.update(m.get("rejected",{}))
json.dump({"target_mm":80,"max_faces":80,"parts":parts,"rejected":dict(rej)},open(f"{C}/manifest.json","w"),indent=1)
fam=collections.Counter((v["family"],v["label"]) for v in parts.values())
print("kept",len(parts),dict(fam),"rejected",dict(rej))
PYEOF
echo "STAGE1 MERGE DONE $(date)" >> $C/logs/stage1.log
