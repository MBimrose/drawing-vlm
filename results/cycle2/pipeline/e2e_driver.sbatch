#!/bin/bash
#SBATCH --job-name=c2-e2e
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodelist=ccc0442
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=30:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/cycle2/pipeline/logs/%x-%j.out
# Cycle-2 end-to-end pipeline driver (2026-10-09; user-approved). Rules declared BEFORE the inputs exist:
#  repairer  = rp4c2 if its chain-1 final beats rp3's on the rft2_rl s20 starts (paired mean delta > 0), else rp3;
#  generator = rft2_rl s60 or s120, higher real-bench vote (clean consistency file); |dvote| < 0.005 -> higher best-of-8.
# Then: K=16 of the generator (serv-20 GPU 1; s60's already exists), scoring + vote + render-compare v3 (ccc0442),
# v3b-EV verifier (serv-20 GPU 4, e51 base copy), top-3 distinct starts (pg_make_starts.py), 3 repair chains
# K=16 x 6 / margin 0.1 / max 6000 tokens (vr_serve via repair_l40s.sbatch, 8 L40S), multi-start v3 pick, summary vs the
# 0.716 and 0.695 systems (chain_compare.py).
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV; S20=wpk-serv-20.mechse.illinois.edu
P=results/cycle2/pipeline; say() { echo "$(date '+%m-%d %H:%M') $*"; }
on() { timeout 600 ssh -o BatchMode=yes $S20 "$@"; }
# 1. repairer
until [ "$(wc -l < $P/chain_rp3_rl2s20_c1.jsonl)" -ge 144 ] && [ "$(wc -l < $P/chain_rp4_rl2s20_c1.jsonl)" -ge 144 ] \
      || [ -z "$(squeue -h -n c2-rep -u bimrose2)" ]; do sleep 120; done
python3 $P/chain_compare.py rp4=$P/chain_rp4_rl2s20_c1.jsonl rp3=$P/chain_rp3_rl2s20_c1.jsonl --start --pairs rp4:rp3,rp4:rp4_start,rp3:rp3_start \
  | tee $P/compare_rp4_rp3_s20.txt
D=$(grep "^| rp4 − rp3 " $P/compare_rp4_rp3_s20.txt | awk -F'|' '{print $4}' | awk '{print $1}')
if python3 -c "import sys; sys.exit(0 if float('$D') > 0 else 1)"; then REP=rp4c2; MODEL=$DV/runs/rp4c2-merged; else REP=rp3; MODEL=$DV/runs/rp3-delta-e55/final; fi
say "repairer: $REP (rp4-rp3 chain-1 delta $D)"
# 2. generator
until [ -f results/grpo_eval/real_rft2_rl_s120_consistency.json ] && [ -f results/grpo_eval/real_rft2_rl_s60_consistency.json ]; do sleep 300; done
sleep 60
G=$(python3 - <<'PY'
import json, numpy as np
def m(n):
    v = np.mean([x["consistency"] for x in json.load(open(f"results/grpo_eval/real_{n}_consistency.json"))["per_part"].values()])
    b = np.mean([max(float(c.get("iou") or 0) for c in p["cands"]) for p in json.load(open(f"results/grpo_eval/real_{n}.json"))["candidates"]])
    return v, b
v60, b60 = m("rft2_rl_s60"); v120, b120 = m("rft2_rl_s120")
pick = ("s60" if v60 > v120 else "s120") if abs(v60 - v120) >= 0.005 else ("s60" if b60 >= b120 else "s120")
print(pick, f"vote s60 {v60:.3f} s120 {v120:.3f} bo8 s60 {b60:.3f} s120 {b120:.3f}")
PY
)
say "generator: $G"; G=${G%% *}; NAME=rl2$G
if [ ! -f $P/starts_${NAME}_r3.json ]; then
  on "cd /srv/scratch/bimrose2; setsid nohup bash cycle2/pipeline/gen_k16_s20.sh runs/grpo_v_rft2_rl/adapter_step${G#s} $NAME > cycle2/pipeline/logs/gen_$NAME.log 2>&1 < /dev/null & disown"
  J=$(sbatch --parsable --cpus-per-task=32 --mem=300G --export=ALL,NAME=$NAME $P/score_rc.sbatch); say "score job $J"
  until [ -f $P/real_k16_${NAME}_rc_v3.json ] && [ -z "$(squeue -h -j $J)" ]; do sleep 120; done
  rsync -a $P/real_k16_$NAME.json $S20:/srv/scratch/bimrose2/cycle2/pipeline/
  on "cd /srv/scratch/bimrose2; setsid nohup bash cycle2/pipeline/vscore_s20.sh $NAME > cycle2/pipeline/logs/vscore_$NAME.out 2>&1 < /dev/null & disown"
  until on "grep -q 'VSCORE DONE 0' /srv/scratch/bimrose2/cycle2/pipeline/logs/vscore_$NAME.out"; do sleep 120; done
  rsync -a $S20:/srv/scratch/bimrose2/cycle2/pipeline/vpreds_k16_$NAME.json $P/
  python3 train_v14/geom/pg_make_starts.py --cands $P/real_k16_$NAME.json --cons $P/real_k16_${NAME}_consistency.json \
    --vpreds $P/vpreds_k16_$NAME.json --rc $P/real_k16_${NAME}_rc_v3.json --out-stem $P/starts_$NAME --k 16
fi
say "starts: $(ls $P/starts_${NAME}_r*.json | tr '\n' ' ')"
# 3. chains (all three on 8 L40S, TP 2 x DP 4, 24 workers each = the 0.716 run's layout)
CF=$P/chains_e2e_$NAME.txt; : > $CF
for c in 1 2 3; do echo "e2e_${NAME}_${REP}_c$c|$DV/$P/starts_${NAME}_r$c.json|$DV/$P/chain_e2e_${NAME}_${REP}_c$c.jsonl" >> $CF; done
until [ -z "$(squeue -h -n c2-rep -u bimrose2)" ]; do sleep 120; done
J=$(sbatch --parsable --gres=gpu:L40S:8 --cpus-per-task=74 --mem=300G --export=ALL,CHAINS_FILE=$CF,WORKERS=24,PORT=8650,MODEL=$MODEL $P/repair_l40s.sbatch)
say "chain job $J ($REP)"
until [ -z "$(squeue -h -j $J)" ]; do sleep 300; done
# 4. summary
E=$P/chain_e2e_${NAME}_${REP}
python3 $P/chain_compare.py e2e=$E\_c1.jsonl+$E\_c2.jsonl+$E\_c3.jsonl e2e_c1=$E\_c1.jsonl \
  sys716=results/pipeline_grpo/chain_sel_c1.jsonl+results/pipeline_grpo/chain_sel_c2.jsonl+results/pipeline_grpo/chain_sel_c3.jsonl \
  sys695=results/repair/sys_pooled_rp3_rep_r32_r6.jsonl+results/repair/sys_rp3_rank2_r6.jsonl+results/repair/sys_rp3_rank3_r6.jsonl \
  --start --pairs e2e:sys716,e2e:sys695,e2e:e2e_start,e2e:e2e_c1 | tee $P/summary_e2e_$NAME.txt
say "E2E DONE"
