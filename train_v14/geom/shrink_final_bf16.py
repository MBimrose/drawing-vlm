"""Re-save a run's `final/` weights as bfloat16 — halving it with no change to how the model behaves.

Every checkpoint here is written as float32 (355 F32 tensors per shard, 109 GB per run) while its
own config declares `torch_dtype: bfloat16`, and every consumer loads bf16: `train_sft_v14.py`
passes `dtype=torch.bfloat16`, and vLLM serves at the config dtype. So the stored fp32 mantissa
is discarded at load time in every path we have; storing it costs ~51 GB per run for nothing.

Safety: the converted copy is written beside the original, verified tensor by tensor against the
bf16 cast of the source (exact equality, not a tolerance), and only then swapped in. The original
is moved to `final.fp32_old` and removed after the swap, so a failure at any point leaves the
run untouched.

    python shrink_final_bf16.py --run runs/e51-... [--keep-old] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import time

import torch
from safetensors import safe_open
from safetensors.torch import save_file


def convert_shard(src: str, dst: str) -> tuple[int, int, int]:
    """Cast one shard to bf16; returns (tensors, src_bytes, dst_bytes)."""
    out = {}
    with safe_open(src, framework="pt", device="cpu") as f:
        meta = f.metadata() or {}
        for k in f.keys():
            t = f.get_tensor(k)
            out[k] = t.to(torch.bfloat16) if t.dtype == torch.float32 else t
    save_file(out, dst, metadata=meta)
    return len(out), os.path.getsize(src), os.path.getsize(dst)


def verify_shard(src: str, dst: str) -> None:
    with safe_open(src, framework="pt", device="cpu") as a, safe_open(dst, framework="pt", device="cpu") as b:
        ka, kb = set(a.keys()), set(b.keys())
        if ka != kb:
            raise RuntimeError(f"key mismatch in {os.path.basename(dst)}: {len(ka ^ kb)} differ")
        for k in ka:
            ta, tb = a.get_tensor(k), b.get_tensor(k)
            want = ta.to(torch.bfloat16) if ta.dtype == torch.float32 else ta
            if tb.dtype != want.dtype or tb.shape != want.shape or not torch.equal(tb, want):
                raise RuntimeError(f"tensor mismatch: {k}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, help="run dir containing final/")
    ap.add_argument("--keep-old", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    fin = os.path.join(a.run, "final")
    idx_path = os.path.join(fin, "model.safetensors.index.json")
    if not os.path.isdir(fin) or not os.path.exists(idx_path):
        print(f"[shrink] {a.run}: no final/ with a shard index; skipping"); return
    idx = json.load(open(idx_path))
    before = idx.get("metadata", {}).get("total_size", 0)
    shards = sorted(set(idx["weight_map"].values()))
    with safe_open(os.path.join(fin, shards[0]), framework="pt", device="cpu") as f:
        k0 = next(iter(f.keys()))
        if f.get_tensor(k0).dtype != torch.float32:
            print(f"[shrink] {a.run}: already {f.get_tensor(k0).dtype}; skipping"); return
    print(f"[shrink] {a.run}: {len(shards)} shards, {before/1e9:.0f} GB fp32", flush=True)
    if a.dry_run:
        print(f"[shrink] would write {before/2e9:.0f} GB bf16 (saves {before/2e9:.0f} GB)"); return

    tmp = os.path.join(a.run, "final.bf16")
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    os.makedirs(tmp)
    t0 = time.time(); new_total = 0
    for s in shards:
        n, sb, db = convert_shard(os.path.join(fin, s), os.path.join(tmp, s))
        verify_shard(os.path.join(fin, s), os.path.join(tmp, s))
        new_total += db
        print(f"[shrink]   {s}: {n} tensors, {sb/1e9:.0f} -> {db/1e9:.0f} GB, verified "
              f"({time.time()-t0:.0f}s)", flush=True)
    for f in os.listdir(fin):                       # config, tokenizer, templates
        if not f.endswith(".safetensors"):
            shutil.copy2(os.path.join(fin, f), os.path.join(tmp, f))
    idx["metadata"]["total_size"] = sum(os.path.getsize(os.path.join(tmp, s)) for s in shards)
    json.dump(idx, open(os.path.join(tmp, "model.safetensors.index.json"), "w"), indent=1)
    cfg_path = os.path.join(tmp, "config.json")
    cfg = json.load(open(cfg_path)); cfg["torch_dtype"] = "bfloat16"
    json.dump(cfg, open(cfg_path, "w"), indent=1)

    old = os.path.join(a.run, "final.fp32_old")
    os.rename(fin, old); os.rename(tmp, fin)
    print(f"[shrink] {a.run}: swapped in bf16 final ({before/1e9:.0f} -> {new_total/1e9:.0f} GB, "
          f"saved {(before-new_total)/1e9:.0f} GB) in {time.time()-t0:.0f}s", flush=True)
    if not a.keep_old:
        shutil.rmtree(old)
        print(f"[shrink] {a.run}: removed the fp32 original", flush=True)


if __name__ == "__main__":
    main()
