"""Zero-shot probe of an OpenAI-compatible vision model on a drawing bench.

Sends every sheet of a bench (eval cache PNGs) to a chat-completions endpoint with EXACTLY
the system/user prompt the fine-tuned model is served with, extracts the ```python block,
executes it through exec_harness.py and scores centered volumetric IoU against the bench's
ground-truth meshes -- so the number is comparable to the "first-exec" column of every
bo8_ext summary in results/ext (same parts, same prompt, same scorer). Greedy (temperature
0) unless --temperature is given; --k > 1 draws sampled candidates and reports the
best-of-K ceiling as well.

    python probe_openai_vlm.py --bench train_v14/mech/benchmarks/data/ext_bench \
        --base-url http://localhost:8000/v1 --model deepseek-ai/DeepSeek-V4.1-Flash \
        --out results/ext/probe_dsv41_ext.json [--n 146] [--k 1] [--workers 4]
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import os
import pickle
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

from collate_v14 import SYSTEM_PROMPTS  # noqa: E402
from geom_eval_worker import USER_PROMPT, extract_code  # noqa: E402
from iou import iou_pair  # noqa: E402

HARNESS = os.path.join(HERE, "exec_harness.py")
PYTHON = sys.executable


def png_b64(png_bytes):
    return base64.b64encode(png_bytes).decode()


def ask(base_url, model, png, system, user, temperature, max_tokens, timeout, think=True):
    import urllib.request
    body = {"model": model, "temperature": temperature, "max_tokens": max_tokens,
            "chat_template_kwargs": {"thinking": think, "enable_thinking": think},
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": [
                             {"type": "image_url", "image_url": {"url": "data:image/png;base64," + png_b64(png)}},
                             {"type": "text", "text": user}]}]}
    req = urllib.request.Request(base_url.rstrip("/") + "/chat/completions",
                                 data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.load(r)
    m = d["choices"][0]["message"]
    return (m.get("content") or ""), (m.get("reasoning_content") or m.get("reasoning") or ""), d.get("usage", {})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bench", required=True)
    ap.add_argument("--base-url", default="http://localhost:8000/v1")
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=0)
    ap.add_argument("--k", type=int, default=1)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--max-tokens", type=int, default=6000)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--system-prompt", default="detailed")
    ap.add_argument("--no-think", action="store_true", help="ask the server to disable the reasoning phase")
    args = ap.parse_args()

    cache = pickle.load(open(os.path.join(args.bench, "eval_cache_v15.pkl"), "rb"))
    gt_dir = os.path.join(args.bench, "gt_meshes_v15")
    keys = [k for k in cache["pools"]["certified"] if os.path.exists(os.path.join(gt_dir, k + ".stl"))]
    if args.n:
        keys = keys[: args.n]
    system, user = SYSTEM_PROMPTS[args.system_prompt], USER_PROMPT
    print(f"[probe] {len(keys)} parts, model {args.model}, K={args.k}, T={args.temperature}", flush=True)

    done = {}
    partial = args.out + ".partial.jsonl"
    if os.path.exists(partial):
        for line in open(partial):
            try:
                r = json.loads(line); done[(r["key"], r["draw"])] = r
            except Exception:
                pass
    out_f = open(partial, "a")
    todo = [(k, d) for k in keys for d in range(args.k) if (k, d) not in done]
    t0 = time.time(); n = [0]

    def one(item):
        key, draw = item
        png = cache["samples"][key]["png"]
        temp = args.temperature if (draw > 0 or args.temperature > 0) else 0.0
        rec = {"key": key, "draw": draw, "exec": False, "iou": 0.0}
        try:
            text, reasoning, usage = ask(args.base_url, args.model, png, system, user, temp, args.max_tokens,
                                         args.timeout, think=not args.no_think)
        except Exception as e:
            rec["error"] = f"{type(e).__name__}: {str(e)[:200]}"; return rec
        rec.update({"code": extract_code(text), "reply_chars": len(text), "reasoning_chars": len(reasoning),
                    "usage": usage})
        if not rec["code"]:
            rec["error"] = "no code block"; return rec
        with tempfile.TemporaryDirectory(prefix="probe_") as td:
            cp, stl = os.path.join(td, "c.py"), os.path.join(td, "c.stl")
            open(cp, "w").write(rec["code"])
            try:
                p = subprocess.run([PYTHON, HARNESS, cp, stl], capture_output=True, text=True, timeout=120)
            except subprocess.TimeoutExpired:
                rec["error"] = "exec timeout"; return rec
            if p.returncode != 0 or not os.path.exists(stl):
                rec["error"] = "exec rc=%d: %s" % (p.returncode, (p.stderr.strip().splitlines() or [""])[-1][:160]); return rec
            rec["exec"] = True
            try:
                rec["iou"] = float(iou_pair(stl, os.path.join(gt_dir, key + ".stl"))["iou_centered"])
            except Exception as e:
                rec["error"] = f"iou {type(e).__name__}"
        return rec

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for rec in ex.map(one, todo):
            done[(rec["key"], rec["draw"])] = rec
            out_f.write(json.dumps(rec) + "\n"); out_f.flush(); n[0] += 1
            if n[0] % 10 == 0:
                print(f"[probe] {n[0]}/{len(todo)}  {(time.time()-t0)/n[0]:.0f} s/req", flush=True)
    out_f.close()

    # summary in the style of analyze_ext: first draw = "first-exec", best draw = ceiling
    per = {}
    for (k, d), r in done.items():
        per.setdefault(k, {})[d] = r
    first, best = [], []
    for k in keys:
        rs = per.get(k, {})
        f = rs.get(0, {})
        first.append(f.get("iou", 0.0) if f.get("exec") else 0.0)
        best.append(max([r.get("iou", 0.0) for r in rs.values() if r.get("exec")] or [0.0]))
    def m(v):
        s = sorted(v); return dict(mean=sum(v) / len(v), median=s[len(s) // 2],
                                    ge85=sum(x >= 0.85 for x in v) / len(v), ge50=sum(x >= 0.5 for x in v) / len(v))
    n_exec = sum(1 for r in done.values() if r.get("exec")); n_code = sum(1 for r in done.values() if r.get("code"))
    errs = {}
    for r in done.values():
        if r.get("error"):
            e = r["error"].split(":")[0]; errs[e] = errs.get(e, 0) + 1
    summary = {"model": args.model, "bench": args.bench, "n": len(keys), "k": args.k, "temperature": args.temperature,
               "first_draw": m(first), "best_of_k": m(best), "n_requests": len(done), "with_code": n_code,
               "executed": n_exec, "errors": errs}
    json.dump({"summary": summary, "records": list(done.values())}, open(args.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
