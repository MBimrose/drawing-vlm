#!/bin/bash
#SBATCH --job-name=tp-pipe
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --constraint=h200
#SBATCH --nodes=1
#SBATCH --cpus-per-task=96
#SBATCH --gres=gpu:H200:8
#SBATCH --mem=800G
#SBATCH --time=06:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/real/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/real/%x-%j.err
# Full serving pipeline on an external drawing bench: e55 (think, K=8) -> vote pick -> rp2 render-guided repair (K, ROUNDS).
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; B=${BENCH:-$DV/data_ext/test_part/bench}; O=${OUT:-$DV/data_ext/test_part/run}
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
S=/dev/shm/bimrose2/tp_$SLURM_JOB_ID; mkdir -p $S/tmp $S/cfg $S/home $O; trap 'pkill -f "vllm serv[e]"; rm -rf $S' EXIT
rsync -a --copy-links $DV/.venv/ $S/venv/ & rsync -a --copy-links $DV/dw_venv/ $S/dw_venv/ & rsync -a $DV/mech_step_to_drw/ $S/step_to_drw/ & cp $DV/containers/vllm-dsv41.from-serv20.sif $S/vllm.sif & wait
export APPTAINERENV_VLLM_ENGINE_READY_TIMEOUT_S=1800
serve() {  # model name gpus port
  CUDA_VISIBLE_DEVICES=$3 APPTAINERENV_CUDA_VISIBLE_DEVICES=$3 APPTAINERENV_PYTHONNOUSERSITE=1 APPTAINERENV_VLLM_CONFIG_ROOT=$S/cfg APPTAINERENV_XDG_CACHE_HOME=$S/home/.cache \
  apptainer exec --nv --home $S/home --bind $DV:$DV --bind /dev/shm:/dev/shm --bind $S/tmp:/tmp $S/vllm.sif \
    vllm serve $1 --served-model-name $2 --host 127.0.0.1 --port $4 --data-parallel-size 4 --tensor-parallel-size 1 --reasoning-parser qwen3 \
    --gpu-memory-utilization 0.90 --max-model-len 16384 --max-num-seqs 32 --limit-mm-per-prompt '{"image": 2}' --trust-remote-code > $O/vllm-$2.log 2>&1 &
}
serve $DV/runs/e55-rft-real-u5-gt-dw423/final e55 0,1,2,3 8100
serve $DV/runs/rp2-delta-e55/final rp2 4,5,6,7 8101
for p in 8100 8101; do for i in $(seq 1 300); do curl -s -m 5 http://127.0.0.1:$p/health >/dev/null && break; sleep 15; done; done
echo "servers up $(date)"
PY=$S/venv/bin/python; G=$DV/train_v14/geom
$PY $G/gen_openai_bo.py --bench $B --base-url http://127.0.0.1:8100/v1 --model e55 --k 8 --temperature 0.7 --nshards 1 --shard 0 --workers 8 --out $O/e55
$PY $G/tp_pick.py "$O/e55.shard*.json.partial.json" $O/picks.json
$PY $G/vr_serve.py --bench $B --picks $O/picks.json --base-url http://127.0.0.1:8101/v1 --model rp2 --k ${K:-16} --rounds ${ROUNDS:-5} --margin 0.1 --workers 8 \
  --out $O/repair.jsonl --py $PY --rpy $S/dw_venv/bin/python --script-dir $S/step_to_drw
$PY $G/tp_report.py $O/repair.jsonl $B/gt_meshes_v15/ref.stl $O/final | tee $O/report.txt
echo "TP DONE $(date)"
