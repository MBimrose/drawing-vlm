#!/usr/bin/env bash
# Usage: ship_finals.sh <run> [<run> ...]
# For each run in order: wait until its SLURM job is gone and runs/<run>/final is
# complete, copy final/ to serv-19, launch the full-pool best-of-8 there (waits for
# any running workers first), and submit the external real-part eval on the cluster.
# Launch detached:  setsid nohup train_v14/serv19/ship_finals.sh e46-rft-real > logs/ship_finals.log 2>&1 < /dev/null &
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
cd $DV
for R in "$@"; do
  until ! squeue -h -n $R -o %T | grep -q . && [ -f runs/$R/final/model.safetensors.index.json ] && [ "$(ls runs/$R/final | wc -l)" -ge 10 ]; do sleep 120; done
  sleep 60
  J=$(sbatch --parsable --export=ALL,RUN=$R --job-name=bo8-ext-$R train_v14/sbatch/bo8_ext_cluster.sbatch)
  echo "$(date) submitted external eval for $R: job $J"
  ssh -o BatchMode=yes wpk-serv-19.mechse.illinois.edu "mkdir -p /srv/scratch/bimrose2/runs/$R/final"
  rsync -a runs/$R/final/ wpk-serv-19.mechse.illinois.edu:/srv/scratch/bimrose2/runs/$R/final/
  until ! ssh -o BatchMode=yes wpk-serv-19.mechse.illinois.edu 'pgrep -u bimrose2 -f "[b]estofn_verifier_eval" >/dev/null'; do sleep 300; done
  ssh -o BatchMode=yes wpk-serv-19.mechse.illinois.edu "cd /srv/scratch/bimrose2; nohup ./run_bo8_full_generic.sh $R > logs/bo8_full_${R}_chain.log 2>&1 &"
  echo "$(date) launched serv-19 full-pool for $R"
done
