#!/bin/bash
#SBATCH --job-name=bench-b
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=96G
#SBATCH --time=10:00:00
#SBATCH --nodelist=ccc0442
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/real/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/real/%x-%j.err
# Bench B (2026-10-10, CPU only): download Fusion 360 Gallery s2.0.1 extended STEP + 2 ABC STEP chunks -> exclusions
# (manifests + inventory + DeepCAD ids + token scan) -> candidates -> prep (prep_external_parts.py, --max-faces 80) ->
# near-dup + stratified selection -> draftwright 0.4.23 renders (render_isolated.sh, no fallback) -> finalize -> leak check.
# Stages are skipped when their output exists, so the job is resumable. STOP_AFTER=<stage> stops early.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; MB=$DV/train_v14/mech/benchmarks; W=$DV/data_ext/bench_b_work
R=$DV/results/bench_b; BB=$R/bench; mkdir -p $W $R
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
unset DW_AUTO_DIMS DW_TOLERANCE DW_DESIGNER DW_DRAWING_NUMBER DW_SCALE_POLICY
if [ -f /dev/shm/bimrose2/c2stage/READY ]; then S=/dev/shm/bimrose2/c2stage   # persistent RAM copy (results/cycle2/pipeline/stage_shm.sh)
else S=/dev/shm/bimrose2/bb_$SLURM_JOB_ID; mkdir -p $S; trap 'rm -rf $S' EXIT
  rsync -a --copy-links $DV/.venv/ $S/venv/ & rsync -a --copy-links $DV/dw_venv/ $S/dw_venv/ & rsync -a $DV/mech_step_to_drw/ $S/step_to_drw/ & wait; fi
echo "staged venvs: $S"
PY=$S/venv/bin/python; $PY -c "import build123d, OCP" || { echo "staged venv broken"; exit 1; }
say() { echo "$(date '+%m-%d %H:%M:%S') $*"; }
stop() { [ "${STOP_AFTER:-}" = "$1" ] && { say "STOP_AFTER $1"; exit 0; }; }
P=$MB/build_bench_b.py
# 1. sources
if [ ! -f $W/fusion/DONE ]; then
  mkdir -p $W/fusion; say "download fusion"
  curl -sS -o $W/fusion/s2.zip https://fusion-360-gallery-dataset.s3.us-west-2.amazonaws.com/segmentation/s2.0.1/s2.0.1_extended_step.zip &&
  (cd $W/fusion && unzip -q -j -o s2.zip 's2.0.1_extended_step/breps/step/*' -d step) && rm -f $W/fusion/s2.zip && touch $W/fusion/DONE
  say "fusion steps: $(ls $W/fusion/step | wc -l)"
