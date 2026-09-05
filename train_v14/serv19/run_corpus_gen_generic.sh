#!/usr/bin/env bash
# Best-of-8 generation pass of <run> over a real-geometry corpus on serv-19, then the tier write.
#   ./run_corpus_gen_generic.sh <run> <corpus_dir_name e.g. rft_corpus3> <tier_out_name e.g. rft_real_c3> [K]
R=$1; CN=$2; OUTN=$3; K=${4:-8}; DV=/srv/scratch/bimrose2; M=$DV/mech_benchmarks; C=$M/$CN; PY=$DV/.venv/bin/python
cd $DV; source train_v14/env.sh
export OPENBLAS_NUM_THREADS=1 DRAWING_VLM_TRACES_JSON=$C/traces_v14.json DRAWING_VLM_EVAL_CACHE=$C/eval_cache_v14.pkl
mkdir -p $C/results $C/logs
for i in 0 1 2 3 4 5 6 7; do
  CUDA_VISIBLE_DEVICES=$i nohup $PY train_v14/geom/bestofn_verifier_eval.py \
    --ckpt runs/$R/final --kind hf --run $R-serv19 --verifier "" --n 100000 --k $K --temperature 0.7 --batch 16 \
    --shard $i --nshards 8 --out $C/results/bo${K}_${CN}_$R.shard$i.json > $C/logs/bo${K}_$R.shard$i.log 2>&1 &
done
wait
$PY train_v14/geom/merge_bo_shards.py $C/results/bo${K}_${CN}_$R.json $C/results/bo${K}_${CN}_$R.shard?.json > $C/logs/merge_$R.log 2>&1
$PY $M/write_rft_real.py --bo8 $C/results/bo${K}_${CN}_$R.json --png-dir $C/render/png --manifest $C/manifest.json --sidecar $C/render/renderers.json --out $M/$OUTN > $C/logs/${OUTN}.log 2>&1
tail -3 $C/logs/${OUTN}.log
echo "GEN DONE $R $CN -> $OUTN"
