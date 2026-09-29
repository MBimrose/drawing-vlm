#!/bin/bash
#SBATCH --job-name=rp-loop
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=120
#SBATCH --gres=gpu:8
#SBATCH --mem=800G
#SBATCH --time=24:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/real/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/real/%x-%j.err
# Render-guided repair loop on a cluster node (all nodes allowed until 2026-10-01): serve a repair model with the
# apptainer vLLM image (TP=$TP, DP=8/TP), stage the build123d + draftwright venvs in RAM, run vr_serve.py.
#   sbatch --nodelist=<node> --export=ALL,MODEL=<final dir>,NAME=<name>,BENCH=<bench>,PICKS=<json>,OUT=<jsonl>,K=16,ROUNDS=5[,TP=2,MARGIN=0.1] rp_loop_cluster.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; TP=${TP:-2}
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
S=/dev/shm/bimrose2/rpl_$SLURM_JOB_ID; mkdir -p $S; trap 'pkill -f "vllm serv[e]"; rm -rf $S' EXIT
rsync -a --copy-links $DV/.venv/ $S/venv/ & rsync -a --copy-links $DV/dw_venv/ $S/dw_venv/ & rsync -a $DV/mech_step_to_drw/ $S/step_to_drw/ & wait
mkdir -p $S/tmp $S/cfg $S/home
APPTAINERENV_PYTHONNOUSERSITE=1 APPTAINERENV_VLLM_CONFIG_ROOT=$S/cfg APPTAINERENV_XDG_CACHE_HOME=$S/home/.cache apptainer exec --nv --home $S/home --bind $DV:$DV --bind /dev/shm:/dev/shm --bind $S/tmp:/tmp $DV/containers/vllm-dsv41.from-serv20.sif \
  vllm serve $MODEL --served-model-name $NAME --host 127.0.0.1 --port 8100 --data-parallel-size $((8 / TP)) --tensor-parallel-size $TP \
  --gpu-memory-utilization 0.90 --max-model-len 16384 --max-num-seqs 32 --limit-mm-per-prompt '{"image": 2}' --trust-remote-code \
  > $DV/logs/real/vllm-rpl-$SLURM_JOB_ID.log 2>&1 &
for i in $(seq 1 240); do curl -s -m 5 http://127.0.0.1:8100/health >/dev/null && break; sleep 15; done
curl -s -m 5 http://127.0.0.1:8100/health >/dev/null || { echo "vLLM never ready"; tail -30 $DV/logs/real/vllm-rpl-$SLURM_JOB_ID.log; exit 1; }
echo "vLLM up $(date)"
$S/venv/bin/python $DV/train_v14/geom/vr_serve.py --bench $BENCH --picks $PICKS --base-url http://127.0.0.1:8100/v1 --model $NAME \
  --k ${K:-8} --rounds ${ROUNDS:-3} --margin ${MARGIN:-0.1} --workers ${WORKERS:-32} --out $OUT \
  --py $S/venv/bin/python --rpy $S/dw_venv/bin/python --script-dir $S/step_to_drw
echo "RP LOOP DONE $(date)"
