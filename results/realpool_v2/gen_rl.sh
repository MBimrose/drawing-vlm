#!/bin/bash
# Real-part pool v2 hard mining (2026-10-07): K=4 draws (draw 0 greedy, T=0.7 top_p 0.95 = grpo_eval recipe) from the
# best RL generator mix_t10 s120 (LoRA t10s120 on e55) over the e55-hard DeepCAD candidates
# (train_v14/mech/benchmarks/data/rft_realpool_v2/mine). Runs as an overlap step inside a grpo-fast job
# (sbatch --export=ALL,HOSTJOB=<job>,CMD_FILE=<this> grpo_overlap_cmd.sbatch). Env: PORTS="8500 8501" (servers to use),
# NSH (total shards), SH0 (first shard index this host runs). Resumable per key.
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV; source train_v14/env.sh
export OMP_NUM_THREADS=2 PYTHONPATH=$DV/train_v14:$DV/train_v14/geom
PY=$(ls -d /dev/shm/bimrose2/gf_${HOSTJOB}/venv/bin/python 2>/dev/null || echo $DV/.venv/bin/python)
PORTS=${PORTS:-"8500 8501"}; NSH=${NSH:-8}; SH0=${SH0:-0}; PER=${PER:-4}; W=${W:-24}
B=train_v14/mech/benchmarks/data/rft_realpool_v2/mine; O=results/realpool_v2
hostname; nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader
for p in $PORTS; do
  curl -s -X POST http://127.0.0.1:$p/v1/load_lora_adapter -H "Content-Type: application/json" \
    -d "{\"lora_name\": \"t10s120\", \"lora_path\": \"$DV/runs/grpo_v_mix_t10/adapter_step120\"}"; echo " lora on :$p"
done
sh=$SH0; PIDS=()
for p in $PORTS; do
  for j in $(seq 1 $PER); do
    $PY train_v14/geom/gen_openai_bo.py --bench $B --keys $B/../mine_keys_e55hard.txt --base-url http://127.0.0.1:$p/v1 \
      --model t10s120 --k 4 --temperature 0.7 --workers $W --shard $sh --nshards $NSH --out $O/bo4_t10s120 \
      > $O/gen_shard$sh.log 2>&1 &
    PIDS+=($!); sh=$((sh + 1))
  done
done
wait "${PIDS[@]}"
echo "GEN RL DONE $(date)"
