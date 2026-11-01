#!/bin/bash
#SBATCH --job-name=am-chains
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --nodelist=ccc0442
#SBATCH --time=48:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/american_vlm/pipeline/logs/%x-%j.out
# American-VLM visual repair (2026-10-28): fn_chains_c442.sbatch for the Glimmer S2 chains. Runners (am_runner.sh) reach
# the Glimmer repairer on serv-05 (:8851/:8852, am_rp_serve05.sh) through ssh tunnels; claims live on serv-19 (glpipe/claims).
# Flash-Next full pipeline (2026-10-22): ccc0442 CPUs run repair-chain block runners (fn_runner.sh -> vr_serve.py, bench-B args
# unchanged) through ssh tunnels -- results/indist_pipeline/chains_c442.sbatch with serv-19 in place of serv-20. Code, pools and Python run from node RAM (stage_code_shm.sh,
# stage_py_shm.sh; a 2026-10-21 reboot wiped /dev/shm, so the c2stage venvs and render scripts are re-staged first).
#   sbatch --cpus-per-task=100 --mem=400G --export=ALL,NR=8,W=12,PORTS="8851 8852" am_chains_c442.sbatch   (ports.txt wins once written)
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; P=$DV/results/american_vlm/pipeline; IP=$DV/results/indist_pipeline; cd $P
mkdir -p logs out done mine locks failed
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
H=wpk-serv-19.mechse.illinois.edu; H5=wpk-serv-05.mechse.illinois.edu   # claims host / repairer host
C2=/dev/shm/bimrose2/c2stage; D=/dev/shm/bimrose2/ipcode; mkdir -p $C2
( flock 8
  [ -x $C2/venv/bin/python ] && [ -x $C2/dw_venv/bin/python ] || {
    rsync -a --copy-links $DV/.venv/ $C2/venv/ & rsync -a --copy-links $DV/dw_venv/ $C2/dw_venv/ & wait; }
  [ -f $C2/step_to_drw/.STAGED ] || { rsync -a $DV/mech_step_to_drw/ $C2/step_to_drw/ && touch $C2/step_to_drw/.STAGED; }
) 8>/dev/shm/bimrose2/c2stage.lock
bash $IP/stage_code_shm.sh && bash $IP/stage_py_shm.sh || { echo "staging failed"; exit 1; }
if [ ! -f $D/bench_b/READY ]; then
  mkdir -p $D/bench_b && rsync -a -L $DV/results/bench_b/bench/eval_cache_v15.pkl $DV/results/bench_b/bench/gt_meshes_v15 $D/bench_b/ \
    && [ "$(ls $D/bench_b/gt_meshes_v15 | wc -l)" = 280 ] && touch $D/bench_b/READY || { echo "bench B staging failed"; exit 1; }
fi
echo "$(date) staged: $(du -sh $D | cut -f1)"
S=/dev/shm/bimrose2/fnc_$SLURM_JOB_ID; mkdir -p $S
PIDS=(); declare -A LP TPID HEALTHY
cleanup() { for p in "${PIDS[@]}"; do kill -- -$p 2>/dev/null; done; for t in "${TPID[@]}"; do kill $t 2>/dev/null; done; rm -rf $S; }
trap cleanup EXIT
until timeout 60 ssh -o BatchMode=yes $H "test -f /srv/scratch/bimrose2/glpipe/SERVERS_UP"; do sleep 120; done   # serv-19 probe passed
# tunnels: one per serv-19 port listed in ports.txt (re-read every 20 s, so fn_s1_cluster.sh can add the S1 servers);
# urls_c442.txt = the healthy ones, read by the runners per block
[ -s $P/ports.txt ] || echo ${PORTS:-8851 8852} | tr ' ' '\n' > $P/ports.txt
tunnel() { ssh -o BatchMode=yes -o ServerAliveInterval=30 -o ExitOnForwardFailure=yes -N -L $2:127.0.0.1:$1 $H5 > /dev/null 2>> $P/logs/tunnel_$SLURM_JOB_ID.log < /dev/null & echo $!; }
open_tunnels() {
  local changed=0 rp lp ok k
  for rp in $(cat $P/ports.txt); do
    lp=$((20000 + rp + (SLURM_JOB_ID % 50) * 10)); LP[$rp]=$lp
    if [ -z "${TPID[$rp]:-}" ] || ! kill -0 ${TPID[$rp]} 2>/dev/null; then
      TPID[$rp]=$(tunnel $rp $lp)
      ok=0; for k in $(seq 1 30); do curl -s -m 5 http://127.0.0.1:$lp/health >/dev/null && { ok=1; break; }; sleep 10; done
      HEALTHY[$rp]=$ok; changed=1; echo "$(date) tunnel :$lp -> serv-05:$rp (healthy $ok)"
    fi
  done
  if [ $changed = 1 ]; then
    for rp in $(cat $P/ports.txt); do [ "${HEALTHY[$rp]:-0}" = 1 ] && echo "http://127.0.0.1:${LP[$rp]}/v1"; done > $P/urls_c442.txt.tmp
    mv $P/urls_c442.txt.tmp $P/urls_c442.txt
  fi
}
open_tunnels
[ -s $P/urls_c442.txt ] || { echo "no healthy tunnel to serv-05"; exit 1; }
FIRST=$(head -1 $P/urls_c442.txt)
cat > $S/host.env <<EOF
ROOT=$P; HT=c442; PY=$D/venv/bin/python; RPY=$D/dw_venv/bin/python; SD=$C2/step_to_drw
BENCH_B=$D/bench_b; BENCH_FULL=$D/fullpool; VRS=$D/train_v14/geom/vr_serve.py; MODEL=glrp; CLAIMS_SSH=$H; CLAIMS_DIR=/srv/scratch/bimrose2/glpipe/claims
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
EOF
for r in $(seq 1 ${NR:-8}); do
  setsid bash $P/am_runner.sh $S/host.env $FIRST ${W:-12} j${SLURM_JOB_ID}r$r > $P/logs/runner_c442_${SLURM_JOB_ID}_r$r.log 2>&1 < /dev/null &
  PIDS+=($!); echo "$(date) runner $r pid $!"; sleep 15
done
# keep tunnels alive while runners work
while :; do
  alive=0; for p in "${PIDS[@]}"; do kill -0 $p 2>/dev/null && alive=1; done
  [ $alive = 0 ] && break
  open_tunnels
  sleep 20
done
echo "AM CHAIN RUNNERS DONE $(date)"
