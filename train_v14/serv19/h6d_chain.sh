#!/usr/bin/env bash
# H6d: Zero-to-CAD translated programs as more ground truth (after zerocad z1 translation and the H6c chain).
# pack+render z1 -> tier (empty think) -> rationalize on serv-20 (think tier ready for a follow-up) ->
# train h6d-zcnt = d0 mix + family n1655 (empty think) + zerocad (empty think), 300 steps from e55;
# judge no-think on held-out families + real bench (vs h6b-n1655: does more / different GT extend the curve?) and think real.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; SDV=/srv/scratch/bimrose2; S20=wpk-serv-20.mechse.illinois.edu
O=$DV/results/h6d; B=$DV/train_v14/mech/benchmarks/data; LOG=$DV/logs/real/h6d_chain.log; mkdir -p $O
say() { echo "$(date '+%m-%d %H:%M') $*" | tee -a $LOG; }
on() { timeout ${T:-180} ssh -o BatchMode=yes $S20 "$@"; }
cd $DV
until on "grep -q 'ZCAD DONE' $SDV/zerocad/z1/run.log"; do sleep 300; done
say "z1: $(on "tail -1 $SDV/zerocad/z1/run.log")"
J=$(SRCROOT=$SDV/zerocad bash train_v14/mech/familysynth/pack_family_corpus.sh z1 zerocad_z1 | tee -a $LOG | awk '/render job/{print $3}')
while [ -n "$(squeue -j $J -h 2>/dev/null)" ]; do sleep 60; done; tail -2 $B/zerocad_z1/logs/stage.log | tee -a $LOG
bash train_v14/serv19/cpu_run.sh -c 4 -t 01:00:00 -m 32G -- ".venv/bin/python train_v14/mech/familysynth/build_h6b.py --corpora $B/zerocad_z1 --pilot-held results/firstprinciples/h6/bench_held --out $O --ns 0 --held-frac 0 --max-held 0 && .venv/bin/python train_v14/geom/pack_rft_shards_dir.py $O/tier_n* $O/tier_n*/png | tail -1" 2>&1 | grep -v srun | tee -a $LOG
T=$(ls -d $O/tier_n* | head -1); mv $T $O/tier_zc; T=$O/tier_zc
on "mkdir -p $SDV/results/h6d"; rsync -a $T/accepted-000.jsonl $T/png $S20:$SDV/results/h6d/tier_zc/
on "cd $SDV; DS_CAP=32 setsid nohup .venv/bin/python train_v14/mech/familysynth/rationalize_family.py --tier results/h6d/tier_zc --out results/h6d/tier_zc_rat --workers 32 > results/h6d/rat.log 2>&1 < /dev/null & echo rat started" | tee -a $LOG
until grep -q "H6C2 DONE" logs/real/h6c_chain.log; do sleep 300; done
BASE=$DV/rft_strict90_all_dw423b/shards; U5=$DV/rft_real_union5_dw423/shards; M=rft_mix_h6d_zcnt
bash train_v14/geom/build_rft_mix.sh $DV/$M $BASE $U5 5 >/dev/null; i=$(ls $DV/$M | wc -l); nb=$i
for t in $DV/results/h6b/tier_n1655 $T; do ns=$(ls $t/shards/rft-*.tar | wc -l); R=$(python3 -c "print(max(1, round(($nb/3)/$ns/2)))")
  for r in $(seq 1 $R); do for f in $t/shards/rft-*.tar; do ln -s "$(readlink -f "$f")" "$DV/$M/rft-$(printf %05d $i).tar"; i=$((i+1)); done; done; done
say "mix $M: $i shards"
R=h6d-zcnt-delta-e55
sed -e "s/^run_name: .*/run_name: $R/" -e "s#^output_dir: .*#output_dir: /srv/scratch/bimrose2/runs/$R#" -e "1s/.*/# H6d: d0 mix + family n1655 + Zero-to-CAD translated GT (both empty think); 300 steps from e55./" \
  train_v14/configs/h6b-n1655-delta-e55.yaml > train_v14/configs/$R.yaml
