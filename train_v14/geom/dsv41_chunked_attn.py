"""Exact, memory-bounded replacement for transformers' DeepSeek-V4.1 `eager_attention_forward_dms` (draft PR #48768).

The eager version builds the full S x S score matrix and masks it, but V4.1's window attention only uses a
128-token sliding window (plus up to index_topk selected compressed keys per query, passed separately). At 33k
tokens the full matrix is ~124 GiB per layer. Here queries are processed in chunks; for each chunk only the key
columns its mask allows ([lo, hi)) are scored, then the selected keys and the per-head sink are appended exactly as
the original does. Columns outside [lo, hi) are -inf for every row of the chunk, so the softmax is unchanged.
    import dsv41_chunked_attn; dsv41_chunked_attn.install(chunk=256)"""
import torch
import torch.nn.functional as F

def chunked_attention_forward_dms(module, query, key, value, attention_mask, scaling, dropout=0.0,
                                  selected_kv=None, selected_valid=None, chunk=256, **kwargs):
    S = query.shape[-2]
    if attention_mask is None or S <= chunk:
        return _ORIG(module, query, key, value, attention_mask, scaling, dropout=dropout,
                     selected_kv=selected_kv, selected_valid=selected_valid, **kwargs)
    B, H = query.shape[0], query.shape[1]; Kn = key.shape[-2]
    neg = torch.finfo(attention_mask.dtype).min / 2 if attention_mask.dtype.is_floating_point else None
    sinks = module.sinks.float()
    outs = []
    for s in range(0, S, chunk):
        e = min(S, s + chunk); m = attention_mask[..., s:e, :]
        allowed = (m > neg) if neg is not None else m
        cols = allowed.reshape(-1, Kn).any(0).nonzero()
        lo, hi = (int(cols[0]), int(cols[-1]) + 1) if len(cols) else (0, 1)
        w = torch.matmul(query[:, :, s:e], key[:, :, lo:hi].transpose(2, 3)) * scaling + m[..., lo:hi]
        win = w.shape[-1]
        if selected_kv is not None:
            skv = selected_kv[:, s:e].to(query.dtype)
            picked = torch.einsum("bhsd,bskd->bhsk", query[:, :, s:e], skv) * scaling
            picked = picked.masked_fill(~selected_valid[:, s:e].unsqueeze(1), float("-inf"))
            w = torch.cat([w, picked], dim=-1)
        snk = sinks.reshape(1, -1, 1, 1).expand(B, -1, e - s, -1)
        logits = torch.cat([w, snk], dim=-1)
        logits = logits - logits.max(dim=-1, keepdim=True).values
        p = F.softmax(logits, dim=-1, dtype=logits.dtype)[..., :-1]
        p = F.dropout(p, p=dropout, training=module.training).to(value.dtype)
        o = torch.matmul(p[..., :win], value[:, :, lo:hi])
        if selected_kv is not None:
            o = o + torch.einsum("bhsk,bskd->bhsd", p[..., win:], skv)
        outs.append(o)
    return torch.cat(outs, dim=2).transpose(1, 2).contiguous(), None

_ORIG = None
def install(chunk=256):
    global _ORIG
    import functools
    import transformers.models.deepseek_v41.modeling_deepseek_v41 as M
    if _ORIG is None:
        _ORIG = M.eager_attention_forward_dms
    M.eager_attention_forward_dms = functools.partial(chunked_attention_forward_dms, chunk=chunk)
