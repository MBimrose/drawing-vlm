#!/bin/bash
#SBATCH --job-name=bb-drv
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodelist=ccc0442
#SBATCH --cpus-per-task=2
#SBATCH --mem=24G
#SBATCH --time=30:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/bench_b/pipeline/logs/%x-%j.out
# Bench B full pipeline driver for system 1 (rft2_rl_s60 + rp3), the e2e_driver.sbatch protocol (2026-10-10):
# wait for serv-20 stage 2 (K=16 scored, vote, render-compare v3, v3b-EV verifier) -> pg_make_starts.py (top-3 distinct by
# verifier+v3) -> 3 rp3 chains 16 x 6, margin 0.1 on 4 L40S -> (summary run by hand with chain_compare.py).
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV; S20=wpk-serv-20.mechse.illinois.edu
P=results/bench_b/pipeline; NAME=rl2s60; say() { echo "$(date '+%m-%d %H:%M') $*"; }
until timeout 120 ssh -o BatchMode=yes $S20 "grep -q 'STAGE2 DONE' /srv/scratch/bimrose2/bench_b/pipeline/logs/stage2.log"; do sleep 120; done
rsync -a --exclude '*_rcpng' "$S20:/srv/scratch/bimrose2/bench_b/pipeline/benchb_k16_$NAME*" "$S20:/srv/scratch/bimrose2/bench_b/pipeline/vpreds_k16_$NAME.json" $P/
say "stage 2 pulled: $(ls $P | grep -c k16)"
$DV/.venv/bin/python train_v14/geom/pg_make_starts.py --cands $P/benchb_k16_$NAME.json --cons $P/benchb_k16_${NAME}_consistency.json \
  --vpreds $P/vpreds_k16_$NAME.json --rc $P/benchb_k16_${NAME}_rc_v3.json --out-stem $P/starts_$NAME --k 16 || { say "starts failed"; exit 1; }
CF=$P/chains_$NAME.txt; : > $CF
for c in 1 2 3; do echo "bb_${NAME}_rp3_c$c|$DV/$P/starts_${NAME}_r$c.json|$DV/$P/chain_${NAME}_rp3_c$c.jsonl" >> $CF; done
J=$(sbatch --parsable --gres=gpu:L40S:4 --cpus-per-task=${CPUS:-44} --mem=200G \
  --export=ALL,CHAINS_FILE=$DV/$CF,WORKERS=16,PORT=8670,MODEL=$DV/runs/rp3-delta-e55/final $P/repair_l40s_b.sbatch)
say "chain job $J"
