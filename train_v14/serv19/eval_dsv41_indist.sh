#!/usr/bin/env bash
# Score the DeepSeek-V4.1-Flash LoRA on the SAME in-distribution pool the Qwen runs use, so the
# base-model table compares like with like (it has only ever been scored on the 146 real parts).
# Greedy, 96 parts of the certified pool; generations are dumped and scored on the cluster CPUs.
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; S04=wpk-serv-04.mechse.illinois.edu; SDV=/srv/scratch/bimrose2
ADAPTER=${1:-spike_dsv41/lora_u5_r32_s600}; N=${2:-96}
until timeout 30 ssh -o BatchMode=yes $S04 "! pgrep -f 'vllm serv[e]|dsv41_lora_trai[n]' >/dev/null && [ \$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | sort -n | tail -1) -lt 5000 ]"; do sleep 600; done
echo "$(date) serv-04 free; scoring $ADAPTER on the in-distribution pool"
timeout 120 ssh -o BatchMode=yes $S04 "cd $SDV; : > logs/dsv41_indist.log; setsid nohup bash -c \"cd $SDV && HF_HOME=$SDV/.cache/huggingface CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 PYTHONPATH=train_v14:train_v14/geom OPENBLAS_NUM_THREADS=1 .venv_dsv41/bin/python train_v14/geom/dsv41_lora_train.py --model models/DeepSeek-V4.1-Flash --tier rft_real_union5_dw423/shards --prompts spike_dsv41/prompts.json --steps 0 --adapter $ADAPTER --out $ADAPTER --eval-bench mech_benchmarks/fullpool_dw423 --eval-n $N --eval-max-new 3000; echo INDIST EXIT \\\$?\" >> logs/dsv41_indist.log 2>&1 < /dev/null & sleep 2; echo launched"
until timeout 30 ssh -o BatchMode=yes $S04 "grep -q 'INDIST EXIT' $SDV/logs/dsv41_indist.log 2>/dev/null"; do sleep 300; done
echo "$(date) generation done"
mkdir -p $DV/runs/dsv41_indist
rsync -a "$S04:$SDV/$ADAPTER/eval_gen.rank0.jsonl" $DV/runs/dsv41_indist/ || { echo "no generations"; exit 1; }
source $DV/.venv/bin/activate; source $DV/train_v14/env.sh
python $DV/train_v14/geom/dsv41_eval_score.py --gens $DV/runs/dsv41_indist/eval_gen.rank0.jsonl \
  --bench $DV/train_v14/mech/benchmarks/data/fullpool_dw423 --out $DV/runs/dsv41_indist/eval.json --workers 8
echo "$(date) DSV41 INDIST DONE"
