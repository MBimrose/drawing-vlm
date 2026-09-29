#!/usr/bin/env bash
# H6c2: rerun of rat / ratnt with the FULL rationalized tier (1,630 plans; H6c trained on a stale 583-plan copy)
# H6c training (serv-20 GPUs 4-7), after h6c_gen.sh and rationalize_family.py:
#   rat    = d0 mix + rationalized family GT (think traces)
#   ratnt  = d0 mix + rationalized (think) + the same parts with empty think (no-think)
#   self   = d0 mix + self-distilled think tier (h6b-n1655 think draws >= 0.8 on its training parts)
# each 300 steps from e55; judged in THINK mode on the permissive real bench (paired vs e55) and held-out families.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; SDV=/srv/scratch/bimrose2; S20=wpk-serv-20.mechse.illinois.edu
O=$DV/results/h6c; B=$DV/train_v14/mech/benchmarks/data; LOG=$DV/logs/real/h6c_chain.log
say() { echo "$(date '+%m-%d %H:%M') $*" | tee -a $LOG; }
on() { timeout ${T:-180} ssh -o BatchMode=yes $S20 "$@"; }
cd $DV
until on "grep -q 'RAT DONE' $SDV/results/h6c/rat.log"; do sleep 300; done
say "rat: $(on "tail -1 $SDV/results/h6c/rat.log")"
rm -rf $O/tier_rat; rsync -a --exclude shards $S20:$SDV/results/h6c/tier_rat $O/; say "tier_rat rows: $(wc -l < $O/tier_rat/accepted-000.jsonl)"
bash train_v14/serv19/cpu_run.sh -c 4 -t 01:00:00 -m 32G -- "for t in $O/tier_rat; do .venv/bin/python train_v14/geom/pack_rft_shards_dir.py \$t \$t/png | tail -1; done" 2>&1 | grep -v srun | tee -a $LOG
BASE=$DV/rft_strict90_all_dw423b/shards; U5=$DV/rft_real_union5_dw423/shards
mkmix() { M=$1; shift; bash train_v14/geom/build_rft_mix.sh $DV/$M $BASE $U5 5 >/dev/null; i=$(ls $DV/$M | wc -l); nb=$i
  for t in "$@"; do ns=$(ls $t/shards/rft-*.tar | wc -l); R=$(python3 -c "print(max(1, round(($nb/3)/$ns/$#)))")
    for r in $(seq 1 $R); do for f in $t/shards/rft-*.tar; do ln -s "$(readlink -f "$f")" "$DV/$M/rft-$(printf %05d $i).tar"; i=$((i+1)); done; done; done
  say "mix $M: $i shards"; }
mkmix rft_mix_h6c_rat2 $O/tier_rat
mkmix rft_mix_h6c_rat2nt $O/tier_rat $DV/results/h6b/tier_n1655
for n in rat2 rat2nt; do sed -e "s/^run_name: .*/run_name: h6c-$n-delta-e55/" -e "s#^output_dir: .*#output_dir: /srv/scratch/bimrose2/runs/h6c-$n-delta-e55#" -e "1s/.*/# H6c $n (see serv19\/h6c_train.sh) on the d0 control mix; 300 steps from e55./" \
  train_v14/configs/h6b-n1655-delta-e55.yaml > train_v14/configs/h6c-$n-delta-e55.yaml; done
rsync -a --exclude 'mech/benchmarks/data' --exclude __pycache__ train_v14/ $S20:$SDV/train_v14/
bash train_v14/serv19/cpu_run.sh -c 2 -t 02:00:00 -m 4G -- "for t in $O/tier_rat; do ssh -o BatchMode=yes $S20 mkdir -p $SDV/results/h6c/\$(basename \$t); rsync -a \$t/shards $S20:$SDV/results/h6c/\$(basename \$t)/; done; rsync -a rft_mix_h6c_* $S20:$SDV/ && echo shipped" 2>&1 | grep -v srun | tee -a $LOG
serve() { on "pkill -u bimrose2 -f 'vllm serv[e]'"; sleep 20
  on "cd $SDV; CUDA_VISIBLE_DEVICES=4,5,6,7 DP=4 SEQS=96 MODEL=$1 NAME=$2 setsid nohup bash train_v14/serv19/run_vllm_e55_serv20.sh > logs/vllm-h6c.log 2>&1 < /dev/null & sleep 1; echo ok"
  for i in $(seq 1 240); do on "curl -s -m 5 http://127.0.0.1:8100/health >/dev/null" && return 0; sleep 15; done; say "vLLM never ready $2"; return 1; }
