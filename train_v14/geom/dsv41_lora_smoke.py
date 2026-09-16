"""Stage 1 of the DeepSeek-V4.1-Flash fine-tune spike: does a LoRA forward+backward run at all?

Loads the checkpoint as released (FP8 block weights, FP4 experts) pipeline-split across the
GPUs with device_map="auto", freezes everything, attaches a rank-r LoRA to the attention and
dense (non-expert) projections through PEFT, builds ONE real training sample (drawing PNG +
the served prompt + a certified build123d answer) with the model's own processor, and runs a
forward/backward, then a few AdamW steps on that sample (the answer loss must fall) and a greedy
continuation. Reports peak memory per GPU, the losses, and whether every LoRA parameter
received a gradient; STAGE1 OK needs all three. Kill criteria for the spike:
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
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--fit-steps", type=int, default=6, help="AdamW steps on the one sample; the loss must fall")
    ap.add_argument("--gen-tokens", type=int, default=48)
    ap.add_argument("--targets", default=r"self_attn\.(q_a_proj|q_b_proj|k_proj|kv_proj|o_a_proj|o_b_proj)$",
                    help="regex on module names for LoRA (attention by default; experts never)")
    args = ap.parse_args()

    import torch
    from PIL import Image
    from transformers import AutoModelForImageTextToText, AutoProcessor
    try:
        from collate_v14 import SYSTEM_PROMPTS
        from geom_eval_worker import USER_PROMPT
        system, user = SYSTEM_PROMPTS["detailed"], USER_PROMPT
    except Exception:   # the spike venv lacks the training deps; prompts.json is written by the main venv
        import json
        pj = json.load(open(os.path.join(os.path.dirname(args.png), "prompts.json")))
        system, user = pj["system"], pj["user"]

    # The released checkpoint ships a tokenizer but no processor config or chat template: the
    # image processor comes from the PR's class defaults, and the prompt format from the
    # checkpoint's own encoding/encoding.py (the reference the model was trained against).
    from transformers import AutoTokenizer
    from transformers.models.deepseek_v41.image_processing_deepseek_v41 import DeepseekV41ImageProcessor
    from transformers.models.deepseek_v41.processing_deepseek_v41 import DeepseekV41Processor
    sys.path.insert(0, os.path.join(args.model, "encoding"))
    import encoding as dsenc
    tok = AutoTokenizer.from_pretrained(args.model)
    proc = DeepseekV41Processor(image_processor=DeepseekV41ImageProcessor(), tokenizer=tok)
    print(f"[smoke] processor built by hand; image token id {proc.image_token_id}", flush=True)
    t0 = time.time()
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
    import collections
    print(f"[smoke] {len(names)} target linears by suffix: "
          f"{dict(collections.Counter(n.rsplit('.', 1)[-1] for n in names))}", flush=True)
    attn = sorted({n.rsplit('.', 1)[-1] for n, m in model.named_modules() if isinstance(m, torch.nn.Linear) and "self_attn" in n})
    print(f"[smoke] attention linear names present: {attn}", flush=True)
    lcfg = LoraConfig(r=args.rank, lora_alpha=2 * args.rank, lora_dropout=0.0, target_modules=names, bias="none")
    model = get_peft_model(model, lcfg)
    n_tr = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[smoke] trainable params {n_tr/1e6:.1f}M", flush=True)
    try:
        model.gradient_checkpointing_enable()
    except ValueError as e:   # the draft class does not implement it; ~230 GB free per B300 makes it optional
        print(f"[smoke] no gradient checkpointing ({e}); continuing without", flush=True)
    model.train()

    # one real sample: served prompt + drawing -> certified answer; loss on the answer span only
    answer = open(args.answer).read()
    msgs = [{"role": "system", "content": system},
            {"role": "user", "content": [{"type": "image_url", "image_url": {"url": os.path.abspath(args.png)}},
                                         {"type": "text", "text": user}]}]
    reply = {"role": "assistant", "content": "```python\n" + answer + "\n```"}
    def enc_prompt(m):
        try:
            r = dsenc.encode_messages(m, thinking_mode="chat")
        except TypeError:
            r = dsenc.encode_messages(m)
        return r[0] if isinstance(r, (tuple, list)) else r
    prompt_only, prompt = enc_prompt(msgs), enc_prompt(msgs + [reply])
    print(f"[smoke] encoded prompt: {len(prompt)} chars, {prompt.count(proc.image_token)} image placeholder(s); "
          f"tail: {prompt[-120:]!r}", flush=True)
    img = Image.open(args.png).convert("RGB")
    enc = proc(text=[prompt], images=[img], return_tensors="pt")
    n_pre = proc(text=[prompt_only], images=[img], return_tensors="pt")["input_ids"].shape[-1]
    if enc["input_ids"].shape[-1] > args.max_len:
        print(f"[smoke] WARNING sample is {enc['input_ids'].shape[-1]} tokens > max-len {args.max_len}", flush=True)
    enc = {k: (v.to(model.device) if hasattr(v, "to") else v) for k, v in enc.items()}
    labels = enc["input_ids"].clone(); labels[:, :n_pre] = -100
    n_ans = int((labels != -100).sum())
    print(f"[smoke] sample tokens {labels.shape[-1]} (prompt {n_pre}, answer {n_ans})", flush=True)
    t1 = time.time()
    out = model(**enc, labels=labels)
    loss0 = out.loss.item()
    print(f"[smoke] forward ok: answer loss {loss0:.4f} nats/token ({time.time()-t1:.0f}s)", flush=True)
    t2 = time.time()
    out.loss.backward()
    got = sum(1 for p in model.parameters() if p.requires_grad and p.grad is not None)
    tot = sum(1 for p in model.parameters() if p.requires_grad)
    gnorm = sum(float(p.grad.float().norm()) ** 2 for p in model.parameters() if p.requires_grad and p.grad is not None) ** 0.5
    print(f"[smoke] backward ok ({time.time()-t2:.0f}s): {got}/{tot} LoRA tensors received a gradient, grad norm {gnorm:.3e}", flush=True)
    for i in range(torch.cuda.device_count()):
        print(f"  gpu{i} peak {torch.cuda.max_memory_allocated(i)/2**30:.0f} GiB", flush=True)

    # does it actually train? a few AdamW steps on this one sample must drive the answer loss down
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=args.lr, weight_decay=0.0)
    losses = [loss0]
    for step in range(args.fit_steps):
        opt.step(); opt.zero_grad(set_to_none=True)
        out = model(**enc, labels=labels); losses.append(out.loss.item()); out.loss.backward()
        print(f"[smoke] fit step {step+1}/{args.fit_steps}: answer loss {losses[-1]:.4f}", flush=True)
    opt.zero_grad(set_to_none=True)
    fell = losses[-1] < 0.8 * losses[0]
    print(f"[smoke] one-sample fit: loss {losses[0]:.4f} -> {losses[-1]:.4f} ({'fell' if fell else 'DID NOT FALL'})", flush=True)

    # and inference through the same weights: greedy continuation of the prompt after the fit
    model.eval()
    penc = proc(text=[prompt_only], images=[img], return_tensors="pt")
    penc = {k: (v.to(model.device) if hasattr(v, "to") else v) for k, v in penc.items()}
    with torch.no_grad():
        gen = model.generate(**penc, max_new_tokens=args.gen_tokens, do_sample=False)
    text = tok.decode(gen[0, penc["input_ids"].shape[-1]:], skip_special_tokens=True)
    print(f"[smoke] greedy continuation ({args.gen_tokens} tokens): {text!r}", flush=True)
    ok = got == tot and fell
    print("[smoke] STAGE1 OK" if ok else "[smoke] STAGE1 PARTIAL", flush=True)


if __name__ == "__main__":
    main()
