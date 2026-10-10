"""Stage 2 of the DeepSeek-V4.1-Flash fine-tune spike: a short LoRA run, then a greedy eval.

Single process, the checkpoint pipeline-split across the GPUs exactly as in the stage-1 smoke
(device_map="auto", FP8/FP4 kept quantized, Triton path), LoRA on the attention projections,
AdamW on the adapter only, batch 1 with gradient accumulation, bf16 autocast, no gradient
checkpointing (the draft class has none; memory allows it).

Data: webdataset-style tar shards with <key>.png / <key>.code.py / <key>.think.txt members
(the RFT tier layout), rendered into the DeepSeek-V4.1 prompt format by the checkpoint's own
encoding/encoding.py in "chat" mode (no thinking phase -- the served model must answer
directly; the probe showed V4.1 otherwise reasons past any budget). Labels are masked to the
assistant span so the loss is on the answer only.

Eval: greedy generation on the first --eval-n parts of a bench (eval_cache_v15.pkl), the
same prompt, scored with iou_pair against gt_meshes_v15 -- comparable to the probe's
first_draw and to every bo8_ext "first-exec" column. Kill criterion for the spike: first-exec
below 0.3 after the run (the 27B passed 0.5 early in its own training).

    python dsv41_lora_train.py --model models/DeepSeek-V4.1-Flash --tier spike_dsv41/tier \
        --steps 300 --accum 8 --lr 1e-4 --rank 16 --out spike_dsv41/lora_r16 \
        --eval-bench mech_benchmarks/ext_bench --eval-n 48
"""
from __future__ import annotations

import argparse
import glob
import io
import json
import os
import pickle
import random
import re
import subprocess
import sys
import tarfile
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)


def load_tier(tier_dir, limit=0):
    rows = []
    for tp in sorted(glob.glob(os.path.join(tier_dir, "*.tar"))):
        with tarfile.open(tp) as t:
            members = {m.name: m for m in t.getmembers()}
            for name in members:
                if not name.endswith(".code.py"):
                    continue
                key = name[:-8]
                if key + ".png" not in members:
                    continue
                row = {"key": key, "png": t.extractfile(members[key + ".png"]).read(),
                       "code": t.extractfile(members[name]).read().decode()}
                # visual repair rows (2026-09-29): second image = the sheet the current program draws, per-row prompt
                if key + ".cand.png" in members:
                    row["png2"] = t.extractfile(members[key + ".cand.png"]).read()
                if key + ".think.txt" in members:
                    row["think"] = t.extractfile(members[key + ".think.txt"]).read().decode().strip()
                if key + ".user.txt" in members:
                    row["user"] = t.extractfile(members[key + ".user.txt"]).read().decode()
                # GRPO rows (2026-10-06): the verbatim sampled reply (notes + code block) and the group advantage
                if key + ".reply.txt" in members:
                    row["reply"] = t.extractfile(members[key + ".reply.txt"]).read().decode()
                if key + ".ctx.json" in members:   # T0 regime: the turns between the first user message and the trained reply
                    row["context"] = json.loads(t.extractfile(members[key + ".ctx.json"]).read().decode())
                if key + ".adv.txt" in members:
                    row["adv"] = float(t.extractfile(members[key + ".adv.txt"]).read().decode().strip())
                rows.append(row)
                if limit and len(rows) >= limit:
                    return rows
    return rows


def build_sample(proc, dsenc, system, user, png, answer, image_token, max_len, png2=None, think=None, reply=None, effort=None,
                 context=None):
    """Prompt via the released encoder; labels masked to the assistant answer. png2 (optional) is a second image
    block after the first (visual repair: target sheet, then the sheet of the current program)."""
    from PIL import Image
    import torch
    # encoding.py takes image blocks by path (as in the stage-1 smoke); the real pixels go to
    # the processor separately, so the path only has to exist for placeholder bookkeeping.
    pngs = [png] + ([png2] if png2 else [])
    paths = []
    for b_ in pngs:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
            tf.write(b_); paths.append(tf.name)
    try:
        msgs = [{"role": "system", "content": system},
                {"role": "user", "content": [{"type": "image_url", "image_url": {"url": p_}} for p_ in paths] + [{"type": "text", "text": user}]}]
        # think (2026-09-29): with a plan, train in "thinking" mode -- the plan in DeepSeek's reasoning span, then the
        # code (the September no-think LoRA matched e55's own no-think first draw, 0.136 vs 0.151; e55 thinking: 0.384)
        mode = "thinking" if think is not None else "chat"
        # reply (GRPO): the assistant content exactly as sampled; effort: the "Reasoning Effort: N" prefix the server used
        for c in context or []:   # earlier turns of a multi-call episode (assistant text only, as the server saw them)
            msgs.append({"role": c["role"], "content": c["text"]})
        amsg = {"role": "assistant", "content": reply if reply is not None else "```python\n" + answer + "\n```"}
        if think is not None: amsg["reasoning_content"] = think
        prompt_no_answer = dsenc.encode_messages(msgs, thinking_mode=mode, reasoning_effort=effort)
        full = dsenc.encode_messages(msgs + [amsg], thinking_mode=mode, reasoning_effort=effort)
    finally:
        for p_ in paths: os.unlink(p_)
    if not full.startswith(prompt_no_answer):
        raise ValueError("encoded prompt is not a prefix of the full sample (mode %s)" % mode)
    imgs = [Image.open(io.BytesIO(b_)).convert("RGB") for b_ in pngs]
    enc = proc(text=[full], images=imgs, return_tensors="pt")
    pre = proc(text=[prompt_no_answer], images=imgs, return_tensors="pt")
    n_pre = pre["input_ids"].shape[-1]
    labels = enc["input_ids"].clone()
    labels[:, :n_pre] = -100
    if labels.shape[-1] > max_len:
        return None
    enc["labels"] = labels
    return enc


