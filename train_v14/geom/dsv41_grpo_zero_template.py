"""Attention-only adapter template for the round-0 control merge (merge_dsv41_lora.py --bf16 --delta-scale 0): copies a
trained adapter's attention LoRA tensors (drops shared-expert keys). Only the key set and r/alpha matter at scale 0.
    python dsv41_grpo_zero_template.py <src adapter> <out dir>"""
import json, os, shutil, sys
from safetensors.torch import load_file, save_file
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
t = {k: v for k, v in load_file(os.path.join(src, "adapter_model.safetensors")).items() if "shared_experts" not in k}
save_file(t, os.path.join(out, "adapter_model.safetensors"))
shutil.copy(os.path.join(src, "adapter_config.json"), os.path.join(out, "adapter_config.json"))
print(len(t), "attention LoRA tensors ->", out)
