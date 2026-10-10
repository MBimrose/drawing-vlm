"""Reference port of DeepSeek-V4.1 attention (the released inference/model.py semantics, plain PyTorch, fp32, prefill)
for ONE layer, run on the HF model's own captured layer input, compared stage by stage with the HF draft and with
vLLM's sublayer dump (2026-10-07; HF diverges from vLLM first at layer 2 = first compressed-attention layer).
    python dsv41_attn_ref.py --ref ref.json --n 128 --layer 2 --vllm grpo_ds/parity/vllm_layers_128.rank0.pt"""
import argparse, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import torch
import torch.nn.functional as F
from dsv41_unitcheck import weight_of, rel


def freqs_cis(dim, seqlen, original_seq_len, base, factor, beta_fast, beta_slow):
    freqs = 1.0 / (base ** (torch.arange(0, dim, 2, dtype=torch.float32) / dim))
    if original_seq_len > 0:
        def corrected_dim(rotations):
            return dim * math.log(original_seq_len / (rotations * 2 * math.pi)) / (2 * math.log(base))
        low = max(math.floor(corrected_dim(beta_fast)), 0); high = min(math.ceil(corrected_dim(beta_slow)), dim - 1)
        ramp = ((torch.arange(dim // 2, dtype=torch.float32) - low) / max(high - low, 1e-3)).clamp(0, 1)
        smooth = 1 - ramp
        freqs = freqs / factor * (1 - smooth) + freqs * smooth
    freqs = torch.outer(torch.arange(seqlen), freqs)
    return torch.polar(torch.ones_like(freqs), freqs)


def rope(x, fc, inverse=False):   # x [S, ..., D] (positions first); rotate the LAST 64 channels as adjacent pairs
    rd = fc.shape[-1] * 2
    y = x.clone().float()
    r = torch.view_as_complex(y[..., -rd:].contiguous().unflatten(-1, (-1, 2)))
    f = (fc.conj() if inverse else fc).to(r.device)
    f = f.view(f.shape[0], *([1] * (r.ndim - 2)), f.shape[-1])
    y[..., -rd:] = torch.view_as_real(r * f).flatten(-2)
    return y


def rms(x, w, eps=1e-20):
    x = x.float(); return x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + eps) * w.float().to(x.device)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--ref"); ap.add_argument("--n", type=int, default=128)
    ap.add_argument("--layer", type=int, default=2); ap.add_argument("--vllm", default="")
    ap.add_argument("--model", default="models/DeepSeek-V4.1-Flash"); ap.add_argument("--chunked-attn", type=int, default=0)
    ap.add_argument("--patch", default="")
    a = ap.parse_args()
    from dsv41_parity import load_model
    import transformers.models.deepseek_v41.modeling_deepseek_v41 as M
    model, proc, tok = load_model(a)
    cfg = model.config.text_config if hasattr(model.config, "text_config") else model.config
    ref = json.load(open(a.ref)); ids = torch.tensor([ref["text"][0]["ids"][: a.n]], device=model.device)
    layers = [m for m in model.modules() if type(m).__name__ == "DeepseekV41DecoderLayer"]
    L = a.layer; att = layers[L].self_attn
    cap = {}
    orig = M.eager_attention_forward_dms

    def spy(module, query, key, value, attention_mask, scaling, dropout=0.0, selected_kv=None, selected_valid=None, **kw):
        if module is att:
            cap.update(q=query.detach(), k=key.detach(), mask=None if attention_mask is None else attention_mask.detach(),
                       skv=None if selected_kv is None else selected_kv.detach(), sval=None if selected_valid is None else selected_valid.detach())
        o = orig(module, query, key, value, attention_mask, scaling, dropout=dropout, selected_kv=selected_kv, selected_valid=selected_valid, **kw)
        if module is att:
            cap["o"] = o[0].detach()
        return o
    M.eager_attention_forward_dms = spy
    h = att.register_forward_pre_hook(lambda m, args, kw: cap.__setitem__("x", (args[0] if args else kw["hidden_states"]).detach()), with_kwargs=True)
    h2 = att.register_forward_hook(lambda m, args, out: cap.__setitem__("out", out[0].detach()))
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
        model(input_ids=ids, attention_mask=torch.ones_like(ids))
    h.remove(); h2.remove(); M.eager_attention_forward_dms = orig

    dev = cap["x"].device; x = cap["x"][0].float(); S = x.shape[0]
    ratio = cfg.compress_ratios[L]
    rs = cfg.rope_scaling or {}
    if ratio:
        fc = freqs_cis(64, S, rs.get("original_max_position_embeddings", 65536), cfg.compress_rope_theta, rs.get("factor", 16), rs.get("beta_fast", 32), rs.get("beta_slow", 1))
    else:
        fc = freqs_cis(64, S, 0, cfg.rope_theta, 1, 32, 1)
    fc = fc.to(dev)
    W = lambda m: weight_of(m).to(dev)
    qr = rms(x @ W(att.q_a_proj).t(), att.q_a_norm.weight)
    q = (qr @ W(att.q_b_proj).t()).view(S, 64, 512)
    q = rope(q, fc)                                             # [S, H, D]
    kv = rms(x @ W(att.kv_proj).t(), att.kv_norm.weight)
    kv = rope(kv, fc)
    kv = M._fake_quant_fp8_block(kv, 32).float()
    hq = cap["q"][0].transpose(0, 1).float()                   # HF [B,H,S,D] -> [S,H,D]
    print(f"[ref] L{L} ratio {ratio} S {S}: q rel {rel(hq, q)[0]:.4f} | kv rel {rel(cap['k'][0, 0].float(), kv)[0]:.4f}", flush=True)
    # window entries
    t = torch.arange(S, device=dev)
    win = (t[None, :] <= t[:, None]) & (t[None, :] > t[:, None] - cfg.sliding_window)  # [S(query), S(key)]
    if cap["mask"] is not None:
        hm = cap["mask"][0, 0] > torch.finfo(cap["mask"].dtype).min / 2
        print(f"[ref] window mask identical: {bool((hm.to(dev) == win).all())} (hf allowed {int(hm.sum())} ref {int(win.sum())})", flush=True)
    keys = [kv]; allow = [win]
    if ratio:
        # compressor of this layer's group source (only kv sources compress; others reuse) -- port only for a source layer
        cmp = att.compressor
        assert cmp is not None, "run on a kv-source layer (2, 8, 14, 20)"
        if ratio == 1:
            lat = rms(x @ W(cmp.kv_proj).t(), cmp.kv_norm.weight)
        else:
            G = S // ratio
            kvc = (x @ W(cmp.kv_proj).t())[: G * ratio].view(G, ratio, -1)
            sc = (x @ W(cmp.gate_proj).t())[: G * ratio].view(G, ratio, -1)
            lat = rms((kvc * sc.softmax(dim=1)).sum(1), cmp.kv_norm.weight)
        G = lat.shape[0]
        fcl = fc[: S - S % ratio: ratio] if ratio > 1 else fc
        latr = rope(lat, fcl)
        latr = M._fake_quant_fp4_block(latr, block_size=16, e4m3_scales=True).float()
        clen = (t + 1) // ratio
        callow = torch.arange(G, device=dev)[None, :] < clen[:, None]   # topk >= G here: every visible entry selected
        keys.append(latr); allow.append(callow)
        if cap["skv"] is not None:
            # HF: selected_kv [B,S,top_k,D], valid [B,S,top_k]; compare the SET of valid selected entries per query
            skv, sval = cap["skv"][0].float(), cap["sval"][0]
            nv = sval.sum(-1)
            print(f"[ref] HF selected per query (first 12): {nv[:12].tolist()} | ref visible: {callow.sum(-1)[:12].tolist()}", flush=True)
            # match HF selected rows to ref latents
            q8 = 8 if S > 8 else S - 1
            for qi in (1, 3, q8, S - 1):
                hs = skv[qi][sval[qi]]
                rv = latr[callow[qi]]
                if hs.shape[0] and rv.shape[0]:
                    d = torch.cdist(hs, rv)
                    print(f"[ref]   query {qi}: hf {hs.shape[0]} entries, ref {rv.shape[0]}; nearest-ref rel dist {float((d.min(1).values / rv.norm(dim=-1).mean()).max()):.4f}", flush=True)
    kall = torch.cat(keys, 0); aall = torch.cat(allow, 1)
    s = torch.einsum("shd,kd->shk", q, kall) * (512 ** -0.5)
    s = s.masked_fill(~aall[:, None, :], float("-inf"))
    sink = att.sinks.float().to(dev)[None, :, None].expand(S, -1, 1)
    p = torch.cat([s, sink], -1).softmax(-1)[..., :-1]
    o = torch.einsum("shk,kd->shd", p, kall)
    ho = cap["o"][0].float()                                       # HF interface output [B,S,H,D] -> [S,H,D]
    print(f"[ref] attention core o rel {rel(ho, o)[0]:.4f}", flush=True)
    o = rope(o, fc, inverse=True)
    Wa = W(att.o_a_proj).view(8, 1024, -1)
    og = torch.einsum("sgd,grd->sgr", o.reshape(S, 8, -1), Wa).flatten(1)
    out = og @ W(att.o_b_proj).t()
    hout = cap["out"][0].float()
    print(f"[ref] L{L} attn_out: ref vs HF rel {rel(hout, out)[0]:.4f}", flush=True)
    if a.vllm:
        v = torch.load(a.vllm)[f"attn_out.{L}"].to(dev)
        r_ = ((out - v).norm(dim=-1) / v.norm(dim=-1))
        print(f"[ref] L{L} attn_out: ref vs vLLM rel {rel(v, out)[0]:.4f} per-token {[round(float(z), 2) for z in r_[:10]]} | HF vs vLLM {rel(v, hout)[0]:.4f}", flush=True)
        # window-only variant: is vLLM attending to the compressed entries at all at this length?
        s2 = torch.einsum("shd,kd->shk", q, kv) * (512 ** -0.5)
        s2 = s2.masked_fill(~win[:, None, :], float("-inf"))
        p2 = torch.cat([s2, sink], -1).softmax(-1)[..., :-1]
        o2 = rope(torch.einsum("shk,kd->shd", p2, kv), fc, inverse=True)
        out2 = torch.einsum("sgd,grd->sgr", o2.reshape(S, 8, -1), Wa).flatten(1) @ W(att.o_b_proj).t()
        print(f"[ref] L{L} window-only ref vs vLLM rel {rel(v, out2)[0]:.4f}", flush=True)


if __name__ == "__main__":
    main()
