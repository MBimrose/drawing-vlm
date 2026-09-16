"""Best-of-K candidate generation through an OpenAI-compatible endpoint (vLLM), in the
bestofn_verifier_eval.py checkpoint format, so scoring stays on the CPU path.

Why: HF `generate` in bestofn_verifier_eval.py does ~20 draws/min/GPU; a 110k-part real corpus
at K=8 is 880k draws (days). vLLM batches the same model 5-10x faster, and the execute-and-score
half already runs from `.partial.json` checkpoints (`score_partials.py`, resumable, bounded
overlap cost). This script only generates:

    <out>.shard<i>.json.partial.json   {"keys": [...], "k": K, "cands": [[{draw, code, think,
                                        exec: false, iou: 0.0}, ...] per key]}

Draw 0 is greedy, draws 1..K-1 are sampled at --temperature / --top-p 0.95 -- the same recipe
as bestofn_verifier_eval.py, so a tier built from these is on-policy for the served model.
Prompt = the fine-tuned model's exact system/user text (collate_v14 / geom_eval_worker).
Reasoning is kept from `reasoning_content` when the server separates it (Qwen3 thinking) or
from a <think> block in the text otherwise. Resumable per key.

    python gen_openai_bo.py --bench <corpus dir with eval_cache_v15.pkl> --base-url http://127.0.0.1:8000/v1 \
        --model e55 --k 8 --shard 0 --nshards 1 --out <corpus>/results/bo8_<corpus>_<run>  [--n 0] [--workers 32]
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import pickle
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

from collate_v14 import SYSTEM_PROMPTS  # noqa: E402
from geom_eval_worker import USER_PROMPT, extract_code  # noqa: E402


def chat(base_url, model, png, system, user, temperature, top_p, n, max_tokens, timeout, think):
    import urllib.request
    body = {"model": model, "temperature": temperature, "top_p": top_p, "n": n, "max_tokens": max_tokens,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": [
                             {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(png).decode()}},
                             {"type": "text", "text": user}]}],
            "chat_template_kwargs": {"enable_thinking": think}}
    req = urllib.request.Request(base_url.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.load(r)
    outs = []
    for ch in d["choices"]:
        m = ch["message"]
        text = m.get("content") or ""
        reasoning = m.get("reasoning_content") or m.get("reasoning") or ""
        if not reasoning and "</think>" in text:
            reasoning, text = text.split("</think>", 1)[0].replace("<think>", "").strip(), text.split("</think>", 1)[1]
        outs.append((text, reasoning))
    return outs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bench", required=True)
    ap.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    ap.add_argument("--model", required=True, help="served-model-name")
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--top-p", type=float, default=0.95)
    ap.add_argument("--max-tokens", type=int, default=2400)
    ap.add_argument("--n", type=int, default=0)
    ap.add_argument("--keys", default="")
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--system-prompt", default="detailed")
    ap.add_argument("--no-think", action="store_true")
    ap.add_argument("--out", required=True, help="output stem; writes <out>.shard<i>.json.partial.json")
    args = ap.parse_args()

    cache = pickle.load(open(os.path.join(args.bench, "eval_cache_v15.pkl"), "rb"))
    gt_dir = os.path.join(args.bench, "gt_meshes_v15")
    keys = [k for k in cache["pools"]["certified"] if os.path.exists(os.path.join(gt_dir, k + ".stl"))]
    if args.keys:
        want = [l.strip() for l in open(args.keys) if l.strip()]; have = set(keys)
        keys = [k for k in want if k in have]
    if args.n:
        keys = keys[: args.n]
    keys = keys[args.shard::args.nshards]
    system, user = SYSTEM_PROMPTS[args.system_prompt], USER_PROMPT
    out_path = f"{args.out}.shard{args.shard}.json.partial.json"
    done = {}
    if os.path.exists(out_path):
        d = json.load(open(out_path))
        done = dict(zip(d["keys"], d["cands"]))
    todo = [k for k in keys if k not in done or len(done[k]) < args.k]
    print(f"[gen] shard {args.shard}/{args.nshards}: {len(keys)} keys, {len(done)} done, {len(todo)} to draw, K={args.k}", flush=True)
    t0 = time.time(); n_done = [0]

    def one(key):
        png = cache["samples"][key]["png"]
        cands = []
        try:
            g = chat(args.base_url, args.model, png, system, user, 0.0, 1.0, 1, args.max_tokens, args.timeout, not args.no_think)
            s = chat(args.base_url, args.model, png, system, user, args.temperature, args.top_p, args.k - 1,
                     args.max_tokens, args.timeout, not args.no_think) if args.k > 1 else []
        except Exception as e:
            print(f"[gen] {key}: {type(e).__name__}: {str(e)[:120]}", flush=True)
            return key, None
        for d, (text, reasoning) in enumerate(g + s):
            cands.append({"draw": d, "code": extract_code(text), "think": reasoning, "exec": False, "iou": 0.0})
        return key, cands

    def flush():
        ks = [k for k in keys if k in done]
        tmp = out_path + ".tmp"
        json.dump({"keys": ks, "k": args.k, "cands": [done[k] for k in ks]}, open(tmp, "w"))
        os.replace(tmp, out_path)

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for key, cands in ex.map(one, todo):
            if cands is not None:
                done[key] = cands
            n_done[0] += 1
            if n_done[0] % 50 == 0:
                flush()
                rate = n_done[0] / (time.time() - t0)
                print(f"[gen] {n_done[0]}/{len(todo)} parts  {rate*60:.1f} parts/min  "
                      f"eta {(len(todo)-n_done[0])/max(rate,1e-9)/3600:.1f} h", flush=True)
    flush()
    n_code = sum(1 for cs in done.values() for c in cs if c["code"])
    print(f"[gen] DONE shard {args.shard}: {len(done)} parts, {n_code} candidates with code -> {out_path}", flush=True)


if __name__ == "__main__":
    main()
