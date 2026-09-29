#!/usr/bin/env bash
# In-house render-guided repair loop: e55 vote pick -> rp1 (K=8 repairs, no-think, 2 images) -> render all -> adopt best v3 if > +0.1; 3 rounds.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; SDV=/srv/scratch/bimrose2; S20=wpk-serv-20.mechse.illinois.edu; LOG=$DV/logs/real/rp1_chain.log
say() { echo "$(date '+%m-%d %H:%M') $*" | tee -a $LOG; }
on() { timeout ${TMO:-180} ssh -o BatchMode=yes $S20 "$@"; }
R=${R:-rp1-delta-e55}
on "pkill -u bimrose2 -f 'vllm serv[e]'"; sleep 20
on "cd $SDV; MM_LIMIT=2 CUDA_VISIBLE_DEVICES=4,5,6,7 DP=4 SEQS=96 MODEL=$SDV/runs/$R/final NAME=$R setsid nohup bash train_v14/serv19/run_vllm_e55_serv20.sh > logs/vllm-rp1loop.log 2>&1 < /dev/null & sleep 1; echo ok"
for i in $(seq 1 240); do on "curl -s -m 5 http://127.0.0.1:8100/health >/dev/null" && break; sleep 15; done
C="--base-url http://127.0.0.1:8100/v1 --model $R --k 8 --rounds 3 --margin 0.1 --workers 24 --py $SDV/.venv/bin/python --rpy $SDV/dw_venv/bin/python --script-dir $SDV/mech_step_to_drw"
TMO=40000 on "cd $SDV; .venv/bin/python train_v14/geom/vr_serve.py --bench mech_benchmarks/ext_bench_dw423_perm --picks results/visrepair/e55_vote_picks.json $C --out results/repair/loop_real_$R.jsonl > logs/loop_real_$R.log 2>&1 &
  .venv/bin/python train_v14/geom/vr_serve.py --bench fp/h6/bench_held2 --picks results/visrepair/fam_e55_firstexec.json $C --out results/repair/loop_fam_$R.jsonl > logs/loop_fam_$R.log 2>&1 & wait"
on "pkill -u bimrose2 -f 'vllm serv[e]'"
rsync -a "$S20:$SDV/results/repair/loop_*_$R.jsonl" $DV/results/repair/
for b in real fam; do echo "$b"; python3 $DV/train_v14/geom/v3adopt_summary.py $DV/results/repair/loop_${b}_$R.jsonl; done 2>/dev/null | tee -a $LOG
say "RP1 LOOP DONE $R"
