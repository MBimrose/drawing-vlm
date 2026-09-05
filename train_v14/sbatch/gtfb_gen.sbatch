#!/bin/bash
#SBATCH --job-name=gtfb-gen
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=64
#SBATCH --gres=gpu:H200:8
#SBATCH --mem=1000G
#SBATCH --time=16:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.err
# Privileged-feedback generation on the unsolved real parts of one corpus, 8 single-GPU shards.
#   sbatch --export=ALL,RUN=<run>,CORPUS=corpus1|corpus2,OUT=<tier_dir>[,ROUNDS=3,K=4] train_v14/sbatch/gtfb_gen.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
D=$DV/train_v14/mech/benchmarks/data
case "$CORPUS" in corpus1) C=$D/rft_corpus;; corpus2) C=$D/rft_corpus2;; *) echo "bad CORPUS"; exit 2;; esac
export OPENBLAS_NUM_THREADS=1 DRAWING_VLM_TRACES_JSON=$C/traces_v14.json DRAWING_VLM_EVAL_CACHE=$C/eval_cache_v15.pkl
G=$DV/train_v14/geom; mkdir -p $DV/logs/gtfb $OUT
COMMON="--ckpt $DV/runs/$RUN/final --run $RUN --keys $D/unsolved_keys.json --corpus $CORPUS --seeds $D/unsolved_seeds.json --rounds ${ROUNDS:-3} --k ${K:-4} --temperature 0.7 --batch 8 --nshards 8"
# smoke: 2 keys, 1 round on GPU 0
CUDA_VISIBLE_DEVICES=0 python $G/gt_feedback_gen.py $COMMON --shard 0 --limit 2 --rounds 1 --out $OUT/smoke > $DV/logs/gtfb/smoke_${CORPUS}.log 2>&1 || { echo "SMOKE FAILED"; tail -30 $DV/logs/gtfb/smoke_${CORPUS}.log; exit 1; }
tail -3 $DV/logs/gtfb/smoke_${CORPUS}.log
for i in 0 1 2 3 4 5 6 7; do
  CUDA_VISIBLE_DEVICES=$i python $G/gt_feedback_gen.py $COMMON --shard $i --out $OUT > $DV/logs/gtfb/${CORPUS}.shard$i.log 2>&1 &
done
wait
cat $OUT/accepted-00?.jsonl > $OUT/accepted-000.jsonl.merged 2>/dev/null
echo "GTFB DONE $CORPUS: $(cat $OUT/accepted-00?.jsonl | wc -l) accepted rows on $(cat $OUT/accepted-00?.jsonl | python -c 'import sys,json; print(len({json.loads(l)["key"] for l in sys.stdin}))') keys"
