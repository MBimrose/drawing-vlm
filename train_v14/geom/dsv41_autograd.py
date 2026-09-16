"""Autograd formulas for the Hub `finegrained-fp8` kernels so LoRA can train through DeepSeek's
frozen FP8 / MXFP4 weights.

transformers' multi-GPU FP8 path runs every quantized linear and every expert projection
through `kernels-community/finegrained-fp8` custom ops (`torch.ops._finegrained_fp8_cuda_*`),
which ship no backward: the first `.backward()` dies with "no autograd formula was registered".
The weights are frozen, so the only gradient we need is w.r.t. the activation input, and that is
a plain matmul against the dequantized weight:

    forward   C = A @ B.T         (B: (N, K) quantized, dequantized here to bf16)
    backward  dA = dC @ B_deq     (dB, dBs: None)

Registered for the 2D, grouped (tokens sorted by expert, `offsets`/`tokens_per_expert`) and
batched (`expert_ids` per row) variants of the block-scaled FP8 op and the MX (UE8M0 group-32,
E4M3 or packed E2M1) op. Dequantization follows the kernel's own conventions: block scales
broadcast over [block_n, block_k] tiles, UE8M0 decoded as 2^(exp-127), E2M1 nibbles low-first
(`E2M1_LOW_FIRST`; `selftest` checks it against the kernel forward).

Usage: `import dsv41_autograd; dsv41_autograd.register()` before the first forward. Exact
gradients cost one bf16 dequant per op per backward (transient, largest ~1.3 GB for lm_head);
experts are looped per expert with tokens.
"""
from __future__ import annotations

import torch

E2M1_LOW_FIRST = True   # element 2i in the low nibble of byte i (OCP MX / tl.dot_scaled convention)
_E2M1_MAG = torch.tensor([0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0])
_REGISTERED = False
_NS = None


def _ops_namespace():
    global _NS
    if _NS is None:
        cands = [n for n in dir(torch.ops) if n.startswith("_finegrained_fp8_")]
        if not cands:   # importing the kernel defines the namespace
            from transformers.integrations.finegrained_fp8 import load_finegrained_fp8_kernel
            load_finegrained_fp8_kernel()
            cands = [n for n in dir(torch.ops) if n.startswith("_finegrained_fp8_")]
        if not cands:
            raise RuntimeError("finegrained-fp8 op namespace not found; load the Hub kernel first")
        _NS = cands[0]
    return _NS


# ---------------------------------------------------------------- dequantization
def decode_scale(s: torch.Tensor) -> torch.Tensor:
    """fp32 scales pass through; UE8M0 (float8_e8m0fnu or uint8 exponent bits) -> 2^(exp-127)."""
    if s.dtype in (torch.float8_e8m0fnu, torch.uint8):
        return ((s.view(torch.uint8).to(torch.int32)) << 23).view(torch.float32)
    return s.to(torch.float32)


def dequant_block_fp8(B: torch.Tensor, Bs: torch.Tensor, block_size, out_dtype=torch.bfloat16) -> torch.Tensor:
    """(N, K) e4m3 with (N//bn, K//bk) block scales -> (N, K) out_dtype."""
    bn, bk = int(block_size[0]), int(block_size[1])
    N, K = B.shape
    s = decode_scale(Bs)
    s = s.repeat_interleave(bn, dim=0)[:N].repeat_interleave(bk, dim=1)[:, :K]
    return (B.to(torch.float32) * s).to(out_dtype)


def dequant_tensor_fp8(B: torch.Tensor, Bs: torch.Tensor, out_dtype=torch.bfloat16) -> torch.Tensor:
    return (B.to(torch.float32) * decode_scale(Bs).reshape(-1)[0]).to(out_dtype)


def unpack_e2m1(Bp: torch.Tensor) -> torch.Tensor:
    """(N, K//2) packed E2M1 bytes -> (N, K) float32 values."""
    u = Bp.view(torch.uint8)
    lo, hi = (u & 0x0F), (u >> 4)
    nib = torch.stack([lo, hi] if E2M1_LOW_FIRST else [hi, lo], dim=-1).reshape(u.shape[0], -1)
    mag = _E2M1_MAG.to(u.device)[(nib & 0x7).long()]
    return torch.where((nib & 0x8) != 0, -mag, mag)


def dequant_mx(B: torch.Tensor, Bs: torch.Tensor, out_dtype=torch.bfloat16) -> torch.Tensor:
    """MX weight: e4m3 (N, K) or packed e2m1 int8 (N, K//2), UE8M0 scales (N, K//32) -> (N, K)."""
    vals = unpack_e2m1(B) if B.dtype in (torch.int8, torch.uint8) else B.to(torch.float32)
    s = decode_scale(Bs).repeat_interleave(32, dim=1)[:, : vals.shape[1]]
    return (vals * s).to(out_dtype)


