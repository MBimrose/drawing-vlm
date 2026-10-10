"""Guide bank for guided GRPO (2026-10-06): best-known programs per training part (found by GT-scored search,
e.g. the DeepSeek repair search targets, which beat e55's own best-of-8 on ~half the parts) + a reasoning trace
in the generator's own voice, so the program can be trained as if the policy had written it.

STaR-style rationalization: the policy is shown the drawing AND the verified program and asked for its usual
plan; the plan (reasoning_content) is kept and later paired with the program under the NORMAL prompt (no hint).
Plans that leak the hint ("the reference/provided program ...") or that end without reasoning are dropped.

    python build_guide_bank.py --bench <bench dir with eval_cache_v15.pkl> --targets <key -> {code, iou}> \
        --base-url http://127.0.0.1:8410/v1 --model e55 --out <bank.json> [--min-iou 0.5] [--workers 16]
Output: {key: {code, iou, think}}; resumable.
"""
import argparse
import base64
import json
import os
import pickle
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from collate_v14 import SYSTEM_PROMPTS, USER_PROMPT  # noqa: E402

HINT = ("\n\nFor reference, a verified correct build123d program for this drawing is given below. Read the drawing "
        "as you normally would and work out the construction plan that this program implements (base feature, then "
        "each added/subtracted feature, then edge treatments, with the dimensions you read from the drawing); then "
        "output the program.\n```python\n{code}\n```")
LEAK = re.compile(r"\b(reference|provided|given|verified)\s+(program|code|script|solution)\b|\bthe program (above|below)\b",
                  re.I)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bench", required=True); ap.add_argument("--targets", required=True)
    ap.add_argument("--base-url", required=True); ap.add_argument("--model", default="e55")
    ap.add_argument("--out", required=True); ap.add_argument("--min-iou", type=float, default=0.5)
    ap.add_argument("--workers", type=int, default=16); ap.add_argument("--max-tokens", type=int, default=2400)
    ap.add_argument("--temperature", type=float, default=0.7)
    a = ap.parse_args()
    S = pickle.load(open(os.path.join(a.bench, "eval_cache_v15.pkl"), "rb"))["samples"]
    T = {k: v for k, v in json.load(open(a.targets)).items() if k in S and v.get("code") and v["iou"] >= a.min_iou}
    bank = json.load(open(a.out)) if os.path.exists(a.out) else {}
    todo = [k for k in T if k not in bank]
    print(f"[bank] {len(T)} targets >= {a.min_iou} with a sheet, {len(bank)} done, {len(todo)} to rationalize", flush=True)

    def one(k):
        body = {"model": a.model, "temperature": a.temperature, "top_p": 0.95, "n": 1, "max_tokens": a.max_tokens,
                "messages": [{"role": "system", "content": SYSTEM_PROMPTS["detailed"]},
                             {"role": "user", "content": [
                                 {"type": "image_url", "image_url": {"url": "data:image/png;base64,"
                                                                     + base64.b64encode(S[k]["png"]).decode()}},
                                 {"type": "text", "text": USER_PROMPT + HINT.format(code=T[k]["code"].strip())}]}],
                "chat_template_kwargs": {"enable_thinking": True, "reasoning_effort": "medium"}}
        req = urllib.request.Request(a.base_url.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                m = json.load(r)["choices"][0]["message"]
        except Exception as e:
            return k, None, f"err {type(e).__name__}"
        think = (m.get("reasoning_content") or m.get("reasoning") or "").strip()
        if len(think) < 80:
            return k, None, "no reasoning"
        if LEAK.search(think):
            return k, None, "leak"
        return k, think, "ok"

    stats = {}
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for i, (k, think, why) in enumerate(ex.map(one, todo)):
            stats[why] = stats.get(why, 0) + 1
            if think:
                bank[k] = {"code": T[k]["code"], "iou": T[k]["iou"], "think": think}
            if (i + 1) % 100 == 0:
                json.dump(bank, open(a.out, "w")); print(f"[bank] {i + 1}/{len(todo)} {stats}", flush=True)
    json.dump(bank, open(a.out, "w"))
    print(f"[bank] DONE {len(bank)} entries -> {a.out} {stats}", flush=True)


if __name__ == "__main__":
    main()
