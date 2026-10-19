#!/bin/bash
#SBATCH --job-name=fn-stage
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=6:00:00
#SBATCH --nodelist=ccc0442
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/bo8/%x-%j.out
# Flash-Next full pipeline (2026-10-19): copy the 27B GRPO / EI inputs off serv-20 (our data; no compute there) to serv-19
# via a /scratch staging dir: GRPO pools (rft_corpus4, rft_corpus2_dw423, train_bench, rft_realpool_v2), hard-key lists, cycle2/.
set -uo pipefail
S=wpk-serv-20.mechse.illinois.edu; T=wpk-serv-19.mechse.illinois.edu; R=/srv/scratch/bimrose2; ST=/scratch/bimrose2/fn_stage
mkdir -p $ST
for p in fp/h6/rft_corpus4 mech_benchmarks/rft_corpus2_dw423 fp/h6/train_bench mech_benchmarks/rft_realpool_v2 cycle2 \
         fp/h6/real4_hard_keys.txt fp/h6/c2_hard_keys.txt fp/h6/fam_hard_keys.txt fp/h6/realpool2_hard_4500.txt; do
  d=$(dirname $p); mkdir -p $ST/$d
  echo "$(date '+%m-%d %H:%M') pull $p"
  rsync -a -e "ssh -o BatchMode=yes" $S:$R/$p $ST/$d/ || { echo "FAILED pull $p"; exit 1; }
  ssh -o BatchMode=yes $T "mkdir -p $R/$d"
  rsync -a -e "ssh -o BatchMode=yes" $ST/$p $T:$R/$d/ || { echo "FAILED push $p"; exit 1; }
done
ssh -o BatchMode=yes $T "touch $R/fn55/GRPO_DATA.STAGED"
echo "$(date '+%m-%d %H:%M') STAGE DONE"
