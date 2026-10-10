"""Fixes for the transformers DeepSeek-V4.1 draft (PR #48768 head a290b39) when it is loaded with device_map
(2026-10-07, DeepSeek GRPO parity work).

ROOT CAUSE of the HF-vs-vLLM gap: the sparse INDEXER never reached the attention. Each index-source layer calls
`self.indexer(hidden_states, q_residual, latent, group_positions, position_ids, cache_layer, shared)` with the CSA2
`shared` dict as a POSITIONAL argument; the indexer publishes its result only by writing `shared["topk_idx"]`
(+ `index_k`, `candidates`). Under device_map, accelerate's AlignDevicesHook on the indexer module runs
`send_to_device(args)`, which rebuilds every Mapping -> the indexer writes into a throw-away COPY. The model class's
`_skip_keys_device_placement = ["shared", ...]` protects only keyword arguments. Result: `topk_idx` is never set,
`selected_kv` stays None, and every compressed-attention layer (2-39) silently runs sliding-window-only (128 tokens):
HF NLL 2.06-2.55 vs vLLM 0.29-0.83 on identical tokens, top-1 agreement ~50%, gap growing with context.

fix_shared_dict_hooks(model): remove accelerate's per-module hooks from every module that receives `shared`
positionally (the indexers), after placing their parameters on their attention's device. Their inputs already live on
that device (the decoder layer's own hook moved them), so no device move is needed inside the layer."""
import torch


def fix_shared_dict_hooks(model, log=print):
    from accelerate.hooks import remove_hook_from_module
    n = 0
    for name, m in model.named_modules():
        if type(m).__name__ != "DeepseekV41Attention" or getattr(m, "indexer", None) is None:
            continue
        idx = m.indexer
        dev = m.q_a_proj.weight.device
        if hasattr(idx, "_hf_hook"):
            remove_hook_from_module(idx, recurse=True)
            n += 1
        for p in list(idx.parameters()) + list(idx.buffers()):
            if p.device != dev:
                p.data = p.data.to(dev)
    log(f"[fix] removed accelerate hooks from {n} indexer modules (shared-dict copy bug)")
    return n