gen() { T=36000 on "cd $SDV; for i in 0 1 2 3; do .venv/bin/python train_v14/geom/gen_openai_bo.py --bench $2 --base-url http://127.0.0.1:8100/v1 --model $1 --k 8 --temperature 0.7 --nshards 4 --shard \$i --workers 24 --out results/split/$3 $4 > logs/gen_$3.\$i.log 2>&1 & done; wait; grep -h DONE logs/gen_$3.*.log | wc -l"; }
JOBS=""
score() { rsync -a "$S20:$SDV/results/split/$1.shard*.json.partial.json" $O/ || { say "no partials $1"; return; }
  JOBS="$JOBS $(sbatch --parsable --job-name=score-$1 --time=08:00:00 --export=ALL,PARTIALS="$O/$1.shard*.json.partial.json",GT=$2,OUT=$O/$1.json,WORKERS=40$3 $DV/train_v14/sbatch/score_generic.sbatch)"; }
for n in rat2 rat2nt; do R=h6c-$n-delta-e55
  on "pkill -u bimrose2 -f 'vllm serv[e]'"; say "training $R"
  on "cd $SDV && MODEL_ID=$SDV/runs/e55-rft-real-u5-gt-dw423/final bash train_v14/serv19/launch_train_serv20.sh $R rft_mix_h6c_$n" | tee -a $LOG
  until on "grep -q 'TRAIN EXIT' $SDV/logs/${R}_serv20.log"; do sleep 120; done
  on "[ -d $SDV/runs/$R/final ]" || { say "no final $R"; continue; }
  serve $SDV/runs/$R/final $R || continue
  gen $R mech_benchmarks/ext_bench_dw423_perm real_$R "" | tee -a $LOG; score real_$R $B/ext_bench_dw423_perm/gt_meshes_v15 ''
  gen $R fp/h6/bench_held2 famT_$R "" | tee -a $LOG; score famT_$R $DV/results/h6b/bench_held2/gt_meshes_v15 ,NO_CONS=1
done
on "pkill -u bimrose2 -f 'vllm serv[e]'"
J=$(echo $JOBS | tr ' ' ','); while [ -n "$(squeue -j $J -h 2>/dev/null)" ]; do sleep 120; done
for n in rat2 rat2nt; do python train_v14/geom/variant_compare.py --base $DV/results/ext/bo8_ext_dw423p_e55-rft-real-u5-gt-dw423 --var $O/real_h6c-$n-delta-e55 2>&1 | sed 's/  \(mean\|exec\|vote\|oracle\)/\n        \1/g' | tee -a $LOG; done
python3 - $O <<'PY' | tee -a $LOG
import json, os, sys, glob, numpy as np
O = sys.argv[1]
for f in sorted(glob.glob(os.path.join(O, "*rat2*.json"))):
    if "consistency" in f or f.endswith("partial.json"): continue
    d = json.load(open(f))["candidates"]
    fi = [float(p["cands"][0].get("iou") or 0) for p in d]; mn = [np.mean([float(c.get("iou") or 0) for c in p["cands"]]) for p in d]
    bo = [max(float(c.get("iou") or 0) for c in p["cands"]) for p in d]; ex = np.mean([bool(c.get("exec")) for p in d for c in p["cands"]])
    print(f"{os.path.basename(f)[:-5]:36s} n={len(d):4d} first {np.mean(fi):.3f} mean {np.mean(mn):.3f} best-of-8 {np.mean(bo):.3f} >=0.8 {np.mean([b>=0.8 for b in bo]):.0%} exec {ex:.0%}")
PY
say "H6C2 DONE"
