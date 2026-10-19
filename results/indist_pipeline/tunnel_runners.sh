#!/bin/bash
# In-dist pipeline (2026-10-14): extra ccc0442 runners whose rp3 requests go to a serv-20 B300 server through an ssh tunnel
# (the L40S server of the chain job is saturated; the CPU work of the runners stays on ccc0442).
# Run inside an existing ccc0442 allocation:  srun --jobid=<job> --overlap ... bash tunnel_runners.sh <NR> <W> <remote_port> <local_port> <tag>
set -uo pipefail
NR=$1; W=$2; RPORT=$3; LPORT=$4; TAG=$5
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; P=$DV/results/indist_pipeline
S=/dev/shm/bimrose2/ipt_${TAG}; mkdir -p $S
C2=/dev/shm/bimrose2/c2stage; [ -f $C2/READY ] || { echo "no node-RAM staging"; exit 1; }
PIDS=()
cleanup() { for p in "${PIDS[@]}"; do kill -- -$p 2>/dev/null; kill $p 2>/dev/null; done; }
trap cleanup EXIT
ssh -o BatchMode=yes -o ServerAliveInterval=30 -o ExitOnForwardFailure=yes -N -L $LPORT:127.0.0.1:$RPORT wpk-serv-20.mechse.illinois.edu &
TP=$!; PIDS+=($TP)
ok=0; for i in $(seq 1 240); do curl -s -m 5 http://127.0.0.1:$LPORT/health >/dev/null && { ok=1; break; }; sleep 15; done
[ $ok = 1 ] || { echo "tunnel/server not ready"; exit 1; }
echo "$(date) tunnel up :$LPORT -> serv-20:$RPORT (ssh pid $TP)"
cat > $S/host.env <<EOF
ROOT=$P; HT=c442; PY=$C2/venv/bin/python; RPY=$C2/dw_venv/bin/python; SD=$C2/step_to_drw
BENCH=$DV/train_v14/mech/benchmarks/data/fullpool_dw423; VRS=$DV/train_v14/geom/vr_serve.py; CLAIMS_SSH=wpk-serv-20.mechse.illinois.edu
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
EOF
for r in $(seq 1 $NR); do
  setsid bash $P/runner.sh $S/host.env http://127.0.0.1:$LPORT/v1 $W ${TAG}r$r > $P/logs/runner_c442_${TAG}_r$r.log 2>&1 < /dev/null &
  PIDS+=($!); echo "$(date) runner $r pid $!"; sleep 20
done
# keep the tunnel alive; restart it if it dies while runners are still working
while :; do
  alive=0; for p in "${PIDS[@]:1}"; do kill -0 $p 2>/dev/null && alive=1; done
  [ $alive = 0 ] && break
  if ! kill -0 $TP 2>/dev/null; then
    ssh -o BatchMode=yes -o ServerAliveInterval=30 -o ExitOnForwardFailure=yes -N -L $LPORT:127.0.0.1:$RPORT wpk-serv-20.mechse.illinois.edu &
    TP=$!; PIDS[0]=$TP; echo "$(date) tunnel restarted (pid $TP)"
  fi
  sleep 30
done
echo "TUNNEL RUNNERS DONE $(date)"
