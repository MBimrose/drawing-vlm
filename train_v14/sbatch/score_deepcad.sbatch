#!/bin/bash
#SBATCH --job-name=score-deepcad
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=120
#SBATCH --exclusive
#SBATCH --mem=400G
#SBATCH --time=24:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/deepcad/%x-%j.out
#SBATCH --error=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/deepcad/%x-%j.err
# CPU-only: execute + score one slice of the DeepCAD full-pass partials (generated on serv-20 by
# e55 on vLLM, K=8). The slice is a glob over shard files so two jobs can run side by side and
# their outputs are merged by merge_scored.py before write_rft_real.
#   sbatch --export=ALL,SHARDS='shard[0-3]',OUT=bo8_full_e55_vllm.a[,WORKERS=120] score_deepcad.sbatch
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
source $DV/train_v14/env.sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
# Every candidate runs in a fresh interpreter that imports OCP/build123d; from the Lustre venv with
# 120 workers that is import-bound (2.6 candidates/s). Stage the venv into node RAM first.
LV=/dev/shm/bimrose2/venv; mkdir -p /dev/shm/bimrose2
T0=$(date +%s); rsync -a --copy-links $DV/.venv/ $LV/ && echo "venv staged to $LV in $(( $(date +%s)-T0 )) s ($(du -sh $LV | cut -f1))"
PY=$LV/bin/python; $PY -c "import build123d, OCP" 2>/dev/null && echo "local venv ok" || { echo "local venv failed; falling back to Lustre"; PY=$DV/.venv/bin/python; }
trap 'rm -rf /dev/shm/bimrose2' EXIT
C=$DV/deepcad/corpus_full; R=$C/results_vllm
echo "$(date) slice $SHARDS -> $OUT on $(hostname), ${WORKERS:-120} workers"
$PY $DV/train_v14/geom/score_partials.py \
  --partials "$R/bo8_full_e55_vllm.${SHARDS}.json.partial.json" \
  --gt-dir $C/gt_meshes_v15 --out $R/$OUT.json \
  --workers ${WORKERS:-120} --exec-timeout ${EXEC_TIMEOUT:-60} --iou-timeout ${IOU_TIMEOUT:-90}
echo "SCORE SLICE DONE $OUT $(date)"
