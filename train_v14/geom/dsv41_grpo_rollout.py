"""DeepSeek GRPO rollouts (2026-10-06): G sampled thinking-mode answers per part from the served policy (vLLM on
serv-19 :8200), brief-reasoning regime (prompt = dsv41_grpo_prompts.json, "Reasoning Effort: 50", max_tokens ~8k).
No scoring here: writes one score_partials-compatible checkpoint per bench (<out>_<bench>.partial.json:
{"keys": [...], "cands": [[{draw, code, think, reply, finish, completion_tokens}, ...]]}) so execute + IoU runs with
score_partials.py on a CPU host. Resumable (<out>.jsonl holds every finished request).

    python dsv41_grpo_rollout.py --parts round_parts.tsv --base-url http://wpk-serv-19...:8200/v1 --model pol \
        --k 4 --temperature 0.8 --max-tokens 8192 --out runs/r00/roll
parts.tsv: <bench dir>\t<key> per line.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import pickle
import sys
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from geom_eval_worker import extract_code  # noqa: E402


def ask(base_url, model, png, system, user, temperature, top_p, max_tokens, effort, timeout, seed=None):
    body = {"model": model, "temperature": temperature, "top_p": top_p, "max_tokens": max_tokens,
            "chat_template_kwargs": {"thinking": True, "enable_thinking": True, "reasoning_effort": effort},
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": [
                             {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(png).decode()}},
                             {"type": "text", "text": user}]}]}
    if seed is not None:
        body["seed"] = seed
    req = urllib.request.Request(base_url.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.load(r)
    ch = d["choices"][0]; m = ch["message"]
    return (m.get("content") or ""), (m.get("reasoning_content") or m.get("reasoning") or ""), ch.get("finish_reason"), d.get("usage", {})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True, help="prefix: <out>.jsonl + <out>_<bench>.partial.json")
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--temperature", type=float, default=0.8)
    ap.add_argument("--top-p", type=float, default=1.0)
    ap.add_argument("--max-tokens", type=int, default=8192)
    ap.add_argument("--effort", type=int, default=50)
    ap.add_argument("--prompts", default=os.path.join(HERE, "dsv41_grpo_prompts.json"))
    ap.add_argument("--workers", type=int, default=48)
    ap.add_argument("--timeout", type=int, default=3600)
    ap.add_argument("--seed", type=int, default=-1, help=">= 0: per-request seed = seed*1000003 + hash -> reproducible draws")
    a = ap.parse_args()

    pj = json.load(open(a.prompts)); system, user = pj["system"], pj["user"]
    parts = [tuple(l.rstrip("\n").split("\t")) for l in open(a.parts) if l.strip()]
    benches = sorted({b for b, _ in parts})
    pngs = {}
    for b in benches:
        c = pickle.load(open(os.path.join(b, "eval_cache_v15.pkl"), "rb"))["samples"]
        for bb, k in parts:
            if bb == b:
                pngs[(b, k)] = c[k]["png"]
        del c
    done = {}
    jl = a.out + ".jsonl"
    if os.path.exists(jl):
        for line in open(jl):
            try:
                r = json.loads(line); done[(r["bench"], r["key"], r["draw"])] = r
            except Exception:
                pass
    todo = [(b, k, d) for b, k in parts for d in range(a.k) if (b, k, d) not in done]
    print(f"[roll] {len(parts)} parts x {a.k} = {len(parts) * a.k} requests, {len(todo)} to do, T={a.temperature} "
          f"max_tokens={a.max_tokens} effort={a.effort}", flush=True)
    lock = threading.Lock(); f = open(jl, "a"); t0 = time.time(); n = [0]

    def one(item):
        b, k, d = item
        rec = {"bench": b, "key": k, "draw": d}
        seed = None if a.seed < 0 else (a.seed * 1000003 + hash((k, d)) % 1000003)
        for attempt in range(3):
            try:
                text, reasoning, fin, usage = ask(a.base_url, a.model, pngs[(b, k)], system, user, a.temperature, a.top_p,
                                                  a.max_tokens, a.effort, a.timeout, seed)
                rec.update({"code": extract_code(text) or "", "think": reasoning, "reply": text, "finish": fin,
                            "completion_tokens": usage.get("completion_tokens", 0), "prompt_tokens": usage.get("prompt_tokens", 0)})
                break
            except Exception as e:
                rec["error"] = f"{type(e).__name__}: {str(e)[:200]}"; time.sleep(10 * (attempt + 1))
        with lock:
            f.write(json.dumps(rec) + "\n"); f.flush(); n[0] += 1
            if n[0] % 20 == 0:
                print(f"[roll] {n[0]}/{len(todo)} {(time.time() - t0) / 60:.1f} min", flush=True)
        return rec

    with ThreadPoolExecutor(a.workers) as ex:
        for rec in ex.map(one, todo):
            done[(rec["bench"], rec["key"], rec["draw"])] = rec
    f.close()
    for b in benches:
        keys = [k for bb, k in parts if bb == b]
        cands = [[{kk: v for kk, v in done.get((b, k, d), {"draw": d, "code": ""}).items() if kk not in ("bench", "key")}
                  for d in range(a.k)] for k in keys]
        json.dump({"keys": keys, "cands": cands}, open(f"{a.out}_{os.path.basename(b.rstrip('/'))}.partial.json", "w"))
    recs = list(done.values())
    trunc = sum(r.get("finish") == "length" for r in recs); code = sum(bool(r.get("code")) for r in recs)
    toks = sorted(r.get("completion_tokens", 0) for r in recs)
    print(f"[roll] done {len(recs)} in {(time.time() - t0) / 60:.1f} min: with code {code}, truncated {trunc}, "
          f"errors {sum('error' in r and 'code' not in r for r in recs)}, completion tokens median {toks[len(toks) // 2] if toks else 0}",
          flush=True)


if __name__ == "__main__":
    main()
