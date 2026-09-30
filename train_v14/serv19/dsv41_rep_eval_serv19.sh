#!/usr/bin/env bash
# Evaluate a DeepSeek repair adapter exactly like rp1/rp2: merge on serv-19, serve (2 images, no-think) on GPUs 4-7,
# vr_serve.py one round K=8 from e55's vote picks on the real bench, inline render + v3 -> gate summary.
#   (cluster) bash dsv41_rep_eval_serv19.sh <adapter dir> <name> [K] [rounds]
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; S19=wpk-serv-19.mechse.illinois.edu; AD=$1; NAME=$2; K=${3:-8}; RD=${4:-1}; LOG=$DV/logs/real/dsv41_eval.log
say() { echo "$(date '+%m-%d %H:%M') $*" | tee -a $LOG; }
cd $DV; say "repair eval $NAME K=$K rounds=$RD"
ssh $S19 "test -f /scratch/bimrose2/dsv41_ft/$NAME/model.safetensors.index.json" && say "merged $NAME exists" || bash train_v14/serv19/dsv41_ft_merge_serv19.sh $AD $NAME | tee -a $LOG
ssh $S19 "for p in \$(ps -u bimrose2 -o pid,args | grep -E 'api_server.*--port 8200|dsv41_ft_serve_serv19.sh' | grep -v grep | awk '{print \$1}'); do kill \$p; done; sleep 45
  cd /scratch/bimrose2/dsv41_flash; setsid nohup bash dsv41_ft_serve_serv19.sh /scratch/bimrose2/dsv41_ft/$NAME $NAME 8200 4,5,6,7 > /scratch/bimrose2/dsv41_ft/serve_$NAME.log 2>&1 < /dev/null &"
for i in $(seq 1 180); do ssh $S19 "curl -sf -m 5 localhost:8200/health >/dev/null" && break; sleep 20; done
ssh $S19 "curl -sf -m 5 localhost:8200/health >/dev/null" || { say "serve $NAME never ready"; exit 1; }
O=results/repair/vs_${NAME}_k${K}r${RD}.jsonl; D=/srv/scratch/bimrose2
ssh $S19 "cd $D; export OPENBLAS_NUM_THREADS=1; .venv/bin/python train_v14/geom/vr_serve.py --bench /scratch/bimrose2/mech_benchmarks/ext_bench_dw423_perm --picks results/visrepair/e55_vote_picks.json --base-url http://localhost:8200/v1 --model $NAME --k $K --rounds $RD --margin 0.1 --max-tokens 6000 --workers 24 --py $D/.venv/bin/python --rpy /scratch/bimrose2/dw_venv/bin/python --script-dir $D/mech_step_to_drw --out $O > /tmp/vs_$NAME.log 2>&1; tail -1 /tmp/vs_$NAME.log"
rsync -a $S19:$D/$O results/repair/
python3 train_v14/geom/vs_summary.py $O | tee -a $LOG; python3 train_v14/geom/vs_gate_summary.py $O 0.05 0.1 | tee -a $LOG
say "REPAIR EVAL DONE $NAME"
