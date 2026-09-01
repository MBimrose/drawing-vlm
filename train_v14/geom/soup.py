"""Uniform weight averaging ("model soup") of N consolidated HF checkpoints
that share one safetensors layout (same recipe, different seeds).

    python soup.py <out_dir> <ckpt_dir_1> <ckpt_dir_2> [...]

Tensor-by-tensor so peak RAM is one output shard (~50 GB for the 27B fp32
finals), not the whole model. Non-weight files (config, tokenizer, chat
template, processor) are copied from the first input.
"""
import json
import os
import shutil
import sys

import torch
from safetensors import safe_open
from safetensors.torch import save_file

out, srcs = sys.argv[1], sys.argv[2:]
assert len(srcs) >= 2, "need at least two checkpoints"
idx = [json.load(open(os.path.join(s, "model.safetensors.index.json"))) for s in srcs]
wm = idx[0]["weight_map"]
for i, other in enumerate(idx[1:], 1):
    assert other["weight_map"] == wm, f"{srcs[i]} has a different shard layout"
os.makedirs(out, exist_ok=True)
for f in os.listdir(srcs[0]):
    if not f.endswith(".safetensors"):
        shutil.copy2(os.path.join(srcs[0], f), os.path.join(out, f))

shards = sorted(set(wm.values()))
n_tensors = 0
for sh in shards:
    names = [k for k, v in wm.items() if v == sh]
    handles = [safe_open(os.path.join(s, sh), framework="pt", device="cpu") for s in srcs]
    merged = {}
    for k in names:
        ts = [h.get_tensor(k) for h in handles]
        acc = ts[0].to(torch.float32).clone()
        for t in ts[1:]:
            acc += t.to(torch.float32)
        acc /= len(ts)
        merged[k] = acc.to(ts[0].dtype).contiguous()
    save_file(merged, os.path.join(out, sh), metadata={"format": "pt"})
    n_tensors += len(merged)
    print(f"[soup] {sh}: {len(merged)} tensors averaged over {len(srcs)} models", flush=True)
    del merged, handles
print(f"[soup] done: {n_tensors} tensors -> {out}", flush=True)
