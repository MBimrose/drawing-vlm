"""rft2_rl collapse diagnosis (2026-10-09): sample K completions per training-pool part from several adapters at the
rollout setting (T 1.0, top_p 1.0, 2400 tokens, think on), keep raw text + finish_reason, execute each extracted program
with exec_harness.py and record the error class. -> <out>.jsonl rows {model, bench, key, draw, finish, think_chars,
text_chars, code_chars, has_code, rc, err_type, err_line}
    python diag_rl.py --models s60,s80,s100,s120 --keys keys.tsv --base-url ... --out diag.jsonl"""
import argparse, base64, json, os, pickle, subprocess, sys, tempfile, threading, urllib.request
from concurrent.futures import ThreadPoolExecutor
G = "/srv/scratch/bimrose2/train_v14/geom"; sys.path.insert(0, os.path.dirname(G)); sys.path.insert(0, G)
from collate_v14 import SYSTEM_PROMPTS  # noqa
from geom_eval_worker import USER_PROMPT, extract_code  # noqa
ap = argparse.ArgumentParser(); ap.add_argument("--models"); ap.add_argument("--keys"); ap.add_argument("--base-url")
ap.add_argument("--out"); ap.add_argument("--k", type=int, default=4); ap.add_argument("--workers", type=int, default=12)
a = ap.parse_args()
rows = [l.rstrip("\n").split("\t") for l in open(a.keys) if l.strip()]   # bench_tag \t bench_dir \t key
caches = {}
for tag, d, k in rows:
    if d not in caches: caches[d] = pickle.load(open(os.path.join(d, "eval_cache_v15.pkl"), "rb"))["samples"]
ENV1 = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
lock = threading.Lock(); out = open(a.out, "a")
def one(job):
    m, (tag, d, k) = job
    png = caches[d][k]["png"]
    body = {"model": m, "temperature": 1.0, "top_p": 1.0, "n": a.k, "max_tokens": 2400,
            "messages": [{"role": "system", "content": SYSTEM_PROMPTS["detailed"]},
                         {"role": "user", "content": [{"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(png).decode()}},
                                                      {"type": "text", "text": USER_PROMPT}]}],
            "chat_template_kwargs": {"enable_thinking": True}}
    rq = urllib.request.Request(a.base_url + "/chat/completions", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    chs = json.load(urllib.request.urlopen(rq, timeout=1200))["choices"]
    for i, ch in enumerate(chs):
        msg = ch["message"]; text = msg.get("content") or ""; think = msg.get("reasoning_content") or msg.get("reasoning") or ""
        code = extract_code(text); rc, et, el = None, "", ""
        if code:
            with tempfile.TemporaryDirectory(prefix="diag_", dir="/dev/shm") as td:
                cp = os.path.join(td, "c.py"); open(cp, "w").write(code)
                try:
                    p = subprocess.run([sys.executable, os.path.join(G, "exec_harness.py"), cp, os.path.join(td, "o.stl")],
                                       capture_output=True, text=True, timeout=60, env=ENV1)
                    rc = p.returncode; lines = [x for x in (p.stderr or "").strip().splitlines() if x.strip()]
                    el = lines[-1][:300] if lines else ""; et = el.split(":")[0] if rc else ""
                except subprocess.TimeoutExpired:
                    rc, et = -9, "Timeout"
        r = {"model": m, "bench": tag, "key": k, "draw": i, "finish": ch.get("finish_reason"), "think_chars": len(think),
             "text_chars": len(text), "code_chars": len(code or ""), "has_code": bool(code), "rc": rc, "err_type": et, "err_line": el,
             "text_tail": text[-300:] if not code or rc else "", "code": code if (code and rc) else ""}
        with lock: out.write(json.dumps(r) + "\n"); out.flush()
jobs = [(m, r) for m in a.models.split(",") for r in rows]
with ThreadPoolExecutor(a.workers) as ex:
    for f in [ex.submit(one, j) for j in jobs]:
        try: f.result()
        except Exception as e: print("err", e, flush=True)
print("DIAG DONE", flush=True)
