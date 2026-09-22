#!/bin/bash
#SBATCH --job-name=render-var
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=48
#SBATCH --mem=200G
#SBATCH --time=06:00:00
#SBATCH --nodelist=ccc0442
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/real/%x-%j.out
# Re-render a bench variant (same STEPs, same key-seeded layout) with renderer env overrides,
# e.g. DW_SCALE_POLICY=fallback (every required dimension placed) or DW_AUTO_DIMS=0 (no dims).
#   sbatch --export=ALL,C=<bench dir>,DW_SCALE_POLICY=...,DW_AUTO_DIMS=... render_variant.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
S=/dev/shm/bimrose2/rv_$SLURM_JOB_ID; mkdir -p $S; trap 'rm -rf $S' EXIT
rsync -a --copy-links $DV/.venv/ $S/venv/ & rsync -a --copy-links $DV/dw_venv/ $S/dw_venv/ & rsync -a $DV/mech_step_to_drw/ $S/step_to_drw/ & wait
echo "env: DW_SCALE_POLICY=${DW_SCALE_POLICY:-} DW_AUTO_DIMS=${DW_AUTO_DIMS:-}"
M=$DV/train_v14/mech/benchmarks PYV=$S/venv/bin/python RPY=$S/dw_venv/bin/python SCRIPT_DIR=$S/step_to_drw \
  bash $DV/train_v14/mech/benchmarks/render_isolated.sh $C ${P:-44}
tail -4 $C/logs/stage.log
