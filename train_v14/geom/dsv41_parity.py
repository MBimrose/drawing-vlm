"""HF-trainer vs vLLM parity harness for DeepSeek-V4.1-Flash (2026-10-06/07).

collect (vLLM server up, :8200, served name "pol"):
  - text-only: a long natural token sequence (BOS + a sampled reasoning trace + code), scored with prompt_logprobs=1
    -> the exact NLL of every token given its prefix + vLLM's top-1 token at every position;
  - image chat samples (T=1, logprobs, token ids) for the multimodal path.
score (GPUs free): the trainer's HF model (same loading as dsv41_lora_train.py) on the SAME token ids; per-position
  NLL / top-1 agreement vs vLLM, bucketed by position (gap vs context length).
    python dsv41_parity.py collect --text-src roll.jsonl --parts p.tsv --out ref.json
    python dsv41_parity.py score --ref ref.json --model models/DeepSeek-V4.1-Flash [--patch ...]
"""
import argparse, base64, io, json, os, pickle, sys, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
BUCKETS = [(0, 128), (128, 512), (512, 2048), (2048, 8192), (8192, 10**9)]


def post(url, body, timeout=3600):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, data=json.dumps(body).encode(),
                                            headers={"Content-Type": "application/json"}), timeout=timeout))


def collect(a):
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(a.model)
    pj = json.load(open(os.path.join(HERE, "dsv41_grpo_prompts.json")))
    ref = {"text": [], "image": []}
    srcs = [json.loads(l) for l in open(a.text_src)]
    srcs = sorted([r for r in srcs if r.get("code")], key=lambda r: -len(r.get("think") or ""))[: a.n_text]
    for r in srcs:
        ids = [0] + tok.encode(r["think"] + "\n\n```python\n" + r["code"] + "\n```", add_special_tokens=False)
        ids = ids[: a.text_len]
        d = post(a.base_url + "/completions", {"model": "pol", "prompt": ids, "max_tokens": 1, "temperature": 1.0,
                                                "prompt_logprobs": 1})
        pl = d["choices"][0]["prompt_logprobs"]
        lp, top1 = [None], [None]
        for i in range(1, len(ids)):
            e = pl[i]; t = str(ids[i])
            lp.append(e[t]["logprob"])
            top1.append(int(min(e.items(), key=lambda kv: kv[1].get("rank", 99))[0]))
        ref["text"].append({"key": r["key"], "ids": ids, "lp": lp, "top1": top1})
        print(f"[collect] text {r['key'][:30]} {len(ids)} tokens, vLLM mean NLL {-sum(lp[1:])/(len(ids)-1):.3f}", flush=True)
    parts = [l.rstrip("\n").split("\t") for l in open(a.parts) if l.strip()][: a.n_image]
    for b, k in parts:
        png = pickle.load(open(os.path.join(b, "eval_cache_v15.pkl"), "rb"))["samples"][k]["png"]
        body = {"model": "pol", "temperature": 1.0, "top_p": 1.0, "max_tokens": a.image_tokens, "logprobs": True, "top_logprobs": 5,
                "return_tokens_as_token_ids": True, "return_token_ids": True,
                "chat_template_kwargs": {"thinking": True, "enable_thinking": True, "reasoning_effort": a.effort},
                "messages": [{"role": "system", "content": pj["system"]}, {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(png).decode()}},
                    {"type": "text", "text": pj["user"]}]}]}
        d = post(a.base_url + "/chat/completions", body)
        ch = d["choices"][0]; content = ch["logprobs"]["content"]
        gen_ids = [int(c["token"].split(":")[1]) for c in content]
        lp = [c["logprob"] for c in content]
        # vLLM lists the SAMPLED token first in top_logprobs -> the argmax is the max-logprob entry, not entry 0
        top1 = [int(max(c["top_logprobs"], key=lambda e: e["logprob"])["token"].split(":")[1]) if c.get("top_logprobs") else None
                for c in content]
        rec = {"bench": b, "key": k, "prompt_ids": d.get("prompt_token_ids") or ch.get("prompt_token_ids"),
               "gen_ids": gen_ids, "lp": lp, "top1": top1, "finish": ch.get("finish_reason"),
               "think": ch["message"].get("reasoning_content") or ch["message"].get("reasoning") or "", "reply": ch["message"].get("content") or ""}
        ref["image"].append(rec)
        print(f"[collect] image {k[:30]} prompt {len(rec['prompt_ids'] or [])} gen {len(gen_ids)} vLLM NLL {-sum(lp)/len(lp):.3f}", flush=True)
    json.dump(ref, open(a.out, "w"))


