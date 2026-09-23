#!/usr/bin/env bash
# Pull accepted family-synthesis parts from serv-20 into a cluster corpus dir and render their sheets
# (draftwright 0.4.23 + font patch via render_variant.sbatch, no env overrides = the training-sheet style).
#   bash pack_family_corpus.sh <serv-20 run dir name, e.g. pilot> <corpus name, e.g. family_pilot>
set -euo pipefail
RUNNAME=${1:?run}; CORPUS=${2:?corpus}
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; S20=wpk-serv-20.mechse.illinois.edu
SRC=/srv/scratch/bimrose2/familysynth/$RUNNAME; C=$DV/train_v14/mech/benchmarks/data/$CORPUS
mkdir -p $C
rsync -a $S20:$SRC/step_mm $S20:$SRC/gt_meshes_v15 $S20:$SRC/code $S20:$SRC/rows.jsonl $S20:$SRC/descriptions.jsonl $C/
python3 - "$C" <<'PY'
import json, os, sys
C = sys.argv[1]; rows = [json.loads(l) for l in open(os.path.join(C, "rows.jsonl"))]
ok = {r["id"]: r for r in rows if r.get("ok") and os.path.exists(os.path.join(C, "step_mm", r["id"] + ".step"))}
# drop steps of ids that were later rejected/overwritten
for f in os.listdir(os.path.join(C, "step_mm")):
    if f[:-5] not in ok: os.remove(os.path.join(C, "step_mm", f))
man = {"parts": {k: {"family": "Z", "src": os.path.join(C, "step_mm", k + ".step"), "part_family": r["family"], "seed": r["seed"], "model": r["model"], "faces": r["faces"],
                      "bbox_mm": r["bbox"], "desc": r["desc"]} for k, r in ok.items()}, "source": "family_synth.py"}
json.dump(man, open(os.path.join(C, "manifest.json"), "w"), indent=1)
json.dump({"test": sorted(ok)}, open(os.path.join(C, "split.json"), "w"))
print(f"{len(ok)} accepted parts of {len(rows)} rows -> {C}")
PY
J=$(sbatch --parsable --export=ALL,C=$C --job-name=render-$CORPUS $DV/train_v14/sbatch/render_variant.sbatch)
echo "render job $J"
