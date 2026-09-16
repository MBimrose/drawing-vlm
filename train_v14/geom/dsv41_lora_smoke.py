"""Stage 1 of the DeepSeek-V4.1-Flash fine-tune spike: does a LoRA forward+backward run at all?

Loads the checkpoint as released (FP8 block weights, FP4 experts) pipeline-split across the
GPUs with device_map="auto", freezes everything, attaches a rank-r LoRA to the attention and
dense (non-expert) projections through PEFT, builds ONE real training sample (drawing PNG +
the served prompt + a certified build123d answer) with the model's own processor, and runs a
single forward/backward with gradient checkpointing. Reports peak memory per GPU, the loss,
and whether every LoRA parameter received a gradient. Kill criteria for the spike:
  * the checkpoint will not load (FP4 experts / engram tables unsupported)  -> stop;
  * forward runs but backward raises (a kernel without autograd)             -> stop;
  * it fits and trains -> stage 2 (a short LoRA run on the certified tier, scored on 96 parts).

    CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 python dsv41_lora_smoke.py --model models/DeepSeek-V4.1-Flash \
        --png <sheet.png> --answer <answer.py> [--rank 16] [--max-len 4096]
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--png", required=True)
    ap.add_argument("--answer", required=True, help="a build123d script that solves the sheet")
    ap.add_argument("--rank", type=int, default=16)
    ap.add_argument("--max-len", type=int, default=4096)
    ap.add_argument("--targets", default=r"(q_proj|q_b_proj|kv_b_proj|kv_a_proj_with_mqa|o_proj)$",
                    help="regex on module names for LoRA (attention by default; experts never)")
    args = ap.parse_args()

    import torch
    from PIL import Image
    from transformers import AutoModelForImageTextToText, AutoProcessor
    from collate_v14 import SYSTEM_PROMPTS
    from geom_eval_worker import USER_PROMPT

    t0 = time.time()
    proc = AutoProcessor.from_pretrained(args.model)
    model = AutoModelForImageTextToText.from_pretrained(args.model, device_map="auto", torch_dtype=torch.bfloat16)
    print(f"[smoke] loaded {type(model).__name__} in {time.time()-t0:.0f}s", flush=True)
    for i in range(torch.cuda.device_count()):
        print(f"  gpu{i} allocated {torch.cuda.memory_allocated(i)/2**30:.0f} GiB", flush=True)
    for p in model.parameters():
        p.requires_grad_(False)

    # LoRA on attention / dense projections only, never on the 384 experts
    from peft import LoraConfig, get_peft_model
    names = [n for n, m in model.named_modules() if isinstance(m, torch.nn.Linear) and re.search(args.targets, n)
             and "expert" not in n and "vision" not in n and "aligner" not in n]
    print(f"[smoke] {len(names)} target linears, e.g. {names[:3]}", flush=True)
    lcfg = LoraConfig(r=args.rank, lora_alpha=2 * args.rank, lora_dropout=0.0, target_modules=names, bias="none")
    model = get_peft_model(model, lcfg)
    n_tr = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[smoke] trainable params {n_tr/1e6:.1f}M", flush=True)
    model.gradient_checkpointing_enable()
    model.train()

    # one real sample: served prompt + drawing -> certified answer
    answer = open(args.answer).read()
    msgs = [{"role": "system", "content": [{"type": "text", "text": SYSTEM_PROMPTS["detailed"]}]},
            {"role": "user", "content": [{"type": "image", "image": Image.open(args.png).convert("RGB")},
                                         {"type": "text", "text": USER_PROMPT}]},
            {"role": "assistant", "content": [{"type": "text", "text": "```python\n" + answer + "\n```"}]}]
    enc = proc.apply_chat_template(msgs, tokenize=True, return_dict=True, return_tensors="pt",
                                   truncation=True, max_length=args.max_len)
    enc = {k: (v.to(model.device) if hasattr(v, "to") else v) for k, v in enc.items()}
    labels = enc["input_ids"].clone()
    print(f"[smoke] sample tokens {labels.shape[-1]}", flush=True)
    t1 = time.time()
    out = model(**enc, labels=labels)
    print(f"[smoke] forward ok: loss {out.loss.item():.4f} ({time.time()-t1:.0f}s)", flush=True)
    t2 = time.time()
    out.loss.backward()
    got = sum(1 for p in model.parameters() if p.requires_grad and p.grad is not None)
    tot = sum(1 for p in model.parameters() if p.requires_grad)
    print(f"[smoke] backward ok ({time.time()-t2:.0f}s): {got}/{tot} LoRA tensors received a gradient", flush=True)
    for i in range(torch.cuda.device_count()):
        print(f"  gpu{i} peak {torch.cuda.max_memory_allocated(i)/2**30:.0f} GiB", flush=True)
    print("[smoke] STAGE1 OK" if got == tot else "[smoke] STAGE1 PARTIAL", flush=True)


if __name__ == "__main__":
    main()
