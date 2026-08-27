#!/bin/bash
#SBATCH --job-name=trace-sync
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=03:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.o%j
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/slurm/%x.e%j

# Daily trace sync from wpk-serv-09 (crontab/scrontab are disabled on this
# cluster, so the job re-submits itself for tomorrow). Kill the chain with:
#   scancel -n trace-sync -u $USER
SCRIPT=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/train_v14/sbatch/trace_sync.sbatch

# Resubmit FIRST so a sync failure never breaks the chain; skip if another
# trace-sync is already pending (avoids runaway duplicates).
if ! squeue -u "$USER" -h -n trace-sync -t PD | grep -q .; then
  sbatch --begin=now+24hours "$SCRIPT"
fi

bash /projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/train_v14/geom/self_heal.sh || true
bash /projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/train_v14/sync_traces.sh
