"""End-to-end latency of ONE candidate, drawing -> part, split by component.

One request at a time (no batching, no concurrency) to a vLLM server holding the generator alone, with the exact
evaluation prompt (SYSTEM_PROMPTS["detailed"] + USER_PROMPT, thinking on, 2,400 max tokens) and greedy decoding
(= draw 0 of the K=8 protocol). Streaming gives three timestamps per request:
  read    send -> first streamed token          (image preprocessing, vision encoder, prompt prefill)
  plan    first token -> first answer token     (reasoning tokens; Qwen3 reasoning parser splits them)
  code    first answer token -> last token      (the build123d program)
Then the returned program is executed in a fresh Python process with build123d already imported (warm-up first,
3 repeats, median): run = exec of the program including its STEP export. Python + build123d import is measured
separately once (a served system keeps a warm worker, so it is reported as a one-off).

    python latency_one_candidate.py --bench <bench dir> --base-url http://127.0.0.1:8150/v1 --model gen \
        --tokenizer <model dir> --n 60 --out latency_rft2_rl_s60.json
"""
import argparse
import base64
import json
import os
import pickle
import random
import statistics
import subprocess
import sys
import tempfile
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from collate_v14 import SYSTEM_PROMPTS  # noqa: E402
from geom_eval_worker import USER_PROMPT, extract_code  # noqa: E402

TIMER = r'''
import json, os, sys, tempfile, time
t_imp = time.perf_counter(); import build123d  # noqa: F401
t_imp = time.perf_counter() - t_imp
code = open(sys.argv[1]).read(); os.chdir(tempfile.mkdtemp(prefix="lat_"))
t0 = time.perf_counter(); ok = True
try:
    exec(compile(code, "<gen>", "exec"), {"__name__": "__main__", "OUTPUT_PATH": "output.step"})
except Exception:
    ok = False
print(json.dumps({"run": time.perf_counter() - t0, "import": t_imp, "ok": ok and os.path.exists("output.step")}))
'''


def stream_one(base_url, model, png, max_tokens, timeout=600):
    body = {"model": model, "temperature": 0.0, "top_p": 1.0, "max_tokens": max_tokens, "stream": True,
            "stream_options": {"include_usage": True},
            "messages": [{"role": "system", "content": SYSTEM_PROMPTS["detailed"]},
                         {"role": "user", "content": [
                             {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(png).decode()}},
                             {"type": "text", "text": USER_PROMPT}]}],
            "chat_template_kwargs": {"enable_thinking": True}}
    req = urllib.request.Request(base_url.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    t_send = time.perf_counter(); t_first = t_answer = None; text, reasoning, usage = [], [], {}
    with urllib.request.urlopen(req, timeout=timeout) as r:
        for raw in r:
            line = raw.decode().strip()
            if not line.startswith("data:") or line == "data: [DONE]":
                continue
            d = json.loads(line[5:])
            if d.get("usage"):
                usage = d["usage"]
            for ch in d.get("choices", []):
                delta = ch.get("delta", {})
                rc, c = delta.get("reasoning_content") or delta.get("reasoning") or "", delta.get("content") or ""
                now = time.perf_counter()
                if (rc or c) and t_first is None:
                    t_first = now
                if c and t_answer is None:
                    t_answer = now
                reasoning.append(rc); text.append(c)
    t_end = time.perf_counter()
    t_first = t_first or t_end; t_answer = t_answer or t_end
    return {"read": t_first - t_send, "plan": t_answer - t_first, "code": t_end - t_answer, "gen_total": t_end - t_send,
            "prompt_tokens": usage.get("prompt_tokens"), "completion_tokens": usage.get("completion_tokens"),
            "reasoning": "".join(reasoning), "text": "".join(text)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bench", required=True); ap.add_argument("--base-url", required=True)
    ap.add_argument("--model", required=True); ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--n", type=int, default=60); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-tokens", type=int, default=2400); ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(a.tokenizer)
    cache = pickle.load(open(os.path.join(a.bench, "eval_cache_v15.pkl"), "rb"))
    keys = sorted(cache["pools"]["certified"]); random.Random(a.seed).shuffle(keys); keys = keys[: a.n]
    td = tempfile.mkdtemp(prefix="latency_"); tp = os.path.join(td, "timer.py"); open(tp, "w").write(TIMER)

    def run_prog(code):
        cp = os.path.join(td, "prog.py"); open(cp, "w").write(code)
        out = subprocess.run([sys.executable, tp, cp], capture_output=True, text=True, timeout=300)
        return json.loads(out.stdout.strip().splitlines()[-1])

    # warm-ups: one generation (server/kernels/graph) and one program (shared libraries), both discarded
    stream_one(a.base_url, a.model, cache["samples"][keys[0]]["png"], a.max_tokens)
    imp = [run_prog('from build123d import *\nexport_step(Box(1, 1, 1), "output.step")\n')["import"] for _ in range(3)]
    rows = []
    for i, k in enumerate(keys):
        g = stream_one(a.base_url, a.model, cache["samples"][k]["png"], a.max_tokens)
        code = extract_code(g["text"])
        g["plan_tokens"] = len(tok(g["reasoning"], add_special_tokens=False)["input_ids"])
        g["code_tokens"] = (g["completion_tokens"] or 0) - g["plan_tokens"]
        runs = [run_prog(code) for _ in range(a.repeats)] if code else []
        g.update(key=k, has_code=bool(code), executes=bool(runs) and all(r["ok"] for r in runs),
                 run=statistics.median(r["run"] for r in runs) if runs else None)
        g.pop("reasoning"); g.pop("text"); rows.append(g)
        print(f"[lat] {i + 1}/{len(keys)} {k[:14]} read {g['read']:.2f}s plan {g['plan']:.2f}s ({g['plan_tokens']} tok) "
              f"code {g['code']:.2f}s ({g['code_tokens']} tok) run {g['run'] if g['run'] is None else round(g['run'], 3)}s", flush=True)
    json.dump({"model": a.model, "n": len(rows), "import_sec": statistics.median(imp), "rows": rows}, open(a.out, "w"), indent=1)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
