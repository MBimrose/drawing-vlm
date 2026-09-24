#!/usr/bin/env bash
# First-principles GPU diagnostics on serv-20 GPUs 4-7 (after the family pilot solve):
#   H4a  e55 K=8 on the real bench with a GT-derived structural description appended to the prompt
#   H7   e55 K=128 on 40 hard real parts (does the ceiling keep climbing with search?)
#   H1   e55 K=8 on the real bench served at native sheet resolution (max_pixels 2,457,600 vs 1,179,648 trained)
# Scoring on the cluster (score_generic; NO_CONS for K=128).   bash fp_gpu_diag.sh   (login node, setsid nohup)
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; SDV=/srv/scratch/bimrose2; S20=wpk-serv-20.mechse.illinois.edu
FP=$DV/results/firstprinciples; B=$DV/train_v14/mech/benchmarks/data; LOG=$DV/logs/real/fp_gpu_diag.log
say() { echo "$(date '+%m-%d %H:%M') $*" | tee -a $LOG; }
on() { timeout ${T:-180} ssh -o BatchMode=yes $S20 "$@"; }
until grep -q "FAMILY PILOT CHAIN EXIT" $DV/logs/real/family_pilot_chain.out 2>/dev/null; do sleep 300; done
say "family pilot chain exited; starting GPU diagnostics"
rsync -a --exclude 'mech/benchmarks/data' --exclude __pycache__ $DV/train_v14/ $S20:$SDV/train_v14/
on "mkdir -p $SDV/fp"; rsync -a $FP/user_prompts_oracle_a.json $FP/h7_keys.txt $S20:$SDV/fp/
serve() {  # $1 = extra vllm args
  on "pkill -u bimrose2 -f 'vllm serv[e]'"; sleep 20
  on "cd $SDV; CUDA_VISIBLE_DEVICES=4,5,6,7 DP=4 SEQS=96 VLLM_EXTRA='$1' setsid nohup bash train_v14/serv19/run_vllm_e55_serv20.sh > logs/vllm-fp.log 2>&1 < /dev/null & sleep 1; echo ok"
  for i in $(seq 1 240); do on "curl -s -m 5 http://127.0.0.1:8100/health >/dev/null" && return 0; sleep 15; done
  say "vLLM never ready ($1)"; on "tail -20 $SDV/logs/vllm-fp.log" >> $LOG; exit 2
}
gen() {  # $1 = stem, rest = extra gen args
  local stem=$1; shift
  T=86400 on "cd $SDV; for i in 0 1 2 3; do .venv/bin/python train_v14/geom/gen_openai_bo.py --bench mech_benchmarks/ext_bench_dw423_perm --base-url http://127.0.0.1:8100/v1 --model e55 --temperature 0.7 --nshards 4 --shard \$i --workers 24 --out results/split/$stem $* > logs/gen_$stem.\$i.log 2>&1 & done; wait; grep -h DONE logs/gen_$stem.*.log | wc -l"
}
serve ""
say "normal server up"; gen fp_h4a_e55 --k 8 --user-prompts $SDV/fp/user_prompts_oracle_a.json | tee -a $LOG
gen fp_h7_e55 --k 128 --keys $SDV/fp/h7_keys.txt | tee -a $LOG
serve '--mm-processor-kwargs {"max_pixels":2457600}'
say "native-resolution server up"; gen fp_h1_e55 --k 8 | tee -a $LOG
on "pkill -u bimrose2 -f 'vllm serv[e]'"; say "generation done, server stopped"
JOBS=""
for s in fp_h4a_e55 fp_h7_e55 fp_h1_e55; do
  rsync -a "$S20:$SDV/results/split/$s.shard*.json.partial.json" $FP/ || { say "no partials $s"; continue; }
  EXTRA=""; [ $s = fp_h7_e55 ] && EXTRA=",NO_CONS=1"
  J=$(sbatch --parsable --job-name=score-$s --time=12:00:00 --export=ALL,PARTIALS="$FP/$s.shard*.json.partial.json",GT=$B/ext_bench_dw423_perm/gt_meshes_v15,OUT=$FP/$s.json,WORKERS=60$EXTRA $DV/train_v14/sbatch/score_generic.sbatch)
  say "scoring $s job $J"; JOBS="$JOBS $J"
done
J=$(echo $JOBS | tr ' ' ','); while [ -n "$(squeue -j $J -h 2>/dev/null)" ]; do sleep 120; done
say "FP GPU DIAG DONE"
