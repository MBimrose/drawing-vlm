#!/bin/bash
#SBATCH --job-name=c2-pgs
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodelist=ccc0442
#SBATCH --cpus-per-task=56
#SBATCH --mem=300G
#SBATCH --time=12:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/cycle2/pipeline/logs/%x-%j.out
# Cycle-2 pipeline stage 2 (ccc0442 CPU): pull the K=16 partials of <NAME> from serv-20 once generated, then exactly
# results/pipeline_grpo's pg_score_rc.sbatch (score_partials eval rule, consistency_rerank, render_compare + rc_metric2 v3).
#   sbatch --export=ALL,NAME=<name> score_rc.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV; S20=wpk-serv-20.mechse.illinois.edu
P=results/cycle2/pipeline
until ssh -o BatchMode=yes $S20 test -f /srv/scratch/bimrose2/cycle2/pipeline/GEN_DONE_$NAME; do sleep 60; done
rsync -a "$S20:/srv/scratch/bimrose2/cycle2/pipeline/real_k16_$NAME.shard*.json.partial.json" $P/
SLURM_JOB_ID=$SLURM_JOB_ID STEM=$P/real_k16_$NAME bash results/cycle2/pipeline/pg_score_rc_c2.sh
