#!/usr/bin/env bash
# Evaluate <run> on the ABC ground-truth-code corpus in both renderings (serv-19), best-of-8 + consistency.
#   ./run_abccode_eval.sh <run>      (needs configs/<run>-serv19.yaml and runs/<run>/final on serv-19)
R=$1; DV=/srv/scratch/bimrose2; M=$DV/mech_benchmarks; cd $DV
./run_corpus_gen_generic.sh $R rft_corpus_abccode_dw400 rft_abccode_dw400_$R 8 > $M/rft_corpus_abccode_dw400/logs/gen_$R.log 2>&1
./run_corpus_gen_generic.sh $R rft_corpus_abccode rft_abccode_dw423_$R 8 > $M/rft_corpus_abccode/logs/gen_$R.log 2>&1
source train_v14/env.sh; export OPENBLAS_NUM_THREADS=1
for C in rft_corpus_abccode_dw400 rft_corpus_abccode; do
  B=$M/$C; export DRAWING_VLM_TRACES_JSON=$B/traces_v14.json DRAWING_VLM_EVAL_CACHE=$B/eval_cache_v14.pkl
  .venv/bin/python train_v14/geom/consistency_rerank.py $B/results/bo8_${C}_$R.json $B/results/bo8_${C}_${R}_consistency.json > $B/logs/consistency_$R.log 2>&1 &
done
wait
echo "ABCCODE EVAL DONE $R $(date)"
