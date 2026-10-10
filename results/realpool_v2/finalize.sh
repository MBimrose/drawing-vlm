#!/bin/bash
# Real-part pool v2 finalize (run on ccc0442 via cpu_run.sh): hard rule on the RL K=4 scores -> keys + stats + e55 K=8
# baseline subset; pack the hard keys into the GRPO bench dir rft_realpool_v2 (eval_cache_v15.pkl + gt_meshes_v15).
set -euo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV
D=train_v14/mech/benchmarks/data/rft_realpool_v2; O=results/realpool_v2; PY=$DV/.venv/bin/python
$PY train_v14/mech/benchmarks/build_realpool_v2.py mine --select $D/select_e55.json \
  --scored "$O/bo4_t10s120_?.json.scored.jsonl" --partials "$O/bo4_t10s120.shard?.json.partial.json" --keys $D/mine_keys_e55hard.txt \
  --out $D/realpool2_hard_keys.txt --e55-out results/h6c/bo8_realpool2_e55.json
cp $D/realpool2_hard_keys.txt results/h6c/realpool2_hard_keys.txt
cp $D/realpool2_hard_keys_stats.json results/h6c/realpool2_hard_keys_stats.json
$PY train_v14/mech/benchmarks/build_realpool_v2.py pack --src $D/mine --out $D --keys $D/realpool2_hard_keys.txt
echo "FINALIZE DONE $(date)"
