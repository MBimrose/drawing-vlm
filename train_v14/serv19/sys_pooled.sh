#!/usr/bin/env bash
# BEST-SYSTEM run (2026-09-30): e55 vote pick -> pooled repair loop, each round 16 repairs from rp3 (Qwen, serv-20 :8100)
# + 16 from the DeepSeek repairer (serv-19 :8200 via ssh tunnel :8201), all rendered, v3-gated adoption, 6 rounds.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; S20=wpk-serv-20.mechse.illinois.edu; SDV=/srv/scratch/bimrose2; NAME=${NAME:-rep_r32}
cd $DV
until grep -q "REPAIR EVAL DONE $NAME" logs/real/dsv41_eval.log 2>/dev/null; do sleep 120; done
until ssh $S20 "grep -q 'SYS RP3 DONE' $SDV/logs/sys_rp3_k16r5.log"; do sleep 120; done
rsync -a --exclude __pycache__ train_v14/geom $S20:$SDV/train_v14/
ssh $S20 "pkill -u bimrose2 -f 'ssh -f -N -L 8201' ; ssh -f -N -o ExitOnForwardFailure=yes -L 8201:localhost:8200 wpk-serv-19.mechse.illinois.edu; sleep 3; curl -s -m 10 -o /dev/null -w 'tunnel %{http_code}\n' http://127.0.0.1:8201/health"
ssh $S20 "cd $SDV; .venv/bin/python train_v14/geom/vr_serve.py --bench mech_benchmarks/ext_bench_dw423_perm --picks results/visrepair/e55_vote_picks.json --base-url http://127.0.0.1:8100/v1 --model rp3 --k 16 --extra-endpoint 'http://127.0.0.1:8201/v1|$NAME|16' --rounds 6 --margin 0.1 --max-tokens 6000 --workers 24 --py $SDV/.venv/bin/python --rpy $SDV/dw_venv/bin/python --script-dir $SDV/mech_step_to_drw --out results/repair/sys_pooled_rp3_${NAME}_r6.jsonl > logs/sys_pooled.log 2>&1; tail -1 logs/sys_pooled.log"
rsync -a "$S20:$SDV/results/repair/sys_*.jsonl" results/repair/
for f in results/repair/sys_rp3_k16r5.jsonl results/repair/sys_pooled_rp3_${NAME}_r6.jsonl; do echo "== $f"; python3 train_v14/geom/v3adopt_summary.py $f 2>/dev/null | grep -v nan; done | tee -a logs/real/sys_pooled.log
echo "SYS POOLED DONE" | tee -a logs/real/sys_pooled.log
