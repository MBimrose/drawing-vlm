#!/bin/bash
#SBATCH --job-name=ship-s20
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=10:00:00
#SBATCH --nodelist=ccc0442
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/real/%x-%j.out
# Ship everything a full fine-tune needs to wpk-serv-20 (same relative layout under /srv/scratch/bimrose2),
# from the cluster (not from serv-04, which is off-limits since 2026-09-23).
#   sbatch --export=ALL,MIX=rft_mix_u10_synthlong_dw423,TIERS="rft_strict90_all_dw423b rft_real_union5_dw423 rft_synth_long" ship_train_serv20.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; H=wpk-serv-20.mechse.illinois.edu; SDV=/srv/scratch/bimrose2
cd $DV
ssh -o BatchMode=yes $H "mkdir -p $SDV/models $SDV/step_to_drw/wds_dataset $SDV/logs $SDV/runs"
R() { rsync -a --info=stats1 "$@" || echo "RSYNC FAIL $*"; }
R train_v14 $H:$SDV/ --exclude mech/benchmarks/data --exclude __pycache__
R models/Qwen3.8-27B $H:$SDV/models/
W=step_to_drw/wds_dataset
R $W/tars_v14_dw423 $W/eval_cache_v15_dw423.pkl $W/eval_cache_v14.pkl $W/exec_bad_keys_v14.txt $W/traces_v14 $H:$SDV/$W/
[ -f $W/traces_v14.json ] && R $W/traces_v14.json $H:$SDV/$W/
R v14_bundle $H:$SDV/
for t in ${TIERS}; do R $t $H:$SDV/ --exclude png; done
R ${MIX} $H:$SDV/
ssh -o BatchMode=yes $H "cd $SDV; du -sh models/Qwen3.8-27B $W/tars_v14_dw423 v14_bundle ${TIERS} 2>&1"
echo "SHIP DONE $(date)"
