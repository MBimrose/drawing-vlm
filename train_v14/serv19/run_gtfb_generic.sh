#!/usr/bin/env bash
# Usage: ./run_gtfb_generic.sh <run> <corpus1|corpus2> <mode: plain|hint> <out_dir_name> [rounds] [k]
# 8 single-GPU workers of gt_feedback_gen.py on the unsolved keys of one corpus (serv-19 paths).
R=$1; CORPUS=$2; MODE=$3; OUTN=$4; ROUNDS=${5:-2}; K=${6:-4}
DV=/srv/scratch/bimrose2; M=$DV/mech_benchmarks
case "$CORPUS" in corpus1) C=$M/rft_corpus;; corpus2) C=$M/rft_corpus2;; *) echo bad corpus; exit 2;; esac
cd $DV; source train_v14/env.sh
export OPENBLAS_NUM_THREADS=1 DRAWING_VLM_TRACES_JSON=$C/traces_v14.json DRAWING_VLM_EVAL_CACHE=$C/eval_cache_v15.pkl
mkdir -p $M/$OUTN logs
for i in 0 1 2 3 4 5 6 7; do
  CUDA_VISIBLE_DEVICES=$i nohup .venv/bin/python train_v14/geom/gt_feedback_gen.py --ckpt runs/$R/final --run $R-serv19 \
    --keys $M/unsolved_keys.json --corpus $CORPUS --seeds $M/unsolved_seeds.json --mode $MODE --rounds $ROUNDS --k $K \
    --temperature 0.7 --batch 8 --shard $i --nshards 8 --out $M/$OUTN > logs/gtfb_${MODE}_${CORPUS}.shard$i.log 2>&1 &
done
wait
echo "GTFB DONE $MODE $CORPUS: $(cat $M/$OUTN/accepted-00?.jsonl | wc -l) rows on $(cat $M/$OUTN/accepted-00?.jsonl | .venv/bin/python -c 'import sys,json; print(len({json.loads(l)["key"] for l in sys.stdin}))') keys"
