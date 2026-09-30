"""Merge a PEFT LoRA adapter (trained through transformers on DeepSeek-V4.1-Flash) into the native FP8 checkpoint so
vLLM can serve it without LoRA support (2026-09-29). Targets are FP8 E4M3 with UE8M0 (power-of-two) scales per 32x32
block: W = q * 2^e  ->  W + (B @ A) * alpha / r  ->  requantize per block (scale = 2^ceil(log2(amax / 448))).
transformers' DeepSeek-V4.1 loader only RENAMES these tensors (conversion_mapping.py, no permutation), so the adapter's
module names map 1:1. Unchanged shards are symlinked; changed shards are rewritten; all other files are linked.
    python merge_dsv41_lora.py --base models/DeepSeek-V4.1-Flash --adapter runs/<run> --out runs/<run>/merged"""
import argparse, json, os, re, collections
import torch
from safetensors import safe_open
from safetensors.torch import save_file
MAP = {"self_attn.q_a_proj": "attn.wq_a", "self_attn.q_b_proj": "attn.wq_b", "self_attn.kv_proj": "attn.wkv", "self_attn.o_b_proj": "attn.wo_b",
       "mlp.shared_experts.gate_proj": "ffn.shared_experts.w1", "mlp.shared_experts.up_proj": "ffn.shared_experts.w3", "mlp.shared_experts.down_proj": "ffn.shared_experts.w2"}
B = 32

def dequant(q, s):
    w = q.float(); sc = s.float().repeat_interleave(B, 0).repeat_interleave(B, 1)[: w.shape[0], : w.shape[1]]
    return w * sc

def requant(w):
    R, C = w.shape; pr, pc = (-R) % B, (-C) % B
    wp = torch.nn.functional.pad(w, (0, pc, 0, pr)); blk = wp.view(wp.shape[0] // B, B, wp.shape[1] // B, B)
    amax = blk.abs().amax(dim=(1, 3)).clamp(min=1e-12)
    e = torch.ceil(torch.log2(amax / 448.0)); s = torch.pow(2.0, e)
    q = (blk / s[:, None, :, None]).clamp(-448, 448).view_as(wp)[:R, :C].to(torch.float8_e4m3fn)
    return q, s.to(torch.float8_e8m0fnu)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--base"); ap.add_argument("--adapter"); ap.add_argument("--out"); a = ap.parse_args()
    cfg = json.load(open(os.path.join(a.adapter, "adapter_config.json"))); scaling = cfg["lora_alpha"] / cfg["r"]
    ad = safe_open(os.path.join(a.adapter, "adapter_model.safetensors"), "pt")
    deltas = {}
    for k in ad.keys():
        m = re.search(r"layers\.(\d+)\.(.+)\.lora_A\.weight$", k)
        if not m: continue
        tgt = f"layers.{m.group(1)}.{MAP[m.group(2)]}.weight"
        A = ad.get_tensor(k).float(); Bm = ad.get_tensor(k.replace("lora_A", "lora_B")).float()
        deltas[tgt] = (Bm @ A) * scaling
    idx = json.load(open(os.path.join(a.base, "model.safetensors.index.json")))["weight_map"]
    by_file = collections.defaultdict(list)
    for t in deltas: by_file[idx[t]].append(t)
    os.makedirs(a.out, exist_ok=True)
    for f in os.listdir(a.base):
        if f not in by_file and not os.path.exists(os.path.join(a.out, f)):
            os.symlink(os.path.abspath(os.path.join(a.base, f)), os.path.join(a.out, f))
    stats = []
    for f, ts in sorted(by_file.items()):
        src = safe_open(os.path.join(a.base, f), "pt"); tensors = {k: src.get_tensor(k) for k in src.keys()}; meta = src.metadata()
        for t in ts:
            sk = t[: -len(".weight")] + ".scale"
            w = dequant(tensors[t], tensors[sk]); d = deltas[t]; assert d.shape == w.shape, (t, d.shape, w.shape)
            q, s = requant(w + d); tensors[t], tensors[sk] = q, s
            err = (dequant(q, s) - (w + d)).norm() / (w + d).norm(); stats.append((t, float(d.norm() / w.norm()), float(err)))
        save_file(tensors, os.path.join(a.out, f), metadata=meta)
        print(f"rewrote {f}: {len(ts)} tensors", flush=True)
    rel = [x[1] for x in stats]; er = [x[2] for x in stats]
    print(f"merged {len(stats)} tensors into {len(by_file)} shards; |delta|/|W| median {sorted(rel)[len(rel)//2]:.2e}, requant rel err median {sorted(er)[len(er)//2]:.2e} max {max(er):.2e}")

if __name__ == "__main__":
    main()
