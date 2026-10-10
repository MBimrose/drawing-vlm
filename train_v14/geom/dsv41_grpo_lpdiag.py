"""Sampler-vs-trainer agreement probe for the DeepSeek GRPO loop (2026-10-06).
vLLM side: re-sample a few parts with logprobs=True and report the mean NLL of the sampled tokens under vLLM's RAW
(T=1) distribution, and save the samples as a tier (adv +1) so the trainer can score the SAME tokens
(dsv41_lora_train.py --adv-weighted --steps-free with --lr 0 ... see grpo_pass log 'ce').
    python dsv41_grpo_lpdiag.py --parts p.tsv --base-url http://...:8200/v1 --out diag.jsonl [--n 3]"""
import argparse, base64, json, math, os, pickle, sys, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)

ap = argparse.ArgumentParser(); ap.add_argument("--parts"); ap.add_argument("--base-url"); ap.add_argument("--out")
ap.add_argument("--n", type=int, default=3); ap.add_argument("--temperature", type=float, default=0.8)
ap.add_argument("--max-tokens", type=int, default=6000)
a = ap.parse_args()
pj = json.load(open(os.path.join(HERE, "dsv41_grpo_prompts.json")))
parts = [l.rstrip("\n").split("\t") for l in open(a.parts) if l.strip()][: a.n]
with open(a.out, "w") as f:
    for b, k in parts:
        png = pickle.load(open(os.path.join(b, "eval_cache_v15.pkl"), "rb"))["samples"][k]["png"]
        body = {"model": "pol", "temperature": a.temperature, "top_p": 1.0, "max_tokens": a.max_tokens, "logprobs": True,
                "chat_template_kwargs": {"thinking": True, "enable_thinking": True, "reasoning_effort": 50},
                "messages": [{"role": "system", "content": pj["system"]}, {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(png).decode()}},
                    {"type": "text", "text": pj["user"]}]}]}
        d = json.load(urllib.request.urlopen(urllib.request.Request(a.base_url + "/chat/completions", data=json.dumps(body).encode(),
                                                                     headers={"Content-Type": "application/json"}), timeout=3600))
        ch = d["choices"][0]; lps = [t["logprob"] for t in (ch.get("logprobs") or {}).get("content") or []]
        lps = [x for x in lps if x is not None and x > -1e9]
        nll = -sum(lps) / max(1, len(lps))
        m = ch["message"]
        rec = {"bench": b, "key": k, "n_logprobs": len(lps), "vllm_nll_raw": nll, "completion_tokens": d["usage"]["completion_tokens"],
               "finish": ch.get("finish_reason"), "think": m.get("reasoning_content") or m.get("reasoning") or "", "reply": m.get("content") or ""}
        f.write(json.dumps(rec) + "\n"); f.flush()
        print(f"{k[:40]} tokens {rec['completion_tokens']} (logprobs {len(lps)}) vLLM mean NLL {nll:.3f} finish {rec['finish']}", flush=True)

# tier for the trainer-side score (dsv41_lora_train.py --adv-weighted --score-only): same tokens, adv +1
import io, tarfile
from geom_eval_worker import extract_code
td = a.out + ".tier"; os.makedirs(td, exist_ok=True)
with tarfile.open(os.path.join(td, "diag-00000.tar"), "w") as t:
    for l in open(a.out):
        r = json.loads(l); n = r["key"]
        png = pickle.load(open(os.path.join(r["bench"], "eval_cache_v15.pkl"), "rb"))["samples"][r["key"]]["png"]
        for ext, data in ((".png", png), (".code.py", (extract_code(r["reply"]) or "pass").encode()), (".think.txt", r["think"].encode()),
                          (".reply.txt", r["reply"].encode()), (".adv.txt", b"1.0")):
            ti = tarfile.TarInfo(n + ext); ti.size = len(data); t.addfile(ti, io.BytesIO(data))
print("tier ->", td)
