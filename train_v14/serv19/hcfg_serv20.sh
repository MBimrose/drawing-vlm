# dsgrpo3 host config: serv-20 GPUs 0,1,2,7 (freed for DeepSeek 2026-10-07; GPUs 0-1 carry ~18 GB of someone else's).
# NEVER 3,4,5,6 (Qwen eval daemon + best Qwen RL arms). SIF = the serv-19/hub image (vllm-dsv41.sif differs).
export GPUS=0,1,2,7 PORT=8500 BUSY_MIB=30000
export SIF=/scratch/bimrose2/containers/dsv41-flash-v0909.sif
export BASE=/scratch/bimrose2/models/DeepSeek-V4.1-Flash
export APPTAINER_TMPDIR=/scratch/bimrose2/tmp/apptainer_grpo3; mkdir -p $APPTAINER_TMPDIR
