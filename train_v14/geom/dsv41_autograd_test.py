"""Check dsv41_autograd against the Hub kernel on real DeepSeek-V4.1-Flash tensors, no model load.

Reads one block-scaled FP8 attention weight and one MXFP4 expert weight straight from the
safetensors shards (native names: layers.N.attn.wq_b / layers.N.ffn.experts.E.w1), runs the
kernel forward against the dequantized matmul (validates scale decoding and the E2M1 nibble
order -- both orders are tried and reported) and the registered backward against the reference
dA; then the grouped op over two experts.

    CUDA_VISIBLE_DEVICES=0 python dsv41_autograd_test.py --model models/DeepSeek-V4.1-Flash
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def load_tensor(model, name):
    from safetensors import safe_open
    idx = json.load(open(os.path.join(model, "model.safetensors.index.json")))["weight_map"]
    with safe_open(os.path.join(model, idx[name]), framework="pt", device="cpu") as f:
        return f.get_tensor(name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--layer", type=int, default=1)
    args = ap.parse_args()
    import torch
    import dsv41_autograd as ag
    dev = torch.device("cuda:0")
    ns = ag.register()
    print("registered on", ns, flush=True)

    # --- block FP8 attention weight
    w = load_tensor(args.model, f"layers.{args.layer}.attn.wq_b.weight").to(dev)
    s = load_tensor(args.model, f"layers.{args.layer}.attn.wq_b.scale").to(dev)
    print("wq_b", tuple(w.shape), w.dtype, "scale", tuple(s.shape), s.dtype, flush=True)
    bs = [w.shape[0] // s.shape[0], w.shape[1] // s.shape[1]]
    ag.selftest(w, s, bs, label=f"wq_b block{bs}")

    # --- MXFP4 expert weight, both nibble orders
    we = load_tensor(args.model, f"layers.{args.layer}.ffn.experts.0.w1.weight").to(dev)
    se = load_tensor(args.model, f"layers.{args.layer}.ffn.experts.0.w1.scale").to(dev)
    print("experts.0.w1", tuple(we.shape), we.dtype, "scale", tuple(se.shape), se.dtype, flush=True)
    results = {}
    for low_first in (True, False):
        ag.E2M1_LOW_FIRST = low_first
        results[low_first] = ag.selftest(we, se, None, label=f"w1 mxfp4 low_first={low_first}")
    best = min(results, key=lambda k: results[k]["fwd_rel_err"])
    ag.E2M1_LOW_FIRST = best
    print(f"E2M1 nibble order: low_first={best} (fwd err {results[best]['fwd_rel_err']:.3e} vs {results[not best]['fwd_rel_err']:.3e})", flush=True)

    # --- grouped op over two experts (block FP8 path uses the same code as MX; test MX since that is what experts are)
    from transformers.integrations.finegrained_fp8 import load_finegrained_fp8_kernel
    k = load_finegrained_fp8_kernel()
    we1 = load_tensor(args.model, f"layers.{args.layer}.ffn.experts.1.w1.weight").to(dev)
    se1 = load_tensor(args.model, f"layers.{args.layer}.ffn.experts.1.w1.scale").to(dev)
    B = torch.stack([we, we1]).contiguous(); Bs = torch.stack([se, se1]).contiguous()
    K = B.shape[-1] * (2 if B.dtype in (torch.int8, torch.uint8) else 1)
    tokens = torch.tensor([24, 40], device=dev, dtype=torch.int32); offsets = torch.cumsum(tokens, 0).to(torch.int32)
    A = torch.randn(64, K, device=dev, dtype=torch.bfloat16, requires_grad=True)
    out = k.grouped_matmul(A, B, Bs, offsets=offsets, tokens_per_expert=tokens, block_size=None)
    W0, W1 = ag.dequant_any(we, se, None, torch.float32), ag.dequant_any(we1, se1, None, torch.float32)
    ref = torch.cat([A[:24].detach().float() @ W0.t(), A[24:].detach().float() @ W1.t()])
    fwd = ((out.float() - ref).norm() / ref.norm()).item()
    g = torch.randn_like(out); out.backward(g)
    dref = torch.cat([g[:24].float() @ W0, g[24:].float() @ W1])
    bwd = ((A.grad.float() - dref).norm() / dref.norm()).item()
    print(f"[autograd selftest] grouped mxfp4 x2 experts: fwd_rel_err {fwd:.3e} bwd_rel_err {bwd:.3e}", flush=True)
    ok = results[best]["fwd_rel_err"] < 0.05 and results[best]["bwd_rel_err"] < 0.05 and fwd < 0.05 and bwd < 0.05
    print("AUTOGRAD SELFTEST", "OK" if ok else "FAILED", f"(use E2M1_LOW_FIRST={best})", flush=True)


if __name__ == "__main__":
    main()
