#!/usr/bin/env bash
# Validate the vLLM generation path against the HF path on the DeepCAD gate corpus, on serv-20:
# serve e55 with vLLM (DP=8), draw K=8 for the 616 gate parts through gen_openai_bo.py, execute
# and score with score_partials.py, and print the same first-exec / ceiling numbers as the HF
# run (results/ext/bo8_deepcad_e55: first-exec 0.713, ceiling 0.808 on the cluster). If the two
# agree within noise the vLLM path is on-policy-equivalent and the 110k-part pass can use it.
#   nohup ./run_vllm_gate_check.sh > logs/vllm_gate_check.log 2>&1 &
set -uo pipefail
DV=/srv/scratch/bimrose2; C=$DV/deepcad/corpus_gate; G=$DV/train_v14/geom
[ -f $C/eval_cache_v15.pkl ] || { echo "no gate cache at $C"; exit 1; }
cd $DV
setsid nohup bash $DV/train_v14/serv19/run_vllm_e55_serv20.sh > $DV/logs/vllm-e55.log 2>&1 < /dev/null &
for i in $(seq 1 180); do
  curl -s -m 5 http://127.0.0.1:8100/health >/dev/null 2>&1 && { echo "$(date) e55 vllm ready after $((i*10)) s"; break; }
  pgrep -f "vllm serve.*served-model-name e5[5]" >/dev/null || { echo "e55 vllm died"; tail -30 $DV/logs/vllm-e55.log; exit 1; }
  sleep 10
done
curl -s -m 5 http://127.0.0.1:8100/health >/dev/null || { echo "e55 vllm never ready"; tail -30 $DV/logs/vllm-e55.log; exit 1; }
export OPENBLAS_NUM_THREADS=1
mkdir -p $C/results_vllm
T0=$(date +%s)
$DV/.venv/bin/python $G/gen_openai_bo.py --bench $C --base-url http://127.0.0.1:8100/v1 --model e55 --k 8 \
  --workers 48 --out $C/results_vllm/bo8_gate_e55_vllm 2>&1 | tail -3
echo "generation wall: $(( $(date +%s) - T0 )) s for $(python3 -c "import json;print(len(json.load(open('$C/results_vllm/bo8_gate_e55_vllm.shard0.json.partial.json'))['keys']))") parts x 8"
EXEC_HARNESS=$G/exec_harness.py $DV/.venv/bin/python $G/score_partials.py \
  --partials "$C/results_vllm/bo8_gate_e55_vllm.shard*.json.partial.json" --gt-dir $C/gt_meshes_v15 \
  --out $C/results_vllm/bo8_gate_e55_vllm.json --workers 48 2>&1 | tail -2
$DV/.venv/bin/python - <<'PY'
import json, statistics as st
d=json.load(open("/srv/scratch/bimrose2/deepcad/corpus_gate/results_vllm/bo8_gate_e55_vllm.json"))["candidates"]
ceil=[max([c["iou"] for c in p["cands"] if c.get("exec")] or [0]) for p in d]
first=[next((c["iou"] for c in sorted(p["cands"],key=lambda c:c["draw"]) if c.get("exec")),0.0) for p in d]
ex=sum(1 for p in d for c in p["cands"] if c.get("exec")); tot=sum(len(p["cands"]) for p in d)
th=sum(1 for p in d for c in p["cands"] if (c.get("think") or "").strip())
print(f"vLLM path, gate {len(d)} parts: first-exec {st.mean(first):.3f} | ceiling {st.mean(ceil):.3f} | >=0.85 {sum(x>=0.85 for x in ceil)/len(d):.0%} | exec {ex}/{tot} | with think {th}/{tot}")
print( "HF path (cluster, job 10571393): first-exec 0.713 | ceiling 0.808 | >=0.85 59%")
PY
echo "GATE CHECK DONE"
