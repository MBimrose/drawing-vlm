#!/usr/bin/env bash
# Detached (login node): wait until serv-04's GPUs are free (other users share the box) and the
# native vLLM venv exists, then run the split evaluation chain for <run>.
RUN=${1:?run}; DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; S04=wpk-serv-04.mechse.illinois.edu
until timeout 30 ssh -o BatchMode=yes $S04 "grep -q 'VLLM VENV DONE' /srv/scratch/bimrose2/logs/build_vllm_venv.log 2>/dev/null"; do sleep 300; done
echo "$(date) vllm venv: $(timeout 30 ssh -o BatchMode=yes $S04 "grep -E 'vllm |True|False' /srv/scratch/bimrose2/logs/build_vllm_venv.log | tr '\n' ' '")"
until timeout 30 ssh -o BatchMode=yes $S04 "[ \$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | sort -n | tail -1) -lt 5000 ]"; do sleep 600; done
echo "$(date) serv-04 GPUs free; running the split eval chain for $RUN"
bash $DV/train_v14/serv19/eval_run_split.sh $RUN 8
echo "$(date) CHAIN EXIT"
