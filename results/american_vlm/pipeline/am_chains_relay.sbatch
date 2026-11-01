#!/bin/bash
#SBATCH --job-name=am-chains-relay
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=64
#SBATCH --mem=200G
#SBATCH --time=24:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/american_vlm/pipeline/logs/%x-%j.out
# Extra chain runners (2026-10-28, user-approved relay): CPU-only runners on another cluster node for an H200 repair job
# (am_rp_cluster.sbatch) whose servers are reached through tcp_relay.py on that node's cluster-internal address.
# am_runner.sh unchanged; own ROOT ($PD/<HT>), same serv-19 claims as the H200 node's runners.
#   sbatch --nodelist=ccc0442 --export=ALL,MODEL=gemma,RELAY_HOST=172.29.x.y,NR=5,W=12 am_chains_relay.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; IP=$DV/results/indist_pipeline; P=$DV/results/american_vlm/pipeline
case ${MODEL:-gemma} in
  gemma) PD=$DV/results/american_vlm/pipeline_gemma; SNAME=gmrp; CLAIMS=/srv/scratch/bimrose2/gmpipe/claims;;
  nemotron) PD=$DV/results/american_vlm/pipeline_nemo; SNAME=nmrp; CLAIMS=/srv/scratch/bimrose2/nmpipe/claims;;
  *) echo "unknown MODEL"; exit 2;;
esac
HT=r$(hostname -s | sed 's/^ccc0*//'); RT=$PD/$HT; mkdir -p $RT/logs
cd $RT; mkdir -p out done mine locks failed
ln -sfn $PD/blocks blocks; ln -sfn $PD/blocks.txt blocks.txt; ln -sfn $PD/drop_empty_rounds.py drop_empty_rounds.py
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
H=wpk-serv-19.mechse.illinois.edu
# --- runner environment, as am_chains_c442.sbatch
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
PIDS=(); trap 'for p in "${PIDS[@]}"; do kill -- -$p 2>/dev/null; done' EXIT
for i in 1 2 3 4 5 6 7 8; do u=http://$RELAY_HOST:3885$i/v1; curl -s -m 5 $u/models >/dev/null && echo $u; done > $RT/urls_$HT.txt
[ -s $RT/urls_$HT.txt ] || { echo "relay $RELAY_HOST not reachable"; exit 1; }
echo "$(date) $(wc -l < $RT/urls_$HT.txt) relayed servers"
cat > $RT/host.env <<EOT
ROOT=$RT; HT=$HT; PY=$D/venv/bin/python; RPY=$D/dw_venv/bin/python; SD=$C2/step_to_drw
BENCH_B=$D/bench_b; BENCH_FULL=$D/fullpool; VRS=$D/train_v14/geom/vr_serve.py; MODEL=$SNAME; CLAIMS_SSH=$H; CLAIMS_DIR=$CLAIMS
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
EOT
FIRST=$(head -1 $RT/urls_$HT.txt)
for r in $(seq 1 ${NR:-5}); do
  setsid bash $P/am_runner.sh $RT/host.env $FIRST ${W:-12} j${SLURM_JOB_ID}r$r > $RT/logs/runner_${SLURM_JOB_ID}_r$r.log 2>&1 < /dev/null &
  PIDS+=($!); echo "$(date) runner $r pid $!"; sleep 15
done
while :; do alive=0; for p in "${PIDS[@]}"; do kill -0 $p 2>/dev/null && alive=1; done; [ $alive = 0 ] && break; sleep 60; done
echo "AM RELAY RUNNERS DONE $(date)"
