#!/bin/bash
# Zero-shot gates for the American open-weight VLM screen (2026-10-26, results/american_vlm/README.md), serv-19.
# Main protocol (eval_nemo.sh: K=8, draw 0 greedy + 7 at T 0.7 / top_p 0.95, think mode, 2400 tokens, the e55
# system/user prompt) on real-144 / synthetic 1,027 / bench B for each base model, one TP2 vLLM server each:
#   Muse-Glimmer-30B (Meta)                   GPUs 0,1 :8901  reasoning parser muse_glimmer
#   gemma-4-31B-it (Google)                    GPUs 2,3 :8902  gemma4, max_soft_tokens 1120 (native-resolution sheets)
#   NVIDIA-Nemotron-3.5-Bolt-74B-A9B-BF16     GPUs 4,5 :8903  nemotron_v3 (Nemotron script, MTP off)
# Generations go to american_vlm/results/<bench>_<name>.json (+ .GEN_DONE); scoring runs on ccc0442 (nemo_score.sbatch).
#   setsid nohup bash train_v14/serv19/zs_american_gates.sh > american_vlm/logs/zs_gates.log 2>&1 < /dev/null &
set -uo pipefail
cd /srv/scratch/bimrose2
say() { echo "$(date '+%m-%d %H:%M') $*"; }
O=american_vlm; mkdir -p $O/results $O/logs
M=/srv/scratch/bimrose2/models
MODEL=$M/Muse-Glimmer-30B NAME=glimmer_zs GPUS=0,1 TP=2 PORT=8901 RPARSER=muse_glimmer SEQS=128 GMU=0.85 \
  setsid nohup bash train_v14/serv19/run_vllm_any_serv19.sh > $O/logs/vllm_glimmer_zs.log 2>&1 < /dev/null &
echo $! > $O/vllm_8901.pgid
MODEL=$M/gemma-4-31B-it NAME=gemma4_31b_zs GPUS=2,3 TP=2 PORT=8902 RPARSER=gemma4 SEQS=128 GMU=0.85 \
  VLLM_EXTRA="--mm-processor-kwargs {\"max_soft_tokens\":1120}" \
  setsid nohup bash train_v14/serv19/run_vllm_any_serv19.sh > $O/logs/vllm_gemma4_31b_zs.log 2>&1 < /dev/null &
echo $! > $O/vllm_8902.pgid
MODEL=$M/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-BF16 NAME=bolt_zs GPUS=4,5 TP=2 PORT=8903 MTP=0 SEQS=64 GMU=0.85 MLEN=16384 \
  setsid nohup bash train_v14/serv19/run_vllm_nemotron_serv19.sh > $O/logs/vllm_bolt_zs.log 2>&1 < /dev/null &
echo $! > $O/vllm_8903.pgid
run() {  # name port
  for i in $(seq 1 240); do curl -s -m 5 http://127.0.0.1:$2/health > /dev/null && break; sleep 15; done
  curl -s -m 5 http://127.0.0.1:$2/health > /dev/null || { say "$1 server never ready: $(tail -3 $O/logs/vllm_$1.log)"; return 1; }
  say "$1 up on :$2"
  NAME=$1 PORT=$2 MTOK=2400 WORKERS=12 OUT=$O/results BENCHES="real full benchb" bash nemotron/eval_nemo.sh > $O/logs/eval_$1.log 2>&1
  say "$1 eval: $(tail -1 $O/logs/eval_$1.log)"
  kill -TERM -- -$(cat $O/vllm_$2.pgid) 2>/dev/null
}
run glimmer_zs 8901 & run gemma4_31b_zs 8902 & run bolt_zs 8903 & wait
say "ZS GATES DONE"
