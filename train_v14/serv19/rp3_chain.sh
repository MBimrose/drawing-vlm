#!/usr/bin/env bash
# RP3: add real-part repair rows from the DeepSeek search on corpora 1+2 to rp2's tiers; train on serv-20; 3-round loop.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; SDV=/srv/scratch/bimrose2; S20=wpk-serv-20.mechse.illinois.edu
O=$DV/results/repair; V=$DV/results/visrepair; LOG=$DV/logs/real/rp3_chain.log; R=rp3-delta-e55; M=rft_mix_rp3
say() { echo "$(date '+%m-%d %H:%M') $*" | tee -a $LOG; }
on() { timeout ${TMO:-180} ssh -o BatchMode=yes $S20 "$@"; }
cd $DV
until on "grep -q 'VR DONE' $SDV/results/visrepair/rft_corpus_dw423_m10.log && grep -q 'VR DONE' $SDV/results/visrepair/rft_corpus2_dw423_m10.log"; do sleep 300; done
JOBS=""
for c in rft_corpus_dw423 rft_corpus2_dw423; do
  rsync -a $S20:$SDV/results/visrepair/${c}_m10.jsonl $V/
  python3 train_v14/geom/v3adopt_summary.py $V/${c}_m10.jsonl 2>/dev/null | head -1 | sed "s/^/$c /" | tee -a $LOG
  python3 train_v14/geom/build_c4_repair.py --log $V/${c}_m10.jsonl --out-bo $O/${c}_rep_inputs.json --out-targets $O/${c}_rep_targets.json | tee -a $LOG
  JOBS="$JOBS:$(sbatch --parsable --export=ALL,BO=$O/${c}_rep_inputs.json,BENCH=$DV/train_v14/mech/benchmarks/data/$c,OUT=$O/rc_${c}_inputs.json,PNGDIR=$O/png_${c}_inputs,WORKERS=90 train_v14/sbatch/render_compare.sbatch)"
done
J=$(echo $JOBS | sed 's/^://' | tr ':' ','); while [ -n "$(squeue -j $J -h 2>/dev/null)" ]; do sleep 60; done
for c in rft_corpus_dw423 rft_corpus2_dw423; do
  bash train_v14/serv19/cpu_run.sh -c 4 -t 01:00:00 -m 48G -- ".venv/bin/python train_v14/geom/pack_repair_shards.py --bo $O/${c}_rep_inputs.json --png-dir $O/png_${c}_inputs --bench train_v14/mech/benchmarks/data/$c --targets $O/${c}_rep_targets.json --out $O/tier_rp_$c" 2>&1 | grep -v srun | tee -a $LOG
done
BASE=$DV/rft_strict90_all_dw423b/shards; U5=$DV/rft_real_union5_dw423/shards
bash train_v14/geom/build_rft_mix.sh $DV/$M $BASE $U5 5 >/dev/null; i=$(ls $DV/$M | wc -l); nb=$i
# repair share ~1/3 of draws: family 1/4 of it, real (c4 + c1 + c2) 3/4
for spec in "$O/tier_rp_fam:0.25" "$O/tier_rp_c4:0.25" "$O/tier_rp_rft_corpus_dw423:0.25" "$O/tier_rp_rft_corpus2_dw423:0.25"; do t=${spec%%:*}; w=${spec#*:}
  ns=$(ls $t/shards/rft-*.tar | wc -l); RR=$(python3 -c "print(max(1, round(($nb/2)*$w/$ns)))")
  for r in $(seq 1 $RR); do for f in $t/shards/rft-*.tar; do ln -s "$(readlink -f "$f")" "$DV/$M/rft-$(printf %05d $i).tar"; i=$((i+1)); done; done; done
say "mix $M: $i shards"
rsync -a --exclude 'mech/benchmarks/data' --exclude __pycache__ train_v14/ $S20:$SDV/train_v14/
bash train_v14/serv19/cpu_run.sh -c 2 -t 02:00:00 -m 4G -- "for c in rft_corpus_dw423 rft_corpus2_dw423; do ssh -o BatchMode=yes $S20 mkdir -p $SDV/results/repair/tier_rp_\$c; rsync -a $O/tier_rp_\$c/shards $S20:$SDV/results/repair/tier_rp_\$c/; done && rsync -a $M $S20:$SDV/ && echo shipped" 2>&1 | grep -v srun | tee -a $LOG
on "pkill -u bimrose2 -f 'vllm serv[e]'"; say "training $R"
on "cd $SDV && MODEL_ID=$SDV/runs/e55-rft-real-u5-gt-dw423/final bash train_v14/serv19/launch_train_serv20.sh $R $M" | tee -a $LOG
until on "grep -q 'TRAIN EXIT' $SDV/logs/${R}_serv20.log"; do sleep 120; done
on "[ -d $SDV/runs/$R/final ]" || { say "no final $R"; exit 1; }
R=$R bash train_v14/serv19/rp1_loop.sh
say "RP3 DONE"
