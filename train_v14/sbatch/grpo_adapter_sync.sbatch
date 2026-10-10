#!/bin/bash
#SBATCH --job-name=grpo-sync
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodelist=ccc0442
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=48:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.out
# Mirror cluster fast-arm GRPO adapters to serv-20 every 15 min so serv19/grpo_autoeval.sh evaluates them
# (2026-10-06; the login node kills long-lived loops).  sbatch --export=ALL,ARMS="a b c" grpo_adapter_sync.sbatch
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; S20=wpk-serv-20.mechse.illinois.edu
while true; do
  for a in $ARMS; do
    ls -d $DV/runs/grpo_v_$a/adapter_step* >/dev/null 2>&1 || continue
    ssh -o BatchMode=yes $S20 "mkdir -p /srv/scratch/bimrose2/runs/grpo_v_$a"
    rsync -a $DV/runs/grpo_v_$a/adapter_step* $S20:/srv/scratch/bimrose2/runs/grpo_v_$a/
  done
  sleep 900
done