def enable_layer_ckpt(model, min_layer):
    """Activation checkpointing for the trainable decoder layers (>= min_layer) of the draft DeepSeek-V4.1 class
    (2026-10-06: a 9k-token row OOMed the last of 4 B300s in FORWARD -- every layer above the first LoRA layer keeps its
    MoE activations for backward). Uses the layers' own GradientCheckpointingLayer hook, non-reentrant. Trap handled:
    `shared` is ONE dict that source layers overwrite (CSA2 group state); a recompute in backward would read the LAST
    writer's state, so each layer's recompute gets a snapshot of the dict as it was when that layer first ran."""
    import torch
    from torch.utils.checkpoint import checkpoint

    def ckpt_func(fn, *args):
        base, kw = fn.func, dict(fn.keywords)
        shared = kw.get("shared")
        snap = dict(shared) if shared is not None else None
        first = [True]

        def run(*a):
            if first[0]:
                first[0] = False
                return base(*a, **kw)
            return base(*a, **({**kw, "shared": dict(snap)} if snap is not None else kw))
        return checkpoint(run, *args, use_reentrant=False)
    n = 0
    for m in model.modules():
        if type(m).__name__ == "DeepseekV41DecoderLayer" and m.layer_idx >= min_layer:
            m.gradient_checkpointing = True; m._gradient_checkpointing_func = ckpt_func; n += 1
    return n


