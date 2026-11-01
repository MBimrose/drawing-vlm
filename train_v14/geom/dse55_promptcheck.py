"""Gate for the DeepSeek e55-recipe run (2026-10-21): the prompt the trainer builds (dsv41_lora_train.build_sample,
thinking mode, the tier's prompts.json, --reasoning-effort) must be the prompt vLLM builds from gen_openai_bo.py's
eval payload (SYSTEM_PROMPTS["detailed"] + image + USER_PROMPT, chat_template_kwargs thinking + reasoning_effort).
  1. prompts.json == the eval strings (system, user)
  2. per row (image included): trainer prompt length == the server's usage.prompt_tokens (max_tokens 1)
  3. text-only render: trainer token ids == vLLM /tokenize ids (catches an effort or thinking-flag mismatch that
     leaves the length unchanged); skipped with a warning if the server has no chat /tokenize
Exit 0 = pass.
    python dse55_promptcheck.py --tier dsv41_e55/tier --prompts dsv41_e55/prompts.json --effort 25 \
        --url http://127.0.0.1:8201/v1 --model base
"""
import argparse
import base64
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)


def post(url, body, timeout=600):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", required=True)
    ap.add_argument("--prompts", required=True)
    ap.add_argument("--effort", type=int, default=25)
    ap.add_argument("--url", required=True)
    ap.add_argument("--model", default="base")
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--model-dir", default="/srv/scratch/bimrose2/models/DeepSeek-V4.1-Flash")
    a = ap.parse_args()
    from collate_v14 import SYSTEM_PROMPTS
    from geom_eval_worker import USER_PROMPT
    from dsv41_lora_train import load_tier, build_sample
    from transformers import AutoTokenizer
    from transformers.models.deepseek_v41.image_processing_pil_deepseek_v41 import DeepseekV41ImageProcessorPil
    from transformers.models.deepseek_v41.processing_deepseek_v41 import DeepseekV41Processor
    sys.path.insert(0, os.path.join(a.model_dir, "encoding"))
    import encoding as dsenc
    pj = json.load(open(a.prompts))
    bad = 0
    if pj["system"] != SYSTEM_PROMPTS["detailed"] or pj["user"] != USER_PROMPT:
        print("FAIL prompts.json differs from the eval prompt (SYSTEM_PROMPTS['detailed'] / USER_PROMPT)"); bad += 1
    tok = AutoTokenizer.from_pretrained(a.model_dir)
    proc = DeepseekV41Processor(image_processor=DeepseekV41ImageProcessorPil(), tokenizer=tok)
    kw = {"enable_thinking": True, "thinking": True, "reasoning_effort": a.effort}   # = gen_openai_bo.chat with REASONING_EFFORT
    rows = [r for r in load_tier(a.tier, limit=4 * a.n) if not r.get("user")][: a.n]
    for r in rows:
        enc = build_sample(proc, dsenc, pj["system"], pj["user"], r["png"], r["code"], proc.image_token, 10**9, None,
                           r.get("think") or "", None, a.effort)
        n_hf = int((enc["labels"][0] == -100).sum())
        d = post(a.url.rstrip("/") + "/chat/completions", {
            "model": a.model, "temperature": 0.0, "max_tokens": 1,
            "messages": [{"role": "system", "content": pj["system"]},
                         {"role": "user", "content": [
                             {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(r["png"]).decode()}},
                             {"type": "text", "text": pj["user"]}]}],
            "chat_template_kwargs": kw})
        n_srv = d["usage"]["prompt_tokens"]
        ok = n_hf == n_srv
        bad += not ok
        print(f"{r['key'][:44]:44s} prompt tokens: trainer {n_hf} server {n_srv} {'OK' if ok else 'MISMATCH'}")
    # text-only render, token ids
    msgs = [{"role": "system", "content": pj["system"]}, {"role": "user", "content": pj["user"]}]
    ids_hf = tok.encode(dsenc.encode_messages(msgs, thinking_mode="thinking", reasoning_effort=a.effort), add_special_tokens=False)
    root = a.url.rstrip("/")
    root = root[:-3] if root.endswith("/v1") else root
    try:
        t = post(root + "/tokenize", {"model": a.model, "messages": msgs, "add_generation_prompt": True, "chat_template_kwargs": kw})
        ids_srv = t["tokens"]
        same = ids_srv == ids_hf
        if not same and (ids_srv[1:] == ids_hf or ids_srv == ids_hf[1:]):
            same = True; print("(BOS counted on one side only)")
        bad += not same
        print(f"text-only render: trainer {len(ids_hf)} ids, server {len(ids_srv)} ids -> {'IDENTICAL' if same else 'DIFFERENT'}")
        if not same:
            print("  trainer tail:", repr(tok.decode(ids_hf[-30:])))
            print("  server  tail:", repr(tok.decode(ids_srv[-30:])))
    except Exception as e:
        print(f"WARN no chat /tokenize on the server ({type(e).__name__}: {str(e)[:100]}); token lengths only")
    print("PROMPT CHECK " + ("PASS" if bad == 0 else f"FAIL ({bad})"))
    sys.exit(0 if bad == 0 else 1)


if __name__ == "__main__":
    main()
