#!/usr/bin/env bash
# e58 (27B full FT on the DeepCAD mix) on wpk-serv-04's 8x H200 instead of the cluster.
# Same run.sh / accelerate FSDP2 8-GPU path; the layout is /srv/scratch/bimrose2 with a
# `drawing_vlm -> .` self-link so env.sh's $ROOT/drawing_vlm/... paths resolve. The in-training
# geometry eval is disabled (serv-04's glibc cannot load OCP); the final checkpoint is judged
# by the split generate-on-serv-04 / score-on-cluster-CPU chain.
#   bash launch_e58_serv04.sh [config=e58-rft-deepcad-dw423]
set -uo pipefail
DV=/srv/scratch/bimrose2; CFG=${1:-e58-rft-deepcad-dw423}
cd $DV; mkdir -p logs runs
[ -e $DV/drawing_vlm ] || ln -s . $DV/drawing_vlm
# the mix dir came over as absolute cluster symlinks: point them at the local copies
for f in $DV/${MIX:-rft_mix_u8_deepcad_dw423}/rft-*.tar; do
  t=$(readlink "$f"); case "$t" in /projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/*) ln -sfn "$DV/${t#/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/}" "$f";; esac
done
bad=$(find $DV/${MIX:-rft_mix_u8_deepcad_dw423} -xtype l | wc -l); echo "mix: $(ls $DV/${MIX:-rft_mix_u8_deepcad_dw423} | wc -l) shards, $bad dangling"
[ "$bad" = 0 ] || { echo "dangling mix links; abort"; exit 1; }
export DRAWING_VLM_ROOT=$DV
export DRAWING_VLM_TARS=$DV/step_to_drw/wds_dataset/tars_v14_dw423
export DRAWING_VLM_EVAL_CACHE_V15=$DV/step_to_drw/wds_dataset/eval_cache_v15_dw423.pkl
export DRAWING_VLM_RFT_SHARDS=$DV/${MIX:-rft_mix_u8_deepcad_dw423}
# data_v14 defaults that env.sh does not derive from ROOT
export DRAWING_VLM_BUNDLE=$DV/v14_bundle
export DRAWING_VLM_EVAL_CACHE=$DV/step_to_drw/wds_dataset/eval_cache_v14.pkl
export DRAWING_VLM_BAD_KEYS=$DV/step_to_drw/wds_dataset/exec_bad_keys_v14.txt
export TRAIN_VENV=$DV/.venv
: > logs/${CFG}_serv04.log
setsid nohup bash -c "cd $DV && bash train_v14/run.sh train_v14/configs/$CFG.yaml \
    --model_id=$DV/models/Qwen3.8-27B --output_dir=$DV/runs/$CFG --eval_every=0; echo TRAIN EXIT \$?" \
    >> logs/${CFG}_serv04.log 2>&1 < /dev/null &
sleep 2; echo "e58 launched on $(hostname): log $DV/logs/${CFG}_serv04.log"