def load_model(a):
    import torch
    import dsv41_autograd; dsv41_autograd.register()
    if a.chunked_attn:
        import dsv41_chunked_attn; dsv41_chunked_attn.install(chunk=a.chunked_attn)
    for p in (a.patch or "").split(","):
        if p:
            import dsv41_hf_fixes; getattr(dsv41_hf_fixes, "apply_" + p)()
            print(f"[score] patch {p} applied", flush=True)
    from transformers import AutoModelForImageTextToText, AutoTokenizer
    from transformers.models.deepseek_v41.image_processing_deepseek_v41 import DeepseekV41ImageProcessor
    from transformers.models.deepseek_v41.processing_deepseek_v41 import DeepseekV41Processor
    tok = AutoTokenizer.from_pretrained(a.model)
    if getattr(a, "fast_image", False):
        proc = DeepseekV41Processor(image_processor=DeepseekV41ImageProcessor(), tokenizer=tok)
    else:   # PIL backend = the reference/vLLM preprocessing (ImageOps.pad, PIL bicubic); the torchvision one differs ~4%
        from transformers.models.deepseek_v41.image_processing_pil_deepseek_v41 import DeepseekV41ImageProcessorPil
        proc = DeepseekV41Processor(image_processor=DeepseekV41ImageProcessorPil(), tokenizer=tok)
    n = torch.cuda.device_count(); tot = [torch.cuda.get_device_properties(i).total_memory / 2**30 for i in range(n)]
    mm = {i: f"{int(tot[i] * 0.9 - (60 if i == n - 1 else 8))}GiB" for i in range(n)}
    model = AutoModelForImageTextToText.from_pretrained(a.model, device_map="auto", dtype=torch.bfloat16, max_memory=mm)
    for m in model.modules():
        if type(m).__name__ == "DeepseekV41EngramEmbedding":
            for _, p in m.named_parameters(recurse=False):
                if p.device.type == "cpu":
                    p.data = p.data.clone()
    dm = getattr(model, "hf_device_map", {}) or {}
    deep = [k for k in dm if ".indexer" in k or ".compressor" in k][:6]
    print(f"[score] device_map entries below attention level (sample): {deep}", flush=True)
    hooked = sum(1 for n_, m in model.named_modules() if n_.endswith(".indexer") and hasattr(m, "_hf_hook"))
    print(f"[score] indexers with an accelerate hook: {hooked}", flush=True)
    if getattr(a, "fix", ""):
        import dsv41_hf_fixes
        dsv41_hf_fixes.fix_shared_dict_hooks(model)
    model.eval()
    return model, proc, tok


def stats(nll, agree, lo, hi):
    import torch
    s = slice(lo, hi)
    x = nll[s]; g = agree[s]
    if x.numel() == 0:
        return None
    return f"[{lo},{min(hi, lo + x.numel())}) n={x.numel()} hf {float(x.mean()):.3f}"


