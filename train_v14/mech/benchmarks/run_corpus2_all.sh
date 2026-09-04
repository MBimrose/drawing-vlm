#!/usr/bin/env bash
# Corpus 2 end-to-end on serv-19. Stage 1 (CPU/download): download -> 40-way prep (--max-faces 120) -> merge
# -> render -> eval cache. Stage 2 (GPU): wait until NO bestofn workers run and all GPUs < 5 GB, then
# 8 x e40 best-of-8 -> merge -> write_rft_real.py -> rft_real2/.
set -u
R=e40-rft-strict-all-6k; DV=/srv/scratch/bimrose2; M=$DV/mech_benchmarks; C=$M/rft_corpus2; PY=$DV/.venv/bin/python
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
mkdir -p $C/logs $C/prep $C/step_mm $C/gt_meshes_v15 $C/results
echo "STAGE1 START $(date)" >> $C/logs/stage.log
$PY $M/build_corpus2.py --out $C --exclude $M/exclude_ids_corpus2.txt > $C/logs/download.log 2>&1
echo "DOWNLOAD DONE $(date)" >> $C/logs/stage.log
ls -d $C/src/*/ | xargs -P 40 -I{} bash -c 'd={}; n=$(basename $d); '"$PY"' '"$M"'/prep_external_parts.py --src $d --out '"$C"'/prep/$n --max-faces 120 --timeout 60 > '"$C"'/logs/prep_$n.log 2>&1'
echo "PREP DONE $(date)" >> $C/logs/stage.log
$PY - <<'PYEOF'
import json, glob, os, shutil, collections
C="/srv/scratch/bimrose2/mech_benchmarks/rft_corpus2"; parts={}; rej=collections.Counter()
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
# ---- stage 2: wait for a free machine ----
while pgrep -f "[b]estofn_verifier_eval" > /dev/null || [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '$1>5000' | wc -l)" -gt 0 ]; do
  echo "waiting: workers=$(pgrep -f '[b]estofn_verifier_eval' | wc -l) busy_gpus=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '$1>5000' | wc -l) $(date)" >> $C/logs/wait.log; sleep 300
done
cd $DV; source train_v14/env.sh
export DRAWING_VLM_TRACES_JSON=$C/traces_v14.json DRAWING_VLM_EVAL_CACHE=$C/eval_cache_v14.pkl
for i in 0 1 2 3 4 5 6 7; do
  CUDA_VISIBLE_DEVICES=$i nohup .venv/bin/python train_v14/geom/bestofn_verifier_eval.py \
    --ckpt runs/$R/final --kind hf --run $R-serv19 --verifier "" --n 100000 --k 8 \
    --temperature 0.7 --batch 16 --shard $i --nshards 8 \
    --out $C/results/bo8_corpus2_$R.shard$i.json > $C/logs/bo8_corpus2.shard$i.log 2>&1 &
done
echo "GEN LAUNCHED $(date)" >> $C/logs/stage.log
wait
.venv/bin/python train_v14/geom/merge_bo_shards.py $C/results/bo8_corpus2_$R.json $C/results/bo8_corpus2_$R.shard?.json > $C/logs/merge.log 2>&1
echo "MERGE DONE $(date)" >> $C/logs/stage.log
mkdir -p $M/rft_real2
$PY $M/write_rft_real.py --bo8 $C/results/bo8_corpus2_$R.json --png-dir $C/render/png --manifest $C/manifest.json --sidecar $C/render/renderers.json --out $M/rft_real2 > $C/logs/rft_real2.log 2>&1
echo "STAGE2 DONE $(date)" >> $C/logs/stage.log
