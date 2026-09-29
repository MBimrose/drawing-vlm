#!/usr/bin/env bash
# RP1: trained visual repair turn (2026-09-29). Zero-shot DeepSeek showed seeing the candidate's own render is worth
# +0.11 over blind repair but untrained repair still net-hurts; e55 zero-shot repair (e59 era) -0.025. Here: supervised
# repair rows on synthesized-family parts (wrong h6b draws, rendered) -> GT program; e55 generates, rp1 repairs.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; SDV=/srv/scratch/bimrose2; S20=wpk-serv-20.mechse.illinois.edu
O=$DV/results/repair; LOG=$DV/logs/real/rp1_chain.log; RJ=${RENDER_JOB:?}
say() { echo "$(date '+%m-%d %H:%M') $*" | tee -a $LOG; }
on() { timeout ${T:-180} ssh -o BatchMode=yes $S20 "$@"; }
cd $DV
while [ -n "$(squeue -j $RJ -h 2>/dev/null)" ]; do sleep 60; done; say "render: $(tail -1 logs/real/render-cmp-$RJ.out)"
bash train_v14/serv19/cpu_run.sh -c 4 -t 01:00:00 -m 32G -- ".venv/bin/python train_v14/geom/pack_repair_shards.py --bo $O/fam_train_wrong.json --png-dir $O/png_fam_train --bench results/h6c/train_bench --out $O/tier_rp_fam" 2>&1 | grep -v srun | tee -a $LOG
BASE=$DV/rft_strict90_all_dw423b/shards; U5=$DV/rft_real_union5_dw423/shards; M=rft_mix_rp1; T=$O/tier_rp_fam
bash train_v14/geom/build_rft_mix.sh $DV/$M $BASE $U5 5 >/dev/null; i=$(ls $DV/$M | wc -l); nb=$i; ns=$(ls $T/shards/rft-*.tar | wc -l); R=$(python3 -c "print(max(1, round(($nb/3)/$ns)))")
for r in $(seq 1 $R); do for f in $T/shards/rft-*.tar; do ln -s "$(readlink -f "$f")" "$DV/$M/rft-$(printf %05d $i).tar"; i=$((i+1)); done; done
say "mix $M: $i shards ($ns tier shards x $R)"
rsync -a --exclude 'mech/benchmarks/data' --exclude __pycache__ train_v14/ $S20:$SDV/train_v14/
bash train_v14/serv19/cpu_run.sh -c 2 -t 02:00:00 -m 4G -- "ssh -o BatchMode=yes $S20 mkdir -p $SDV/results/repair/tier_rp_fam; rsync -a $T/shards $S20:$SDV/results/repair/tier_rp_fam/ && rsync -a $M $S20:$SDV/ && rsync -a $DV/results/visrepair/e55_vote_picks.json $S20:$SDV/results/visrepair/ && echo shipped" 2>&1 | grep -v srun | tee -a $LOG
until grep -q "H6C2 DONE" logs/real/h6c_chain.log; do sleep 300; done
serve() { on "pkill -u bimrose2 -f 'vllm serv[e]'"; sleep 20
  on "cd $SDV; MM_LIMIT=2 CUDA_VISIBLE_DEVICES=4,5,6,7 DP=4 SEQS=96 MODEL=$1 NAME=$2 setsid nohup bash train_v14/serv19/run_vllm_e55_serv20.sh > logs/vllm-rp1.log 2>&1 < /dev/null & sleep 1; echo ok"
  for i in $(seq 1 240); do on "curl -s -m 5 http://127.0.0.1:8100/health >/dev/null" && return 0; sleep 15; done; say "vLLM never ready $2"; return 1; }
vs() { T=36000 on "cd $SDV; .venv/bin/python train_v14/geom/vr_serve.py --bench mech_benchmarks/ext_bench_dw423_perm --picks results/visrepair/e55_vote_picks.json --base-url http://127.0.0.1:8100/v1 --model $1 --k 8 --workers 24 --out results/repair/vs_$1.jsonl --py $SDV/.venv/bin/python --rpy $SDV/dw_venv/bin/python --script-dir $SDV/mech_step_to_drw > logs/vs_$1.log 2>&1; tail -1 logs/vs_$1.log"; }
serve $SDV/runs/e55-rft-real-u5-gt-dw423/final e55 && vs e55 | tee -a $LOG
R=rp1-delta-e55; on "pkill -u bimrose2 -f 'vllm serv[e]'"; say "training $R"
on "cd $SDV && MODEL_ID=$SDV/runs/e55-rft-real-u5-gt-dw423/final bash train_v14/serv19/launch_train_serv20.sh $R $M" | tee -a $LOG
until on "grep -q 'TRAIN EXIT' $SDV/logs/${R}_serv20.log"; do sleep 120; done
on "[ -d $SDV/runs/$R/final ]" && serve $SDV/runs/$R/final $R && vs $R | tee -a $LOG
on "pkill -u bimrose2 -f 'vllm serv[e]'"
rsync -a "$S20:$SDV/results/repair/vs_*.jsonl" $O/
python3 train_v14/geom/vs_summary.py $O/vs_e55.jsonl $O/vs_$R.jsonl | tee -a $LOG
say "RP1 DONE"
