#!/bin/bash
#SBATCH --job-name=c2-gts
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --nodelist=ccc0442
#SBATCH --time=24:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/cycle2/logs/%x-%j.out
# Expert iteration round 2 (2026-10-09), stage 2: GT-selected repair search (geom/gt_search.py, rp3, K=8 repairs/round,
# <= 4 rounds, patience 2, adopt by true IoU, = round-1 bank-v2 settings) on TRAINING parts whose best known program is
# < 0.9 (results/cycle2/search/keys_<corpus>.txt, starts_<corpus>.json from build_starts.py). rp3 served on this node's
# L40S GPUs (TP 2 x DP 4), the pg_repair_l40s.sbatch pattern (server killed by its own process group, no pkill).
#   sbatch --gres=gpu:L40S:8 --cpus-per-task=N --mem=M --export=ALL,SPEC_FILE=<file> results/cycle2/gts_l40s.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
S=/dev/shm/bimrose2/c2gts_$SLURM_JOB_ID; mkdir -p $S/tmp $S/cfg $S/home
L=$DV/results/cycle2/logs; O=$DV/results/cycle2/search
VPID=""
cleanup() { [ -n "$VPID" ] && { kill -- -$VPID 2>/dev/null; sleep 10; kill -9 -- -$VPID 2>/dev/null; }; rm -rf $S; }
trap cleanup EXIT
NG=$(nvidia-smi -L | wc -l); TP=${TP:-2}; DP=$((NG / TP)); PORT=${PORT:-8620}
T0=$(date +%s)
rsync -a --copy-links $DV/.venv/ $S/venv/ & rsync -a --copy-links $DV/dw_venv/ $S/dw_venv/ & rsync -a $DV/mech_step_to_drw/ $S/step_to_drw/ & cp $DV/containers/vllm-dsv41.from-serv20.sif $S/vllm.sif & wait
echo "$(date) staged in $(( $(date +%s)-T0 )) s; $NG GPUs ($CUDA_VISIBLE_DEVICES) -> TP $TP DP $DP"
PY=$S/venv/bin/python; RPY=$S/dw_venv/bin/python
$PY -c "import build123d, scipy, PIL" && $RPY -c "import draftwright, OCP" || { echo "staged env broken"; exit 1; }
APPTAINERENV_CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES APPTAINERENV_VLLM_ENGINE_READY_TIMEOUT_S=1800 \
  APPTAINERENV_PYTHONNOUSERSITE=1 APPTAINERENV_VLLM_CONFIG_ROOT=$S/cfg APPTAINERENV_XDG_CACHE_HOME=$S/home/.cache \
  setsid apptainer exec --nv --cleanenv --home $S/home --bind $DV:$DV --bind /dev/shm:/dev/shm --bind $S/tmp:/tmp $S/vllm.sif \
  vllm serve $DV/runs/rp3-delta-e55/final --served-model-name rp3 --host 127.0.0.1 --port $PORT \
    --data-parallel-size $DP --tensor-parallel-size $TP --gpu-memory-utilization ${GMU:-0.92} --max-model-len 16384 \
    --max-num-seqs ${SEQS:-96} --limit-mm-per-prompt '{"image": 2}' --trust-remote-code \
    > $L/vllm-rp3-$SLURM_JOB_ID.log 2>&1 < /dev/null &
VPID=$!
ok=0; for i in $(seq 1 160); do curl -s -m 5 http://127.0.0.1:$PORT/health >/dev/null && { ok=1; break; }; sleep 15; done
[ $ok = 1 ] || { echo "vLLM never ready"; tail -40 $L/vllm-rp3-$SLURM_JOB_ID.log; exit 1; }
echo "$(date) vLLM up"
echo "$(date) server ready" > $O/SERVER_UP_$SLURM_JOB_ID
# streams: each line of SPEC_FILE = "<corpus> <workers> <keys file> <out jsonl>", run concurrently against this server;
# later CPU-only jobs (gts_worker.sbatch) attach to the same server (127.0.0.1:$PORT on ccc0442) with their own key/out files.
# The job then stays up (serving) until $O/STOP_SERVER exists, so worker jobs can keep using it.
bash $DV/results/cycle2/gts_streams.sh $SPEC_FILE $PORT $PY $RPY $S/step_to_drw
echo "$(date) own streams done; serving until $O/STOP_SERVER"
until [ -f $O/STOP_SERVER ]; do sleep 60; done
echo "C2 GTS SERVER DONE $(date) ($(( $(date +%s)-T0 )) s)"
