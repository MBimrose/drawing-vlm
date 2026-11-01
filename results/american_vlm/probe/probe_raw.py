"""Print raw chat replies (content / reasoning / finish_reason / token counts) for a few bench parts, for each served
model name given (2026-10-28: Gemma LoRA row scored ~0 with empty code and think)."""
import json, os, pickle, sys, base64, urllib.request
sys.path.insert(0, "/srv/scratch/bimrose2/train_v14/geom")
from gen_openai_bo import SYSTEM_PROMPTS, USER_PROMPT
url, names, n = sys.argv[1], sys.argv[2].split(","), int(sys.argv[3])
bench = "/srv/scratch/bimrose2/mech_benchmarks/ext_bench_dw423_perm"
cache = pickle.load(open(f"{bench}/eval_cache_v15.pkl", "rb"))
keys = cache["pools"]["certified"][:n]
for name in names:
    for k in keys:
        png = cache["samples"][k]["png"]
        body = {"model": name, "temperature": 0.0, "max_tokens": 2400, "messages": [
            {"role": "system", "content": SYSTEM_PROMPTS["detailed"]},
            {"role": "user", "content": [{"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(png).decode()}},
                                         {"type": "text", "text": USER_PROMPT}]}],
            "chat_template_kwargs": {"enable_thinking": True, "thinking": True}}
        req = urllib.request.Request(url + "/chat/completions", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        d = json.load(urllib.request.urlopen(req, timeout=900))
        m = d["choices"][0]["message"]
        print(f"=== {name} {k} finish={d['choices'][0]['finish_reason']} usage={d['usage']}")
        print("REASONING:", repr((m.get("reasoning_content") or m.get("reasoning") or "")[:800]))
        print("CONTENT:", repr((m.get("content") or "")[:1500]), flush=True)
    # raw completion without the reasoning parser's split: /v1/completions on the rendered prompt is not needed if the above is informative
