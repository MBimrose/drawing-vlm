#!/bin/bash
#SBATCH --job-name=selfdistill
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=64
#SBATCH --gres=gpu:H200:8
#SBATCH --mem=1000G
#SBATCH --time=24:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.err
# Self-distilled reasoning tier for hard real parts (K=32 over the still-unsolved corpus keys).
#   sbatch --export=ALL,CORPUS=rft_corpus_dw423 train_v14/sbatch/selfdistill_k32.sbatch
set -uo pipefail
bash /projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/train_v14/serv19/selfdistill_k32.sh
