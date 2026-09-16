#!/usr/bin/env bash
# Build the DeepSeek-V4.1 spike venv on /projects (run on the login node: it needs the network).
# Same stack as serv-20's .venv_dsv41: torch 2.13 + torchvision from the cu130 index (a PyPI
# torchvision silently downgrades torch to 2.9 / Triton 3.5), transformers PR #48768, peft,
# kernels 0.16 for the Hub finegrained-fp8 matmul (prefetched into HF_HOME here, compute nodes
# may have no outbound network).
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV
export UV_CACHE_DIR=$DV/.uv_cache HF_HOME=$DV/.cache/huggingface; mkdir -p $UV_CACHE_DIR $HF_HOME
UV=/home/bimrose2/.local/bin/uv; VP=$DV/.venv_dsv41/bin/python
[ -x $VP ] || UV_PYTHON=/home/bimrose2/.local/bin/python3.12 $UV venv .venv_dsv41 --python 3.12
unset UV_PYTHON
$UV pip install --python $VP --quiet "torch==2.13.0" torchvision --index-url https://download.pytorch.org/whl/cu130 || echo "torch install rc=$?"
$UV pip install --python $VP --quiet "git+https://github.com/huggingface/transformers.git@refs/pull/48768/head" peft accelerate safetensors pillow tiktoken "kernels==0.16.0" trimesh numpy || echo "deps install rc=$?"
$VP - <<'PY'
import torch, triton, transformers, peft, kernels
print("torch", torch.__version__, "triton", triton.__version__, "transformers", transformers.__version__, "peft", peft.__version__, "kernels", kernels.__version__)
from transformers.models.deepseek_v41.image_processing_deepseek_v41 import DeepseekV41ImageProcessor
print("deepseek_v41 classes present")
from transformers.integrations.finegrained_fp8 import load_finegrained_fp8_kernel
k = load_finegrained_fp8_kernel(); print("hub kernel prefetched:", [n for n in ("matmul", "batched_matmul", "grouped_matmul") if getattr(k, n, None)])
PY
echo "VENV DONE $(date)"
