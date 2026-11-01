"""Repair a Gemma 4 FSDP2 'final' for vLLM (2026-10-27). The run demoted persistent buffers to non-persistent (needed for
rank-0 loading under FSDP2, configs/am-gemma4-31b-e55recipe.yaml), so the 60 per-layer `layer_scalar` buffers and the vision tower's
std_bias / std_scale - constants, never trained - were not saved, and transformers 5.16 rewrote config.json into a per_layer_config form this vLLM build
does not read (no global_head_dim / num_global_key_value_heads). Output dir: the final's shards symlinked, one extra
shard with the base model's copies of those buffers, the index extended, the base model's config.json.
    python fix_gemma4_final.py <final dir> <base model dir> <out dir>"""
import json
import os
import shutil
import sys

from safetensors import safe_open
from safetensors.torch import save_file

src, base, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
fi = json.load(open(f"{src}/model.safetensors.index.json"))
bi = json.load(open(f"{base}/model.safetensors.index.json"))["weight_map"]
missing = sorted(set(bi) - set(fi["weight_map"]))
BUFFERS = ("layer_scalar", "std_bias", "std_scale")   # non-persistent under the run: per-layer scalars, vision-input normalisation
assert missing and all(k.endswith(BUFFERS) for k in missing), [k for k in missing if not k.endswith(BUFFERS)]
t = {}
for shard in sorted({bi[k] for k in missing}):
    with safe_open(f"{base}/{shard}", "pt") as f:
        t.update({k: f.get_tensor(k) for k in missing if bi[k] == shard})
save_file(t, f"{out}/model-layer-scalars.safetensors", metadata={"format": "pt"})
for k in missing:
    fi["weight_map"][k] = "model-layer-scalars.safetensors"
json.dump(fi, open(f"{out}/model.safetensors.index.json", "w"), indent=2)
for n in os.listdir(src):
    if n.endswith(".safetensors") and not os.path.exists(f"{out}/{n}"):
        os.symlink(os.path.abspath(f"{src}/{n}"), f"{out}/{n}")
    elif n not in ("model.safetensors.index.json", "config.json") and not n.endswith(".safetensors"):
        shutil.copy(f"{src}/{n}", f"{out}/{n}")
shutil.copy(f"{base}/config.json", f"{out}/config.json")
vals = sorted(float(v.float().mean()) for v in t.values())
print(f"added {len(missing)} buffers (means {vals[0]:.4f} .. {vals[-1]:.4f}): {sorted({k.rsplit('.', 1)[1] for k in missing})}; base config.json -> {out}")
