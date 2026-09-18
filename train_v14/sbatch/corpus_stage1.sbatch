#!/bin/bash
#SBATCH --job-name=corpus-stage1
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=110
#SBATCH --mem=400G
#SBATCH --time=36:00:00
#SBATCH --nodelist=ccc0442
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/real/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/real/%x-%j.err
# CPU-only (L40S node, no GPU): stage 1 of a real-STEP corpus on the cluster -- chunked prep
# (scale to 80 mm, filters, GT meshes), manifest merge, draftwright 0.4.23 sheets (one renderer
# process per part, no legacy fallback), eval cache. Venvs + renderer scripts staged in node RAM.
#   sbatch --export=ALL,CORPUS=rft_corpus4[,MAXFACES=120,PP=50,PR=90] corpus_stage1.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; MB=$DV/train_v14/mech/benchmarks; C=$MB/data/$CORPUS
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
S=/dev/shm/bimrose2/st1_$SLURM_JOB_ID; mkdir -p $S; trap 'rm -rf $S' EXIT
rsync -a --copy-links $DV/.venv/ $S/venv/ & rsync -a --copy-links $DV/dw_venv/ $S/dw_venv/ & rsync -a $DV/mech_step_to_drw/ $S/step_to_drw/ & wait
PY=$S/venv/bin/python; $PY -c "import build123d, OCP" || { echo "staged venv broken"; exit 1; }
mkdir -p $C/logs $C/prep $C/step_mm $C/gt_meshes_v15 $C/results
echo "STAGE1 START $(date) $(find $C/src -name '*.step' | wc -l) STEPs in $(ls -d $C/src/*/ | wc -l) chunks" >> $C/logs/stage.log
ls -d $C/src/*/ | xargs -P ${PP:-50} -I{} bash -c 'd={}; n=$(basename $d); [ -f '"$C"'/prep/$n/manifest.json ] || '"$PY $MB"'/prep_external_parts.py --src $d --out '"$C"'/prep/$n --max-faces '"${MAXFACES:-120}"' --max-aspect '"${MAXASPECT:-15}"' > '"$C"'/logs/prep_$n.log 2>&1'
echo "PREP DONE $(date)" >> $C/logs/stage.log
$PY - "$C" "${MAXFACES:-120}" <<'PY'
import json, glob, os, shutil, collections, sys, re
C, mf = sys.argv[1], int(sys.argv[2]); parts = {}; rej = collections.Counter()
for m in sorted(glob.glob(f"{C}/prep/*/manifest.json")):
    man = json.load(open(m)); d = os.path.dirname(m)
    for k, v in man["parts"].items():
        mm = re.match(r"^([A-Z])_.+_(easy|medium|hard|x)$", k)
        v["family"] = mm.group(1) if mm else k[0]; v["label"] = mm.group(2) if mm else "x"; parts[k] = v
        for sub in ("step_mm", "gt_meshes_v15"):
            for f in glob.glob(f"{d}/{sub}/{k}.*"):
                dst = f"{C}/{sub}/{os.path.basename(f)}"
                if not os.path.exists(dst): shutil.move(f, dst)
    rej.update(man.get("rejected", {}))
json.dump({"target_mm": 80, "max_faces": mf, "parts": parts, "rejected": dict(rej)}, open(f"{C}/manifest.json", "w"), indent=1)
print("kept", len(parts), "by family", dict(collections.Counter(v["family"] for v in parts.values())), "rejected", dict(rej))
PY
echo "MERGE DONE $(date) $(ls $C/step_mm | wc -l) step_mm" >> $C/logs/stage.log
M=$MB PYV=$PY RPY=$S/dw_venv/bin/python SCRIPT_DIR=$S/step_to_drw bash $MB/render_isolated.sh $C ${PR:-90} >> $C/logs/stage.log 2>&1
echo "CORPUS STAGE1 DONE $(date) sheets $(ls $C/render/png | wc -l)" | tee -a $C/logs/stage.log
