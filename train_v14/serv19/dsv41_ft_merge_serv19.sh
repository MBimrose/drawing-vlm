#!/usr/bin/env bash
# Merge a DeepSeek-V4.1-Flash LoRA adapter into the FP8 base ON serv-19 (local NVMe base, inside the vLLM image's torch).
#   bash dsv41_ft_merge_serv19.sh <cluster adapter dir> <name>     -> serv-19 /scratch/bimrose2/dsv41_ft/<name>
set -euo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; S19=wpk-serv-19.mechse.illinois.edu; AD=$1; NAME=$2
R=/scratch/bimrose2/dsv41_ft; BASE=$(ssh $S19 "ls -d /scratch/bimrose2/dsv41_flash/models/models--deepseek-ai--DeepSeek-V4.1-Flash/snapshots/*/ | head -1")
ssh $S19 "mkdir -p $R/adapters/$NAME $R/code"
rsync -a $AD/adapter_config.json $AD/adapter_model.safetensors $S19:$R/adapters/$NAME/
rsync -a $DV/train_v14/geom/merge_dsv41_lora.py $S19:$R/code/
ssh $S19 "cd /scratch/bimrose2/dsv41_flash && apptainer exec --bind /scratch/bimrose2:/scratch/bimrose2 dsv41-flash-v0909.sif python3 $R/code/merge_dsv41_lora.py --base $BASE --adapter $R/adapters/$NAME --out $R/$NAME 2>&1 | tail -2"
