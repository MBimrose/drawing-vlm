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
                rows.append({"key": key, "png": t.extractfile(members[key + ".png"]).read(),
                             "code": t.extractfile(members[name]).read().decode()})
                if limit and len(rows) >= limit:
                    return rows
    return rows


def build_sample(proc, dsenc, system, user, png, answer, image_token, max_len):
    """Prompt via the released encoder; labels masked to the assistant answer."""
    from PIL import Image
    import torch
    # encoding.py takes image blocks by path (as in the stage-1 smoke); the real pixels go to
    # the processor separately, so the path only has to exist for placeholder bookkeeping.
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
        tf.write(png); png_path = tf.name
    try:
        msgs = [{"role": "system", "content": system},
                {"role": "user", "content": [{"type": "image_url", "image_url": {"url": png_path}},
                                             {"type": "text", "text": user}]}]
        prompt_no_answer = dsenc.encode_messages(msgs, thinking_mode="chat")
        full = dsenc.encode_messages(msgs + [{"role": "assistant", "content": "```python\n" + answer + "\n```"}],
                                     thinking_mode="chat")
    finally:
        os.unlink(png_path)
    if not full.startswith(prompt_no_answer):
        prompt_no_answer = full[: full.rfind("```python")]
    img = Image.open(io.BytesIO(png)).convert("RGB")
    enc = proc(text=[full], images=[img], return_tensors="pt")
    pre = proc(text=[prompt_no_answer], images=[img], return_tensors="pt")
    n_pre = pre["input_ids"].shape[-1]
    labels = enc["input_ids"].clone()
    labels[:, :n_pre] = -100
    if labels.shape[-1] > max_len:
        return None
    enc["labels"] = labels
    return enc


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
    ap.add_argument("--prompts", default="", help="prompts.json (system/user); default: next to the tier, else spike_dsv41/prompts.json")
    ap.add_argument("--dist", action="store_true",
                    help="one process per node (SLURM_PROCID/SLURM_NTASKS, MASTER_ADDR/PORT); each node holds a full "
                         "pipeline-split replica, LoRA gradients are averaged across nodes over NCCL")
    args = ap.parse_args()

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
    import dsv41_autograd; dsv41_autograd.register()   # backward for the Hub FP8/MXFP4 ops (input grads only)
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
    proc = DeepseekV41Processor(image_processor=DeepseekV41ImageProcessor(), tokenizer=tok)
    model = AutoModelForImageTextToText.from_pretrained(args.model, device_map="auto", dtype=torch.bfloat16)
    for p in model.parameters():
        p.requires_grad_(False)
    from peft import LoraConfig, get_peft_model, PeftModel
    if args.adapter:
        model = PeftModel.from_pretrained(model, args.adapter, is_trainable=args.steps > 0)
        names = [n for n, m in model.named_modules() if hasattr(m, "lora_A")]
        log(f"[train] loaded adapter {args.adapter}", flush=True)
    else:
        names = [n for n, m in model.named_modules() if isinstance(m, torch.nn.Linear) and re.search(args.targets, n)]
        model = get_peft_model(model, LoraConfig(r=args.rank, lora_alpha=2 * args.rank, lora_dropout=0.0,
                                                  target_modules=names, bias="none"))
    params = [p for p in model.parameters() if p.requires_grad]
    log(f"[train] {len(names)} LoRA targets, {sum(p.numel() for p in params)/1e6:.1f}M trainable", flush=True)
    opt = torch.optim.AdamW(params, lr=args.lr, weight_decay=0.0, betas=(0.9, 0.95))
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / 20) * max(0.1, 1 - s / max(1, args.steps)))

    rows = load_tier(args.tier, args.limit)
    random.Random(args.seed).shuffle(rows)
    rows = rows[rank::world]
    log(f"[train] {len(rows) * world} tier rows ({len(rows)} per rank), {args.accum * world} samples per optimizer step", flush=True)
    model.train()
    t0 = time.time(); step = 0; i = 0; acc_loss = 0.0; n_acc = 0; skipped = 0
    dev = model.device
    while step < args.steps:
        row = rows[i % len(rows)]; i += 1
        enc = build_sample(proc, dsenc, system, user, row["png"], row["code"], proc.image_token, args.max_len)
        if enc is None:
            skipped += 1; continue
        enc = {k: (v.to(dev) if hasattr(v, "to") else v) for k, v in enc.items()}
        ts = time.time()
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
    from geom_eval_worker import extract_code
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
            prompt = dsenc.encode_messages(msgs, thinking_mode="chat")
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
