#!/usr/bin/env bash
# H6b family-GT learning curve (serv-20 GPUs 4-7; hub/CPU steps first). See RECIPE 2026-09-24.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; SDV=/srv/scratch/bimrose2; S20=wpk-serv-20.mechse.illinois.edu
O=$DV/results/h6b; B=$DV/train_v14/mech/benchmarks/data; LOG=$DV/logs/real/h6b_chain.log; mkdir -p $O
say() { echo "$(date '+%m-%d %H:%M') $*" | tee -a $LOG; }
on() { timeout ${T:-180} ssh -o BatchMode=yes $S20 "$@"; }
cd $DV
until on 'grep -qE "SCALE1 DONE|SCALE1 FAILED" /srv/scratch/bimrose2/familysynth/scale1/run.log'; do sleep 300; done
say "scale-up: $(on 'tail -2 /srv/scratch/bimrose2/familysynth/scale1/run.log' | tr '\n' ' ')"
J=$(bash train_v14/mech/familysynth/pack_family_corpus.sh scale1 family_scale1 | tee -a $LOG | awk '/render job/{print $3}')
while [ -n "$(squeue -j $J -h 2>/dev/null)" ]; do sleep 60; done; tail -2 $B/family_scale1/logs/stage.log | tee -a $LOG
bash train_v14/serv19/cpu_run.sh -c 4 -t 01:00:00 -m 32G -- ".venv/bin/python train_v14/mech/familysynth/build_h6b.py --corpora $B/family_pilot $B/family_scale1 --pilot-held results/firstprinciples/h6/bench_held --out $O --ns 500 0 && for t in $O/tier_n*; do .venv/bin/python train_v14/geom/pack_rft_shards_dir.py \$t \$t/png | tail -1; done" 2>&1 | grep -v srun | tee -a $LOG
BASE=$DV/rft_strict90_all_dw423b/shards; U5=$DV/rft_real_union5_dw423/shards; NAMES=""
for t in $O/tier_n*; do n=$(basename $t | sed 's/tier_//'); M=rft_mix_h6b_$n; NAMES="$NAMES $n"
  bash train_v14/geom/build_rft_mix.sh $DV/$M $BASE $U5 5 >/dev/null
  i=$(ls $DV/$M | wc -l); ns=$(ls $t/shards/rft-*.tar | wc -l); R=$(python3 -c "print(max(1, round(($i/3)/$ns)))")
  for r in $(seq 1 $R); do for f in $t/shards/rft-*.tar; do ln -s "$(readlink -f "$f")" "$DV/$M/rft-$(printf %05d $i).tar"; i=$((i+1)); done; done
  sed -e "s/^run_name: .*/run_name: h6b-$n-delta-e55/" -e "s#^output_dir: .*#output_dir: /srv/scratch/bimrose2/runs/h6b-$n-delta-e55#" train_v14/configs/d0-delta-e55.yaml > train_v14/configs/h6b-$n-delta-e55.yaml
  sed -i "1i # H6b ($n family GT programs, empty think, ~25% of RFT draws) on top of the d0 control mix; 300 steps from e55." train_v14/configs/h6b-$n-delta-e55.yaml
  say "mix $M: $i shards ($ns tier shards x $R)"
done
until grep -q "DELTA DONE" logs/real/delta_chain.log 2>/dev/null; do sleep 300; done
say "delta chain done; shipping H6b inputs"
rsync -a --exclude 'mech/benchmarks/data' --exclude __pycache__ train_v14/ $S20:$SDV/train_v14/
bash train_v14/serv19/cpu_run.sh -c 2 -t 02:00:00 -m 4G -- "on_() { :; }; for t in $O/tier_n*; do ssh -o BatchMode=yes $S20 mkdir -p $SDV/results/h6b/\$(basename \$t); rsync -a \$t/shards $S20:$SDV/results/h6b/\$(basename \$t)/; done; rsync -a $O/bench_held2 $S20:$SDV/fp/h6/ && rsync -a rft_mix_h6b_* $S20:$SDV/ && echo shipped" 2>&1 | grep -v srun | tee -a $LOG
# the mix links point at $DV/results/h6b/tier_*/shards; launch_train_serv20 rewrites the cluster prefix to $SDV
serve() { on "pkill -u bimrose2 -f 'vllm serv[e]'"; sleep 20
  on "cd $SDV; CUDA_VISIBLE_DEVICES=4,5,6,7 DP=4 SEQS=96 MODEL=$1 NAME=$2 setsid nohup bash train_v14/serv19/run_vllm_e55_serv20.sh > logs/vllm-h6b.log 2>&1 < /dev/null & sleep 1; echo ok"
  for i in $(seq 1 240); do on "curl -s -m 5 http://127.0.0.1:8100/health >/dev/null" && return 0; sleep 15; done; say "vLLM never ready $2"; return 1; }
