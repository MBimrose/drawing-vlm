#!/bin/bash
#SBATCH --job-name=rft3-pack
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.e%j
set -euo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
$DV/.venv/bin/python $DV/train_v14/geom/pack_rft_shards.py $DV/rft_v3
cd $DV/rft_all/shards && for f in ../../rft_v3/shards/rft-*.tar; do ln -sf "$f" "rft-v3-$(basename $f .tar | cut -d- -f2).tar"; done && echo "rft_all: $(ls | wc -l) shards"
