"""Consolidate an FSDP2 SHARDED_STATE_DICT (DCP) checkpoint into a plain
bf16 HF directory. CPU-only, run as an isolated subprocess: doing DCP work
inside the inference process was observed to numerically corrupt later
generation (degenerate '!' floods at batch>=8 on L40S).

Usage: python consolidate_dcp.py <checkpoint_dir> <out_dir>
"""
import os
import sys

import torch

MODEL_BASE = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/models/Qwen3.8-27B"


def main():
    ckpt_dir, out_dir = sys.argv[1], sys.argv[2]
    base = sys.argv[3] if len(sys.argv) > 3 else MODEL_BASE
    dcp_dir = os.path.join(ckpt_dir, "pytorch_model_fsdp_0")
    tmp_pt = out_dir.rstrip("/") + ".tmp.pt"
    os.makedirs(os.path.dirname(tmp_pt), exist_ok=True)

    from torch.distributed.checkpoint.format_utils import dcp_to_torch_save
    print(f"[consolidate] {dcp_dir} -> {tmp_pt} (base={base})", flush=True)
    dcp_to_torch_save(dcp_dir, tmp_pt)

    from transformers import AutoConfig, AutoProcessor
    arch = (AutoConfig.from_pretrained(base).architectures or [""])[0]
    if arch.startswith("Qwen3_5"):
        from transformers import Qwen3_5ForConditionalGeneration as M
    elif "Moe" in arch:
        from transformers import Qwen3VLMoeForConditionalGeneration as M
    else:
        from transformers import Qwen3VLForConditionalGeneration as M
    print(f"[consolidate] building bf16 {M.__name__} on CPU", flush=True)
    model = M.from_pretrained(
        base, dtype=torch.bfloat16, low_cpu_mem_usage=True)
    state = torch.load(tmp_pt, map_location="cpu", mmap=True, weights_only=False)
    if "model" in state and isinstance(state["model"], dict):
        state = state["model"]
    missing, unexpected = model.load_state_dict(state, strict=False)
    print(f"[consolidate] applied: {len(missing)} missing, {len(unexpected)} unexpected",
          flush=True)
    if len(missing) > 50:
        sys.exit(3)
    del state
    os.unlink(tmp_pt)
    os.makedirs(out_dir, exist_ok=True)
    model.save_pretrained(out_dir, safe_serialization=True)
    AutoProcessor.from_pretrained(base).save_pretrained(out_dir)
    print(f"[consolidate] saved -> {out_dir}", flush=True)


if __name__ == "__main__":
    main()
