#!/usr/bin/env bash
# H6c step 1 (serv-20 GPUs 4-7): think-mode generation by h6b-n1655 on its own 1,655 family training parts (self-distilled
# think traces for the GT programs it learned in no-think mode), plus think-mode family held-out evals for h6b-n1655 and e55.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; SDV=/srv/scratch/bimrose2; S20=wpk-serv-20.mechse.illinois.edu
O=$DV/results/h6c; LOG=$DV/logs/real/h6c_chain.log; mkdir -p $O
say() { echo "$(date '+%m-%d %H:%M') $*" | tee -a $LOG; }
on() { timeout ${T:-180} ssh -o BatchMode=yes $S20 "$@"; }
cd $DV
rsync -a --exclude __pycache__ train_v14/geom train_v14/serv19 $S20:$SDV/train_v14/
on "mkdir -p $SDV/fp/h6c"; rsync -a $O/train_bench $S20:$SDV/fp/h6c/ && say "shipped train_bench"
serve() { on "pkill -u bimrose2 -f 'vllm serv[e]'"; sleep 20
  on "cd $SDV; CUDA_VISIBLE_DEVICES=4,5,6,7 DP=4 SEQS=96 MODEL=$1 NAME=$2 setsid nohup bash train_v14/serv19/run_vllm_e55_serv20.sh > logs/vllm-h6c.log 2>&1 < /dev/null & sleep 1; echo ok"
  for i in $(seq 1 240); do on "curl -s -m 5 http://127.0.0.1:8100/health >/dev/null" && return 0; sleep 15; done; say "vLLM never ready $2"; return 1; }
gen() { T=36000 on "cd $SDV; for i in 0 1 2 3; do .venv/bin/python train_v14/geom/gen_openai_bo.py --bench $2 --base-url http://127.0.0.1:8100/v1 --model $1 --k 8 --temperature 0.7 --nshards 4 --shard \$i --workers 24 --out results/split/$3 $4 > logs/gen_$3.\$i.log 2>&1 & done; wait; grep -h DONE logs/gen_$3.*.log | wc -l"; }
JOBS=""
score() { rsync -a "$S20:$SDV/results/split/$1.shard*.json.partial.json" $O/ || { say "no partials $1"; return; }
  JOBS="$JOBS $(sbatch --parsable --job-name=score-$1 --time=12:00:00 --export=ALL,PARTIALS="$O/$1.shard*.json.partial.json",GT=$2,OUT=$O/$1.json,WORKERS=40,NO_CONS=1 $DV/train_v14/sbatch/score_generic.sbatch)"; }
R=h6b-n1655-delta-e55
serve $SDV/runs/$R/final $R && { gen $R fp/h6/bench_held2 famT_$R "" | tee -a $LOG; score famT_$R $DV/results/h6b/bench_held2/gt_meshes_v15
  gen $R fp/h6c/train_bench trainT_$R "" | tee -a $LOG; score trainT_$R $O/train_bench/gt_meshes_v15; }
serve $SDV/runs/e55-rft-real-u5-gt-dw423/final e55 && { gen e55 fp/h6/bench_held2 famT_e55 "" | tee -a $LOG; score famT_e55 $DV/results/h6b/bench_held2/gt_meshes_v15; }
on "pkill -u bimrose2 -f 'vllm serv[e]'"
say "H6C GEN DONE jobs $JOBS"
