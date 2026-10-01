#!/usr/bin/env bash
# After serv-20 training: fetch adapter -> merge on serv-19 -> serve (native context) -> probe 144 real parts at
# T=0.7, effort 75, 250k tokens (vanilla's 0.299 protocol) -> paired comparison vs vanilla.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; S19=wpk-serv-19.mechse.illinois.edu; S20=wpk-serv-20.mechse.illinois.edu; LOG=$DV/logs/real/dsv41_eval.log
cd $DV
until ssh $S20 "grep -q 'TRAIN EXIT' /srv/scratch/bimrose2/logs/dsv41_selftrain.log"; do sleep 120; done
echo "$(date '+%m-%d %H:%M') selftrain: $(ssh $S20 'grep "\[train\] step" /srv/scratch/bimrose2/logs/dsv41_selftrain.log | tail -1; tail -1 /srv/scratch/bimrose2/logs/dsv41_selftrain.log')" | tee -a $LOG
mkdir -p runs/dsv41_selftrain_r32; rsync -a $S20:/srv/scratch/bimrose2/runs/dsv41_selftrain_r32/ runs/dsv41_selftrain_r32/
bash train_v14/serv19/dsv41_ft_merge_serv19.sh runs/dsv41_selftrain_r32 selftrain_r32 | tee -a $LOG
ssh $S19 "for p in \$(ps -u bimrose2 -o pid,args | grep -E 'api_server.*--port 8200|dsv41_ft_serve_serv19.sh' | grep -v grep | awk '{print \$1}'); do kill \$p; done; sleep 45; cd /scratch/bimrose2/dsv41_flash; setsid nohup bash dsv41_ft_serve_serv19.sh /scratch/bimrose2/dsv41_ft/selftrain_r32 selftrain_r32 8200 4,5,6,7 > /scratch/bimrose2/dsv41_ft/serve_selftrain.log 2>&1 < /dev/null &"
for i in $(seq 1 240); do ssh $S19 "curl -sf -m 5 localhost:8200/health >/dev/null" && break; sleep 15; done
ssh $S19 "cd /srv/scratch/bimrose2; source train_v14/env.sh 2>/dev/null; export OPENBLAS_NUM_THREADS=1 REASONING_EFFORT=75; .venv/bin/python train_v14/geom/probe_openai_vlm.py --bench /scratch/bimrose2/mech_benchmarks/ext_bench_dw423_perm --base-url http://localhost:8200/v1 --model selftrain_r32 --out results/ext/probe_selftrain_r32_t07_uncapped.json --n 0 --k 1 --temperature 0.7 --workers 48 --max-tokens 250000 --timeout 14400 > /tmp/probe_selftrain.log 2>&1"
rsync -a $S19:/srv/scratch/bimrose2/results/ext/probe_selftrain_r32_t07_uncapped.json results/ext/
python3 - <<'PY' | tee -a $LOG
import json, numpy as np
def L(f): return {r["key"]: r for r in json.load(open(f))["records"]}
v = L("results/ext/probe_vanilla_think_e75_uncapped_t07.json"); s = L("results/ext/probe_selftrain_r32_t07_uncapped.json")
ks = sorted(set(v) & set(s)); g = lambda d, k: float(d[k].get("iou") or 0)
for n, d in (("vanilla", v), ("self-trained", s)):
    a = np.array([g(d, k) for k in ks]); F = np.array([k[0] for k in ks]); tok = [((d[k].get("usage") or {}).get("completion_tokens") or 0) for k in ks]
    print(f"{n:13s} mean {a.mean():.3f} ABC {a[F=='A'].mean():.3f} Fusion {a[F=='F'].mean():.3f} exec {sum(bool(d[k].get('exec')) for k in ks)} >=0.8 {(a>=0.8).sum()} tokens med {np.median(tok):.0f}")
dd = np.array([g(s, k) - g(v, k) for k in ks]); rng = np.random.default_rng(0); bs = [dd[rng.integers(0, len(dd), len(dd))].mean() for _ in range(3000)]
print(f"self-trained - vanilla: {dd.mean():+.3f} [{np.percentile(bs,2.5):+.3f},{np.percentile(bs,97.5):+.3f}]")
PY
echo "SELFTRAIN EVAL DONE" | tee -a $LOG
