#!/bin/bash
#SBATCH --job-name=grpo-migr
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodelist=ccc0442
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=02:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x-%j.out
# Hand H200 nodes back (2026-10-08): optionally cancel the host jobs, push the arms' final adapters to serv-20, cancel their
# sync jobs, then resume each arm on serv-20 via grpo_migrate.sh. MIGR_FILE lines: name|stop_arm|gpu|port|serv-20 args
#   sbatch [--begin=...|--dependency=afterany:<host>] --export=ALL,CANCEL="<jobids>",SYNCJOBS="<jobids>",MIGR_FILE=<f> grpo_migrate.sbatch
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; S20=wpk-serv-20.mechse.illinois.edu
for j in ${CANCEL:-}; do scancel $j; done
[ -n "${CANCEL:-}" ] && sleep 120   # let the jobs' steps die before the final sync
while IFS='|' read -r name stop gpu port args; do
  [ -n "$name" ] || continue
  ssh -o BatchMode=yes $S20 mkdir -p /srv/scratch/bimrose2/runs/grpo_v_$name
  rsync -a $DV/runs/grpo_v_$name/adapter_step* $S20:/srv/scratch/bimrose2/runs/grpo_v_$name/
done < $MIGR_FILE
for j in ${SYNCJOBS:-}; do scancel $j; done
while IFS='|' read -r name stop gpu port args; do
  [ -n "$name" ] || continue
  ssh -o BatchMode=yes $S20 "setsid nohup bash /srv/scratch/bimrose2/train_v14/serv19/grpo_migrate.sh $name $stop $gpu $port $args > /dev/null 2>&1 < /dev/null &"
  echo "$(date) migrated $name -> serv-20 GPU $gpu (stopped $stop)"
done < $MIGR_FILE
