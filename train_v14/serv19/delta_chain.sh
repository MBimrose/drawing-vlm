#!/usr/bin/env bash
# Delta fine-tune chain on serv-20 GPUs 4-7 (after H6): for d0/d1/d2, train 300 steps from e55, then K=8 (think mode)
# on the permissive real bench and the 50 held-out family parts; score on the cluster; compare with e55.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; SDV=/srv/scratch/bimrose2; S20=wpk-serv-20.mechse.illinois.edu
O=$DV/results/delta; B=$DV/train_v14/mech/benchmarks/data; LOG=$DV/logs/real/delta_chain.log; mkdir -p $O
say() { echo "$(date '+%m-%d %H:%M') $*" | tee -a $LOG; }
on() { timeout ${T:-180} ssh -o BatchMode=yes $S20 "$@"; }
until grep -q "H6 DONE" $DV/logs/real/h6_chain.log 2>/dev/null; do sleep 120; done
say "H6 done; shipping delta inputs"
rsync -a --exclude 'mech/benchmarks/data' --exclude __pycache__ $DV/train_v14/ $S20:$SDV/train_v14/
bash $DV/train_v14/serv19/cpu_run.sh -c 2 -t 02:00:00 -m 4G -- "rsync -a rft_real_corpus4/shards rft_real_corpus4/stats.json $S20:$SDV/rft_real_corpus4/ && rsync -a rft_rel_corpus4/shards $S20:$SDV/rft_rel_corpus4/ && rsync -a rft_mix_d0 rft_mix_d1 rft_mix_d2 $S20:$SDV/ && echo shipped" | tee -a $LOG
serve() { on "pkill -u bimrose2 -f 'vllm serv[e]'"; sleep 20
  on "cd $SDV; CUDA_VISIBLE_DEVICES=4,5,6,7 DP=4 SEQS=96 MODEL=$1 NAME=$2 setsid nohup bash train_v14/serv19/run_vllm_e55_serv20.sh > logs/vllm-delta.log 2>&1 < /dev/null & sleep 1; echo ok"
  for i in $(seq 1 240); do on "curl -s -m 5 http://127.0.0.1:8100/health >/dev/null" && return 0; sleep 15; done; say "vLLM never ready $2"; return 1; }
gen() { T=14400 on "cd $SDV; for i in 0 1 2 3; do .venv/bin/python train_v14/geom/gen_openai_bo.py --bench $2 --base-url http://127.0.0.1:8100/v1 --model $1 --k 8 --temperature 0.7 --nshards 4 --shard \$i --workers 16 --out results/split/$3 > logs/gen_$3.\$i.log 2>&1 & done; wait; grep -h DONE logs/gen_$3.*.log | wc -l"; }
score() {  # stem gtdir extra
  rsync -a "$S20:$SDV/results/split/$1.shard*.json.partial.json" $O/ || { say "no partials $1"; return; }
  sbatch --parsable --job-name=score-$1 --time=08:00:00 --export=ALL,PARTIALS="$O/$1.shard*.json.partial.json",GT=$2,OUT=$O/$1.json,WORKERS=40$3 $DV/train_v14/sbatch/score_generic.sbatch; }
JOBS=""
# e55 baseline on the family held-out set, think mode (the real-bench baseline already exists)
serve $SDV/runs/e55-rft-real-u5-gt-dw423/final e55 && gen e55 fp/h6/bench_held fam_e55 | tee -a $LOG && JOBS="$JOBS $(score fam_e55 $DV/results/firstprinciples/h6/bench_held/gt_meshes_v15 ,NO_CONS=1)"
on "pkill -u bimrose2 -f 'vllm serv[e]'"
for v in d0 d1 d2; do R=$v-delta-e55
  say "training $R"
  on "cd $SDV && MODEL_ID=$SDV/runs/e55-rft-real-u5-gt-dw423/final bash train_v14/serv19/launch_train_serv20.sh $R rft_mix_$v" | tee -a $LOG
  until on "grep -q 'TRAIN EXIT' $SDV/logs/${R}_serv20.log"; do sleep 120; done
  say "$R: $(on "grep 'TRAIN EXIT' $SDV/logs/${R}_serv20.log | tail -1")"
  on "[ -d $SDV/runs/$R/final ]" || { say "no final for $R"; continue; }
  serve $SDV/runs/$R/final $R || continue
  gen $R mech_benchmarks/ext_bench_dw423_perm real_$R | tee -a $LOG; gen $R fp/h6/bench_held fam_$R | tee -a $LOG
  on "pkill -u bimrose2 -f 'vllm serv[e]'"
  JOBS="$JOBS $(score real_$R $B/ext_bench_dw423_perm/gt_meshes_v15 '') $(score fam_$R $DV/results/firstprinciples/h6/bench_held/gt_meshes_v15 ,NO_CONS=1)"
  say "$R generated; scoring queued"
done
J=$(echo $JOBS | tr ' ' ','); while [ -n "$(squeue -j $J -h 2>/dev/null)" ]; do sleep 120; done
source $DV/.venv/bin/activate
for v in d0 d1 d2; do python $DV/train_v14/geom/variant_compare.py --base $DV/results/ext/bo8_ext_dw423p_e55-rft-real-u5-gt-dw423 --var $O/real_$v-delta-e55 2>&1 | sed 's/  \(mean\|exec\|vote\|oracle\)/\n        \1/g' | tee -a $LOG; done
python3 - $O <<'PY' | tee -a $LOG
import json, os, sys, numpy as np
O = sys.argv[1]
for s in ("fam_e55", "fam_d0-delta-e55", "fam_d1-delta-e55", "fam_d2-delta-e55"):
    f = os.path.join(O, s + ".json")
    if not os.path.exists(f): print(s, "missing"); continue
    d = json.load(open(f))["candidates"]
    fi = [float(p["cands"][0].get("iou") or 0) for p in d]; mn = [np.mean([float(c.get("iou") or 0) for c in p["cands"]]) for p in d]
    bo = [max(float(c.get("iou") or 0) for c in p["cands"]) for p in d]
    print(f"family held-out {s:18s} first {np.mean(fi):.3f} mean {np.mean(mn):.3f} best-of-8 {np.mean(bo):.3f}")
PY
say "DELTA DONE"