def grpo_pass(args, model, opt, sched, params, rows, proc, dsenc, system, user, dev, log, t0):
    """One advantage-weighted pass (GRPO round, 2026-10-06). Rows were sampled by the served policy (vLLM, the
    current merged adapter) in thinking mode; adv = group-centred reward (optionally / batch std), never 0 here.
    loss = sum_rows adv_row * CE_row / n_chunk_rows, CE_row = mean token NLL of reasoning + reply (labels masked to the
    assistant span by build_sample), so adv < 0 pushes the sample down. Grad clip 1.0, one optimizer step per chunk."""
    import torch
    rows = [r for r in rows if r.get("adv") is not None and r["adv"] != 0.0]
    stats = {"rows": len(rows), "trained": 0, "skipped_long": 0, "tokens": [], "ce_pos": [], "ce_neg": []}
    if args.ckpt_check:
        layers = [m for m in model.modules() if type(m).__name__ == "DeepseekV41DecoderLayer" and m.gradient_checkpointing]
        r0 = rows[0]
        enc = build_sample(proc, dsenc, system, r0.get("user") or user, r0["png"], r0["code"], proc.image_token, 10**9,
                           None, r0.get("think") or "", r0.get("reply"), args.reasoning_effort)
        enc = {k: (v.to(dev) if hasattr(v, "to") else v) for k, v in enc.items()}
        grads = []
        for on in (True, False):
            for m in layers: m.gradient_checkpointing = on
            torch.cuda.reset_peak_memory_stats()
            ts = time.time()
            with torch.autocast("cuda", dtype=torch.bfloat16):
                out = model(**enc)
            out.loss.backward()
            mem = " ".join(f"{torch.cuda.max_memory_allocated(d)/2**30:.0f}" for d in range(torch.cuda.device_count()))
            grads.append(torch.cat([p.grad.reshape(-1).float().cpu() for p in params if p.grad is not None]))
            log(f"[ckpt-check] ckpt={on} loss {out.loss.item():.5f} {time.time()-ts:.1f}s peak GiB/GPU {mem}", flush=True)
            opt.zero_grad(set_to_none=True); del out
        for m in layers: m.gradient_checkpointing = True
        a_, b_ = grads
        log(f"[ckpt-check] {enc['input_ids'].shape[-1]} tokens, grad rel err {float((a_-b_).norm()/b_.norm()):.2e} "
            f"cos {float(torch.nn.functional.cosine_similarity(a_, b_, dim=0)):.6f}", flush=True)
        del enc
    if args.score_only:   # sampler-vs-trainer agreement: mean token NLL of the sampled tokens, train vs eval mode, T=1 vs logit_temp
        for row in rows:
            enc = build_sample(proc, dsenc, system, row.get("user") or user, row["png"], row["code"], proc.image_token, 10**9,
                               None, row.get("think") or "", row.get("reply"), args.reasoning_effort)
            enc = {k: (v.to(dev) if hasattr(v, "to") else v) for k, v in enc.items()}
            labels = enc.pop("labels"); res = []
            import contextlib
            import transformers.models.deepseek_v41.modeling_deepseek_v41 as M
            chunked = M.eager_attention_forward_dms
            orig = getattr(sys.modules.get("dsv41_chunked_attn"), "_ORIG", None) or chunked
            model.eval()
            # variants: bf16 autocast (the training default) vs none (fp32-kept hyper-connection sites stay fp32), chunked vs eager
            with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
                out = model(**enc)
            ids = enc["input_ids"][0].to(out.logits.device); lab0 = labels[0].to(out.logits.device); pos = (lab0 != -100).nonzero()[:, 0]
            lg = out.logits[0].float()
            for off in (0, 1, 2):   # logits[t] should predict token t+1 (off=1)
                pp = pos[pos >= off]
                nll = torch.nn.functional.cross_entropy(lg[pp - off], ids[pp], reduction="none")
                res.append(f"off{off} mean {float(nll.mean()):.3f} median {float(nll.median()):.3f} p90 {float(nll.quantile(0.9)):.2f} "
                           f">5nats {float((nll > 5).float().mean()):.3f} top1 {float((lg[pp - off].argmax(-1) == ids[pp]).float().mean()):.3f}")
            nll = torch.nn.functional.cross_entropy(lg[pos - 1], ids[pos], reduction="none")
            worst = nll.topk(8).indices
            res.append("worst: " + " ".join(repr(proc.tokenizer.decode([int(ids[pos[w]])])) + f"={float(nll[w]):.1f}" for w in worst))
            res.append("first40: " + " ".join(f"{proc.tokenizer.decode([int(ids[p_])])!r}:{float(x):.1f}" for p_, x in zip(pos[:40], nll[:40])))
            del out, lg
            for uc in (True, False):   # cache-building prefill path vs the no-cache (training) path
                with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
                    out = model(**enc, use_cache=uc)
                lab = labels[0, 1:].to(out.logits.device); m = lab != -100
                nll = torch.nn.functional.cross_entropy(out.logits[0, :-1][m].float(), lab[m], reduction="none")
                res.append(f"use_cache={uc} {float(nll.mean()):.3f} top1 {float((out.logits[0, :-1][m].argmax(-1) == lab[m]).float().mean()):.3f}")
                del out
            log(f"[train] config.use_cache={getattr(model.config, 'use_cache', None)} text use_cache={getattr(getattr(model.config, 'text_config', None), 'use_cache', None)}", flush=True)
            for name, ac, attn in (("autocast+chunked", True, chunked),):
                M.eager_attention_forward_dms = attn
                try:
                    with torch.no_grad(), (torch.autocast("cuda", dtype=torch.bfloat16) if ac else contextlib.nullcontext()):
                        out = model(**enc)
                    lab = labels[0, 1:].to(out.logits.device); m = lab != -100
                    nll = torch.nn.functional.cross_entropy(out.logits[0, :-1][m].float(), lab[m], reduction="none")
                    res.append(f"{name} {float(nll.mean()):.3f} (first-500 {float(nll[:500].mean()):.3f}, last-500 {float(nll[-500:].mean()):.3f})")
                    del out
                except Exception as e:
                    res.append(f"{name} ERROR {type(e).__name__}: {str(e)[:150]}")
            M.eager_attention_forward_dms = chunked
            log(f"[score] {row['key'][:40]} {int(m.sum())} label tokens: " + " | ".join(res), flush=True)
        return
    chunks = [rows[j:j + args.accum] for j in range(0, len(rows), args.accum)]
    log(f"[grpo] {len(rows)} rows -> {len(chunks)} optimizer steps of <= {args.accum} rows, lr {args.lr:g}", flush=True)
    for ci, chunk in enumerate(chunks):
        n_ok = 0; ts0 = time.time()
        for row in chunk:
            enc = build_sample(proc, dsenc, system, row.get("user") or user, row["png"], row["code"], proc.image_token,
                               args.max_len, row.get("png2"), row.get("think") or "", row.get("reply"), args.reasoning_effort,
                               row.get("context"))
            if enc is None:
                stats["skipped_long"] += 1; continue
            enc = {k: (v.to(dev) if hasattr(v, "to") else v) for k, v in enc.items()}
            ts = time.time()
            if args.logit_temp != 1.0:   # rollouts sampled at T != 1: score the same tempered distribution
                labels = enc.pop("labels")
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    out = model(**enc)
                lab = labels[0, 1:].to(out.logits.device); m = lab != -100
                lg = out.logits[0, :-1][m].float() / args.logit_temp
                loss = torch.nn.functional.cross_entropy(lg, lab[m]); enc["labels"] = labels; del lg
            else:
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    out = model(**enc)
                loss = out.loss
            tf = time.time() - ts
            (loss * (row["adv"] / len(chunk))).backward()
            ce = float(loss.item()); n_tok = int(enc["input_ids"].shape[-1])
            stats["tokens"].append(n_tok); stats["ce_pos" if row["adv"] > 0 else "ce_neg"].append(ce); n_ok += 1
            if stats["trained"] + n_ok <= 3:
                mem = " ".join(f"{torch.cuda.max_memory_allocated(d)/2**30:.0f}" for d in range(torch.cuda.device_count()))
                log(f"[grpo] row {row['key'][:40]}: {n_tok} tokens adv {row['adv']:+.3f} ce {ce:.3f} forward {tf:.1f}s "
                    f"backward {time.time()-ts-tf:.1f}s peak GiB/GPU {mem}", flush=True)
            del out, enc, loss
        stats["trained"] += n_ok
        if n_ok == 0:
            opt.zero_grad(set_to_none=True); continue
        gn = float(torch.nn.utils.clip_grad_norm_(params, 1.0))
        opt.step(); sched.step(); opt.zero_grad(set_to_none=True)
        log(f"[grpo] step {ci+1}/{len(chunks)} rows {n_ok} grad_norm {gn:.3f} {time.time()-ts0:.0f}s "
            f"(elapsed {time.time()-t0:.0f}s)", flush=True)
    mean = lambda v: sum(v) / len(v) if v else 0.0
    summ = {"rows": stats["rows"], "trained": stats["trained"], "skipped_long": stats["skipped_long"],
            "mean_tokens": mean(stats["tokens"]), "ce_pos": mean(stats["ce_pos"]), "ce_neg": mean(stats["ce_neg"]),
            "steps": len(chunks), "seconds": time.time() - t0}
    os.makedirs(args.out, exist_ok=True)
    json.dump(summ, open(os.path.join(args.out, "grpo_train.json"), "w"), indent=1)
    log("[grpo] " + json.dumps(summ), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tier", required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--steps", type=int, default=300)
    ap.add_argument("--accum", type=int, default=8)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--rank", type=int, default=16)
    ap.add_argument("--max-len", type=int, default=4096)
    ap.add_argument("--targets", default=r"self_attn\.(q_a_proj|q_b_proj|kv_proj|o_b_proj)$")
    ap.add_argument("--out", required=True)
    ap.add_argument("--eval-bench", default="")
    ap.add_argument("--eval-n", type=int, default=48)
    ap.add_argument("--eval-max-new", type=int, default=3000)
    ap.add_argument("--adapter", default="", help="load this saved LoRA instead of creating one (with --steps 0: eval only)")
    ap.add_argument("--eval-gen-out", default="", help="write generations (key, text, code) as jsonl; default <out>/eval_gen.jsonl")
    ap.add_argument("--exec-python", default=os.environ.get("EXEC_PYTHON", ""),
                    help="interpreter with build123d/trimesh for exec_harness + iou_once; empty -> dump generations only "
                         "(score later with dsv41_eval_score.py)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--think", action="store_true", help="train rows that carry think.txt in thinking mode (plan in the reasoning span)")
    ap.add_argument("--save-every", type=int, default=0, help="also save the adapter to <out>/step_<n> every n optimizer steps")
    ap.add_argument("--chunked-attn", type=int, default=0, help="query chunk for the banded attention replacement (0 = eager)")
    ap.add_argument("--max-mem-list", default="", help="comma list of per-GPU caps in GiB (overrides the other memory options)")
    ap.add_argument("--max-mem-gib", type=float, default=0, help="per-GPU weight cap (forces an even spread; 4 B300s: ~150)")
    ap.add_argument("--last-gpu-headroom", type=float, default=0, help="GiB kept free on the last GPU (logits); 0 = device_map auto defaults")
    ap.add_argument("--min-layer", type=int, default=0, help="LoRA only on decoder layers >= this index (backward stops at the first adapted layer)")
    ap.add_argument("--prompts", default="", help="prompts.json (system/user); default: next to the tier, else spike_dsv41/prompts.json")
    ap.add_argument("--reasoning-effort", default=None, help="thinking-mode effort prefix (int 1-100 or low/high/max); "
                    "default = encoding.py's default (high = 75). Must match the server's chat_template_kwargs.")
    ap.add_argument("--adv-weighted", action="store_true",
                    help="GRPO update: ONE pass over the tier rows (each carries adv.txt), loss per row = adv * mean token NLL "
                         "of the assistant span (reasoning + reply), chunks of --accum rows per optimizer step (steps ignored)")
    ap.add_argument("--fast-image", action="store_true", help="torchvision image processor (pre-2026-10-07 behaviour)")
    ap.add_argument("--no-fix-shared", action="store_true",
                    help="do NOT apply dsv41_hf_fixes.fix_shared_dict_hooks (reproduces the pre-2026-10-07 broken forward)")
    ap.add_argument("--score-only", action="store_true", help="GRPO debug: log the NLL of each row's tokens, no update")
    ap.add_argument("--grad-ckpt", action="store_true", help="activation checkpointing on decoder layers >= --min-layer")
    ap.add_argument("--ckpt-check", action="store_true", help="debug: LoRA grads of the first row with vs without --grad-ckpt")
    ap.add_argument("--logit-temp", type=float, default=1.0, help="GRPO: divide logits by the rollout temperature")
    ap.add_argument("--opt-state", default="", help="AdamW state to resume (saved again to <out>/optimizer.pt)")
    ap.add_argument("--const-lr", action="store_true", help="constant learning rate (no warmup/decay)")
    ap.add_argument("--dist", action="store_true",
                    help="one process per node (SLURM_PROCID/SLURM_NTASKS, MASTER_ADDR/PORT); each node holds a full "
                         "pipeline-split replica, LoRA gradients are averaged across nodes over NCCL")
    args = ap.parse_args()
    if args.reasoning_effort is not None and str(args.reasoning_effort).isdigit():
        args.reasoning_effort = int(args.reasoning_effort)
    if args.adv_weighted:
        args.steps = max(args.steps, 1)   # a trainable adapter; the real step count is set by the row count

    import socket
    import torch
    rank, world, dist = 0, 1, None
    if args.dist:
        import torch.distributed as dist
        rank = int(os.environ.get("SLURM_PROCID", os.environ.get("RANK", "0")))
        world = int(os.environ.get("SLURM_NTASKS", os.environ.get("WORLD_SIZE", "1")))
        os.environ.setdefault("RANK", str(rank)); os.environ.setdefault("WORLD_SIZE", str(world))
        from datetime import timedelta
        # steps are minutes long and per-rank sample lengths differ, so a rank can wait well past NCCL's 10-min default
        dist.init_process_group("nccl", rank=rank, world_size=world, device_id=torch.device("cuda:0"), timeout=timedelta(hours=3))
        print(f"[train] rank {rank}/{world} on {socket.gethostname()} ({torch.cuda.device_count()} GPUs)", flush=True)
    log = (lambda *a, **k: print(*a, **k)) if rank == 0 else (lambda *a, **k: None)
    import dsv41_autograd; dsv41_autograd.register()
    if args.chunked_attn:   # exact banded attention: the eager S x S score matrix OOMs on long (>16k-token) rows
        import dsv41_chunked_attn; dsv41_chunked_attn.install(chunk=args.chunked_attn)   # backward for the Hub FP8/MXFP4 ops (input grads only)
    from transformers import AutoModelForImageTextToText, AutoTokenizer
    from transformers.models.deepseek_v41.image_processing_deepseek_v41 import DeepseekV41ImageProcessor
    from transformers.models.deepseek_v41.processing_deepseek_v41 import DeepseekV41Processor
    sys.path.insert(0, os.path.join(args.model, "encoding"))
    import encoding as dsenc
    pp = args.prompts or os.path.join(os.path.dirname(args.tier.rstrip("/")), "prompts.json")
    if not os.path.exists(pp):   # tiers other than the spike's carry no prompts.json; the served prompt is the same
        pp = os.path.join(os.path.dirname(HERE), "..", "spike_dsv41", "prompts.json")
    pj = json.load(open(os.path.abspath(pp)))
    system, user = pj["system"], pj["user"]

    tok = AutoTokenizer.from_pretrained(args.model)
    if args.fast_image:
        proc = DeepseekV41Processor(image_processor=DeepseekV41ImageProcessor(), tokenizer=tok)
    else:   # 2026-10-07: PIL backend = reference/vLLM preprocessing (ImageOps.pad + PIL bicubic); torchvision differs ~4% in ViT features
        from transformers.models.deepseek_v41.image_processing_pil_deepseek_v41 import DeepseekV41ImageProcessorPil
        proc = DeepseekV41Processor(image_processor=DeepseekV41ImageProcessorPil(), tokenizer=tok)
    # --last-gpu-headroom: device_map="auto" packs the last GPU full; the lm_head logits (vocab x ~3k tokens, fp32) then OOM
    # on two-image rows (serv-20 B300 smoke, 2026-09-30). Cap every GPU and leave extra room on the last one.
    mm = None
    if args.max_mem_list:   # explicit per-GPU caps: front-load the frozen lower layers, keep the trainable top layers thin
        mm = {i: f"{int(float(x))}GiB" for i, x in enumerate(args.max_mem_list.split(","))}
        log(f"[train] max_memory {mm}", flush=True)
    elif args.last_gpu_headroom > 0:
        n = torch.cuda.device_count(); tot = [torch.cuda.get_device_properties(i).total_memory / 2**30 for i in range(n)]
        free = [torch.cuda.mem_get_info(i)[0] / 2**30 for i in range(n)]
        cap = lambda i: min(free[i], tot[i]) * 0.90 if args.max_mem_gib <= 0 else min(args.max_mem_gib, free[i] * 0.95)
        mm = {i: f"{int(cap(i) - (args.last_gpu_headroom if i == n - 1 else 8))}GiB" for i in range(n)}
        log(f"[train] max_memory {mm}", flush=True)
    model = AutoModelForImageTextToText.from_pretrained(args.model, device_map="auto", dtype=torch.bfloat16, max_memory=mm)
    for p in model.parameters():
        p.requires_grad_(False)
    # The two ~98 GB engram tables stay in host RAM, memory-mapped from the safetensors files; on a network
    # filesystem every gather page-faults from Lustre (15 s per lookup on the cluster). Copy them into RAM once.
    t_e = time.time(); n_bytes = 0
    for m in model.modules():
        if type(m).__name__ == "DeepseekV41EngramEmbedding":
            for _, p in m.named_parameters(recurse=False):
                if p.device.type == "cpu":
                    p.data = p.data.clone(); n_bytes += p.numel() * p.element_size()
    if n_bytes:
        log(f"[train] engram tables copied off the mmap into host RAM: {n_bytes/2**30:.0f} GiB in {time.time()-t_e:.0f}s", flush=True)
    if not args.no_fix_shared:   # 2026-10-07: without this every compressed-attention layer ran window-only (see dsv41_hf_fixes)
        import dsv41_hf_fixes
        dsv41_hf_fixes.fix_shared_dict_hooks(model, log=lambda m: log(m, flush=True))
    import collections
    dm = getattr(model, "hf_device_map", {}) or {}
    log(f"[train] device map: {dict(collections.Counter(str(v) for v in dm.values()))}", flush=True)
    log("[train] GiB allocated per GPU after load: " + " ".join(f"{torch.cuda.memory_allocated(d)/2**30:.0f}" for d in range(torch.cuda.device_count())), flush=True)
    from peft import LoraConfig, get_peft_model, PeftModel
    if args.adapter:
        model = PeftModel.from_pretrained(model, args.adapter, is_trainable=args.steps > 0)
        names = [n for n, m in model.named_modules() if hasattr(m, "lora_A")]
        log(f"[train] loaded adapter {args.adapter}", flush=True)
    else:
        names = [n for n, m in model.named_modules() if isinstance(m, torch.nn.Linear) and re.search(args.targets, n)
                 and int((re.search(r"layers\.(\d+)\.", n) or [0, 0])[1]) >= args.min_layer]
        model = get_peft_model(model, LoraConfig(r=args.rank, lora_alpha=2 * args.rank, lora_dropout=0.0,
                                                  target_modules=names, bias="none"))
    if args.grad_ckpt:
        log(f"[train] activation checkpointing on {enable_layer_ckpt(model, args.min_layer)} decoder layers", flush=True)
    params = [p for p in model.parameters() if p.requires_grad]
    log(f"[train] {len(names)} LoRA targets, {sum(p.numel() for p in params)/1e6:.1f}M trainable", flush=True)
    if args.steps > 0:
        opt = torch.optim.AdamW(params, lr=args.lr, weight_decay=0.0, betas=(0.9, 0.95))
        sched = torch.optim.lr_scheduler.LambdaLR(opt, (lambda s: 1.0) if args.const_lr else
                                                  (lambda s: min(1.0, (s + 1) / 20) * max(0.1, 1 - s / max(1, args.steps))))
        if args.opt_state and os.path.exists(args.opt_state):
            opt.load_state_dict(torch.load(args.opt_state, map_location="cpu"))
            for g in opt.param_groups: g["lr"] = args.lr; g["initial_lr"] = args.lr
            log(f"[train] optimizer state resumed from {args.opt_state}", flush=True)

    rows = load_tier(args.tier, args.limit)
    random.Random(args.seed).shuffle(rows)
    rows = rows[rank::world]
    log(f"[train] {len(rows) * world} tier rows ({len(rows)} per rank), {args.accum * world} samples per optimizer step", flush=True)
    model.train()
    t0 = time.time(); step = 0; i = 0; acc_loss = 0.0; n_acc = 0; skipped = 0
    dev = model.device
    if args.adv_weighted:
        grpo_pass(args, model, opt, sched, params, rows, proc, dsenc, system, user, dev, log, t0)
        if args.score_only:
            return
        os.makedirs(args.out, exist_ok=True)
        model.save_pretrained(args.out)
        torch.save(opt.state_dict(), os.path.join(args.out, "optimizer.pt"))
        print(f"[train] adapter saved -> {args.out} ({time.time()-t0:.0f}s)", flush=True)
        return
    while step < args.steps:
        row = rows[i % len(rows)]; i += 1
        enc = build_sample(proc, dsenc, system, row.get("user") or user, row["png"], row["code"], proc.image_token, args.max_len, row.get("png2"),
                           row.get("think") if args.think and row.get("think") else None, None, args.reasoning_effort)
        if enc is None:
            skipped += 1; continue
        enc = {k: (v.to(dev) if hasattr(v, "to") else v) for k, v in enc.items()}
        ts = time.time()
        if os.environ.get("DSV41_PROFILE") and i == 2 and rank == 0:   # torch profiler on the second forward: where do the seconds go?
            from torch.profiler import profile, ProfilerActivity
            with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA]) as prof:
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    out = model(**enc)
                torch.cuda.synchronize()
            ka = prof.key_averages()
            print("[profile] top self-CPU:", flush=True)
            print(ka.table(sort_by="self_cpu_time_total", row_limit=18, max_name_column_width=70), flush=True)
            print("[profile] top CUDA:", flush=True)
            print(ka.table(sort_by="cuda_time_total", row_limit=18, max_name_column_width=70), flush=True)
        else:
            with torch.autocast("cuda", dtype=torch.bfloat16):
                out = model(**enc)
        tf = time.time() - ts
        (out.loss / args.accum).backward()
        if i <= 4:
            log(f"[train] sample {i}: {enc['input_ids'].shape[-1]} tokens, forward {tf:.1f}s, backward {time.time()-ts-tf:.1f}s", flush=True)
        acc_loss += out.loss.item(); n_acc += 1
        if n_acc % args.accum == 0:
            if dist is not None:   # average the adapter gradients across replicas (one flat buffer, ~184 MB fp32)
                flat = torch.cat([(p.grad if p.grad is not None else torch.zeros_like(p)).reshape(-1).float().to("cuda:0") for p in params])
                dist.all_reduce(flat, op=dist.ReduceOp.AVG)
                off = 0
                for p in params:
                    n = p.numel()
                    if p.grad is None:
                        p.grad = torch.zeros_like(p)
                    p.grad.copy_(flat[off:off + n].view_as(p).to(p.device, p.dtype)); off += n
                del flat
            torch.nn.utils.clip_grad_norm_(params, 1.0)
            opt.step(); sched.step(); opt.zero_grad(set_to_none=True); step += 1
            if args.save_every and step % args.save_every == 0 and rank == 0:
                model.save_pretrained(os.path.join(args.out, f"step_{step}")); log(f"[train] checkpoint step_{step}", flush=True)
            if step % 5 == 0 or step == 1:
                log(f"[train] step {step}/{args.steps} loss {acc_loss/n_acc:.4f} lr {sched.get_last_lr()[0]:.2e} "
                      f"{(time.time()-t0)/step:.0f} s/step skipped {skipped}", flush=True)
                acc_loss = 0.0; n_acc = 0
    if rank == 0:
        os.makedirs(args.out, exist_ok=True)
        if args.steps > 0:
            model.save_pretrained(args.out)
            print(f"[train] adapter saved -> {args.out} ({time.time()-t0:.0f}s)", flush=True)
    if dist is not None:
        dist.barrier()

    if not args.eval_bench or args.eval_n <= 0:
        return
    # --- greedy eval: generations are always dumped; execution + IoU only with an interpreter that has the CAD stack
    # same extractor as geom_eval_worker (copied: that module imports the training stack)
    _CODE_RE = re.compile(r"```python\s*\n(.*?)```", re.DOTALL)
    def extract_code(text):
        if "</think>" in text:
            text = text.rsplit("</think>", 1)[1]
        blocks = _CODE_RE.findall(text)
        return blocks[-1].strip() if blocks else None
    cache = pickle.load(open(os.path.join(args.eval_bench, "eval_cache_v15.pkl"), "rb"))
    gt_dir = os.path.join(args.eval_bench, "gt_meshes_v15")
    gen_path = args.eval_gen_out or os.path.join(args.out, f"eval_gen.rank{rank}.jsonl")
    os.makedirs(os.path.dirname(os.path.abspath(gen_path)), exist_ok=True)
    gen_f = open(gen_path, "a")
    exec_py = args.exec_python
    if exec_py and subprocess.run([exec_py, "-c", "import build123d, trimesh"], capture_output=True).returncode != 0:
        log(f"[eval] {exec_py} lacks build123d/trimesh; dumping generations only", flush=True); exec_py = ""
    iou_once = os.path.join(HERE, "iou_once.py")
    keys = [k for k in cache["pools"]["certified"] if os.path.exists(os.path.join(gt_dir, k + ".stl"))][: args.eval_n]
    keys = keys[rank::world]   # the eval is sharded across replicas and merged by rank 0
    model.eval(); harness = os.path.join(HERE, "exec_harness.py"); recs = []
    from PIL import Image
    for k in keys:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
            tf.write(cache["samples"][k]["png"]); png_path = tf.name
        try:
            msgs = [{"role": "system", "content": system},
                    {"role": "user", "content": [{"type": "image_url", "image_url": {"url": png_path}},
                                                 {"type": "text", "text": user}]}]
            prompt = dsenc.encode_messages(msgs, thinking_mode="thinking" if args.think else "chat")
        finally:
            os.unlink(png_path)
        img = Image.open(io.BytesIO(cache["samples"][k]["png"])).convert("RGB")
        enc = proc(text=[prompt], images=[img], return_tensors="pt")
        enc = {kk: (v.to(dev) if hasattr(v, "to") else v) for kk, v in enc.items()}
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
            out = model.generate(**enc, max_new_tokens=args.eval_max_new, do_sample=False)
        text = tok.decode(out[0, enc["input_ids"].shape[-1]:], skip_special_tokens=True)
        code = extract_code(text); rec = {"key": k, "exec": False, "iou": 0.0, "chars": len(text), "scored": bool(exec_py)}
        gen_f.write(json.dumps({"key": k, "text": text, "code": code or ""}) + "\n"); gen_f.flush()
        if code and exec_py:
            with tempfile.TemporaryDirectory() as td:
                cp, stl = os.path.join(td, "c.py"), os.path.join(td, "c.stl")
                open(cp, "w").write(code)
                try:
                    p = subprocess.run([exec_py, harness, cp, stl], capture_output=True, text=True, timeout=120)
                    if p.returncode == 0 and os.path.exists(stl):
                        q = subprocess.run([exec_py, iou_once, stl, os.path.join(gt_dir, k + ".stl")], capture_output=True, text=True, timeout=120)
                        rec["exec"] = True; rec["iou"] = float(json.loads(q.stdout.strip().splitlines()[-1])["iou_centered"]) if q.returncode == 0 else 0.0
                except Exception:
                    pass
        recs.append(rec)
        print(f"[eval r{rank}] {len(recs)}/{len(keys)} {k[:24]} exec={rec['exec']} iou={rec['iou']:.3f} chars={rec['chars']}", flush=True)
    if dist is not None:
        gathered = [None] * world
        dist.all_gather_object(gathered, recs)
        if rank != 0:
            return
        recs = [r for part in gathered for r in part]
    ious = [r["iou"] for r in recs]
    summ = {"n": len(recs), "first_exec_mean": sum(ious) / len(ious), "ge85": sum(x >= 0.85 for x in ious) / len(ious),
            "executed": sum(r["exec"] for r in recs), "with_code": sum(1 for r in recs if r["chars"] and r["exec"] or r["iou"] > 0)}
    json.dump({"summary": summ, "records": recs}, open(os.path.join(args.out, "eval.json"), "w"), indent=1)
    print("[eval] " + json.dumps(summ) + ("" if exec_py else "  (generations only -> score with dsv41_eval_score.py)"), flush=True)


if __name__ == "__main__":
    main()
