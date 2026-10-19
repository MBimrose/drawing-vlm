#!/bin/bash
#SBATCH --job-name=ip-rep
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --nodelist=ccc0442
#SBATCH --time=48:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/indist_pipeline/logs/%x-%j.out
# In-dist full pipeline (2026-10-14): rp3 repair chains on ccc0442. Copy of results/bench_b/pipeline/repair_l40s_b.sbatch
# (same staging, same vllm serve flags: TP 2 x DP #GPU/2, max-model-len 16384, 2 images), but instead of one vr_serve per
# chain it starts NR block runners (runner.sh, W vr_serve workers each) that share the block queue with serv-20.
# With NOSERVE=1 it starts no server and points the runners at URL (another job's server on this node).
#   sbatch --gres=gpu:L40S:8 --cpus-per-task=84 --mem=600G --export=ALL,NR=7,W=12 chains_l40s.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV; P=$DV/results/indist_pipeline
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
S=/dev/shm/bimrose2/ipr_$SLURM_JOB_ID; mkdir -p $S/tmp $S/cfg $S/home
VPID=""; RP=()
cleanup() { for p in "${RP[@]}"; do kill -- -$p 2>/dev/null; done; [ -n "$VPID" ] && { kill -- -$VPID 2>/dev/null; sleep 10; kill -9 -- -$VPID 2>/dev/null; }; rm -rf $S; }
trap cleanup EXIT
T0=$(date +%s)
C2=/dev/shm/bimrose2/c2stage
if [ -f $C2/READY ]; then ln -s $C2/venv $S/venv; ln -s $C2/dw_venv $S/dw_venv; ln -s $C2/step_to_drw $S/step_to_drw; ln -s $C2/vllm.sif $S/vllm.sif
else rsync -a --copy-links $DV/.venv/ $S/venv/ & rsync -a --copy-links $DV/dw_venv/ $S/dw_venv/ & rsync -a $DV/mech_step_to_drw/ $S/step_to_drw/ & cp $DV/containers/vllm-dsv41.from-serv20.sif $S/vllm.sif & wait; fi
PY=$S/venv/bin/python; RPY=$S/dw_venv/bin/python
$PY -c "import build123d, scipy, PIL" && $RPY -c "import draftwright, OCP" || { echo "staged env broken"; exit 1; }
PORT=${PORT:-8730}; URL=${URL:-http://127.0.0.1:$PORT/v1}
if [ "${NOSERVE:-0}" != 1 ]; then
  NG=$(nvidia-smi -L | wc -l); TP=${TP:-2}; DP=$((NG / TP))
  echo "$(date) $NG GPUs ($CUDA_VISIBLE_DEVICES) -> TP $TP DP $DP"
  APPTAINERENV_CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES APPTAINERENV_VLLM_ENGINE_READY_TIMEOUT_S=1800 \
    APPTAINERENV_PYTHONNOUSERSITE=1 APPTAINERENV_VLLM_CONFIG_ROOT=$S/cfg APPTAINERENV_XDG_CACHE_HOME=$S/home/.cache \
    setsid apptainer exec --nv --cleanenv --home $S/home --bind $DV:$DV --bind /dev/shm:/dev/shm --bind $S/tmp:/tmp $S/vllm.sif \
    vllm serve $DV/runs/rp3-delta-e55/final --served-model-name rp3 --host 127.0.0.1 --port $PORT \
      --data-parallel-size $DP --tensor-parallel-size $TP --gpu-memory-utilization ${GMU:-0.92} --max-model-len 16384 \
      --max-num-seqs ${SEQS:-64} --limit-mm-per-prompt '{"image": 2}' --trust-remote-code \
      > $P/logs/vllm-rp3-$SLURM_JOB_ID.log 2>&1 < /dev/null &
  VPID=$!
fi
ok=0; for i in $(seq 1 160); do curl -s -m 5 ${URL%/v1}/health >/dev/null && { ok=1; break; }; sleep 15; done
[ $ok = 1 ] || { echo "vLLM never ready"; [ -n "$VPID" ] && tail -40 $P/logs/vllm-rp3-$SLURM_JOB_ID.log; exit 1; }
echo "$(date) vLLM up at $URL ($(( $(date +%s)-T0 )) s)"
cat > $S/host.env <<EOF
ROOT=$P; HT=c442; PY=$PY; RPY=$RPY; SD=$S/step_to_drw
BENCH=$DV/train_v14/mech/benchmarks/data/fullpool_dw423; VRS=$DV/train_v14/geom/vr_serve.py; CLAIMS_SSH=wpk-serv-20.mechse.illinois.edu
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
EOF
for r in $(seq 1 ${NR:-7}); do
  setsid bash $P/runner.sh $S/host.env $URL ${W:-12} j${SLURM_JOB_ID}r$r > $P/logs/runner_c442_${SLURM_JOB_ID}_r$r.log 2>&1 < /dev/null &
  RP+=($!); echo "$(date) runner $r pid $!"; sleep 20
done
wait "${RP[@]}"
echo "IP REPAIR DONE $(date) ($(( $(date +%s)-T0 )) s)"
