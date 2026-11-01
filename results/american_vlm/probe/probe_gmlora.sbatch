#!/bin/bash
#SBATCH --job-name=probe-gmlora
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --gres=gpu:1
#SBATCH --mem=200G
#SBATCH --time=2:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/american_vlm/probe/%x-%j.out
# 2026-10-28: why the Gemma LoRA row (base gemma-4-31B-it + am-gemma4-lora-e55recipe/final) gave empty replies: the
# am_eval_cluster.sbatch server (gmftpf template, gemma4 parser) on 1 H200, raw replies for 3 real parts, base vs LoRA.
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; SX=$DV/train_v14/sbatch/srv_exec.sh; R=/srv/scratch/bimrose2
P=$DV/results/american_vlm/probe; RP=${RP:-gemma4}
export LOCAL_TMP=/tmp/bimrose2_srv_$SLURM_JOB_ID APPTAINERENV_VLLM_ALLOW_RUNTIME_LORA_UPDATING=True
export APPTAINERENV_CUDA_HOME=/software/cuda-13.0 APPTAINERENV_PREPEND_PATH=/software/cuda-13.0/bin
setsid bash $SX "vllm serve $R/models/gemma-4-31B-it --served-model-name base --host 127.0.0.1 --port 8990 \
  --tensor-parallel-size 1 --trust-remote-code ${RP:+--reasoning-parser $RP} --gpu-memory-utilization 0.85 --max-model-len 16384 \
  --max-num-seqs 32 --limit-mm-per-prompt '{\"image\": 1, \"video\": 0}' --enable-lora --max-lora-rank 64 --max-loras 1 \
  --lora-modules gmlora=$R/amvlm/runs/am-gemma4-lora-e55recipe/final \
  --chat-template $R/american_vlm/templates/gmftpf.jinja --mm-processor-kwargs {\\\"max_soft_tokens\\\":1120}" > $P/vllm-$SLURM_JOB_ID.log 2>&1 < /dev/null &
SP=$!; trap "kill -- -$SP 2>/dev/null" EXIT
for t in $(seq 1 240); do curl -s -m 5 http://127.0.0.1:8990/health >/dev/null && break; sleep 15; done
echo "$(date) up"; grep -iE "lora" $P/vllm-$SLURM_JOB_ID.log | grep -v -E "GET|POST" | tail -5
bash $SX "cd $R; .venv/bin/python $P/probe_raw.py http://127.0.0.1:8990/v1 gmlora,base 3"
