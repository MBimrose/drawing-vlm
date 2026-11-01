#!/bin/bash
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodelist=ccc0442
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --job-name=dsstats
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/dataset_stats/logs/run_all_%j.log
# Dataset statistics: static pass (collect.py) -> exec/STEP B-rep pass (run_exec.py) -> tables.
set -euo pipefail
D=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/dataset_stats
PY=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/.venv/bin/python
cd $D/scripts
STAGE=${STAGE:-all}
if [ "$STAGE" = all ] || [ "$STAGE" = collect ]; then
  $PY collect.py
fi
if [ "$STAGE" = all ] || [ "$STAGE" = exec ]; then
  $PY run_exec.py $D/out/exec_tasks.jsonl $D/out/exec_results.jsonl --workers 16 --timeout 60
fi
if [ "$STAGE" = all ] || [ "$STAGE" = summarize ]; then
  $PY summarize.py
fi