def _is_mx(B, Bs):
    return Bs.dtype in (torch.float8_e8m0fnu, torch.uint8) and Bs.shape[-1] * 32 == (B.shape[-1] * (2 if B.dtype in (torch.int8, torch.uint8) else 1))


def dequant_any(B, Bs, block_size=None, out_dtype=torch.bfloat16):
    if _is_mx(B, Bs):
        return dequant_mx(B, Bs, out_dtype)
    if block_size is None or (tuple(block_size) == tuple(B.shape[-2:])):
        return dequant_tensor_fp8(B, Bs, out_dtype)
    return dequant_block_fp8(B, Bs, block_size, out_dtype)


# ---------------------------------------------------------------- backward helpers
def _grad_2d(grad_out, B, Bs, block_size):
    W = dequant_any(B, Bs, block_size, torch.bfloat16)            # (N, K)
    g = grad_out.reshape(-1, grad_out.shape[-1]).to(torch.bfloat16)
    dA = g @ W                                                        # (M, K)
    return dA.reshape(*grad_out.shape[:-1], W.shape[1])


def _grad_grouped(grad_out, B, Bs, offsets, tokens_per_expert, block_size):
    """A (S, K) sorted by expert; rows [offsets[e]-tokens[e], offsets[e]) belong to expert e."""
    S = grad_out.shape[0]
    dA = torch.zeros(S, B.shape[-1] * (2 if B.dtype in (torch.int8, torch.uint8) else 1),
                     dtype=torch.bfloat16, device=grad_out.device)
    off = offsets.to("cpu").tolist(); cnt = tokens_per_expert.to("cpu").tolist()
    g = grad_out.to(torch.bfloat16)
    for e, (o, c) in enumerate(zip(off, cnt)):
        c = int(c)
        if c <= 0:
            continue
        o = int(o); lo = o - c
        if lo >= S:
            break
        hi = min(o, S)
        W = dequant_any(B[e], Bs[e], block_size, torch.bfloat16)
        dA[lo:hi] = g[lo:hi] @ W
    return dA


def _grad_batched(grad_out, B, Bs, expert_ids, block_size):
    S = grad_out.shape[0]
    dA = torch.zeros(S, B.shape[-1] * (2 if B.dtype in (torch.int8, torch.uint8) else 1),
                     dtype=torch.bfloat16, device=grad_out.device)
    g = grad_out.to(torch.bfloat16)
    ids = expert_ids.to("cpu").long()
    for e in ids.unique().tolist():
        if e >= B.shape[0]:
            continue
        rows = (ids == e).nonzero().flatten().to(grad_out.device)
        W = dequant_any(B[e], Bs[e], block_size, torch.bfloat16)
        dA[rows] = g[rows] @ W
    return dA


def _cast_like(dA, A):
    return dA.to(A.dtype) if dA.dtype != A.dtype else dA


