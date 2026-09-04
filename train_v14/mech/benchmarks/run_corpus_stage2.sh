#!/usr/bin/env bash
# Stage 2 on serv-19: render corpus (CPU) -> eval cache -> 8x single-GPU e40 best-of-8 -> merge -> rft_real files.
set -u
R=e40-rft-strict-all-6k; DV=/srv/scratch/bimrose2; M=$DV/mech_benchmarks; C=$M/rft_corpus; PY=$DV/.venv/bin/python
cd $M; echo "STAGE2 START $(date)" >> $C/logs/stage2.log
SCRIPT_DIR=$M/step_to_drw OMP_NUM_THREADS=2 /software/python-3.11.1/bin/python3 $M/render_ext.py --src $C/step_mm --out $C/render --workers 96 > $C/logs/render.log 2>&1
echo "RENDER DONE $(date) $(ls $C/render/png | wc -l) png" >> $C/logs/stage2.log
$PY $M/build_ext_eval_cache.py --bench $C --png-dir $C/render/png > $C/logs/cache.log 2>&1; cat $C/logs/cache.log >> $C/logs/stage2.log
N=$($PY -c "import pickle;print(len(pickle.load(open('$C/eval_cache_v15.pkl','rb'))['pools']['certified']))")
echo "CACHE $N parts" >> $C/logs/stage2.log
# GPU guard: wait until every GPU is under 5 GB
while [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '$1>5000' | wc -l)" -gt 0 ]; do echo "GPUs busy, waiting $(date)" >> $C/logs/stage2.log; sleep 300; done
cd $DV; source train_v14/env.sh
export DRAWING_VLM_TRACES_JSON=$C/traces_v14.json DRAWING_VLM_EVAL_CACHE=$C/eval_cache_v14.pkl
mkdir -p $C/results
for i in 0 1 2 3 4 5 6 7; do
  CUDA_VISIBLE_DEVICES=$i nohup .venv/bin/python train_v14/geom/bestofn_verifier_eval.py \
    --ckpt runs/$R/final --kind hf --run $R-serv19 --verifier "" --n 100000 --k 8 \
    --temperature 0.7 --batch 16 --shard $i --nshards 8 \
    --out $C/results/bo8_corpus_$R.shard$i.json > $C/logs/bo8_corpus.shard$i.log 2>&1 &
done
echo "GEN LAUNCHED $(date)" >> $C/logs/stage2.log
wait
.venv/bin/python train_v14/geom/merge_bo_shards.py $C/results/bo8_corpus_$R.json $C/results/bo8_corpus_$R.shard?.json > $C/logs/merge.log 2>&1
echo "MERGE DONE $(date)" >> $C/logs/stage2.log
mkdir -p $M/rft_real
$PY $M/write_rft_real.py --bo8 $C/results/bo8_corpus_$R.json --png-dir $C/render/png --manifest $C/manifest.json --sidecar $C/render/renderers.json --out $M/rft_real > $C/logs/rft_real.log 2>&1
echo "STAGE2 DONE $(date)" >> $C/logs/stage2.log
