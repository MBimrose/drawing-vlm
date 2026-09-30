#!/usr/bin/env bash
# RP4: rp3 mix + self-distilled repair tier (rp2's own IoU-verified repairs on corpus 4) -> train serv-20 -> K=8 x 3 loop.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; SDV=/srv/scratch/bimrose2; S20=wpk-serv-20.mechse.illinois.edu
O=$DV/results/repair; LOG=$DV/logs/real/rp4_chain.log; R=rp4-delta-e55; M=rft_mix_rp4
say() { echo "$(date '+%m-%d %H:%M') $*" | tee -a $LOG; }
on() { timeout ${TMO:-180} ssh -o BatchMode=yes $S20 "$@"; }
cd $DV
J=$(sbatch --parsable --export=ALL,BO=$O/self_c4_inputs.json,BENCH=$DV/train_v14/mech/benchmarks/data/rft_corpus4,OUT=$O/rc_self_c4_inputs.json,PNGDIR=$O/png_self_c4_inputs,WORKERS=90 train_v14/sbatch/render_compare.sbatch)
while [ -n "$(squeue -j $J -h 2>/dev/null)" ]; do sleep 60; done
bash train_v14/serv19/cpu_run.sh -c 4 -t 01:00:00 -m 48G -- ".venv/bin/python train_v14/geom/pack_repair_shards.py --bo $O/self_c4_inputs.json --png-dir $O/png_self_c4_inputs --bench train_v14/mech/benchmarks/data/rft_corpus4 --targets $O/self_c4_targets.json --out $O/tier_rp_self" 2>&1 | grep -v srun | tee -a $LOG
rm -rf $DV/$M; mkdir -p $DV/$M; i=0
for f in $DV/rft_mix_rp3/rft-*.tar; do ln -s "$(readlink -f "$f")" "$DV/$M/rft-$(printf %05d $i).tar"; i=$((i+1)); done
nb=$i; ns=$(ls $O/tier_rp_self/shards/rft-*.tar | wc -l); RR=$(python3 -c "print(max(1, round($nb*0.1/$ns)))")
for r in $(seq 1 $RR); do for f in $O/tier_rp_self/shards/rft-*.tar; do ln -s "$(readlink -f "$f")" "$DV/$M/rft-$(printf %05d $i).tar"; i=$((i+1)); done; done
say "mix $M: $i shards (rp3 mix + self tier x $RR)"
rsync -a --exclude 'mech/benchmarks/data' --exclude __pycache__ train_v14/ $S20:$SDV/train_v14/
bash train_v14/serv19/cpu_run.sh -c 2 -t 02:00:00 -m 4G -- "ssh -o BatchMode=yes $S20 mkdir -p $SDV/results/repair/tier_rp_self; rsync -a $O/tier_rp_self/shards $S20:$SDV/results/repair/tier_rp_self/ && rsync -a $M $S20:$SDV/ && echo shipped" 2>&1 | grep -v srun | tee -a $LOG
on "pkill -u bimrose2 -f 'vllm serv[e]'"; say "training $R"
on "cd $SDV && MODEL_ID=$SDV/runs/e55-rft-real-u5-gt-dw423/final bash train_v14/serv19/launch_train_serv20.sh $R $M" | tee -a $LOG
until on "grep -q 'TRAIN EXIT' $SDV/logs/${R}_serv20.log"; do sleep 120; done
on "[ -d $SDV/runs/$R/final ]" || { say "no final $R"; exit 1; }
R=$R bash train_v14/serv19/rp1_loop.sh
say "RP4 DONE"