# ---------------------------------------------------------------- registration
def register():
    """Attach backward formulas to every finegrained-fp8 op present (idempotent)."""
    global _REGISTERED
    if _REGISTERED:
        return
    ns = _ops_namespace()
    present = set(dir(getattr(torch.ops, ns)))

    def reg(name, setup, backward):
        if name not in present:
            return
        try:
            torch.library.register_autograd(f"{ns}::{name}", backward, setup_context=setup)
        except RuntimeError as e:   # already has autograd (a newer kernel) -> keep theirs
            if "already" not in str(e):
                raise

    # -- 2D: (A, B, Bs, block_size, output_dtype)
    def setup_2d(ctx, inputs, output):
        A, B, Bs, block_size, _ = inputs
        ctx.save_for_backward(B, Bs); ctx.block_size = list(block_size); ctx.a_dtype = A.dtype
    def bw_2d(ctx, grad):
        B, Bs = ctx.saved_tensors
        return _grad_2d(grad, B, Bs, ctx.block_size).to(ctx.a_dtype), None, None, None, None
    reg("w8a8_block_dynamic_fp8_matmul", setup_2d, bw_2d)

    # -- 2D static: (A, B, Bs, As, block_size, output_dtype)
    def setup_2d_static(ctx, inputs, output):
        A, B, Bs, As, block_size, _ = inputs
        ctx.save_for_backward(B, Bs); ctx.block_size = list(block_size); ctx.a_dtype = A.dtype
    def bw_2d_static(ctx, grad):
        B, Bs = ctx.saved_tensors
        return _grad_2d(grad, B, Bs, ctx.block_size).to(ctx.a_dtype), None, None, None, None, None
    reg("w8a8_block_static_fp8_matmul", setup_2d_static, bw_2d_static)

    # -- 2D tensor-wide / MX: (A, B, Bs, output_dtype)
    def setup_2d_nb(ctx, inputs, output):
        A, B, Bs, _ = inputs
        ctx.save_for_backward(B, Bs); ctx.a_dtype = A.dtype
    def bw_2d_nb(ctx, grad):
        B, Bs = ctx.saved_tensors
        return _grad_2d(grad, B, Bs, None).to(ctx.a_dtype), None, None, None
    reg("w8a8_tensor_dynamic_fp8_matmul", setup_2d_nb, bw_2d_nb)
    reg("mxfp_dynamic_matmul", setup_2d_nb, bw_2d_nb)

    # -- grouped block: (A, B, Bs, offsets, tokens_per_expert, block_size, output_dtype)
    def setup_g(ctx, inputs, output):
        A, B, Bs, offsets, tpe, block_size, _ = inputs
        ctx.save_for_backward(B, Bs, offsets, tpe); ctx.block_size = list(block_size); ctx.a_dtype = A.dtype
    def bw_g(ctx, grad):
        B, Bs, offsets, tpe = ctx.saved_tensors
        return _grad_grouped(grad, B, Bs, offsets, tpe, ctx.block_size).to(ctx.a_dtype), None, None, None, None, None, None
    reg("w8a8_block_dynamic_fp8_matmul_grouped", setup_g, bw_g)

    # -- grouped tensor-wide / MX: (A, B, Bs, offsets, tokens_per_expert, output_dtype)
    def setup_g_nb(ctx, inputs, output):
        A, B, Bs, offsets, tpe, _ = inputs
        ctx.save_for_backward(B, Bs, offsets, tpe); ctx.a_dtype = A.dtype
    def bw_g_nb(ctx, grad):
        B, Bs, offsets, tpe = ctx.saved_tensors
        return _grad_grouped(grad, B, Bs, offsets, tpe, None).to(ctx.a_dtype), None, None, None, None, None
    reg("w8a8_tensor_dynamic_fp8_matmul_grouped", setup_g_nb, bw_g_nb)
    reg("mxfp_dynamic_matmul_grouped", setup_g_nb, bw_g_nb)

    # -- batched block: (A, B, Bs, expert_ids, block_size, output_dtype)
    def setup_b(ctx, inputs, output):
        A, B, Bs, ids, block_size, _ = inputs
        ctx.save_for_backward(B, Bs, ids); ctx.block_size = list(block_size); ctx.a_dtype = A.dtype
    def bw_b(ctx, grad):
        B, Bs, ids = ctx.saved_tensors
        return _grad_batched(grad, B, Bs, ids, ctx.block_size).to(ctx.a_dtype), None, None, None, None, None
    reg("w8a8_block_dynamic_fp8_matmul_batched", setup_b, bw_b)

    # -- batched tensor-wide / MX: (A, B, Bs, expert_ids, output_dtype)
    def setup_b_nb(ctx, inputs, output):
        A, B, Bs, ids, _ = inputs
        ctx.save_for_backward(B, Bs, ids); ctx.a_dtype = A.dtype
    def bw_b_nb(ctx, grad):
        B, Bs, ids = ctx.saved_tensors
        return _grad_batched(grad, B, Bs, ids, None).to(ctx.a_dtype), None, None, None, None
    reg("w8a8_tensor_dynamic_fp8_matmul_batched", setup_b_nb, bw_b_nb)
    reg("mxfp_dynamic_matmul_batched", setup_b_nb, bw_b_nb)

    _REGISTERED = True
    return ns


# ---------------------------------------------------------------- self-test
def selftest(B: torch.Tensor, Bs: torch.Tensor, block_size=None, M: int = 64, label: str = "") -> dict:
    """Kernel forward vs dequantized matmul, and the registered backward vs the reference dA.
    Returns relative errors; run on a GPU with real checkpoint tensors."""
    from transformers.integrations.finegrained_fp8 import load_finegrained_fp8_kernel
    k = load_finegrained_fp8_kernel()
    dev = B.device
    K = B.shape[-1] * (2 if B.dtype in (torch.int8, torch.uint8) else 1)
    A = torch.randn(M, K, device=dev, dtype=torch.bfloat16, requires_grad=True)
    W = dequant_any(B, Bs, block_size, torch.float32)
    ref = A.detach().float() @ W.t()
    out = k.matmul(A, B, Bs, block_size, torch.bfloat16)
    fwd_err = ((out.float() - ref).norm() / ref.norm()).item()
    g = torch.randn_like(out)
    out.backward(g)
    dA_ref = g.float() @ W
    bwd_err = ((A.grad.float() - dA_ref).norm() / dA_ref.norm()).item()
    res = {"label": label, "shape": tuple(B.shape), "dtype": str(B.dtype), "scale_dtype": str(Bs.dtype),
           "fwd_rel_err": fwd_err, "bwd_rel_err": bwd_err}
    print("[autograd selftest]", res, flush=True)
    return res
