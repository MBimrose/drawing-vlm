#!/bin/bash
#SBATCH --job-name=ip-cpu
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --nodelist=ccc0442
#SBATCH --time=48:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/indist_pipeline/logs/%x-%j.out
# In-dist full pipeline (2026-10-14), v2 of chains_l40s.sbatch: ccc0442 CPUs run block runners (runner.sh -> vr_serve.py, bench-B
# args unchanged) from the node-RAM code/pool copy (stage_code_shm.sh); the rp3 requests go to serv-20 B300 servers through
# ssh tunnels (ports PORTS, runners assigned round-robin). The L40S server was the bottleneck (8 x L40S ~ 14 rounds/min) and the
# Lustre-resident code and Python stdlib (uv homes) left the scorers in D state: code, pool and Python homes are staged in
# /dev/shm (stage_code_shm.sh, stage_py_shm.sh; exec_harness 19.4 s -> 4.2 s wall under load).
#   sbatch --cpus-per-task=80 --mem=500G --export=ALL,NR=8,W=12,PORTS="8721 8722" chains_c442.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; P=$DV/results/indist_pipeline; cd $P
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
C2=/dev/shm/bimrose2/c2stage; D=/dev/shm/bimrose2/ipcode
[ -f $C2/READY ] || { echo "no c2stage venvs in node RAM"; exit 1; }
bash $P/stage_code_shm.sh && bash $P/stage_py_shm.sh || { echo "staging failed"; exit 1; }
S=/dev/shm/bimrose2/ipc_$SLURM_JOB_ID; mkdir -p $S
PIDS=(); TUN=()
cleanup() { for p in "${PIDS[@]}"; do kill -- -$p 2>/dev/null; done; for t in "${TUN[@]}"; do kill $t 2>/dev/null; done; rm -rf $S; }
trap cleanup EXIT
PORTS=(${PORTS:-8721 8722}); i=0; declare -A LP
tunnel() { ssh -o BatchMode=yes -o ServerAliveInterval=30 -o ExitOnForwardFailure=yes -N -L $2:127.0.0.1:$1 wpk-serv-20.mechse.illinois.edu > /dev/null 2>> $P/logs/tunnel_$SLURM_JOB_ID.log < /dev/null & echo $!; }
for rp in "${PORTS[@]}"; do
  lp=$((20000 + rp + (SLURM_JOB_ID % 50) * 10)); LP[$rp]=$lp
  TUN+=($(tunnel $rp $lp))
  ok=0; for k in $(seq 1 60); do curl -s -m 5 http://127.0.0.1:$lp/health >/dev/null && { ok=1; break; }; sleep 10; done
  [ $ok = 1 ] || { echo "tunnel to serv-20:$rp not healthy"; exit 1; }
  echo "$(date) tunnel :$lp -> serv-20:$rp"
done
cat > $S/host.env <<EOF
ROOT=$P; HT=c442; PY=$D/venv/bin/python; RPY=$D/dw_venv/bin/python; SD=$C2/step_to_drw
BENCH=$D/fullpool; VRS=$D/train_v14/geom/vr_serve.py; CLAIMS_SSH=wpk-serv-20.mechse.illinois.edu
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
EOF
for r in $(seq 1 ${NR:-8}); do
  rp=${PORTS[$(( (r - 1) % ${#PORTS[@]} ))]}
  setsid bash $P/runner.sh $S/host.env http://127.0.0.1:${LP[$rp]}/v1 ${W:-12} j${SLURM_JOB_ID}r$r > $P/logs/runner_c442_${SLURM_JOB_ID}_r$r.log 2>&1 < /dev/null &
  PIDS+=($!); echo "$(date) runner $r pid $! -> serv-20:$rp"; sleep 15
done
# keep tunnels alive while runners work
while :; do
  alive=0; for p in "${PIDS[@]}"; do kill -0 $p 2>/dev/null && alive=1; done
  [ $alive = 0 ] && break
  n=0; for rp in "${PORTS[@]}"; do
    if ! kill -0 ${TUN[$n]} 2>/dev/null; then TUN[$n]=$(tunnel $rp ${LP[$rp]}); echo "$(date) tunnel to $rp restarted"; fi
    n=$((n + 1)); done
  sleep 20
done
echo "IP CPU RUNNERS DONE $(date)"
