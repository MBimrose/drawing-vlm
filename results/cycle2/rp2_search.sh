#!/bin/bash
# Cycle 2 (2026-10-09): GT-selected rp3 repair search for the realpool2 subset ON SERV-20 (the cluster rp3 server on 8 L40S
# was GPU-bound with the CADBench parts). rp3 on GPUs $GPUS (DP), gt_search2.py with $W workers (niced, single-thread
# scoring), starts = best K=16 draw (no earlier tier/bank for these parts), priority = IoU band as build_starts.py.
# Also launches the DeepSeek teacher on rp2 parts whose start < 0.3.
cd /srv/scratch/bimrose2
GPUS=${GPUS:-2,5}; NDP=$(echo $GPUS | tr ',' '\n' | wc -l); PORT=8622; W=${W:-20}
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
say() { echo "$(date '+%m-%d %H:%M') $*"; }
until [ -f cycle2/gen/SCORED_B_rp2_c2pol ]; do sleep 60; done
say "B_rp2 scored"
.venv/bin/python - <<'PY'
import json
d = json.load(open("cycle2/gen/B_rp2_c2pol.json"))
def band(i):
    for r, (lo, hi) in enumerate(((0.5, 0.75), (0.3, 0.5), (0.75, 0.9), (0.1, 0.3), (-1, 0.1))):
        if lo <= i < hi: return r
    return 9
best = {}
for p in d["candidates"]:
    c = max((c for c in p["cands"] if c.get("code") and c.get("exec")), key=lambda c: float(c.get("iou") or 0), default=None)
    if c is not None: best[p["key"]] = (float(c["iou"]), c["code"])
json.dump({"candidates": [{"key": k, "cands": [{"draw": 0, "code": v[1], "exec": True, "iou": v[0], "src": "k16"}]} for k, v in sorted(best.items())]},
          open("cycle2/search/starts_rp2.json", "w"))
todo = sorted((k for k in best if best[k][0] < 0.9), key=lambda k: (band(best[k][0]), -best[k][0]))
open("cycle2/search/keys_rp2.txt", "w").write("\n".join(todo) + "\n")
json.dump({k: {"code": best[k][1], "iou": best[k][0]} for k in best if best[k][0] < 0.3}, open("cycle2/teacher/picks_rp2.json", "w"))
print("rp2 parts", len(d["candidates"]), "with start", len(best), "to search", len(todo), "teacher picks", sum(best[k][0] < 0.3 for k in best))
PY
CORPORA=rp2 setsid nohup bash cycle2/ds_teacher.sh > cycle2/logs/ds_teacher_rp2_driver.log 2>&1 < /dev/null &
CUDA_VISIBLE_DEVICES=$GPUS DP=$NDP SEQS=256 GMU=0.85 PORT=$PORT MODEL=/srv/scratch/bimrose2/runs/rp3-delta-e55/final NAME=rp3 MM_LIMIT=2 \
  setsid bash train_v14/serv19/run_vllm_e55_serv20.sh > cycle2/logs/vllm-rp3-s20.log 2>&1 < /dev/null &
VPID=$!; echo $VPID > cycle2/logs/vllm-rp3-s20.pgid
ok=0; for i in $(seq 1 160); do curl -s -m 5 http://127.0.0.1:$PORT/health >/dev/null && { ok=1; break; }; sleep 15; done
[ $ok = 1 ] || { say "rp3 never ready"; tail -30 cycle2/logs/vllm-rp3-s20.log; kill -- -$VPID; exit 1; }
say "rp3 up on GPUs $GPUS :$PORT"
touch cycle2/search/RP2_UNTIL
nice -n 10 .venv/bin/python cycle2/train_v14/geom/gt_search2.py --bench rp2=mech_benchmarks/rft_realpool_v2 \
  --starts rp2=cycle2/search/starts_rp2.json --keys cycle2/search/keys_rp2.txt --base-url http://127.0.0.1:$PORT/v1 \
  --model rp3 --k 8 --rounds 4 --workers $W --py $PWD/.venv/bin/python --rpy $PWD/dw_venv/bin/python \
  --script-dir $PWD/mech_step_to_drw --out cycle2/search/gts_rp2.jsonl > cycle2/logs/gts_rp2.log 2>&1
say "RP2 SEARCH DONE"
