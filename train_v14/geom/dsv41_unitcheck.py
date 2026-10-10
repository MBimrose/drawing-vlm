"""Module-level checks of the HF DeepSeek-V4.1 draft against a plain-PyTorch dequantized reference (2026-10-07).
Runs the first N tokens of a parity text sequence through the HF model with hooks, then recomputes selected modules
from their captured inputs with weights dequantized exactly as the reference inference/convert.py does (FP8 E4M3 x UE8M0
32x32 blocks; FP4 e2m1 low-nibble-first x UE8M0 per 32 along K). Also dumps every decoder layer's output for a
later per-layer comparison against vLLM.
    python dsv41_unitcheck.py --ref ref.json --n 128 --layers 0,2,21,30 --dump layers_hf.pt"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import torch
import torch.nn.functional as F

LUT = torch.tensor([0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, -0.0, -0.5, -1.0, -1.5, -2.0, -3.0, -4.0, -6.0])


def deq_fp8(w, s, bs=32):
    w = w.float(); s = s.float()
    return w * s.repeat_interleave(bs, -2).repeat_interleave(bs, -1)[..., : w.shape[-2], : w.shape[-1]]


def deq_fp4(w, s):   # w int8 [.., N, K/2] two nibbles per byte (low first), s [.., N, K/32]
    u = w.view(torch.uint8).long()
    v = torch.stack([LUT.to(w.device)[u & 15], LUT.to(w.device)[(u >> 4) & 15]], -1).flatten(-2)
    return v * s.float().repeat_interleave(32, -1)[..., : v.shape[-1]]


def weight_of(mod):
    """dequantized fp32 weight of an HF (FP8) linear-like module, whatever its storage"""
    w = mod.weight
    s = None
    for n in ("weight_scale_inv", "weight_scale", "scale_inv"):
        if hasattr(mod, n) and getattr(mod, n) is not None:
            s = getattr(mod, n); break
    if w.dtype == torch.float8_e4m3fn:
        return deq_fp8(w, s)
    if w.dtype in (torch.int8, torch.uint8):
        return deq_fp4(w, s)
    return w.float()


def rel(a, b):
    a, b = a.float().flatten(), b.float().flatten().to(a.device)
    return float((a - b).norm() / (b.norm() + 1e-30)), float(F.cosine_similarity(a, b, dim=0))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--ref"); ap.add_argument("--n", type=int, default=128)
    ap.add_argument("--layers", default="0,2,21,30"); ap.add_argument("--dump", default="")
    ap.add_argument("--model", default="models/DeepSeek-V4.1-Flash"); ap.add_argument("--chunked-attn", type=int, default=0)
    ap.add_argument("--patch", default=""); ap.add_argument("--fix", default="shared"); ap.add_argument("--image", action="store_true"); ap.add_argument("--fast-image", action="store_true")
    ap.add_argument("--checks", type=int, default=1)
    a = ap.parse_args()
    from dsv41_parity import load_model
    model, proc, tok = load_model(a)
    ref = json.load(open(a.ref)); ids = torch.tensor([ref["text"][0]["ids"][: a.n]], device=model.device)
    kw_img = {}
    if a.image:   # the first image record: vLLM's prompt ids + the HF processor's pixel inputs
        import pickle
        sys.path.insert(0, os.path.join(a.model, "encoding")); import encoding as dsenc
        from dsv41_lora_train import build_sample
        r = ref["image"][0]; pj = json.load(open(os.path.join(HERE, "dsv41_grpo_prompts.json")))
        png = pickle.load(open(os.path.join(r["bench"], "eval_cache_v15.pkl"), "rb"))["samples"][r["key"]]["png"]
        enc = build_sample(proc, dsenc, pj["system"], pj["user"], png, "", proc.image_token, 10**9, None, "", "", 50)
        ids = torch.tensor([r["prompt_ids"]], device=model.device)
        kw_img = {k: v.to(model.device) for k, v in enc.items() if k not in ("input_ids", "labels", "attention_mask") and hasattr(v, "to")}
        print(f"[unit] image prompt {ids.shape[-1]} tokens, pixel inputs {[(k, tuple(v.shape)) for k, v in kw_img.items()]}", flush=True)
    layers = [m for m in model.modules() if type(m).__name__ == "DeepseekV41DecoderLayer"]
    print(f"[unit] {len(layers)} decoder layers", flush=True)
    want = [int(x) for x in a.layers.split(",")]
    cap = {}

    def hook(name):
        def f(mod, args, kwargs, out):
            cap[name] = ([x.detach() if torch.is_tensor(x) else x for x in args],
                         {k: (v.detach() if torch.is_tensor(v) else v) for k, v in kwargs.items()},
                         out.detach() if torch.is_tensor(out) else [o.detach() if torch.is_tensor(o) else o for o in out])
        return f
    hs = []
    for L in want:
        lay = layers[L]
        for n in ("self_attn.q_a_proj", "self_attn.kv_proj", "self_attn.q_b_proj", "self_attn.o_a_proj", "self_attn.o_b_proj",
                  "mlp.experts", "mlp.shared_experts", "mlp.gate"):
            m = lay.get_submodule(n)
            hs.append(m.register_forward_hook(hook(f"{L}.{n}"), with_kwargs=True))
    outs = {}
    for i, lay in enumerate(layers):
        hs.append(lay.register_forward_hook(lambda m, a_, o, i=i: outs.__setitem__(i, o[0].detach().float().cpu())))
        # sublayer inputs/outputs ([tokens, hidden]) -- directly comparable with dsv41_vllm_layerdump.py
        hs.append(lay.self_attn.register_forward_pre_hook(lambda m, a_, k_, i=i: outs.__setitem__(f"attn_in.{i}", (a_[0] if a_ else k_["hidden_states"]).detach().float().cpu()[0]), with_kwargs=True))
        hs.append(lay.mlp.register_forward_pre_hook(lambda m, a_, k_, i=i: outs.__setitem__(f"ffn_in.{i}", a_[0].detach().float().cpu()[0]), with_kwargs=True))
        hs.append(lay.self_attn.register_forward_hook(lambda m, a_, o, i=i: outs.__setitem__(f"attn_out.{i}", o[0].detach().float().cpu()[0])))
        hs.append(lay.mlp.register_forward_hook(lambda m, a_, o, i=i: outs.__setitem__(f"ffn_out.{i}", o.detach().float().cpu()[0])))
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
        lg = model(input_ids=ids, attention_mask=torch.ones_like(ids), **kw_img).logits[0].float()
    for h in hs: h.remove()
    tgt = ids[0, 1:]
    nll = -torch.log_softmax(lg[:-1], -1).gather(1, tgt[:, None].to(lg.device))[:, 0]
    if not a.image:
        v = -torch.tensor(ref["text"][0]["lp"][1: a.n])
        print(f"[unit] NLL first {a.n}: hf {float(nll.mean()):.3f} vllm {float(v.mean()):.3f}", flush=True)
    if a.dump:
        torch.save({"ids": ids.cpu(), "layers": outs}, a.dump)
    if not a.checks:
        return
    for L in want:
        lay = layers[L]
        for n in ("self_attn.q_a_proj", "self_attn.kv_proj", "self_attn.q_b_proj", "self_attn.o_b_proj"):
            args, kw, out = cap[f"{L}.{n}"]; m = lay.get_submodule(n)
            x = args[0].float(); W = weight_of(m).to(x.device)
            y = x @ W.t()
            print(f"[unit] L{L} {n:22s} {type(m).__name__} w {m.weight.dtype} {tuple(m.weight.shape)} rel {rel(out, y)[0]:.4f} cos {rel(out, y)[1]:.5f}", flush=True)
        # grouped o_a: x [.., G, Din], weight [G*R, Din]
        args, kw, out = cap[f"{L}.self_attn.o_a_proj"]; m = lay.get_submodule("self_attn.o_a_proj")
        x = args[0].float(); W = weight_of(m).to(x.device); G = m.n_groups
        Wg = W.view(G, -1, W.shape[-1]); y = torch.einsum("...gd,grd->...gr", x, Wg)
        print(f"[unit] L{L} o_a_proj {type(m).__name__} w {m.weight.dtype} {tuple(m.weight.shape)} x {tuple(x.shape)} out {tuple(out.shape)} rel {rel(out, y)[0]:.4f}", flush=True)
        # shared expert
        args, kw, out = cap[f"{L}.mlp.shared_experts"]; m = lay.get_submodule("mlp.shared_experts")
        x = args[0].float()
        g = x @ weight_of(m.gate_proj).to(x.device).t(); u = x @ weight_of(m.up_proj).to(x.device).t()
        u = u.clamp(-10, 10); g = g.clamp(max=10)
        y = (F.silu(g) * u) @ weight_of(m.down_proj).to(x.device).t()
        print(f"[unit] L{L} shared_experts rel {rel(out, y)[0]:.4f} cos {rel(out, y)[1]:.5f}", flush=True)
        # router
        args, kw, out = cap[f"{L}.mlp.gate"]; m = lay.get_submodule("mlp.gate")
        x = args[0].reshape(-1, args[0].shape[-1]).float()
        sc = F.softplus(x @ m.weight.float().t().to(x.device)).sqrt()
        idx = (sc + m.e_score_correction_bias.to(x.device)).topk(6, -1)[1]
        wts = sc.gather(1, idx); wts = wts / (wts.sum(-1, keepdim=True) + 1e-20) * 1.5
        _, w_hf, i_hf = out
        same = (torch.sort(idx, -1)[0] == torch.sort(i_hf.to(idx.device), -1)[0]).all(-1).float().mean()
        print(f"[unit] L{L} router idx-match {float(same):.3f} weight rel {rel(torch.sort(w_hf.to(x.device),-1)[0], torch.sort(wts,-1)[0])[0]:.4f} score_fn {m.score_fn}", flush=True)
        # routed experts
        args, kw, out = cap[f"{L}.mlp.experts"]; m = lay.get_submodule("mlp.experts")
        hid, ti, tw = args[0], args[1], args[2]
        pn = {n: (tuple(p.shape), p.dtype) for n, p in m.named_parameters()}
        print(f"[unit] L{L} experts params {pn}", flush=True)
        I = m.intermediate_dim
        gu_s = getattr(m, "gate_up_proj_scale_inv", None); dn_s = getattr(m, "down_proj_scale_inv", None)
        y = torch.zeros(hid.shape[0], hid.shape[1], dtype=torch.float32, device=hid.device)
        for t in range(min(8, hid.shape[0])):
            for j in range(ti.shape[1]):
                e = int(ti[t, j])
                gu = deq_fp4(m.gate_up_proj[e], gu_s[e]) if m.gate_up_proj.dtype in (torch.int8, torch.uint8) else deq_fp8(m.gate_up_proj[e], gu_s[e])
                dn = deq_fp4(m.down_proj[e], dn_s[e]) if m.down_proj.dtype in (torch.int8, torch.uint8) else deq_fp8(m.down_proj[e], dn_s[e])
                xx = hid[t].float().to(gu.device)
                g, u = xx @ gu[:I].t(), xx @ gu[I:].t()
                act = F.silu(g.clamp(max=10)) * u.clamp(-10, 10) * float(tw[t, j])
                y[t] += (act @ dn.t()).to(y.device)
        print(f"[unit] L{L} experts (8 tokens) rel {rel(out[:8], y[:8])[0]:.4f} cos {rel(out[:8], y[:8])[1]:.5f}", flush=True)


if __name__ == "__main__":
    main()
