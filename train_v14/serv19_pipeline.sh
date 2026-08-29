#!/usr/bin/env bash
# wpk-serv-19 (no SLURM) pipeline for the Flash-Next full FT:
#   wait for e26-full-serv19 -> geometric eval -> RFT-4 generation with the
#   trained model (4 workers x 2 B300, 4 candidates/part, every candidate
#   logged for the verifier) -> pack -> round-2 training (e32).
# Resumable: finished stages are recorded in runs/<RUN>/pipeline.state.
set -uo pipefail
DV=/srv/scratch/bimrose2
RUN=${RUN:-e26-full-serv19}
cd "$DV"
source train_v14/env.sh
source .venv/bin/activate
export DRAWING_VLM_RUNS=$DV/runs OPENBLAS_NUM_THREADS=1
STATE=$DV/runs/$RUN/pipeline.state
done_stage() { grep -qx "$1" "$STATE" 2>/dev/null; }
mark() { echo "$1" >> "$STATE"; echo "[pipeline $(date -Is)] stage $1 done"; }
echo "[pipeline $(date -Is)] start RUN=$RUN"

# 1. wait for training to finish
while pgrep -f "train_sft_v1[4].py" >/dev/null; do sleep 300; done
[ -f "runs/$RUN/final/model.safetensors.index.json" ] || { echo "[pipeline] no final model for $RUN"; exit 1; }

# 2. geometric eval of best_model + final (8 GPUs, Qwen4Exp path)
done_stage eval || { python train_v14/geom/geom_eval_worker.py --runs "$RUN" --n 96 --batch 8 && mark eval; }

# 3. pick the generator (higher repair IoU of final vs best_model)
CK=$(python - "$RUN" <<'PY'
import json, os, sys
run = sys.argv[1]; st = f"/srv/scratch/bimrose2/runs/{run}/geom_eval_state.json"
best, bk = -1, "final"
if os.path.exists(st):
    for k, m in json.load(open(st)).items():
        if m.get("final_iou_mean", -1) > best:
            best, bk = m["final_iou_mean"], k
print("best_model" if bk.startswith("best_model") else "final")
PY
)
echo "[pipeline] generator: runs/$RUN/$CK"

# 4. RFT-4 generation: 4 workers x 2 GPUs (336 GB model), 4 samples/part, log all
OUT=$DV/rft_v4
if ! done_stage gen; then
  for w in 0 1 2 3; do
    CUDA_VISIBLE_DEVICES=$((2*w)),$((2*w+1)) python train_v14/geom/rft_generate.py \
      --ckpt "runs/$RUN/$CK" --kind hf --run "$RUN" --worker $w --stride 4 --out "$OUT" \
      --batch 8 --n-samples 4 --log-all --min-iou 0.8 --temperature 0.7 \
      --max-accepted 60000 > "logs/rft4-w$w.log" 2>&1 &
  done
  wait
  mark gen
fi

# 5. pack
done_stage pack || { python train_v14/geom/pack_rft_shards.py "$OUT" && mark pack; }

# 6. round 2 training on RFT-4
done_stage train2 || {
  export DRAWING_VLM_RFT_SHARDS=$OUT/shards
  bash train_v14/run.sh train_v14/configs/e32-full-serv19-r2.yaml > logs/e32-full-serv19-r2.log 2>&1 && mark train2
}
# 7. eval round 2
done_stage eval2 || { python train_v14/geom/geom_eval_worker.py --runs e32-full-serv19-r2 --n 96 --batch 8 && mark eval2; }
echo "[pipeline $(date -Is)] ALL DONE"