fi
for ch in 0042:88795 0043:88799; do
  c=${ch%%:*}; id=${ch##*:}
  [ -f $W/abc/$c/DONE ] && continue
  mkdir -p $W/abc/$c; say "download abc $c"
  curl -sS -o $W/abc/$c.7z https://archive.nyu.edu/rest/bitstreams/$id/retrieve &&
  (cd $W/abc/$c && 7za x -y -bd ../$c.7z > ../$c.x.log) && rm -f $W/abc/$c.7z && touch $W/abc/$c/DONE
  say "abc $c steps: $(find $W/abc/$c -name '*.step' | wc -l)"
done
stop download
# 2. exclusions
if [ ! -f $R/exclusion/exclusion_sources.json ]; then
  say "exclusions"
  $PY $P exclusions --out $R/exclusion --deepcad-ids $W/deepcad_full_ids.txt --scan $DV/results $MB/data $W/s20_keys \
    $(ls -d $DV/rft_* $DV/dsv41_*tier* $DV/conn_tier_unused 2>/dev/null) $DV/hard_keys_v1.txt $DV/hard_keys_near_v1.txt $DV/hard_keys_never_v1.txt \
    || { say "exclusions FAILED"; exit 1; }
fi
stop exclusions
# 3. candidates + prep
if [ ! -f $W/cand/candidates.json ]; then
  say "candidates"; $PY $P candidates --excl $R/exclusion --fusion-dir $W/fusion/step --abc-dir $W/abc --out $W/cand \
    --n-f ${NF:-1500} --n-a ${NA:-1500} || { say "candidates FAILED"; exit 1; }
fi
if [ ! -f $W/prep/manifest.json ]; then
  say "prep"; mkdir -p $W/prep/chunks $W/prep/step_mm $W/prep/gt_meshes_v15 $W/logs
  ls -d $W/cand/src/*/ | xargs -P 15 -I{} bash -c 'd={}; n=$(basename $d); [ -f '"$W"'/prep/chunks/$n/manifest.json ] || '"$PY $MB"'/prep_external_parts.py --src $d --out '"$W"'/prep/chunks/$n --max-faces 80 > '"$W"'/logs/prep_$n.log 2>&1'
  $PY - $W/prep <<'PYX'
import json, glob, os, shutil, collections, sys
C = sys.argv[1]; parts = {}; rej = collections.Counter()
for m in sorted(glob.glob(f"{C}/chunks/*/manifest.json")):
    man = json.load(open(m)); d = os.path.dirname(m)
    for k, v in man["parts"].items():
        v["family"] = k[0]; v["label"] = "x"; parts[k] = v
        for sub in ("step_mm", "gt_meshes_v15"):
            for f in glob.glob(f"{d}/{sub}/{k}.*"):
                dst = f"{C}/{sub}/{os.path.basename(f)}"
                if not os.path.exists(dst): shutil.move(f, dst)
    rej.update(man.get("rejected", {}))
json.dump({"target_mm": 80, "max_faces": 80, "parts": parts, "rejected": dict(rej)}, open(f"{C}/manifest.json", "w"), indent=1)
print("kept", len(parts), dict(collections.Counter(v["family"] for v in parts.values())), "rejected", dict(rej))
PYX
fi
stop prep
# 4. select
[ -f $R/selection.json ] || { say "select"; $PY $P select --prep-manifest $W/prep/manifest.json --excl $R/exclusion --out $R/selection.json --target ${TARGET:-280} || exit 1; }
stop select
# 5. render the selected set (one renderer process per part; no legacy fallback)
RS=$W/render_set
if [ ! -f $RS/RENDER_DONE ]; then
  mkdir -p $RS/step_mm $RS/gt_meshes_v15
  $PY - $R/selection.json $W/prep $RS <<'PYX'
import json, os, sys
sel, prep, rs = sys.argv[1:4]; s = json.load(open(sel)); man = json.load(open(f"{prep}/manifest.json"))
for k in s["render_list"]:
    for sub, ext in (("step_mm", "step"), ("gt_meshes_v15", "stl")):
        d = f"{rs}/{sub}/{k}.{ext}"
        if not os.path.lexists(d): os.symlink(f"{prep}/{sub}/{k}.{ext}", d)
json.dump({"target_mm": 80, "max_faces": 80, "parts": {k: man["parts"][k] for k in s["render_list"]}}, open(f"{rs}/manifest.json", "w"), indent=1)
print("render set", len(s["render_list"]))
PYX
  say "render"; M=$MB PYV=$PY RPY=$S/dw_venv/bin/python SCRIPT_DIR=$S/step_to_drw bash $MB/render_isolated.sh $RS 15 > $W/logs/render.log 2>&1
  touch $RS/RENDER_DONE; say "render: $(grep -c ' ok' $RS/logs/iso.log) ok, $(grep -c FAIL $RS/logs/iso.log) FAIL"
fi
stop render
# 6. finalize + leak check (freeze)
if [ ! -f $BB/eval_cache_v15.pkl ]; then
  say "finalize"; $PY $P finalize --select $R/selection.json --prep-manifest $RS/manifest.json --prep-dir $W/prep --render-dir $RS/render --bench $BB || exit 1
fi
$PY $P leakcheck --bench $BB --excl $R/exclusion --out $R/leakcheck.json || { say "LEAK CHECK FAILED"; exit 1; }
say "BENCH B BUILD DONE"
