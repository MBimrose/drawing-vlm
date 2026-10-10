#!/bin/bash
#SBATCH --job-name=c2-rep
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --nodelist=ccc0442
#SBATCH --time=24:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/cycle2/pipeline/logs/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/cycle2/pipeline/logs/%x-%j.err
# Cycle-2 copy (2026-10-09) of pg_repair_l40s.sbatch with the repairer weights as a parameter (MODEL, default rp3) --
# protocol unchanged. Original: Full pipeline on the GRPO generator (2026-10-08): rp3 repair chains (vr_serve.py, the 0.695 protocol: K=16, 6 rounds,
# margin 0.1, max-tokens 6000, T 0.7) on ccc0442 L40S GPUs. One vLLM server (TP=2, DP=#GPUs/2) serves rp3; every line
# "name|picks.json|out.jsonl" of CHAINS_FILE runs as its own vr_serve process against it, concurrently.
# No pkill trap: the server is killed by its own process-group id; staged dirs are this job's own.
#   sbatch --gres=gpu:L40S:8 --cpus-per-task=72 --mem=250G --export=ALL,CHAINS_FILE=<file>[,WORKERS=24,K=16,ROUNDS=6,LIMIT=0] pg_repair_l40s.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
S=/dev/shm/bimrose2/pgr_$SLURM_JOB_ID; mkdir -p $S/tmp $S/cfg $S/home
VPID=""
cleanup() { [ -n "$VPID" ] && { kill -- -$VPID 2>/dev/null; sleep 10; kill -9 -- -$VPID 2>/dev/null; }; rm -rf $S; }
trap cleanup EXIT
NG=$(nvidia-smi -L | wc -l); TP=${TP:-2}; DP=$((NG / TP)); PORT=${PORT:-8600}
T0=$(date +%s)
# use the persistent node-RAM copy when present (results/cycle2/pipeline/stage_shm.sh; Lustre staging took 20-40 min)
C2=/dev/shm/bimrose2/c2stage
if [ -f $C2/READY ]; then ln -s $C2/venv $S/venv; ln -s $C2/dw_venv $S/dw_venv; ln -s $C2/step_to_drw $S/step_to_drw; ln -s $C2/vllm.sif $S/vllm.sif
else rsync -a --copy-links $DV/.venv/ $S/venv/ & rsync -a --copy-links $DV/dw_venv/ $S/dw_venv/ & rsync -a $DV/mech_step_to_drw/ $S/step_to_drw/ & cp $DV/containers/vllm-dsv41.from-serv20.sif $S/vllm.sif & wait; fi
echo "$(date) staged in $(( $(date +%s)-T0 )) s; $NG GPUs ($CUDA_VISIBLE_DEVICES) -> TP $TP DP $DP"
PY=$S/venv/bin/python; RPY=$S/dw_venv/bin/python
$PY -c "import build123d, scipy, PIL" && $RPY -c "import draftwright, OCP" || { echo "staged env broken"; exit 1; }
APPTAINERENV_CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES APPTAINERENV_VLLM_ENGINE_READY_TIMEOUT_S=1800 \
  APPTAINERENV_PYTHONNOUSERSITE=1 APPTAINERENV_VLLM_CONFIG_ROOT=$S/cfg APPTAINERENV_XDG_CACHE_HOME=$S/home/.cache \
  setsid apptainer exec --nv --cleanenv --home $S/home --bind $DV:$DV --bind /dev/shm:/dev/shm --bind $S/tmp:/tmp $S/vllm.sif \
  vllm serve ${MODEL:-$DV/runs/rp3-delta-e55/final} --served-model-name rp3 --host 127.0.0.1 --port $PORT \
    --data-parallel-size $DP --tensor-parallel-size $TP --gpu-memory-utilization ${GMU:-0.92} --max-model-len 16384 \
    --max-num-seqs ${SEQS:-64} --limit-mm-per-prompt '{"image": 2}' --trust-remote-code ${VLLM_EXTRA:-} \
    > $DV/results/cycle2/pipeline/logs/vllm-rp3-$SLURM_JOB_ID.log 2>&1 < /dev/null &
VPID=$!
ok=0; for i in $(seq 1 160); do curl -s -m 5 http://127.0.0.1:$PORT/health >/dev/null && { ok=1; break; }; sleep 15; done
[ $ok = 1 ] || { echo "vLLM never ready"; tail -40 $DV/results/cycle2/pipeline/logs/vllm-rp3-$SLURM_JOB_ID.log; exit 1; }
echo "$(date) vLLM up"
# start files may still be in the making (selection stage): wait for every picks file of CHAINS_FILE
while IFS='|' read -r name picks out; do
  [ -z "$name" ] && continue
  until [ -s $picks ]; do sleep 30; done
done < $CHAINS_FILE
sleep 30; echo "$(date) start files present"
CP=()
while IFS='|' read -r name picks out; do
  [ -z "$name" ] && continue
  $PY $DV/train_v14/geom/vr_serve.py --bench $DV/train_v14/mech/benchmarks/data/ext_bench_dw423_perm --picks $picks \
    --base-url http://127.0.0.1:$PORT/v1 --model rp3 --k ${K:-16} --rounds ${ROUNDS:-6} --margin ${MARGIN:-0.1} \
    --max-tokens 6000 --workers ${WORKERS:-24} --limit ${LIMIT:-0} --py $PY --rpy $RPY --script-dir $S/step_to_drw \
    --out $out > $DV/results/cycle2/pipeline/logs/chain_$name.log 2>&1 &
  CP+=($!); echo "$(date) chain $name: $picks -> $out (pid $!)"
done < $CHAINS_FILE
wait "${CP[@]}"
echo "PG REPAIR DONE $(date) ($(( $(date +%s)-T0 )) s)"
