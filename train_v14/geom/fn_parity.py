"""HF-vs-vLLM per-token logprob parity for GRPO on Flash-Next (2026-10-19).

The GRPO trainer samples with vLLM and scores the same completions with HF (grpo_round.completion_logps). If the
two disagree, every PPO ratio is biased (the 27B T-mismatch and the DeepSeek indexer bugs). For a few training
parts: sample one completion from vLLM, send it back as an assistant prefill with prompt_logprobs (teacher-forced
vLLM logprobs of exactly those tokens), compute the HF logprobs of the same completion through the training
collator (content_raw = the verbatim text, as --train-raw), align the two token streams and compare.

    python fn_parity.py --url http://127.0.0.1:8750/v1 --model fnpol --ckpt <hf dir> \
        --model-base models/Qwen3.8-Flash-Next --run e59-flashnext-e55recipe --bench fp/h6/train_bench [--adapter <dir>]
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import random
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import torch  # noqa: E402

from collate_v14 import SYSTEM_PROMPTS, USER_PROMPT, VLMCollator  # noqa: E402
from data_v14 import _decode_png  # noqa: E402
from geom_eval_worker import classify_ckpt, load_model, run_config  # noqa: E402
from grpo_round import load_bench  # noqa: E402


def post(url, body, timeout=900):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--model", required=True, help="served model / LoRA name")
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--model-base", default="")
    ap.add_argument("--run", default="")
    ap.add_argument("--adapter", default="", help="peft adapter applied on the HF side (= the served LoRA)")
    ap.add_argument("--bench", required=True)
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--max-tokens", type=int, default=1200)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    cfg = run_config(args.run) or {}
    if args.model_base:
        cfg["model_id"] = args.model_base
    model, processor = load_model(args.ckpt, classify_ckpt(args.ckpt), cfg)
    if args.adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, args.adapter)
    model.eval()
    collator = VLMCollator(processor, max_seq_len=5120, system_prompt="detailed", reasoning_effort="medium")
    tmpl = {"enable_thinking": True, "reasoning_effort": "medium"}

    cache, keys, _ = load_bench(args.bench, "")
    random.Random(0).shuffle(keys)
    rows = []
    for k in keys[:args.n]:
        png = cache["samples"][k]["png"]
        msgs = [{"role": "system", "content": SYSTEM_PROMPTS["detailed"]},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(png).decode()}},
                    {"type": "text", "text": USER_PROMPT}]}]
        d = post(args.url.rstrip("/") + "/chat/completions",
                 {"model": args.model, "messages": msgs, "temperature": 1.0, "top_p": 1.0,
                  "max_tokens": args.max_tokens, "chat_template_kwargs": tmpl})
        m = d["choices"][0]["message"]
        reasoning = (m.get("reasoning_content") or m.get("reasoning") or "").strip()
        content = (m.get("content") or "").strip()
        raw = f"<think>\n{reasoning}\n</think>\n\n{content}" if reasoning else content
        # vLLM teacher-forced logprobs of the same assistant text (prefill continued, 1 new token)
        v = post(args.url.rstrip("/") + "/chat/completions",
                 {"model": args.model, "messages": msgs + [{"role": "assistant", "content": raw}],
                  "add_generation_prompt": False, "continue_final_message": True, "max_tokens": 1,
                  "temperature": 1.0, "prompt_logprobs": 0, "chat_template_kwargs": tmpl})
        plp = v.get("prompt_logprobs") or v["choices"][0].get("prompt_logprobs")
        v_ids, v_lp = [], []
        for e in plp[1:]:
            # each entry: {token_id: {"logprob", "rank", "decoded_token"}}; the actual token is the one listed (rank may vary)
            tid, info = next(iter(e.items())) if len(e) == 1 else min(e.items(), key=lambda kv: kv[1].get("rank", 0) or 0)
            v_ids.append(int(tid)); v_lp.append(float(info["logprob"]))
        # HF logprobs of the completion through the training collator
        processor.tokenizer.padding_side = "right"
        # as grpo_round --train-raw builds it: trace = the reasoning, content_raw = the answer text after </think>
        enc = collator([{"image": _decode_png(png), "trace": reasoning, "code": "", "content_raw": content}])
        dev = model.get_input_embeddings().weight.device
        enc = {kk: (vv.to(dev) if hasattr(vv, "to") else vv) for kk, vv in enc.items()}
        labels = enc.pop("labels")
        with torch.no_grad():
            logits = model(**enc).logits
        labels = labels.to(logits.device)
        js = (labels[0] != -100).nonzero(as_tuple=True)[0]
        h_ids = labels[0, js].tolist()
        h_lp = torch.log_softmax(logits[0, js - 1, :].float(), -1).gather(-1, labels[0, js].unsqueeze(-1)).squeeze(-1).tolist()
        # align: the vLLM prompt ends inside the assistant turn; locate HF's first 16 completion ids in the vLLM stream
        probe = h_ids[:16]
        start = next((i for i in range(len(v_ids) - len(probe) + 1) if v_ids[i:i + len(probe)] == probe), None)
        if start is None:
            print(f"[parity] {k}: could not align (hf {len(h_ids)} toks, vllm {len(v_ids)})", flush=True)
            rows.append({"key": k, "aligned": False}); continue
        n = min(len(h_ids), len(v_ids) - start)
        match = sum(a == b for a, b in zip(h_ids[:n], v_ids[start:start + n])) / max(1, n)
        diffs = [h - vv for h, vv in zip(h_lp[:n], v_lp[start:start + n])]
        ad = sorted(abs(x) for x in diffs)
        r = {"key": k, "aligned": True, "n": n, "id_match": round(match, 4),
             "mean_diff": round(sum(diffs) / n, 5), "mean_abs": round(sum(ad) / n, 5),
             "p99_abs": round(ad[int(0.99 * (n - 1))], 4), "frac_abs_gt_0.5": round(sum(x > 0.5 for x in ad) / n, 4),
             "hf_mean_lp": round(sum(h_lp[:n]) / n, 4), "vllm_mean_lp": round(sum(v_lp[start:start + n]) / n, 4)}
        print(f"[parity] {json.dumps(r)}", flush=True)
        rows.append(r)
    ok = [r for r in rows if r.get("aligned")]
    if ok:
        tot = sum(r["n"] for r in ok)
        summ = {"parts": len(ok), "tokens": tot,
                "mean_diff": round(sum(r["mean_diff"] * r["n"] for r in ok) / tot, 5),
                "mean_abs": round(sum(r["mean_abs"] * r["n"] for r in ok) / tot, 5),
                "id_match": round(sum(r["id_match"] * r["n"] for r in ok) / tot, 4)}
        print(f"[parity] SUMMARY {json.dumps(summ)}", flush=True)
    if args.out:
        json.dump(rows, open(args.out, "w"), indent=1)


if __name__ == "__main__":
    main()
