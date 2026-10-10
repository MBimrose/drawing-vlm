"""Worker-side hook functions for dsv41_vllm_layerdump.py (importable, so collective_rpc can pickle them by reference)."""
import os


def reg(model):
    store = {}
    lm = model.language_model if hasattr(model, "language_model") else model
    layers = lm.model.layers
    for i, l in enumerate(layers):
        if not hasattr(l, "attn"):
            continue
        l.attn.register_forward_pre_hook(lambda m, a, i=i: store.__setitem__(f"attn_in.{i}", a[1].detach().float().cpu()))
        l.ffn.register_forward_pre_hook(lambda m, a, i=i: store.__setitem__(f"ffn_in.{i}", a[0].detach().float().cpu()))
        l.attn.register_forward_hook(lambda m, a, o, i=i: store.__setitem__(f"attn_out.{i}", (o[0] if isinstance(o, tuple) else o).detach().float().cpu()))
        l.ffn.register_forward_hook(lambda m, a, o, i=i: store.__setitem__(f"ffn_out.{i}", (o[0] if isinstance(o, tuple) else o).detach().float().cpu()))
    model._dbg = store
    return [type(l).__name__ for l in layers][:2] + [type(layers[0].attn).__name__, type(layers[0].ffn).__name__,
            bool(getattr(layers[0], "use_sequence_parallel", False))]



def dump(model):
    import torch, torch.distributed as dist
    r = dist.get_rank() if dist.is_initialized() else 0
    torch.save(model._dbg, os.environ['VDUMP_OUT'] + '.rank%d.pt' % r)
    return (r, {k: tuple(v.shape) for k, v in list(model._dbg.items())[:4]})