gen() { T=14400 on "cd $SDV; for i in 0 1 2 3; do .venv/bin/python train_v14/geom/gen_openai_bo.py --bench $2 --base-url http://127.0.0.1:8100/v1 --model $1 --k 8 --temperature 0.7 --nshards 4 --shard \$i --workers 16 --out results/split/$3 $4 > logs/gen_$3.\$i.log 2>&1 & done; wait; grep -h DONE logs/gen_$3.*.log | wc -l"; }
JOBS=""
score() { rsync -a "$S20:$SDV/results/split/$1.shard*.json.partial.json" $O/ || { say "no partials $1"; return; }
  JOBS="$JOBS $(sbatch --parsable --job-name=score-$1 --time=08:00:00 --export=ALL,PARTIALS="$O/$1.shard*.json.partial.json",GT=$2,OUT=$O/$1.json,WORKERS=40$3 $DV/train_v14/sbatch/score_generic.sbatch)"; }
evalset() {  # served name
  gen $1 fp/h6/bench_held2 famNT_$1 --no-think | tee -a $LOG; gen $1 mech_benchmarks/ext_bench_dw423_perm realNT_$1 --no-think | tee -a $LOG
  score famNT_$1 $O/bench_held2/gt_meshes_v15 ,NO_CONS=1; score realNT_$1 $B/ext_bench_dw423_perm/gt_meshes_v15 ''; }
serve $SDV/runs/e55-rft-real-u5-gt-dw423/final e55 && evalset e55
serve $SDV/runs/d0-delta-e55/final d0-delta-e55 && evalset d0-delta-e55
for n in $NAMES; do R=h6b-$n-delta-e55
  on "pkill -u bimrose2 -f 'vllm serv[e]'"; say "training $R"
  on "cd $SDV && MODEL_ID=$SDV/runs/e55-rft-real-u5-gt-dw423/final bash train_v14/serv19/launch_train_serv20.sh $R rft_mix_h6b_$n" | tee -a $LOG
  until on "grep -q 'TRAIN EXIT' $SDV/logs/${R}_serv20.log"; do sleep 120; done
  on "[ -d $SDV/runs/$R/final ]" || { say "no final $R"; continue; }
  serve $SDV/runs/$R/final $R || continue
  evalset $R; gen $R mech_benchmarks/ext_bench_dw423_perm real_$R "" | tee -a $LOG; score real_$R $B/ext_bench_dw423_perm/gt_meshes_v15 ''
done
on "pkill -u bimrose2 -f 'vllm serv[e]'"
J=$(echo $JOBS | tr ' ' ','); while [ -n "$(squeue -j $J -h 2>/dev/null)" ]; do sleep 120; done
python3 - $O <<'PY' | tee -a $LOG
import json, os, sys, glob, numpy as np
O = sys.argv[1]
for f in sorted(glob.glob(os.path.join(O, "*.json"))):
    if "consistency" in f or f.endswith("partial.json"): continue
    d = json.load(open(f))["candidates"]
    fi = [float(p["cands"][0].get("iou") or 0) for p in d]; mn = [np.mean([float(c.get("iou") or 0) for c in p["cands"]]) for p in d]
    bo = [max(float(c.get("iou") or 0) for c in p["cands"]) for p in d]; ex = np.mean([bool(c.get("exec")) for p in d for c in p["cands"]])
    print(f"{os.path.basename(f)[:-5]:36s} n={len(d):3d} first {np.mean(fi):.3f} mean {np.mean(mn):.3f} best-of-8 {np.mean(bo):.3f} exec {ex:.0%}")
PY
say "H6B DONE"
