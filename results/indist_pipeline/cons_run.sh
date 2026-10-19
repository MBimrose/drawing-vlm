#!/bin/bash
# In-dist pipeline (2026-10-14): sharded consistency_rerank for full_k16_rl2s60 (see cons_shard.py), run inside the stage-2
# allocation (srun --overlap). Writes full_k16_rl2s60_consistency.json atomically when all shards are done.
set -uo pipefail
P=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/indist_pipeline; cd $P; N=${N:-12}
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
PY=/dev/shm/bimrose2/ipcode/venv/bin/python; CODE=/dev/shm/bimrose2/ipcode/train_v14
python3 cons_shard.py split full_k16_rl2s60.json cons_shards $N
PIDS=(); for i in $(seq 0 $((N - 1))); do
  $PY $CODE/geom/consistency_rerank.py cons_shards/shard_$i.json cons_shards/shard_${i}_consistency.json > cons_shards/shard_$i.log 2>&1 &
  PIDS+=($!); done
fail=0; for p in "${PIDS[@]}"; do wait $p || fail=1; done
[ $fail = 0 ] || { echo "a shard failed"; exit 1; }
[ -f full_k16_rl2s60_consistency.json ] && { echo "consistency file already exists; merged copy -> cons_shards/merged_consistency.json"; python3 cons_shard.py merge full_k16_rl2s60.json cons_shards $N cons_shards/merged_consistency.json; exit 0; }
python3 cons_shard.py merge full_k16_rl2s60.json cons_shards $N full_k16_rl2s60_consistency.json
echo "CONS SHARDS DONE $(date)"