rsync -a --exclude 'mech/benchmarks/data' --exclude __pycache__ train_v14/ $S20:$SDV/train_v14/
bash train_v14/serv19/cpu_run.sh -c 2 -t 02:00:00 -m 4G -- "ssh -o BatchMode=yes $S20 mkdir -p $SDV/results/h6d/tier_zc; rsync -a $T/shards $S20:$SDV/results/h6d/tier_zc/ && rsync -a $M $S20:$SDV/ && echo shipped" 2>&1 | grep -v srun | tee -a $LOG
serve() { on "pkill -u bimrose2 -f 'vllm serv[e]'"; sleep 20
  on "cd $SDV; CUDA_VISIBLE_DEVICES=4,5,6,7 DP=4 SEQS=96 MODEL=$1 NAME=$2 setsid nohup bash train_v14/serv19/run_vllm_e55_serv20.sh > logs/vllm-h6d.log 2>&1 < /dev/null & sleep 1; echo ok"
  for i in $(seq 1 240); do on "curl -s -m 5 http://127.0.0.1:8100/health >/dev/null" && return 0; sleep 15; done; say "vLLM never ready $2"; return 1; }
gen() { T=36000 on "cd $SDV; for i in 0 1 2 3; do .venv/bin/python train_v14/geom/gen_openai_bo.py --bench $2 --base-url http://127.0.0.1:8100/v1 --model $1 --k 8 --temperature 0.7 --nshards 4 --shard \$i --workers 24 --out results/split/$3 $4 > logs/gen_$3.\$i.log 2>&1 & done; wait; grep -h DONE logs/gen_$3.*.log | wc -l"; }
JOBS=""
score() { rsync -a "$S20:$SDV/results/split/$1.shard*.json.partial.json" $O/ || { say "no partials $1"; return; }
  JOBS="$JOBS $(sbatch --parsable --job-name=score-$1 --time=08:00:00 --export=ALL,PARTIALS="$O/$1.shard*.json.partial.json",GT=$2,OUT=$O/$1.json,WORKERS=40$3 $DV/train_v14/sbatch/score_generic.sbatch)"; }
on "pkill -u bimrose2 -f 'vllm serv[e]'"; say "training $R"
on "cd $SDV && MODEL_ID=$SDV/runs/e55-rft-real-u5-gt-dw423/final bash train_v14/serv19/launch_train_serv20.sh $R $M" | tee -a $LOG
until on "grep -q 'TRAIN EXIT' $SDV/logs/${R}_serv20.log"; do sleep 120; done
if on "[ -d $SDV/runs/$R/final ]" && serve $SDV/runs/$R/final $R; then
  gen $R fp/h6/bench_held2 famNT_$R --no-think | tee -a $LOG; score famNT_$R $DV/results/h6b/bench_held2/gt_meshes_v15 ,NO_CONS=1
  gen $R mech_benchmarks/ext_bench_dw423_perm realNT_$R --no-think | tee -a $LOG; score realNT_$R $B/ext_bench_dw423_perm/gt_meshes_v15 ''
  gen $R mech_benchmarks/ext_bench_dw423_perm real_$R "" | tee -a $LOG; score real_$R $B/ext_bench_dw423_perm/gt_meshes_v15 ''
else say "no final / no serve $R"; fi
on "pkill -u bimrose2 -f 'vllm serv[e]'"
J=$(echo $JOBS | tr ' ' ','); while [ -n "$(squeue -j $J -h 2>/dev/null)" ]; do sleep 120; done
python train_v14/geom/variant_compare.py --base $DV/results/h6b/realNT_h6b-n1655-delta-e55 --var $O/realNT_$R 2>&1 | sed 's/  \(mean\|exec\|vote\|oracle\)/\n        \1/g' | tee -a $LOG
python train_v14/geom/variant_compare.py --base $DV/results/ext/bo8_ext_dw423p_e55-rft-real-u5-gt-dw423 --var $O/real_$R 2>&1 | sed 's/  \(mean\|exec\|vote\|oracle\)/\n        \1/g' | tee -a $LOG
say "H6D DONE"
