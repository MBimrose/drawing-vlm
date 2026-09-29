#!/usr/bin/env bash
# RP2: rp1's family repair rows + real-part repair rows (corpus 4) -> train on serv-20 GPUs 4-7 -> 1 round K=8 on the
# real bench -> render-compare v3 gate on the cluster CPU node (same protocol as rp1: +0.040).
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; SDV=/srv/scratch/bimrose2; S20=wpk-serv-20.mechse.illinois.edu
O=$DV/results/repair; LOG=$DV/logs/real/rp2_chain.log; RJ=${RENDER_JOB:?}; R=rp2-delta-e55; M=rft_mix_rp2
say() { echo "$(date '+%m-%d %H:%M') $*" | tee -a $LOG; }
on() { timeout ${TMO:-180} ssh -o BatchMode=yes $S20 "$@"; }
cd $DV
while [ -n "$(squeue -j $RJ -h 2>/dev/null)" ]; do sleep 60; done; say "render: $(tail -1 logs/real/render-cmp-$RJ.out)"
bash train_v14/serv19/cpu_run.sh -c 4 -t 01:00:00 -m 48G -- ".venv/bin/python train_v14/geom/pack_repair_shards.py --bo $O/c4_rep_inputs.json --png-dir $O/png_c4_inputs --bench train_v14/mech/benchmarks/data/rft_corpus4 --targets $O/c4_rep_targets.json --out $O/tier_rp_c4" 2>&1 | grep -v srun | tee -a $LOG
BASE=$DV/rft_strict90_all_dw423b/shards; U5=$DV/rft_real_union5_dw423/shards
bash train_v14/geom/build_rft_mix.sh $DV/$M $BASE $U5 5 >/dev/null; i=$(ls $DV/$M | wc -l); nb=$i
for t in $O/tier_rp_fam $O/tier_rp_c4; do ns=$(ls $t/shards/rft-*.tar | wc -l); RR=$(python3 -c "print(max(1, round(($nb/3)/$ns/2)))")
  for r in $(seq 1 $RR); do for f in $t/shards/rft-*.tar; do ln -s "$(readlink -f "$f")" "$DV/$M/rft-$(printf %05d $i).tar"; i=$((i+1)); done; done; done
say "mix $M: $i shards"
until grep -q "RP1 LOOP DONE" logs/real/rp1_chain.log; do sleep 300; done
rsync -a --exclude 'mech/benchmarks/data' --exclude __pycache__ train_v14/ $S20:$SDV/train_v14/
bash train_v14/serv19/cpu_run.sh -c 2 -t 02:00:00 -m 4G -- "ssh -o BatchMode=yes $S20 mkdir -p $SDV/results/repair/tier_rp_c4; rsync -a $O/tier_rp_c4/shards $S20:$SDV/results/repair/tier_rp_c4/ && rsync -a $M $S20:$SDV/ && echo shipped" 2>&1 | grep -v srun | tee -a $LOG
on "pkill -u bimrose2 -f 'vllm serv[e]'"; say "training $R"
on "cd $SDV && MODEL_ID=$SDV/runs/e55-rft-real-u5-gt-dw423/final bash train_v14/serv19/launch_train_serv20.sh $R $M" | tee -a $LOG
until on "grep -q 'TRAIN EXIT' $SDV/logs/${R}_serv20.log"; do sleep 120; done
on "[ -d $SDV/runs/$R/final ]" || { say "no final $R"; exit 1; }
on "cd $SDV; MM_LIMIT=2 CUDA_VISIBLE_DEVICES=4,5,6,7 DP=4 SEQS=96 MODEL=$SDV/runs/$R/final NAME=$R setsid nohup bash train_v14/serv19/run_vllm_e55_serv20.sh > logs/vllm-rp2.log 2>&1 < /dev/null & sleep 1; echo ok"
for i in $(seq 1 240); do on "curl -s -m 5 http://127.0.0.1:8100/health >/dev/null" && break; sleep 15; done
TMO=40000 on "cd $SDV; .venv/bin/python train_v14/geom/vr_serve.py --bench mech_benchmarks/ext_bench_dw423_perm --picks results/visrepair/e55_vote_picks.json --base-url http://127.0.0.1:8100/v1 --model $R --k 8 --rounds 1 --margin 99 --workers 24 --py $SDV/.venv/bin/python --rpy $SDV/dw_venv/bin/python --script-dir $SDV/mech_step_to_drw --out results/repair/vs_$R.jsonl > logs/vs_$R.log 2>&1; tail -1 logs/vs_$R.log"
on "pkill -u bimrose2 -f 'vllm serv[e]'"
rsync -a $S20:$SDV/results/repair/vs_$R.jsonl $O/
python3 train_v14/geom/vs_summary.py $O/vs_$R.jsonl | tee -a $LOG; python3 train_v14/geom/vs_gate_summary.py $O/vs_$R.jsonl | tee -a $LOG
say "RP2 DONE"
