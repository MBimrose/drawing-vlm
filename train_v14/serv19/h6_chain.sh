#!/usr/bin/env bash
# H6 overfit test chain (serv-20 GPUs 4-7): train h6-overfit-family from e55, then K=8 no-think generation with the
# trained model and with e55 (baseline) on the 50 trained and 50 held-out family parts; score on the cluster.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; SDV=/srv/scratch/bimrose2; S20=wpk-serv-20.mechse.illinois.edu
H=$DV/results/firstprinciples/h6; LOG=$DV/logs/real/h6_chain.log; RUN=h6-overfit-family
say() { echo "$(date '+%m-%d %H:%M') $*" | tee -a $LOG; }
on() { timeout ${T:-180} ssh -o BatchMode=yes $S20 "$@"; }
rsync -a --exclude 'mech/benchmarks/data' --exclude __pycache__ $DV/train_v14/ $S20:$SDV/train_v14/
on "mkdir -p $SDV/fp/h6"; rsync -a $H/train_tier/shards $H/bench_train $H/bench_held $S20:$SDV/fp/h6/
on "cd $SDV && MODEL_ID=$SDV/runs/e55-rft-real-u5-gt-dw423/final bash train_v14/serv19/launch_train_serv20.sh h6-overfit-family fp/h6/shards" | tee -a $LOG
until on "grep -q 'TRAIN EXIT' $SDV/logs/${RUN}_serv20.log"; do sleep 120; done
say "training ended: $(on "grep 'TRAIN EXIT' $SDV/logs/${RUN}_serv20.log | tail -1"); loss: $(on "tr '\r' '\n' < $SDV/logs/${RUN}_serv20.log | grep \"'loss'\" | sed -n '1p;\$p' | cut -c1-60 | tr '\n' ' '")"
on "[ -d $SDV/runs/$RUN/final ]" || { say "no final"; exit 2; }
serve() {  # $1 model dir, $2 served name
  on "pkill -u bimrose2 -f 'vllm serv[e]'"; sleep 20
  on "cd $SDV; CUDA_VISIBLE_DEVICES=4,5,6,7 DP=4 SEQS=96 MODEL=$1 NAME=$2 setsid nohup bash train_v14/serv19/run_vllm_e55_serv20.sh > logs/vllm-h6.log 2>&1 < /dev/null & sleep 1; echo ok"
  for i in $(seq 1 240); do on "curl -s -m 5 http://127.0.0.1:8100/health >/dev/null" && return 0; sleep 15; done
  say "vLLM never ready for $2"; exit 2
}
gen() {  # $1 served name, $2 bench name
  T=14400 on "cd $SDV; for i in 0 1 2 3; do .venv/bin/python train_v14/geom/gen_openai_bo.py --bench fp/h6/$2 --base-url http://127.0.0.1:8100/v1 --model $1 --k 8 --temperature 0.7 --no-think --nshards 4 --shard \$i --workers 16 --out results/split/h6_${1}_$2 > logs/gen_h6_${1}_$2.\$i.log 2>&1 & done; wait; grep -h DONE logs/gen_h6_${1}_$2.*.log | wc -l"
}
serve $SDV/runs/$RUN/final h6; say "h6 served"; gen h6 bench_train; gen h6 bench_held
serve $SDV/runs/e55-rft-real-u5-gt-dw423/final e55; say "e55 served"; gen e55 bench_train; gen e55 bench_held
on "pkill -u bimrose2 -f 'vllm serv[e]'"; say "generation done"
JOBS=""
for m in h6 e55; do for b in bench_train bench_held; do s=h6_${m}_$b
  rsync -a "$S20:$SDV/results/split/$s.shard*.json.partial.json" $H/ || { say "no partials $s"; continue; }
  J=$(sbatch --parsable --job-name=score-$s --time=06:00:00 --export=ALL,PARTIALS="$H/$s.shard*.json.partial.json",GT=$H/$b/gt_meshes_v15,OUT=$H/$s.json,WORKERS=40,NO_CONS=1 $DV/train_v14/sbatch/score_generic.sbatch)
  JOBS="$JOBS $J"; done; done
J=$(echo $JOBS | tr ' ' ','); while [ -n "$(squeue -j $J -h 2>/dev/null)" ]; do sleep 60; done
python3 - $H <<'PY' | tee -a $LOG
import json, sys, os, numpy as np
H = sys.argv[1]
for b in ("bench_train", "bench_held"):
    for m in ("e55", "h6"):
        f = os.path.join(H, f"h6_{m}_{b}.json")
        if not os.path.exists(f): print(b, m, "missing"); continue
        d = json.load(open(f))["candidates"]
        fi = [float(p["cands"][0].get("iou") or 0) for p in d]; mn = [np.mean([float(c.get("iou") or 0) for c in p["cands"]]) for p in d]
        bo = [max(float(c.get("iou") or 0) for c in p["cands"]) for p in d]; ex = np.mean([bool(c.get("exec")) for p in d for c in p["cands"]])
        print(f"{b:12s} {m:4s} n={len(d)} first {np.mean(fi):.3f} mean {np.mean(mn):.3f} best-of-8 {np.mean(bo):.3f} >=0.8 {np.mean(np.array(bo)>=0.8):.0%} exec {ex:.0%}")
PY
say "H6 DONE"
