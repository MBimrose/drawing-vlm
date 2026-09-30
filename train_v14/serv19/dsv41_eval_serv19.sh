#!/usr/bin/env bash
# Evaluate a DeepSeek-V4.1-Flash LoRA adapter the reliable way (the in-job HF eval under-reports): FP8-merge on serv-19,
# serve with vLLM on GPUs 4-7 (port 8200, replacing whatever runs there), one greedy draw per part on a bench.
#   (cluster) bash dsv41_eval_serv19.sh <adapter dir> <name> <think|nothink> [bench dir on serv-19] [n]
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; S19=wpk-serv-19.mechse.illinois.edu; AD=$1; NAME=$2; MODE=$3
B=${4:-/scratch/bimrose2/mech_benchmarks/ext_bench_dw423_perm}; N=${5:-0}; LOG=$DV/logs/real/dsv41_eval.log
say() { echo "$(date '+%m-%d %H:%M') $*" | tee -a $LOG; }
cd $DV; say "eval $NAME ($MODE) adapter $AD"
bash train_v14/serv19/dsv41_ft_merge_serv19.sh $AD $NAME | tee -a $LOG
rsync -a train_v14/geom/probe_openai_vlm.py $S19:/srv/scratch/bimrose2/train_v14/geom/; rsync -a train_v14/serv19/dsv41_ft_serve_serv19.sh $S19:/scratch/bimrose2/dsv41_flash/
ssh $S19 "for p in \$(ps -u bimrose2 -o pid,args | grep -E 'api_server.*--port 8200|dsv41_ft_serve_serv19.sh' | grep -v grep | awk '{print \$1}'); do kill \$p; done; sleep 45
  cd /scratch/bimrose2/dsv41_flash; setsid nohup bash dsv41_ft_serve_serv19.sh /scratch/bimrose2/dsv41_ft/$NAME $NAME 8200 4,5,6,7 > /scratch/bimrose2/dsv41_ft/serve_$NAME.log 2>&1 < /dev/null &"
for i in $(seq 1 180); do ssh $S19 "curl -sf -m 5 localhost:8200/health >/dev/null" && break; sleep 20; done
ssh $S19 "curl -sf -m 5 localhost:8200/health >/dev/null" || { say "serve $NAME never ready"; ssh $S19 "grep ERROR /scratch/bimrose2/dsv41_ft/serve_$NAME.log | head -5"; exit 1; }
F=$([ $MODE = nothink ] && echo --no-think || echo ""); T=probe_${NAME}_${MODE}_$(basename $B)
ssh $S19 "cd /srv/scratch/bimrose2; mkdir -p results/ext; source train_v14/env.sh 2>/dev/null; export OPENBLAS_NUM_THREADS=1; .venv/bin/python train_v14/geom/probe_openai_vlm.py --bench $B --base-url http://localhost:8200/v1 --model $NAME --out results/ext/$T.json --n $N --k 1 --temperature 0 --workers 16 --max-tokens 5000 --timeout 1800 $F > /tmp/$T.log 2>&1"
rsync -a $S19:/srv/scratch/bimrose2/results/ext/$T.json results/ext/
python3 -c "
import json,numpy as np; d=json.load(open('results/ext/$T.json'))['records']; v=np.array([float(r.get('iou') or 0) for r in d]); F=np.array([r['key'][0] for r in d])
print('$T n=%d mean %.3f A %.3f F %.3f exec %d >=0.8 %d'%(len(v),v.mean(),v[F=='A'].mean() if (F=='A').any() else -1,v[F=='F'].mean() if (F=='F').any() else -1,sum(bool(r.get('exec')) for r in d),(v>=0.8).sum()))" | tee -a $LOG
say "EVAL DONE $NAME"
