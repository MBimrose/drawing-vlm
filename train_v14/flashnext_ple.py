"""Qwen3.8-Flash-Next (Qwen4Exp) n-gram PLE table served from an mmap.

The model carries ONE 320M x 160 bf16 embedding (102 GB) in layer 1
(`ple.ple_embedding.ngram_embedding`). It is a frozen lookup, but FSDP2
all-gathers whole decoder layers, so every GPU would need 100 GiB at that
layer's forward -> OOM on H200. Transformers' own device_map path skips it
(`_no_placement_params`); we do the FSDP equivalent: drop the parameter and
answer lookups from the 128 safetensors shards mmapped read-only. The page
cache is shared by all ranks (run.sh warms it), so the host cost is 102 GB
per NODE, not per rank, and the gather of ~80k rows/step is milliseconds.
"""
from __future__ import annotations

import json
import os
import re

import torch
import torch.nn as nn
from safetensors import safe_open

SUFFIX = "ple.ple_embedding.ngram_embedding"


class MmapNgramEmbedding(nn.Module):
    def __init__(self, model_dir: str, fqn: str):
        super().__init__()
        index = json.load(open(os.path.join(model_dir, "model.safetensors.index.json")))["weight_map"]
        pat = re.compile(re.escape(fqn) + r"\.shard_(\d+)\.weight$")
        shards = sorted(((int(m.group(1)), k) for k in index if (m := pat.match(k))))
        assert shards and [s[0] for s in shards] == list(range(len(shards))), fqn
        # FLASHNEXT_PLE_DIR: node-local copy of the shard files (e.g. /dev/shm,
        # staged by the sbatch) so gathers never page-fault against Lustre.
        src_dir = os.environ.get("FLASHNEXT_PLE_DIR") or model_dir
        handles: dict[str, object] = {}
        self._shards = []
        for _, key in shards:
            f = index[key]
            if f not in handles:
                path = os.path.join(src_dir, f)
                if not os.path.exists(path):
                    path = os.path.join(model_dir, f)
                handles[f] = safe_open(path, framework="pt", device="cpu")
            self._shards.append(handles[f].get_tensor(key))  # zero-copy mmap
        self._handles = handles
        self.rows = self._shards[0].shape[0]
        assert all(s.shape[0] == self.rows for s in self._shards[:-1])
        self.dim = self._shards[0].shape[1]
        self.num_embeddings = sum(s.shape[0] for s in self._shards)
        # `.weight.device` is consulted by the model's forward; plain attribute
        # (not a Parameter/Buffer) so FSDP/accelerate never touch it.
        self.weight = torch.empty(0, dtype=self._shards[0].dtype)

    def forward(self, ids: torch.Tensor) -> torch.Tensor:
        flat = ids.reshape(-1).cpu()
        shard_idx = torch.div(flat, self.rows, rounding_mode="floor")
        row = flat - shard_idx * self.rows
        out = torch.empty(flat.numel(), self.dim, dtype=self.weight.dtype)
        for s in torch.unique(shard_idx).tolist():
            m = shard_idx == s
            out[m] = self._shards[s][row[m]]
        return out.view(*ids.shape, self.dim).to(ids.device, non_blocking=True)

    def extra_repr(self) -> str:
        return f"{self.num_embeddings}x{self.dim} mmap ({len(self._shards)} shards)"


def replace_ngram_embedding(model, model_dir: str) -> int:
    """Swap every huge ngram nn.Embedding for the mmap module. Returns count."""
    n = 0
    for fqn, mod in list(model.named_modules()):
        if fqn.endswith(SUFFIX) and isinstance(mod, nn.Embedding):
            parent = model.get_submodule(fqn.rsplit(".", 1)[0])
            # strip a leading "model." only if the index keys carry it too
            index_fqn = fqn if fqn.startswith("model.") else "model." + fqn
            new = MmapNgramEmbedding(model_dir, index_fqn)
            assert new.num_embeddings == mod.num_embeddings and new.dim == mod.embedding_dim, \
                (new.num_embeddings, mod.num_embeddings, new.dim, mod.embedding_dim)
            setattr(parent, fqn.rsplit(".", 1)[1], new)
            del mod
            n += 1
            print(f"[ple] {fqn}: {new.num_embeddings}x{new.dim} -> mmap "
                  f"({len(new._shards)} shards), 102 GB param dropped", flush=True)
    return n


def reattach_ngram_shards(model_dir: str, out_dir: str) -> None:
    """A full-model save made with the mmap table has no ngram_embedding
    weights. Hard-link the original shard files into `out_dir` and merge their
    index entries so the saved model loads standalone (table is frozen, so the
    original bytes are exact)."""
    import shutil
    src_index = json.load(open(os.path.join(model_dir, "model.safetensors.index.json")))
    idx_path = os.path.join(out_dir, "model.safetensors.index.json")
    out_index = json.load(open(idx_path))
    files = sorted({f for k, f in src_index["weight_map"].items() if ".ngram_embedding.shard_" in k})
    for f in files:
        dst = os.path.join(out_dir, "ple-" + f)
        if not os.path.exists(dst):
            try:
                os.link(os.path.join(model_dir, f), dst)
            except OSError:
                shutil.copy2(os.path.join(model_dir, f), dst)
    # only the ngram keys from those files; other tensors in them are already saved
    for k, f in src_index["weight_map"].items():
        if ".ngram_embedding.shard_" in k:
            out_index["weight_map"][k] = "ple-" + f
    with open(idx_path, "w") as fh:
        json.dump(out_index, fh, indent=2)
    print(f"[ple] re-attached {len(files)} shard files / "
          f"{sum('.ngram_embedding.shard_' in k for k in src_index['weight_map'])} keys to {out_dir}", flush=True)
