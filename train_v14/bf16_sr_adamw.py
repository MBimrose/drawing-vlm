"""AdamW for pure-bf16 FSDP2 training: fp32 moment estimates, bf16 parameters
updated with STOCHASTIC ROUNDING so lr~1e-6 updates are not lost to bf16's
2^-8 resolution. No torch.compile, no tensor subclasses (torchao 0.18's
compiled AdamW8bit fails to trace on torch 2.13 + DTensor). States are stored
as DTensors matching the parameter placements so DCP optimizer checkpoints
work unchanged. Cost: 8 bytes/param of states (117 GB/rank for Flash-Next)."""
from __future__ import annotations

import math

import torch
from torch.distributed.tensor import DTensor


def stochastic_round_to_bf16(x: torch.Tensor) -> torch.Tensor:
    """fp32 -> bf16 with probability proportional to the truncated bits."""
    bits = x.view(torch.int32)
    rnd = torch.randint(0, 1 << 16, bits.shape, device=x.device, dtype=torch.int32)
    bits = (bits + rnd) & -65536          # add noise, keep the upper 16 bits
    return bits.view(torch.float32).to(torch.bfloat16)


def _like(p: torch.Tensor, local: torch.Tensor) -> torch.Tensor:
    if isinstance(p, DTensor):
        return DTensor.from_local(local, p.device_mesh, p.placements,
                                  run_check=False, shape=p.shape, stride=p.stride())
    return local


def _local(t: torch.Tensor) -> torch.Tensor:
    return t.to_local() if isinstance(t, DTensor) else t


class Bf16SRAdamW(torch.optim.Optimizer):
    def __init__(self, params, lr=1e-5, betas=(0.9, 0.999), eps=1e-8, weight_decay=0.0):
        super().__init__(params, dict(lr=lr, betas=betas, eps=eps, weight_decay=weight_decay))

    @torch.no_grad()
    def step(self, closure=None):
        loss = closure() if closure is not None else None
        for group in self.param_groups:
            lr = float(group["lr"])
            b1, b2 = group["betas"]
            eps, wd = group["eps"], group["weight_decay"]
            for p in group["params"]:
                if p.grad is None:
                    continue
                pl, gl = _local(p), _local(p.grad)
                st = self.state[p]
                if not st:
                    st["step"] = torch.zeros((), dtype=torch.float32)
                    st["exp_avg"] = _like(p, torch.zeros_like(pl, dtype=torch.float32))
                    st["exp_avg_sq"] = _like(p, torch.zeros_like(pl, dtype=torch.float32))
                st["step"] += 1
                t = float(st["step"])
                m, v = _local(st["exp_avg"]), _local(st["exp_avg_sq"])
                g = gl.float()
                m.mul_(b1).add_(g, alpha=1 - b1)
                v.mul_(b2).addcmul_(g, g, value=1 - b2)
                bc1, bc2 = 1 - b1 ** t, 1 - b2 ** t
                denom = v.sqrt().div_(math.sqrt(bc2)).add_(eps)
                new = pl.float()
                if wd:
                    new.mul_(1 - lr * wd)
                new.addcdiv_(m, denom, value=-lr / bc1)
                pl.copy_(stochastic_round_to_bf16(new))
        return loss