def score(a):
    import torch
    ref = json.load(open(a.ref))
    model, proc, tok = load_model(a)
    dev = model.device
    hooks = None
    out_rec = {"text": [], "image": []}
    for r in ref["text"]:
        ids = torch.tensor([r["ids"]], device=dev)
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
            lg = model(input_ids=ids, attention_mask=torch.ones_like(ids)).logits[0].float()
        tgt = ids[0, 1:]; logp = torch.log_softmax(lg[:-1], -1)
        nll_hf = -logp.gather(1, tgt[:, None])[:, 0].cpu()
        nll_v = -torch.tensor(r["lp"][1:])
        top_hf = lg[:-1].argmax(-1).cpu(); top_v = torch.tensor(r["top1"][1:])
        line = []
        for lo, hi in BUCKETS:
            if lo >= len(nll_hf): break
            s = slice(lo, hi)
            line.append(f"pos[{lo},{hi}) hf {float(nll_hf[s].mean()):.3f} vllm {float(nll_v[s].mean()):.3f} top1-agree {float((top_hf[s] == top_v[s]).float().mean()):.3f}")
        print(f"[score] TEXT {r['key'][:30]} {len(r['ids'])} tok | " + " | ".join(line), flush=True)
        out_rec["text"].append({"key": r["key"], "nll_hf": nll_hf.tolist(), "top_hf": top_hf.tolist()})
        del lg, logp
    sys.path.insert(0, os.path.join(a.model, "encoding")); import encoding as dsenc
    from dsv41_lora_train import build_sample
    pj = json.load(open(os.path.join(HERE, "dsv41_grpo_prompts.json")))
    for r in ref["image"]:
        png = pickle.load(open(os.path.join(r["bench"], "eval_cache_v15.pkl"), "rb"))["samples"][r["key"]]["png"]
        enc = build_sample(proc, dsenc, pj["system"], pj["user"], png, "", proc.image_token, 10**9, None, "", "", a.effort)
        hf_prompt = enc["input_ids"][0][enc["labels"][0] == -100].tolist()
        vp = r["prompt_ids"] or []
        same = hf_prompt == vp
        diff_at = next((i for i, (x, y) in enumerate(zip(hf_prompt, vp)) if x != y), None)
        print(f"[score] IMAGE {r['key'][:30]} prompt ids identical: {same} (hf {len(hf_prompt)} vllm {len(vp)} first diff {diff_at})", flush=True)
        ids = torch.tensor([vp + r["gen_ids"]], device=dev)
        kw = {k: v.to(dev) for k, v in enc.items() if k not in ("input_ids", "labels", "attention_mask") and hasattr(v, "to")}
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
            lg = model(input_ids=ids, attention_mask=torch.ones_like(ids), **kw).logits[0].float()
        P = len(vp); g = torch.tensor(r["gen_ids"], device=lg.device)
        logp = torch.log_softmax(lg[P - 1:-1], -1)
        nll_hf = -logp.gather(1, g[:, None])[:, 0].cpu(); nll_v = -torch.tensor(r["lp"])
        top_hf = lg[P - 1:-1].argmax(-1).cpu(); top_v = torch.tensor([t if t is not None else -1 for t in r["top1"]])
        line = []
        for lo, hi in BUCKETS:
            if lo >= len(nll_hf): break
            s = slice(lo, hi)
            line.append(f"gen[{lo},{hi}) hf {float(nll_hf[s].mean()):.3f} vllm {float(nll_v[s].mean()):.3f} top1 {float((top_hf[s] == top_v[s]).float().mean()):.3f}")
        print(f"[score] IMAGE {r['key'][:30]} | ALL hf {float(nll_hf.mean()):.3f} vllm {float(nll_v.mean()):.3f} top1 {float((top_hf == top_v).float().mean()):.3f} | " + " | ".join(line), flush=True)
        del lg, logp
    if a.out:
        json.dump(out_rec, open(a.out, "w"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("mode", choices=["collect", "score"])
    ap.add_argument("--model", default="models/DeepSeek-V4.1-Flash"); ap.add_argument("--base-url", default="http://127.0.0.1:8200/v1")
    ap.add_argument("--text-src"); ap.add_argument("--parts"); ap.add_argument("--out", default=""); ap.add_argument("--ref")
    ap.add_argument("--n-text", type=int, default=2); ap.add_argument("--text-len", type=int, default=8192)
    ap.add_argument("--n-image", type=int, default=3); ap.add_argument("--image-tokens", type=int, default=3000)
    ap.add_argument("--effort", type=int, default=50); ap.add_argument("--chunked-attn", type=int, default=256)
    ap.add_argument("--patch", default="", help="comma list of dsv41_hf_fixes.apply_<name> patches")
    ap.add_argument("--fast-image", action="store_true", help="torchvision image processor (pre-2026-10-07 trainer default)")
    ap.add_argument("--fix", default="", help="'shared': remove accelerate hooks that copy the CSA2 shared dict (dsv41_hf_fixes)")
    a = ap.parse_args()
    collect(a) if a.mode == "collect" else score(a)
