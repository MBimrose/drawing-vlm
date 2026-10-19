"""SFT entrypoint for Qwen3.8-27B on drawing -> (trace) -> build123d (v14).

Usage (via run.sh normally):
    accelerate launch --config_file configs/<accel>.yaml \
        train_sft_v14.py configs/<experiment>.yaml [--key=value ...]
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import torch
import yaml
from transformers import (
    AutoProcessor,
    Qwen3_5ForConditionalGeneration,
    Trainer,
    TrainerCallback,
    TrainingArguments,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collate_v14 import VLMCollator
from data_v14 import EvalDataset, EvalDatasetV2, build_mixed_v2, build_train_dataset


def _coerce(v: str):
    if v.lower() in {"true", "false"}:
        return v.lower() == "true"
    for cast in (int, float):
        try:
            return cast(v)
        except ValueError:
            pass
    return v


def _parse_overrides(argv: list[str]) -> dict:
    out = {}
    for a in argv:
        if a.startswith("--"):
            k, _, v = a[2:].partition("=")
            out[k] = _coerce(v) if v else True
    return out


def load_cfg(path: str, overrides: dict) -> dict:
    with open(path) as f:
        cfg = yaml.safe_load(f)
    cfg.update(overrides)
    return cfg


def find_vision_tower(model):
    for path in ("model.visual", "visual", "vision_tower", "vision_model"):
        obj = model
        try:
            for part in path.split("."):
                obj = getattr(obj, part)
            return path, obj
        except AttributeError:
            continue
    for name, mod in model.named_modules():
        if name.endswith("visual") or name.endswith("vision_tower"):
            return name, mod
    return None, None


def apply_vision_strategy(model, strategy: str):
    _, visual = find_vision_tower(model)
    if visual is None:
        raise RuntimeError("could not locate vision tower")
    for p in visual.parameters():
        p.requires_grad_(False)
    if strategy == "frozen":
        pass
    elif strategy == "projector":
        for name in ("merger", "deepstack_merger_list"):
            if hasattr(visual, name):
                for p in getattr(visual, name).parameters():
                    p.requires_grad_(True)
    elif strategy == "full":
        for p in visual.parameters():
            p.requires_grad_(True)
    elif strategy.startswith("last_"):
        n_last = int(strategy.split("_")[1])
        for blk in list(visual.blocks)[-n_last:]:
            for p in blk.parameters():
                p.requires_grad_(True)
        for name in ("merger", "deepstack_merger_list"):
            if hasattr(visual, name):
                for p in getattr(visual, name).parameters():
                    p.requires_grad_(True)
    else:
        raise ValueError(f"unknown vision_strategy {strategy!r}")
    n_t = sum(p.numel() for p in visual.parameters() if p.requires_grad)
    n_f = sum(p.numel() for p in visual.parameters() if not p.requires_grad)
    print(f"[vision] strategy={strategy} trainable={n_t/1e6:.1f}M frozen={n_f/1e6:.1f}M",
          flush=True)


def auto_lora_targets(model) -> list[str]:
    """Collect leaf names of every nn.Linear in the language model (covers the
    hybrid stack: full-attention q/k/v/o, Gated-DeltaNet in/out projections,
    and MLP gate/up/down). Excludes vision tower, lm_head, mtp, embeddings."""
    import torch.nn as nn

    _, visual = find_vision_tower(model)
    vis_ids = {id(m) for m in visual.modules()} if visual is not None else set()
    names = set()
    for fqn, mod in model.named_modules():
        if not isinstance(mod, nn.Linear):
            continue
        if id(mod) in vis_ids:
            continue
        low = fqn.lower()
        if "lm_head" in low or "mtp" in low or "embed" in low:
            continue
        names.add(fqn.rsplit(".", 1)[-1])
    out = sorted(names)
    print(f"[lora] auto target modules: {out}", flush=True)
    return out


def demote_persistent_buffers(model):
    """Make every persistent buffer non-persistent. FSDP2 only shards
    parameters; accelerate's cpu_ram_efficient_loading path assumes every
    state_dict entry is a DTensor and crashes on plain-tensor buffers
    (Qwen4Exp's ple.ple_embedding.* constants). Non-persistent buffers are
    captured and re-registered by accelerate itself. Only config-derived
    constants are affected, so nothing is lost from the adapter checkpoint."""
    n = 0
    for mod in model.modules():
        for name in list(mod._buffers):
            if name not in mod._non_persistent_buffers_set:
                mod._non_persistent_buffers_set.add(name)
                n += 1
    print(f"[model] demoted {n} persistent buffers to non-persistent", flush=True)


def maybe_wrap_lora(model, cfg):
    if not cfg.get("use_lora", False):
        return model
    from peft import LoraConfig, TaskType, get_peft_model
    if cfg.get("lora_init_adapter"):
        # warm start (2026-10-07, verifier v5): continue training an existing adapter instead of a fresh LoRA
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, cfg["lora_init_adapter"], is_trainable=True)
        print(f"[lora] warm start from {cfg['lora_init_adapter']}", flush=True)
        model.print_trainable_parameters()
        return model

    targets = cfg.get("lora_target_modules", "auto")
    if targets == "auto":
        targets = auto_lora_targets(model)
    lora_cfg = LoraConfig(
        r=int(cfg.get("lora_rank", 64)),
        lora_alpha=int(cfg.get("lora_alpha", 2 * int(cfg.get("lora_rank", 64)))),
        target_modules=targets,
        lora_dropout=float(cfg.get("lora_dropout", 0.05)),
        bias="none",
        task_type=TaskType.CAUSAL_LM,
    )
    model = get_peft_model(model, lora_cfg)
    model.print_trainable_parameters()
    return model


class ConfigToWandb(TrainerCallback):
    def __init__(self, cfg: dict):
        self.cfg = cfg

    def on_train_begin(self, args, state, control, **kwargs):
        if state.is_world_process_zero:
            try:
                import wandb
                if wandb.run is not None:
                    wandb.config.update({f"exp/{k}": v for k, v in self.cfg.items()},
                                        allow_val_change=True)
            except Exception:
                pass
        return control


class TorchaoSRTrainer(Trainer):
    """torchao AdamW8bit with bf16 stochastic rounding: 8-bit states and
    bf16 master params (no fp32 copy) — the only way a 126B-param full FT fits
    8 GPUs; stochastic rounding keeps lr~1e-6 updates from vanishing in bf16.
    Supports FSDP2 DTensor params; accelerate re-points the param groups."""

    kind = "torchao"

    def create_optimizer(self, model=None):
        if self.optimizer is None:
            m = model if model is not None else self.model
            params = [p for p in m.parameters() if p.requires_grad]
            kw = dict(lr=self.args.learning_rate,
                      betas=(self.args.adam_beta1, self.args.adam_beta2),
                      eps=self.args.adam_epsilon, weight_decay=self.args.weight_decay)
            if self.kind == "torchao":
                from torchao.optim import AdamW8bit
                self.optimizer = AdamW8bit(params, bf16_stochastic_round=True, **kw)
            else:
                from bf16_sr_adamw import Bf16SRAdamW
                self.optimizer = Bf16SRAdamW(params, **kw)
            n = sum(p.numel() for p in params)
            print(f"[optim] {type(self.optimizer).__name__} (bf16 stochastic rounding) "
                  f"over {n/1e9:.2f}B params", flush=True)
        return self.optimizer

    # Warm restart (2026-10-16): continue a cosine_with_min_lr schedule of `total` steps (warmup `warm`) from
    # global step `start` with a fresh optimizer, ramping linearly over the first `rewarm` steps so the
    # re-initialised Adam moments do not take full-size steps. Set by main() as (total, warm, start, rewarm, min_rate).
    lr_resume = None

    def create_scheduler(self, num_training_steps, optimizer=None):
        if self.lr_resume is None or self.lr_scheduler is not None:
            return super().create_scheduler(num_training_steps, optimizer)
        import math
        from torch.optim.lr_scheduler import LambdaLR
        total, warm, start, rewarm, min_rate = self.lr_resume

        def f(s):
            g = start + s
            if g < warm:
                base = g / max(1, warm)
            else:
                prog = (g - warm) / max(1, total - warm)
                base = min_rate + (1 - min_rate) * 0.5 * (1 + math.cos(math.pi * prog))
            return base * min(1.0, (s + 1) / max(1, rewarm))

        self.lr_scheduler = LambdaLR(optimizer if optimizer is not None else self.optimizer, f)
        self._created_lr_scheduler = True
        print(f"[lr] resume: cosine_with_min_lr over {total} (warmup {warm}) from step {start}, re-warm {rewarm}, "
              f"first lr {self.args.learning_rate * f(0):.3e}", flush=True)
        return self.lr_scheduler


class Bf16SRTrainer(TorchaoSRTrainer):
    kind = "bf16_sr"

def fsdp_lora_active() -> bool:
    return os.environ.get("ACCELERATE_USE_FSDP", "").lower() == "true"


def save_lora_adapter(model, out_dir: str) -> None:
    """Gather the trainable (LoRA) params from FSDP2 DTensors on every rank
    (collective: all ranks must call this) and write a standard PEFT adapter
    from rank 0. trainer.save_model() writes nothing for PEFT under FSDP2
    SHARDED_STATE_DICT, and Trainer's own checkpoint would DCP-dump the whole
    sharded base model (250 GB) at every improvement."""
    import torch.distributed as dist
    rank = dist.get_rank() if dist.is_initialized() else 0
    sd = {}
    for name, p in model.named_parameters():
        if not p.requires_grad:
            continue
        t = p.full_tensor() if hasattr(p, "full_tensor") else p.detach()
        if rank == 0:
            # FSDP activation checkpointing leaks its wrapper into the FQN
            sd[name.replace("._checkpoint_wrapped_module", "")] = t.detach().to(torch.bfloat16).cpu()
    if rank == 0:
        os.makedirs(out_dir, exist_ok=True)
        model.save_pretrained(out_dir, state_dict=sd)
        n = sum(v.numel() for v in sd.values())
        print(f"[lora_save] {len(sd)} tensors / {n/1e6:.1f}M params -> {out_dir}", flush=True)
    if dist.is_initialized():
        dist.barrier()


def save_trainable_subset(model, out_dir: str, processor, model_id: str) -> None:
    """Partial-FT checkpoint (2026-10-15, Nemotron with frozen routed experts): gather only the trained params
    (bf16, ~16 GB instead of 243 GB) and write them through save_pretrained so the checkpoint key names are the
    base checkpoint's. `geom/nemotron_merge.py` overlays them on the base shards for serving. Collective."""
    import json as _json
    save_lora_adapter(model, out_dir)
    import torch.distributed as dist
    if (dist.get_rank() if dist.is_initialized() else 0) == 0:
        processor.save_pretrained(out_dir)
        with open(os.path.join(out_dir, "TRAINED_SUBSET.json"), "w") as f:
            _json.dump({"base_model": model_id}, f)
        print(f"[subset_save] trained subset of {model_id} -> {out_dir}", flush=True)
    if dist.is_initialized():
        dist.barrier()


def save_full_model(model, out_dir: str, processor, model_id: str, cfg: dict) -> None:
    """Gather the sharded bf16 model to rank 0 and write an HF directory
    (no optimizer states: a DCP checkpoint of a full FT would be model +
    fp32 Adam moments, ~1.2 TB for Flash-Next). Collective — all ranks call."""
    import torch.distributed as dist
    from torch.distributed.checkpoint.state_dict import StateDictOptions, get_model_state_dict
    rank = dist.get_rank() if dist.is_initialized() else 0
    full_state = get_model_state_dict(
        model, options=StateDictOptions(full_state_dict=True, cpu_offload=True))
    if rank == 0:
        os.makedirs(out_dir, exist_ok=True)
        # Saved artifacts are for inference: write use_cache=True even though the
        # live model must keep it off (activation checkpointing). Restored below
        # so training continues unchanged after a best-model save.
        flipped = []
        for c in [model.config, getattr(model.config, "text_config", None),
                  getattr(model, "generation_config", None)]:
            if c is not None and getattr(c, "use_cache", None) is False:
                c.use_cache = True
                flipped.append(c)
        try:
            model.save_pretrained(out_dir, state_dict=full_state, safe_serialization=True)
        finally:
            for c in flipped:
                c.use_cache = False
        processor.save_pretrained(out_dir)
        if cfg.get("mmap_ngram_embedding", False):
            from flashnext_ple import reattach_ngram_shards
            reattach_ngram_shards(model_id, out_dir)
        print(f"[full_save] model saved to {out_dir}", flush=True)
    del full_state
    if dist.is_initialized():
        dist.barrier()


class ParamProbe(TrainerCallback):
    """Debug (2026-10-15): does the optimizer hold the live (FSDP2-sharded) trainable params, and do they move?
    Prints, per step on rank 0: #trainable model params, #optimizer params, #model params found in the optimizer
    by identity, and the local-shard |sum| / dtype of a few named params."""

    def __init__(self, names=("lm_head", "norm_f", "layers.1.mixer.in_proj", "vision_projector.mlp1.linear1")):
        self.names = names
        self.prev = {}

    def on_step_end(self, args, state, control, model=None, optimizer=None, **kwargs):
        if model is None:
            return control
        tr = [(n, p) for n, p in model.named_parameters() if p.requires_grad]
        opt_ids = set()
        if optimizer is not None:
            for g in optimizer.param_groups:
                opt_ids.update(id(p) for p in g["params"])
        match = sum(1 for _, p in tr if id(p) in opt_ids)
        msgs = []
        for key in self.names:
            for n, p in tr:
                if key in n:
                    t = p.to_local() if hasattr(p, "to_local") else p
                    s = float(t.detach().double().abs().sum())
                    d = s - self.prev.get(n, s)
                    self.prev[n] = s
                    msgs.append(f"{n.split('.')[-2]}.{n.split('.')[-1]}:{str(t.dtype)[6:]} {s:.6e} (d {d:+.3e})")
                    break
        if state.is_world_process_zero:
            print(f"[probe] step {state.global_step}: trainable {len(tr)} opt {len(opt_ids)} in-opt {match} | "
                  + " | ".join(msgs), flush=True)
        return control


class BroadcastBuffers(TrainerCallback):
    """cpu_ram_efficient_loading safety (2026-10-15): only rank 0 holds real weights at load; FSDP2 broadcasts the
    parameters, but buffers (demoted to non-persistent so accelerate does not crash on them) keep each rank's
    placeholder values. Checkpoint-loaded buffers such as the Nemotron router's e_score_correction_bias would then
    be garbage on ranks 1..N. Broadcast every buffer from rank 0 once, before the first step, and log a checksum."""

    def on_train_begin(self, args, state, control, model=None, **kwargs):
        import torch.distributed as dist
        if model is None or not dist.is_initialized():
            return control
        n, tot = 0, 0.0
        for name, b in model.named_buffers():
            if b is None or not torch.is_tensor(b):
                continue
            t = b.to_local() if hasattr(b, "to_local") else b
            if t.device.type != "cuda":
                continue
            dist.broadcast(t, src=0)
            n += 1
            if t.is_floating_point():
                tot += float(t.double().abs().sum())
        print(f"[buffers] rank {dist.get_rank()}: broadcast {n} buffers from rank 0, |sum| {tot:.6e}", flush=True)
        return control


class RouterLoadMonitor(TrainerCallback):
    """MoE routing health (2026-10-15, Nemotron full FT). Forward hooks on every *TopkRouter count the experts
    each token is routed to; every `every` steps the counts are summed over ranks and per-layer load spread is
    logged: max/mean expert load, coefficient of variation, share of experts with no tokens. (Activation
    checkpointing re-runs the router in the recompute, which doubles every count alike; the ratios are unchanged.)
    The first logged window is the baseline. If `stop_ratio` > 0 and any layer's max/mean load exceeds
    max(stop_ratio x its baseline, stop_floor), or its dead-expert share rises by > stop_dead, training stops
    (routing collapse)."""

    def __init__(self, model, every: int = 10, stop_ratio: float = 3.0, stop_floor: float = 20.0,
                 stop_dead: float = 0.25):
        self.every, self.stop_ratio, self.stop_floor, self.stop_dead = every, stop_ratio, stop_floor, stop_dead
        self.counts: dict[int, torch.Tensor] = {}
        self.base = None
        self.n_layers = 0
        for name, mod in model.named_modules():
            if type(mod).__name__.endswith("TopkRouter"):
                i = self.n_layers
                self.n_layers += 1
                mod.register_forward_hook(self._hook(i, int(getattr(mod, "num_experts", 0))))
        print(f"[router] monitoring {self.n_layers} routers every {every} steps", flush=True)

    def _hook(self, i: int, n_exp: int):
        # index_add_ into a preallocated per-layer counter: no host sync (torch.bincount on CUDA reads the input's
        # max back to size its output, i.e. one stall per router per forward; 2026-10-16 py-spy put ~30% of
        # rank 0's main-thread samples on that line).
        assert n_exp > 0, "router without num_experts"

        def h(mod, inp, out):
            idx = out[2].detach().reshape(-1).long()
            c = self.counts.get(i)
            if c is None:
                c = self.counts[i] = torch.zeros(n_exp, dtype=torch.int64, device=idx.device)
            c.index_add_(0, idx, torch.ones_like(idx))
        return h

    def on_step_end(self, args, state, control, **kwargs):
        if not self.n_layers or state.global_step % self.every != 0 or not self.counts:
            return control
        import torch.distributed as dist
        dev = next(iter(self.counts.values())).device
        C = torch.stack([self.counts.get(i, torch.zeros_like(next(iter(self.counts.values()))))
                         for i in range(self.n_layers)]).to(dev).double()
        if dist.is_initialized():
            dist.all_reduce(C)
        for c in self.counts.values():
            c.zero_()
        mean = C.mean(dim=1, keepdim=True).clamp_min(1e-9)
        mx = (C.max(dim=1).values / mean.squeeze(1)).cpu()
        cv = (C.std(dim=1) / mean.squeeze(1)).cpu()
        dead = (C == 0).double().mean(dim=1).cpu()
        if self.base is None:
            self.base = (mx.clone(), dead.clone())
        bmx, bdead = self.base
        worst = int(torch.argmax(mx / bmx))
        msg = (f"[router] step {state.global_step}: max/mean load median {mx.median():.2f} max {mx.max():.2f} "
               f"(L{int(mx.argmax())}), cv median {cv.median():.2f}, dead-expert share mean {dead.mean():.3f} "
               f"max {dead.max():.3f}; worst vs baseline L{worst} {mx[worst]:.2f}/{bmx[worst]:.2f}")
        collapse = self.stop_ratio > 0 and bool(
            ((mx > torch.maximum(self.stop_ratio * bmx, torch.full_like(bmx, self.stop_floor))) |
             (dead - bdead > self.stop_dead)).any())
        if state.is_world_process_zero:
            print(msg + ("  ** ROUTING COLLAPSE -> stopping **" if collapse else ""), flush=True)
            try:
                import wandb
                if wandb.run is not None:
                    wandb.log({"router/maxmean_median": float(mx.median()), "router/maxmean_max": float(mx.max()),
                               "router/cv_median": float(cv.median()), "router/dead_mean": float(dead.mean())},
                              step=state.global_step)
            except Exception:
                pass
        if collapse:
            control.should_training_stop = True
        return control


class StepTimer(TrainerCallback):
    """Throughput diagnostics (2026-10-16, Nemotron full FT slowed from 18 to 35-55 s/step with no outside cause).
    Each step, on every rank: wall time, the time to drain the rank's own GPU queue at step end (`drain`), and
    the time then spent waiting for the other ranks at a tiny all_reduce (`wait`; the straggler waits least),
    plus the tokens the rank processed (`tok_buf`, filled by the loss function) and caching-allocator counters.
    Every `every` steps the per-rank window means are gathered and rank 0 prints them."""

    STATS = ("num_alloc_retries", "num_device_alloc", "num_device_free", "num_sync_all_streams")

    def __init__(self, tok_buf: list, every: int = 10):
        self.tok_buf, self.every = tok_buf, every
        self.rows = []
        self.t0 = None
        self.prev = None

    def on_step_begin(self, args, state, control, **kwargs):
        self.t0 = __import__("time").perf_counter()
        return control

    def on_step_end(self, args, state, control, **kwargs):
        import time
        import torch.distributed as dist
        if self.t0 is None:
            return control
        t1 = time.perf_counter()
        torch.cuda.synchronize()
        t2 = time.perf_counter()
        dev = torch.device("cuda", torch.cuda.current_device())
        if dist.is_initialized():
            dist.all_reduce(torch.zeros(1, device=dev))
            torch.cuda.synchronize()
        t3 = time.perf_counter()
        tok = sum(self.tok_buf)
        self.tok_buf.clear()
        self.rows.append((t3 - self.t0, t2 - t1, t3 - t2, tok))
        if state.global_step % self.every:
            return control
        ms = torch.cuda.memory_stats()
        cur = [float(ms.get(k, 0)) for k in self.STATS]
        delta = [c - p for c, p in zip(cur, self.prev)] if self.prev else [0.0] * len(cur)
        self.prev = cur
        n = len(self.rows)
        mean = [sum(r[j] for r in self.rows) / n for j in range(4)]
        self.rows = []
        v = torch.tensor(mean + delta + [torch.cuda.memory_reserved() / 2**30], device=dev, dtype=torch.float64)
        if dist.is_initialized():
            out = [torch.zeros_like(v) for _ in range(dist.get_world_size())]
            dist.all_gather(out, v)
        else:
            out = [v]
        if state.is_world_process_zero:
            M = torch.stack(out).cpu()
            per = lambda j, f: " ".join(f.format(x) for x in M[:, j].tolist())
            print(f"[timing] step {state.global_step}: {M[0, 0]:.1f} s/step | drain {per(1, '{:.1f}')} | "
                  f"wait {per(2, '{:.1f}')} | tok/step {per(3, '{:.0f}')} | alloc_retries {per(4, '{:.0f}')} | "
                  f"dev_alloc {per(5, '{:.0f}')} dev_free {per(6, '{:.0f}')} | reserved GB {per(8, '{:.0f}')}",
                  flush=True)
        return control


class EvalLossCallback(TrainerCallback):
    """Fixed-set eval loss every `every` steps. All ranks forward the same
    batches (safe under FSDP/DDP); rank 0 logs val/loss to wandb.

    With save_best=True, an improved val/loss triggers a checkpoint save
    (control.should_save). Combined with save_strategy="no" and
    save_total_limit=1, exactly one checkpoint — the best so far — is kept
    on disk (only-on-improvement saves mean newest == best)."""

    def __init__(self, eval_ds, collator, every: int, n_batches: int, batch_size: int,
                 save_best: bool = True, adapter_dir: str | None = None,
                 best_saver=None):
        self.every = every
        self.save_best = save_best
        self.adapter_dir = adapter_dir   # LoRA+FSDP: gather adapter instead of DCP checkpoint
        self.best_saver = best_saver     # full FT: callable(model) -> gathered HF dir
        self.best = float("inf")
        self.batches = []
        for i in range(0, min(len(eval_ds), n_batches * batch_size), batch_size):
            self.batches.append(collator([eval_ds[j] for j in range(i, i + batch_size)]))
        print(f"[eval] prepared {len(self.batches)} fixed eval batches", flush=True)

    def on_step_end(self, args, state, control, model=None, **kwargs):
        if state.global_step <= 0 or state.global_step % self.every != 0 or model is None:
            return control
        device = next(model.parameters()).device
        was_training = model.training
        model.eval()
        losses = []
        with torch.no_grad():
            for b in self.batches:
                bb = {k: (v.to(device) if hasattr(v, "to") else v) for k, v in b.items()}
                out = model(**bb)
                if out.loss is not None:
                    losses.append(float(out.loss.detach().item()))
        if was_training:
            model.train()
        mean = sum(losses) / len(losses) if losses else float("inf")

        # The improve/save decision must be identical on every rank; broadcast
        # rank 0's value so float non-determinism can never split the ranks.
        import torch.distributed as dist
        if dist.is_initialized():
            t = torch.tensor([mean], device=device)
            dist.broadcast(t, src=0)
            mean = float(t.item())

        improved = mean < self.best
        if improved:
            self.best = mean
            if self.save_best:
                if self.adapter_dir:
                    save_lora_adapter(model, self.adapter_dir)
                elif self.best_saver is not None:
                    self.best_saver(model)
                else:
                    control.should_save = True
        if state.is_world_process_zero:
            tag = "  (new best -> saving checkpoint)" if improved and self.save_best else ""
            print(f"[eval] step {state.global_step} val/loss={mean:.4f}{tag}", flush=True)
            try:
                import wandb
                if wandb.run is not None:
                    wandb.log({"val/loss": mean, "val/loss_best": self.best},
                              step=state.global_step)
            except Exception:
                pass
        return control


def main():
    ap = argparse.ArgumentParser(allow_abbrev=False)
    ap.add_argument("config")
    args, rest = ap.parse_known_args()
    cfg = load_cfg(args.config, _parse_overrides(rest))

    run_name = cfg["run_name"]
    output_dir = cfg["output_dir"]
    model_id = cfg["model_id"]
    os.environ.setdefault("WANDB_RUN_NAME", run_name)

    # NOTE: every rank loads the full bf16 model into host RAM (~108 GB peak
    # each with the state-dict copy) — jobs must request >=1.4 TB on 8 ranks.
    # The meta-device fast path (dist init before from_pretrained +
    # cpu_ram_efficient_loading) deadlocked accelerate 1.14's FSDP2 broadcast
    # on this hybrid arch, so we stick with the proven load-everywhere path.

    trust = bool(cfg.get("trust_remote_code", False))
    from transformers import AutoConfig
    arch = (AutoConfig.from_pretrained(model_id, trust_remote_code=trust).architectures or [""])[0]
    nemotron = arch.startswith("NemotronH_Omni")
    if nemotron:
        # 2026-10-15 Nemotron-3.5-Super-VL: remote-code processor with its own dynamic-resolution rule
        # (min/max_num_patches on a 16-px grid, 32 px per LLM token after pixel shuffle).
        processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
        if cfg.get("max_num_patches"):
            processor.image_processor.max_num_patches = int(cfg["max_num_patches"])
        print(f"[processor] {type(processor).__name__} min/max_num_patches="
              f"{processor.image_processor.min_num_patches}/{processor.image_processor.max_num_patches}", flush=True)
    else:
        processor = AutoProcessor.from_pretrained(
            model_id,
            min_pixels=cfg.get("min_pixels", 256 * 28 * 28),
            max_pixels=cfg.get("max_pixels", 1179648),
        )

    # Arch dispatch: Qwen3.5/3.8 hybrid family vs Qwen3-VL (dense/MoE).
    if nemotron:
        from transformers import AutoModelForCausalLM as model_cls
    elif arch.startswith("Qwen3_5"):
        model_cls = Qwen3_5ForConditionalGeneration
    elif arch.startswith("Qwen3VL"):
        from transformers import Qwen3VLForConditionalGeneration
        model_cls = Qwen3VLForConditionalGeneration
        if "Moe" in arch:
            from transformers import Qwen3VLMoeForConditionalGeneration
            model_cls = Qwen3VLMoeForConditionalGeneration
    else:
        # Anything newer (Qwen4Exp / Flash-Next ...): let the auto class
        # resolve it (transformers >= 5.16 in .venv_next).
        try:
            from transformers import AutoModelForMultimodalLM as model_cls
        except ImportError:
            from transformers import AutoModelForImageTextToText as model_cls
    print(f"[model] arch={arch} -> {model_cls.__name__}", flush=True)
    # FSDP cpu_ram_efficient_loading: transformers materialises EVERY param on
    # non-zero ranks with torch.zeros_like(..., device="cpu") before accelerate
    # moves them to meta and broadcasts rank 0's weights. Zero-fill touches the
    # pages, so 7 ranks x 336 GB host RAM (2.3 TB) for Flash-Next. Untouched
    # empty_like costs nothing and the values are never read.
    _lazy = (os.environ.get("FSDP_CPU_RAM_EFFICIENT_LOADING", "").lower() == "true"
             and int(os.environ.get("LOCAL_RANK", "0")) != 0)
    _zeros_like = torch.zeros_like
    if _lazy:
        torch.zeros_like = lambda t, *a, **k: torch.empty_like(t, *a, **k)
        print("[model] non-zero rank: lazy (empty_like) placeholder params", flush=True)
    extra = {"trust_remote_code": True} if trust else {}
    if cfg.get("experts_implementation"):
        extra["experts_implementation"] = cfg["experts_implementation"]
    model = model_cls.from_pretrained(
        model_id,
        dtype=torch.bfloat16,
        attn_implementation=cfg.get("attn_implementation", "sdpa"),
        low_cpu_mem_usage=True,
        **extra,
    )
    torch.zeros_like = _zeros_like
    if hasattr(model.config, "text_config") and hasattr(model.config.text_config, "attention_dropout"):
        model.config.text_config.attention_dropout = cfg.get("attention_dropout", 0.0)

    # Kill the KV/recurrent cache for training: with activation checkpointing
    # the recompute pass appends to the cache a second time and doubles the
    # key length (SDPA mask-size crash). Trainer only does this for its own
    # gradient_checkpointing flag, not FSDP's activation checkpointing.
    model.config.use_cache = False
    if hasattr(model.config, "text_config"):
        model.config.text_config.use_cache = False
    if hasattr(model, "generation_config") and model.generation_config is not None:
        model.generation_config.use_cache = False
    # Submodules built via _from_config hold deep-copied configs — walk them.
    for m in model.modules():
        sub_cfg = getattr(m, "config", None)
        if sub_cfg is not None and hasattr(sub_cfg, "use_cache"):
            sub_cfg.use_cache = False

    apply_vision_strategy(model, cfg.get("vision_strategy", "frozen"))
    if cfg.get("freeze_routed_experts", False):
        # MoE full FT that does not fit: keep the routed experts at the base weights (Nemotron: 112.7B of 121B
        # params); router, shared expert, latent projections and everything else train.
        n_fr = 0
        for name, mod in model.named_modules():
            if type(mod).__name__.endswith("Experts"):
                for p in mod.parameters():
                    p.requires_grad_(False)
                    n_fr += p.numel()
        print(f"[model] froze routed experts: {n_fr/1e9:.2f}B params", flush=True)
    n_tr = sum(p.numel() for p in model.parameters() if p.requires_grad)
    n_all = sum(p.numel() for p in model.parameters())
    print(f"[model] trainable {n_tr/1e9:.3f}B of {n_all/1e9:.2f}B params", flush=True)
    if cfg.get("fast_qsa_indexer", False):
        from flashnext_qsa import patch_qsa_indexer
        patch_qsa_indexer()
    if cfg.get("mmap_ngram_embedding", False):
        from flashnext_ple import replace_ngram_embedding
        assert replace_ngram_embedding(model, model_id) > 0, "no ngram embedding found"
        import gc; gc.collect()
    if cfg.get("demote_persistent_buffers", False):
        demote_persistent_buffers(model)
    model = maybe_wrap_lora(model, cfg)

    if int(cfg.get("data_version", 1)) == 3:
        # Verifier / reranker: (drawing, candidate code) -> IoU as text.
        from data_v14 import build_verifier_dataset
        train_ds = build_verifier_dataset(
            image_aug=bool(cfg.get("image_aug", True)),
            binary_threshold=cfg.get("verifier_binary_threshold"),
            pos_keep=float(cfg.get("verifier_pos_keep", 1.0)),
            seed=int(cfg.get("seed", 42)))
    elif int(cfg.get("data_version", 1)) == 2:
        # Certified-manifest era: bundle reasoning tier + filtered plain tier.
        train_ds = build_mixed_v2(
            reasoning_frac=float(cfg.get("reasoning_frac", 0.2)),
            image_aug=bool(cfg.get("image_aug", True)),
            exec_filter=bool(cfg.get("exec_filter", True)),
            rft_frac=float(cfg.get("rft_frac", 0.0)),
            dims_filter=bool(cfg.get("dims_filter", False)),
            seed=int(cfg.get("seed", 42)),
        )
    else:
        train_ds = build_train_dataset(
            trace_mode=cfg.get("trace_mode", "required"),
            trace_gate=cfg.get("trace_gate", "pass_only"),
            image_aug=bool(cfg.get("image_aug", False)),
            exec_filter=bool(cfg.get("exec_filter", False)),
        )

    collator = VLMCollator(
        processor,
        max_seq_len=cfg.get("max_seq_len", 5120),
        system_prompt=cfg.get("system_prompt", "detailed"),
        reasoning_effort=cfg.get("reasoning_effort", "medium"),
        trace_style=cfg.get("trace_style", "think"),
    )

    # Plain transformers Trainer: TRL 1.x's SFTTrainer rejects torch
    # IterableDatasets (webdataset), and our collator + compute_loss_func
    # already cover everything SFT-specific.
    sft_cfg = TrainingArguments(
        output_dir=output_dir,
        run_name=run_name,
        num_train_epochs=cfg.get("epochs", 1),
        max_steps=cfg.get("max_steps", 3000),
        per_device_train_batch_size=cfg["per_device_train_batch_size"],
        gradient_accumulation_steps=cfg.get("gradient_accumulation_steps", 1),
        learning_rate=cfg["lr"],
        lr_scheduler_type=cfg.get("lr_scheduler_type", "cosine_with_min_lr"),
        lr_scheduler_kwargs=cfg.get("lr_scheduler_kwargs", {"min_lr_rate": 0.1}) or {},
        # TRL 1.x SFTConfig dropped warmup_ratio; derive warmup_steps from it.
        warmup_steps=int(float(cfg.get("warmup_ratio", 0.03))
                         * int(cfg.get("max_steps", 3000))),
        weight_decay=cfg.get("weight_decay", 0.0),
        optim=("adamw_torch" if cfg.get("optim") in ("torchao_adamw8bit_sr", "bf16_sr_adamw")
               else cfg.get("optim", "adamw_torch_fused")),
        max_grad_norm=cfg.get("max_grad_norm", 1.0),
        bf16=bool(cfg.get("bf16", True)),   # False = pure-bf16 params, no fp32 upcast
        gradient_checkpointing=cfg.get("gradient_checkpointing", False),
        gradient_checkpointing_kwargs={"use_reentrant": False}
        if cfg.get("gradient_checkpointing", False) else None,
        logging_steps=cfg.get("logging_steps", 10),
        eval_strategy="no",
        save_strategy=cfg.get("save_strategy", "steps"),
        save_steps=cfg.get("save_steps", 500),
        save_total_limit=cfg.get("save_total_limit", 2),
        save_only_model=cfg.get("save_only_model", False),
        report_to=["wandb"],
        dataloader_num_workers=cfg.get("dataloader_num_workers", 6),
        dataloader_prefetch_factor=cfg.get("dataloader_prefetch_factor", 4),
        remove_unused_columns=False,
        seed=cfg.get("seed", 42),
        logging_nan_inf_filter=not cfg.get("lean_sync", False),   # its isnan() is a host sync per micro-batch
        # FSDP2 full FT: no_sync() during accumulation keeps UNSHARDED grads on
        # every rank (126B x 2 B = 252 GB -> OOM); sync_each_batch reduce-scatters
        # every micro-batch instead.
        accelerator_config={"dispatch_batches": False, "split_batches": False,
                            **({"gradient_accumulation_kwargs": {"sync_each_batch": True}}
                               if cfg.get("sync_each_batch", False) else {})},
    )

    _loss_buffer: list[tuple[float, float]] = []
    _tok_buffer: list[int] = []
    lean_sync = bool(cfg.get("lean_sync", False))

    def vlm_loss(outputs, labels, num_items_in_batch=None, **kwargs):
        if getattr(outputs, "loss", None) is not None:
            loss = outputs.loss
        else:
            import torch.nn.functional as F
            logits = outputs.logits[..., :-1, :].contiguous()
            shift = labels[..., 1:].contiguous()
            loss = F.cross_entropy(
                logits.view(-1, logits.size(-1)), shift.view(-1), ignore_index=-100)
        if lean_sync:
            # No host sync (2026-10-16): keep loss / accuracy as device tensors, read them at log time.
            with torch.no_grad():
                shift = labels[..., 1:].to(outputs.logits.device)
                mask = shift != -100
                hit = ((outputs.logits[..., :-1, :].argmax(dim=-1) == shift) & mask).sum()
                # clone: HF scales the returned loss in place (loss *= num_processes), which a detach() view shares
                _loss_buffer.append((loss.detach().clone(), hit / mask.sum()))   # 0/0 -> nan, dropped below
                _tok_buffer.append(labels.numel())
            return loss
        with torch.no_grad():
            try:
                logits = outputs.logits[..., :-1, :]
                shift = labels[..., 1:]
                mask = shift != -100
                if mask.any():
                    preds = logits.argmax(dim=-1)
                    if preds.device != shift.device:
                        shift = shift.to(preds.device)
                        mask = mask.to(preds.device)
                    acc = (preds[mask] == shift[mask]).float().mean().item()
                else:
                    acc = float("nan")
            except Exception:
                acc = float("nan")
        _loss_buffer.append((float(loss.detach().item()), float(acc)))
        return loss

    class ManualLossLogger(TrainerCallback):
        def __init__(self, buf, log_every: int):
            self.buf, self.log_every = buf, log_every

        def on_step_end(self, args, state, control, **kwargs):
            if state.global_step <= 0 or state.global_step % self.log_every != 0 or not self.buf:
                return control
            vals = [(float(a), float(b)) for a, b in self.buf]   # device tensors under lean_sync
            losses = [x[0] for x in vals]
            accs = [x[1] for x in vals if x[1] == x[1]]
            mean_loss = sum(losses) / len(losses)
            mean_acc = sum(accs) / len(accs) if accs else float("nan")
            self.buf.clear()
            if state.is_world_process_zero:
                print(f"[step {state.global_step}/{state.max_steps}] "
                      f"loss={mean_loss:.4f} token_acc={mean_acc:.4f}", flush=True)
                try:
                    import wandb
                    if wandb.run is not None:
                        wandb.log({"train/loss_manual": mean_loss,
                                   "train/token_acc": mean_acc}, step=state.global_step)
                except Exception:
                    pass
            return control

    callbacks: list[TrainerCallback] = [
        ConfigToWandb(cfg),
        ManualLossLogger(_loss_buffer, cfg.get("logging_steps", 10)),
    ]
    if cfg.get("step_timing_every", 0):
        callbacks.append(StepTimer(_tok_buffer, every=int(cfg["step_timing_every"])))
    if cfg.get("param_probe", False):
        callbacks.append(ParamProbe())
    if cfg.get("broadcast_buffers", False):
        callbacks.append(BroadcastBuffers())
    if cfg.get("router_monitor_every", 0):
        callbacks.append(RouterLoadMonitor(model, every=int(cfg["router_monitor_every"]),
                                           stop_ratio=float(cfg.get("router_stop_ratio", 3.0))))

    if cfg.get("eval_every", 500) > 0:
        if int(cfg.get("data_version", 1)) == 3:
            from data_v14 import VerifierEvalDataset
            eval_ds = VerifierEvalDataset(max_n=cfg.get("eval_n", 128))
            thr = cfg.get("verifier_binary_threshold")
            if thr is not None:
                for smp in eval_ds.samples:
                    smp["label"] = smp["iou"] >= float(thr)
        elif int(cfg.get("data_version", 1)) == 2:
            eval_ds = EvalDatasetV2(max_n=cfg.get("eval_n", 128))
        else:
            eval_ds = EvalDataset(
                trace_mode=cfg.get("trace_mode", "required"),
                trace_gate=cfg.get("trace_gate", "pass_only"),
                max_n=cfg.get("eval_n", 128),
            )
        print(f"[data] {len(eval_ds)} validation examples", flush=True)
        callbacks.append(EvalLossCallback(
            eval_ds, collator,
            every=cfg.get("eval_every", 500),
            n_batches=cfg.get("eval_n_batches", 16),
            batch_size=cfg.get("per_device_eval_batch_size", 2),
            save_best=bool(cfg.get("save_best", True)),
            adapter_dir=(os.path.join(output_dir, "best_adapter")
                         if cfg.get("use_lora", False) and fsdp_lora_active() else None),
            best_saver=((lambda m: save_full_model(
                            m, os.path.join(output_dir, "best_model"), processor, model_id, cfg))
                        if cfg.get("best_save_mode") == "gather" else
                        (lambda m: save_trainable_subset(m, os.path.join(output_dir, "best_model"),
                                                         processor, model_id))
                        if cfg.get("best_save_mode") == "trainable" else None),
        ))

    trainer_cls = {"torchao_adamw8bit_sr": TorchaoSRTrainer,
                   "bf16_sr_adamw": Bf16SRTrainer}.get(cfg.get("optim"), Trainer)
    trainer = trainer_cls(
        model=model,
        processing_class=processor,
        args=sft_cfg,
        train_dataset=train_ds,
        eval_dataset=None,
        data_collator=collator,
        callbacks=callbacks,
        compute_loss_func=vlm_loss,
    )

    if cfg.get("lr_resume_from_step") is not None:
        # warm restart from a gathered checkpoint (model_id) of an earlier run: continue its schedule
        tot = int(cfg["lr_resume_total_steps"])
        trainer.lr_resume = (tot, int(float(cfg.get("warmup_ratio", 0.03)) * tot),
                             int(cfg["lr_resume_from_step"]), int(cfg.get("lr_resume_rewarm", 50)),
                             float((cfg.get("lr_scheduler_kwargs") or {}).get("min_lr_rate", 0.1)))
    trainer.train(resume_from_checkpoint=cfg.get("resume"))

    # Final consolidated save.
    import torch.distributed as dist
    rank = dist.get_rank() if dist.is_initialized() else 0
    if cfg.get("save_final", True):
        final_dir = os.path.join(output_dir, "final")
        if cfg.get("use_lora", False):
            if fsdp_lora_active():
                save_lora_adapter(model, final_dir)   # trainer.save_model is a no-op here
            else:
                # Adapters are small; DDP saves them via trainer.
                trainer.save_model(final_dir)
            if rank == 0:
                processor.save_pretrained(final_dir)
                print(f"[final_save] adapter saved to {final_dir}", flush=True)
        elif cfg.get("best_save_mode") == "trainable":
            save_trainable_subset(model, final_dir, processor, model_id)
        else:
            try:
                save_full_model(trainer.accelerator.unwrap_model(model), final_dir,
                                processor, model_id, cfg)
                if rank == 0:
                    print(f"[final_save] full model saved to {final_dir}", flush=True)
            except Exception as e:
                if rank == 0:
                    print(f"[final_save] gather failed ({type(e).__name__}: {e}); "
                          f"falling back to trainer.save_model", flush=True)
                trainer.save_model(final_dir)
        if dist.is_initialized():
            dist.barrier()


if __name__ == "__main__":
    main()
