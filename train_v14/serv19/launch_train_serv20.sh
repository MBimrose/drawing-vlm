#!/usr/bin/env bash
# Full fine-tune on wpk-serv-20 GPUs 4-7 ONLY (GPUs 0-3 belong to someone else; serv-04 is off-limits
# since 2026-09-23). Same run.sh / FSDP2 path as launch_e58_serv04.sh with a 4-rank accelerate config.
#   bash launch_train_serv20.sh <config> <mix dir>        (run on serv-20)
set -uo pipefail
DV=/srv/scratch/bimrose2; CFG=${1:?config}; MIX=${2:?mix}
cd $DV; mkdir -p logs runs
[ -e $DV/drawing_vlm ] || ln -s . $DV/drawing_vlm
for f in $DV/$MIX/rft-*.tar; do
  t=$(readlink "$f"); case "$t" in /projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/*) ln -sfn "$DV/${t#/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/}" "$f";; esac
done
bad=$(find $DV/$MIX -xtype l | wc -l); echo "mix: $(ls $DV/$MIX | wc -l) shards, $bad dangling"
[ "$bad" = 0 ] || { echo "dangling mix links; abort"; exit 1; }
export CUDA_VISIBLE_DEVICES=4,5,6,7
export DRAWING_VLM_ROOT=$DV
export DRAWING_VLM_TARS=$DV/step_to_drw/wds_dataset/tars_v14_dw423
export DRAWING_VLM_EVAL_CACHE_V15=$DV/step_to_drw/wds_dataset/eval_cache_v15_dw423.pkl
export DRAWING_VLM_RFT_SHARDS=$DV/$MIX
export DRAWING_VLM_BUNDLE=$DV/v14_bundle
export DRAWING_VLM_EVAL_CACHE=$DV/step_to_drw/wds_dataset/eval_cache_v14.pkl
export DRAWING_VLM_BAD_KEYS=$DV/step_to_drw/wds_dataset/exec_bad_keys_v14.txt
export TRAIN_VENV=$DV/.venv
RUN=$(grep -E "^run_name:" train_v14/configs/$CFG.yaml | awk '{print $2}')
: > logs/${RUN}_serv20.log
setsid nohup bash -c "cd $DV && bash train_v14/run.sh train_v14/configs/$CFG.yaml \
    --model_id=$DV/models/Qwen3.8-27B --output_dir=$DV/runs/$RUN --eval_every=0; echo TRAIN EXIT \$?" \
    >> logs/${RUN}_serv20.log 2>&1 < /dev/null &
sleep 2; echo "$RUN launched on $(hostname) GPUs $CUDA_VISIBLE_DEVICES: log $DV/logs/${RUN}_serv20.log"
