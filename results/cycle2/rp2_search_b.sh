#!/bin/bash
# Cycle 2: second realpool2 rp3 search instance on serv-20 GPU 4 for the 0.3-0.5 start band (instance 1, rp2_search.sh, is
# stopped when it reaches that band). Out cycle2/search/gts_rp2b.jsonl.
cd /srv/scratch/bimrose2
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
PORT=8623
.venv/bin/python -c "
import json
d=json.load(open('cycle2/search/starts_rp2.json'))['candidates']
b=sorted((p for p in d if 0.3<=float(p['cands'][0]['iou'])<0.5), key=lambda p:-float(p['cands'][0]['iou']))
open('cycle2/search/keys_rp2b.txt','w').write('\n'.join(p['key'] for p in b)+'\n'); print('rp2 band 0.3-0.5:', len(b))"
CUDA_VISIBLE_DEVICES=4 DP=1 SEQS=256 GMU=0.85 PORT=$PORT MODEL=/srv/scratch/bimrose2/runs/rp3-delta-e55/final NAME=rp3 MM_LIMIT=2 \
  setsid bash train_v14/serv19/run_vllm_e55_serv20.sh > cycle2/logs/vllm-rp3-s20b.log 2>&1 < /dev/null &
VPID=$!; echo $VPID > cycle2/logs/vllm-rp3-s20b.pgid
ok=0; for i in $(seq 1 160); do curl -s -m 5 http://127.0.0.1:$PORT/health >/dev/null && { ok=1; break; }; sleep 15; done
[ $ok = 1 ] || { echo "rp3 never ready"; kill -- -$VPID; exit 1; }
echo "$(date) rp3 up GPU 4"
nice -n 10 .venv/bin/python cycle2/train_v14/geom/gt_search2.py --bench rp2=mech_benchmarks/rft_realpool_v2 \
  --starts rp2=cycle2/search/starts_rp2.json --keys cycle2/search/keys_rp2b.txt --base-url http://127.0.0.1:$PORT/v1 \
  --model rp3 --k 8 --rounds 4 --workers ${W:-16} --py $PWD/.venv/bin/python --rpy $PWD/dw_venv/bin/python \
  --script-dir $PWD/mech_step_to_drw --out cycle2/search/gts_rp2b.jsonl > cycle2/logs/gts_rp2b.log 2>&1
echo "$(date) RP2B SEARCH DONE"
