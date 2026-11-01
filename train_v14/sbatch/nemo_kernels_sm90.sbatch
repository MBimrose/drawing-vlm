#!/bin/bash
#SBATCH --job-name=nemo-sm90
#SBATCH --account=wpk
#SBATCH --partition=wpk
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=48
#SBATCH --mem=80G
#SBATCH --time=04:00:00
#SBATCH --output=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/logs/%x-%j.out
# Rebuild causal_conv1d / mamba_ssm in the MIRROR .venv_nemo with sm_90 added (2026-10-28): serv-19's build targets
# sm_100/103 only ("no kernel image is available" on the H200 nodes). Sources = serv-19 nemo_build, setup.py + Hopper.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; R=/srv/scratch/bimrose2
bash $DV/train_v14/sbatch/srv_exec.sh "export CUDA_HOME=/software/cuda-13.0 PATH=/software/cuda-13.0/bin:\$PATH MAX_JOBS=40 \
  CAUSAL_CONV1D_FORCE_BUILD=TRUE MAMBA_FORCE_BUILD=TRUE UV_CACHE_DIR=/tmp/bimrose2_uvc; cd $R/nemo_build; \
  for p in causal_conv1d-1.7.0 mamba_ssm-2.3.2.post1; do $R/tmp/uv pip install --python $R/.venv_nemo/bin/python \
    --no-build-isolation --no-deps --reinstall ./\$p || exit 1; done; \
  for f in $R/.venv_nemo/lib/python3.12/site-packages/{causal_conv1d_cuda,selective_scan_cuda}*.so; do \
    echo \$f \$(/software/cuda-13.0/bin/cuobjdump --list-elf \$f | grep -oE 'sm_[0-9]+' | sort -u | tr '\n' ' '); done"
echo "exit $?"
