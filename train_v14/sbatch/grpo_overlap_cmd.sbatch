#!/bin/bash
#SBATCH --job-name=grpo-ovlcmd
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodelist=ccc0442
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=24:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.out
# Run an arbitrary command inside a running grpo-fast job's node (overlapping step), e.g. bulk generation through
# one of its vLLM servers (2026-10-07).  sbatch --export=ALL,HOSTJOB=<jobid>,CMD_FILE=<script> grpo_overlap_cmd.sbatch
for v in $(env | grep -oE "^SLURM_[A-Z_]+"); do unset $v; done
srun --jobid=$HOSTJOB --overlap -N1 -n1 bash $CMD_FILE
echo "overlap cmd exit $?"
