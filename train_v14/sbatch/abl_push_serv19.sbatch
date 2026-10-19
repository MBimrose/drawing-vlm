#!/bin/bash
#SBATCH --job-name=abl-push
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=12:00:00
#SBATCH --nodelist=ccc0442
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/bo8/%x-%j.out
# Results-table ablations (2026-10-17): copy the cluster-only checkpoints to serv-19 /srv/scratch/bimrose2/abl/
# (e2 / e16 / e22 full-FT finals, e12 LoRA adapter, Qwen3.8-27B base for the e12 merge); touches abl/<name>.PUSHED
# after each one so the serv-19 eval lanes (abl_lane.sh) can start. Serving + K=8 eval run on serv-19.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; H=wpk-serv-19.mechse.illinois.edu; T=/srv/scratch/bimrose2/abl
for spec in base=models/Qwen3.8-27B e12=runs/e12-lora-alldata-aug/final e2=runs/e2-full-alldata-aug/final \
            e16=runs/e16-full-execfilter/final e22=runs/e22-combined/final; do
  n=${spec%%=*}; src=${spec#*=}; dst=$T/ckpt/$n
  ssh -o BatchMode=yes $H "mkdir -p $dst"
  echo "$(date '+%m-%d %H:%M') push $src -> $dst"
  rsync -a -e "ssh -o BatchMode=yes" $DV/$src/ $H:$dst/ || { echo "FAILED $src"; exit 1; }
  ssh -o BatchMode=yes $H "touch $T/$n.PUSHED"
done
echo "$(date '+%m-%d %H:%M') PUSH DONE"
