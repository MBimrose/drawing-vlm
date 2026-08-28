"""Vectorised QSA indexer for Qwen3.8-Flash-Next (Qwen4Exp).

transformers' reference `Qwen4ExpTextQSAIndexer.forward` loops in Python over
batch x every query position (matmul + topk per token). At 5k tokens x 12
sparse-attention layers x (fwd + ckpt recompute + bwd) that is ~200k tiny
kernel sequences per micro-batch -> ~45 s/micro-batch on H200 (measured:
360 s/step in the e26 smoke). The block keys do not depend on the query, so
the whole selection is a few batched ops. Exact same selection semantics;
falls back to the reference loop for masks that are not contiguous-causal.
"""
from __future__ import annotations

import math

import torch
from transformers.models.qwen4_exp import modeling_qwen4_exp as mq

_ORIG = mq.Qwen4ExpTextQSAIndexer.forward


def _fast_forward(self, hidden_states, position_embeddings, attention_mask, past_key_values):
    B, S, _ = hidden_states.shape
    R, D = self.compress_ratio, self.index_head_dim
    dev = hidden_states.device

    vis = attention_mask if attention_mask.dtype == torch.bool else attention_mask == 0
    v = vis[:, 0]                                   # (B, S, K)
    K = v.shape[-1]
    ar = torch.arange(K, device=dev)
    cnt = v.sum(-1)                                 # (B, S) visible tokens per query
    first = torch.where(v, ar, K).amin(-1)          # (B, S)
    last = torch.where(v, ar, -1).amax(-1)
    s = first.amin(-1)                              # (B,) block-grid start per batch row
    contiguous = ((last - first + 1) == cnt) | (cnt == 0)
    same_start = (first == s[:, None]) | (cnt == 0)
    if not bool((contiguous & same_start).all()):
        return _ORIG(self, hidden_states, position_embeddings, attention_mask, past_key_values)

    full_cos, full_sin = position_embeddings
    cur_cos, cur_sin = full_cos[:, -S:, :], full_sin[:, -S:, :]
    qk = self.index_qk_proj(hidden_states)
    q, token_k = torch.split(qk, [self.index_n_heads * D, self.index_kv_heads * D], dim=-1)
    q = self.q_layernorm(q.reshape(B, S, -1, D))
    q = mq.apply_rotary_pos_emb(q, cos=cur_cos, sin=cur_sin, unsqueeze_dim=2)   # (B, S, H, D)
    raw_keys = token_k.reshape(B, S, -1, D).squeeze(2)
    if past_key_values is not None:
        raw_keys = past_key_values.update_indexer(raw_keys, self.layer_idx)
    assert raw_keys.shape[1] == K, (raw_keys.shape, K)

    # --- block grid per batch row: block j covers tokens s_b + j*R + r ------
    nblk = torch.div(K - s, R, rounding_mode="floor")          # (B,)
    J = int(nblk.max())
    j = torch.arange(J, device=dev)
    r = torch.arange(R, device=dev)
    tok = (s[:, None, None] + j[None, :, None] * R + r[None, None, :]).clamp(max=K - 1)  # (B, J, R)
    kg = raw_keys.gather(1, tok.reshape(B, J * R, 1).expand(-1, -1, D)).view(B, J, R, D)
    pooled = self.k_layernorm(kg.float().mean(2).to(raw_keys.dtype))                     # (B, J, D)
    gstart = tok[:, :, 0]
    rot = full_cos.shape[-1]
    cos_b = full_cos.gather(1, gstart.unsqueeze(-1).expand(-1, -1, rot))
    sin_b = full_sin.gather(1, gstart.unsqueeze(-1).expand(-1, -1, rot))
    blk_keys = mq.apply_rotary_pos_emb(pooled.unsqueeze(2), cos=cos_b, sin=sin_b, unsqueeze_dim=2).squeeze(2)

    # --- scores: relu(q_h . k_j) summed over heads, per (query, block) ------
    H = q.shape[2]
    scores = torch.bmm(q.float().reshape(B, S * H, D), blk_keys.float().transpose(1, 2))  # (B, S*H, J)
    scores = torch.relu(scores).view(B, S, H, J).sum(2) / math.sqrt(D)                    # (B, S, J)

    C = torch.div(cnt, R, rounding_mode="floor")                 # (B, S) complete blocks per query
    eligible = j[None, None, :] < C[:, :, None]
    scores = scores.masked_fill(~eligible, float("-inf"))
    k = min(self.block_topk, J)
    top = scores.topk(k, dim=-1).indices                          # (B, S, k)
    sel_ok = top < C[:, :, None]
    tok_sel = s[:, None, None, None] + top[..., None] * R + r[None, None, None, :]        # (B, S, k, R)
    tok_sel = torch.where(sel_ok[..., None], tok_sel, K).reshape(B, S, k * R)
    # partial tail block: tokens s + C*R + r (r < R-1) that are visible
    rt = torch.arange(R - 1, device=dev)
    tail = s[:, None, None] + C[:, :, None] * R + rt[None, None, :]
    tail = torch.where((C[:, :, None] * R + rt[None, None, :]) < cnt[:, :, None], tail, K)

    idx = torch.cat([tok_sel, tail], dim=-1)
    mask = torch.zeros((B, S, K + 1), device=attention_mask.device, dtype=torch.bool)
    mask = mask.scatter(-1, idx.to(attention_mask.device), True)[..., :K].unsqueeze(1)
    if attention_mask.is_floating_point():
        min_dtype = torch.finfo(attention_mask.dtype).min
        mask = torch.where(mask, attention_mask.new_zeros(()), min_dtype)
    return mask


def patch_qsa_indexer() -> None:
    if mq.Qwen4ExpTextQSAIndexer.forward is not _fast_forward:
        mq.Qwen4ExpTextQSAIndexer.forward = _fast_forward
        print("[qsa] Qwen4ExpTextQSAIndexer.forward -> vectorised implementation", flush=True)


def unpatch_qsa_indexer() -> None:
    mq.Qwen4ExpTextQSAIndexer.forward = _ORIG
