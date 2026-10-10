#!/bin/bash
# Real-part pool v2: score the RL K=4 partials as they appear (score_partials.py is resumable via <out>.scored.jsonl;
# exec 60 s / IoU 90 s subprocess timeouts = eval rule). Runs as an overlap step inside a grpo-fast job whose CPUs are
# idle (sbatch --export=ALL,HOSTJOB=<job>,CMD_FILE=<this>,SHARDS='[0-7]',TAG=a,WORKERS=48 grpo_overlap_cmd.sbatch).
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV; source train_v14/env.sh
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=$DV/train_v14:$DV/train_v14/geom
PY=$(ls -d /dev/shm/bimrose2/gf_${HOSTJOB}/venv/bin/python 2>/dev/null || echo $DV/.venv/bin/python)
$PY -c "import build123d, OCP" || PY=$DV/.venv/bin/python
O=results/realpool_v2; GT=train_v14/mech/benchmarks/data/rft_realpool_v2/mine/gt_meshes_v15
SHARDS=${SHARDS:-[0-7]}; TAG=${TAG:-a}; WORKERS=${WORKERS:-48}
hostname; uptime
while true; do
  ndone=$(grep -l "DONE shard" $O/gen_shard*.log 2>/dev/null | wc -l)
  $PY train_v14/geom/score_partials.py --partials "$O/bo4_t10s120.shard${SHARDS}.json.partial.json" --gt-dir $GT \
    --out $O/bo4_t10s120_$TAG.json --workers $WORKERS --exec-timeout 60 --iou-timeout 90 >> $O/score_$TAG.log 2>&1
  [ "$ndone" -ge 8 ] && break
  sleep 300
done
echo "SCORE LOOP DONE $(date)" >> $O/score_$TAG.log
