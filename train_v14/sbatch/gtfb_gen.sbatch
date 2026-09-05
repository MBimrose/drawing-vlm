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
# Privileged-hint generation on the unsolved real parts of one corpus, 8 single-GPU shards.
#   sbatch --export=ALL,RUN=<run>,CORPUS=corpus1|corpus2,OUT=<tier_dir>[,ROUNDS=2,K=4,MODE=hint] train_v14/sbatch/gtfb_gen.sbatch
# Weights are staged once to /dev/shm (the shared FS took ~1 h per load with three jobs reading finals).
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
D=$DV/train_v14/mech/benchmarks/data
case "$CORPUS" in corpus1) C=$D/rft_corpus;; corpus2) C=$D/rft_corpus2;; *) echo "bad CORPUS"; exit 2;; esac
export OPENBLAS_NUM_THREADS=1 DRAWING_VLM_TRACES_JSON=$C/traces_v14.json DRAWING_VLM_EVAL_CACHE=$C/eval_cache_v15.pkl
G=$DV/train_v14/geom; mkdir -p $DV/logs/gtfb $OUT
SHM=/dev/shm/bimrose2_$SLURM_JOB_ID; trap 'rm -rf $SHM' EXIT
mkdir -p $SHM && echo "$(date) staging weights to $SHM" && cp -r $DV/runs/$RUN/final $SHM/ && echo "$(date) staged" || { echo "staging failed, loading from Lustre"; SHM=""; }
CK=${SHM:+$SHM/final}; CK=${CK:-$DV/runs/$RUN/final}
COMMON="--ckpt $CK --run $RUN --keys $D/unsolved_keys.json --corpus $CORPUS --seeds $D/unsolved_seeds.json --mode ${MODE:-hint} --k ${K:-4} --temperature 0.7 --batch 8 --nshards 8"
# smoke: 16 keys x K draws on GPU 0; proceed only if it accepts something or beats the seeds
rm -rf $OUT/smoke; CUDA_VISIBLE_DEVICES=0 python $G/gt_feedback_gen.py $COMMON --rounds 1 --shard 0 --limit 16 --out $OUT/smoke > $DV/logs/gtfb/smoke_${CORPUS}.log 2>&1 || { echo "SMOKE FAILED"; tail -30 $DV/logs/gtfb/smoke_${CORPUS}.log; exit 1; }
grep "gtfb\] DONE" $DV/logs/gtfb/smoke_${CORPUS}.log
python - "$OUT/smoke/summary-000.json" <<'PY' || { echo "SMOKE GATE: no gain over seeds — stopping"; exit 1; }
import json, sys, statistics as st
b = json.load(open(sys.argv[1]))["best"]
new = [v["iou"] for v in b.values() if v["iou"] >= 0]; seed = [v["seed_iou"] or 0 for v in b.values()]
acc = sum(v["iou"] >= 0.8 for v in b.values())
print(f"SMOKE: {len(b)} keys, best-of-hinted mean {st.mean(new) if new else 0:.3f} vs seed mean {st.mean(seed):.3f}, accepted keys {acc}")
sys.exit(0 if (acc >= 1 or (new and st.mean(new) > st.mean(seed) + 0.02)) else 1)
PY
for i in 0 1 2 3 4 5 6 7; do
  CUDA_VISIBLE_DEVICES=$i python $G/gt_feedback_gen.py $COMMON --rounds ${ROUNDS:-2} --shard $i --out $OUT > $DV/logs/gtfb/${CORPUS}.shard$i.log 2>&1 &
done
wait
echo "GTFB DONE $CORPUS: $(cat $OUT/accepted-00?.jsonl | wc -l) accepted rows on $(cat $OUT/accepted-00?.jsonl | python -c 'import sys,json; print(len({json.loads(l)["key"] for l in sys.stdin}))') keys"
