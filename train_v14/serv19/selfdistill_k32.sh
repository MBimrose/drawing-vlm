#!/usr/bin/env bash
# Step 3 of the 2026-09-10 queue: self-distilled reasoning for hard real parts.
#
# The real-part tiers so far were built at K=8: a part enters the tier only if one
# of 8 draws verifies at IoU >= 0.8, so the tier teaches the parts the model already
# finds easily and saturates (~1,000 parts, RECIPE "round 4/5"). The ceiling keeps
# rising with K (e55 real bench: vote 0.539 but oracle 0.646 at K=32), so the parts
# solvable ONLY at 32 draws are exactly the ones no tier has taught yet -- and their
# winning draw carries the model's OWN think trace, which is what the ground-truth
# ABC tier lacked (e56: base-model plans memorise, do not generalise).
#
# This pass: e55, K=32, T=0.7, over the corpus keys still unsolved after rounds 1-5,
# on draftwright-0.4.23 sheets (the engine e55 and serving now use), then the tier
# write (accepted = exec and IoU >= 0.8, think trace kept).
#
#   sbatch train_v14/sbatch/selfdistill_k32.sbatch          (one H200 node per corpus)
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
R=${RUN:-e55-rft-real-u5-gt-dw423}
CN=${CORPUS:-rft_corpus_dw423}          # rft_corpus_dw423 | rft_corpus2_dw423
KEYS=${KEYS:-$DV/train_v14/mech/benchmarks/data/unsolved_${CN}.txt}
K=${K:-32}
C=$DV/train_v14/mech/benchmarks/data/$CN
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
# e55's config is data_version 2, so the eval scripts read EVAL_CACHE_V15 (pool "certified")
# and gt_meshes_v15 next to EVAL_CACHE -- both must point INSIDE the corpus.
export OPENBLAS_NUM_THREADS=1 DRAWING_VLM_TRACES_JSON=$C/traces_v14.json \
  DRAWING_VLM_EVAL_CACHE=$C/eval_cache_v14.pkl DRAWING_VLM_EVAL_CACHE_V15=$C/eval_cache_v15.pkl
mkdir -p $C/results $C/logs
# Stage the weights once: 8 workers reading runs/$R/final off Lustre took ~1 h under contention.
SHM=/dev/shm/bimrose2_sd_${SLURM_JOB_ID:-$$}; trap 'rm -rf $SHM' EXIT
CK=$DV/runs/$R/final
if mkdir -p $SHM && cp -r $CK $SHM/base; then CK=$SHM/base; echo "$(date) staged weights -> $CK";
else echo "$(date) staging failed, loading from Lustre"; rm -rf $SHM; SHM=""; fi
for i in 0 1 2 3 4 5 6 7; do
  CUDA_VISIBLE_DEVICES=$i python $DV/train_v14/geom/bestofn_verifier_eval.py \
    --ckpt $CK --kind hf --run $R --verifier "" --n 0 --k $K --keys $KEYS \
    --temperature 0.7 --batch 16 --shard $i --nshards 8 \
    --out $C/results/bo${K}_${CN}_$R.shard$i.json > $C/logs/bo${K}_$R.shard$i.log 2>&1 &
done
wait
python $DV/train_v14/geom/merge_bo_shards.py $C/results/bo${K}_${CN}_$R.json \
  $C/results/bo${K}_${CN}_$R.shard?.json > $C/logs/merge_$R.log 2>&1
python $DV/train_v14/mech/benchmarks/write_rft_real.py --bo8 $C/results/bo${K}_${CN}_$R.json \
  --png-dir $C/render/png --manifest $C/manifest.json --out $DV/rft_selfdistill_${CN} > $C/logs/tier_${CN}.log 2>&1
tail -5 $C/logs/tier_${CN}.log
echo "SELFDISTILL DONE $CN -> rft_selfdistill_${CN}"
