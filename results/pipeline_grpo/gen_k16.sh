#!/bin/bash
# Full pipeline on the GRPO generator (2026-10-08), stage 1: K=16 real-bench draws from e55 + ent_t10 step-120 LoRA
# (draw 0 greedy, T 0.7 / top_p 0.95, max 2400 tokens, think kept = the grpo_eval / selection-study recipe).
# Runs as an overlap step inside grpo-fast job 11213000 on ccc0451, H200 GPU 6 only, own vLLM on :8530.
# The server is killed by its process-group id at the end (no pkill patterns).
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV; source train_v14/env.sh
export OMP_NUM_THREADS=2 PYTHONPATH=$DV/train_v14:$DV/train_v14/geom
HS=/dev/shm/bimrose2/gf_11213000; S=/dev/shm/bimrose2/pg_gen_$$; mkdir -p $S/tmp $S/cfg $S/home
PY=$HS/venv/bin/python; [ -x $PY ] || PY=$DV/.venv/bin/python
E55=$DV/runs/e55-rft-real-u5-gt-dw423/final; AD=$DV/runs/grpo_v_ent_t10/adapter_step120
O=$DV/results/pipeline_grpo; L=$O/logs; PORT=8530
echo "$(date) start on $(hostname)"
CUDA_VISIBLE_DEVICES=6 APPTAINERENV_CUDA_VISIBLE_DEVICES=6 APPTAINERENV_VLLM_ENGINE_READY_TIMEOUT_S=3600 \
  APPTAINERENV_PYTHONNOUSERSITE=1 APPTAINERENV_VLLM_CONFIG_ROOT=$S/cfg APPTAINERENV_XDG_CACHE_HOME=$S/home/.cache \
  setsid apptainer exec --nv --cleanenv --home $S/home --bind $DV:$DV --bind /dev/shm:/dev/shm --bind $S/tmp:/tmp $HS/vllm.sif \
  vllm serve $E55 --served-model-name e55 --host 127.0.0.1 --port $PORT --reasoning-parser qwen3 \
    --gpu-memory-utilization 0.78 --max-model-len 16384 --max-num-seqs 256 --limit-mm-per-prompt '{"image": 1}' \
    --trust-remote-code --enable-lora --max-lora-rank 64 --max-loras 1 --lora-modules ent_t10s120=$AD \
    > $L/vllm_gen.log 2>&1 < /dev/null &
VPID=$!
ok=0; for i in $(seq 1 240); do curl -s -m 5 http://127.0.0.1:$PORT/health >/dev/null && { ok=1; break; }; sleep 15; done
[ $ok = 1 ] || { echo "vLLM never ready"; tail -30 $L/vllm_gen.log; kill -- -$VPID; exit 1; }
curl -s http://127.0.0.1:$PORT/v1/models | head -c 400; echo
echo "$(date) vLLM up"
$PY train_v14/geom/gen_openai_bo.py --bench train_v14/mech/benchmarks/data/ext_bench_dw423_perm --base-url http://127.0.0.1:$PORT/v1 \
  --model ent_t10s120 --k 16 --temperature 0.7 --workers 16 --out $O/real_k16_ent_t10s120 > $L/gen_k16.log 2>&1
echo "$(date) gen exit $?"
kill -- -$VPID 2>/dev/null; sleep 15; kill -9 -- -$VPID 2>/dev/null; rm -rf $S
echo "GEN K16 DONE $(date)"
