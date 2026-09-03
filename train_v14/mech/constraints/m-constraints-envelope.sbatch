#!/bin/bash
#SBATCH --job-name=m-constraints-envelope
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=120G
#SBATCH --time=8:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/mech/constraints/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/mech/constraints/%x.e%j
# CPU-only: execute every stored champion candidate (1,030 x 8) and a sample of
# RFT-scored candidates (with think blocks); record built envelope / volume,
# declared dims, stated envelope, GT envelope.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
export OPENBLAS_NUM_THREADS=1
M=$DV/train_v14/mech/constraints
python $M/envelope_features.py --bo8 $DV/results/bo8_full_e24.json --workers 30 --out $M/out/env_bo8_full_e24.jsonl
python $M/envelope_features.py --scored "$DV/rft_scored_v1/scored-00[0-3].jsonl" --max 8000 --workers 30 --out $M/out/env_scored_v1.jsonl
