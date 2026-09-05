"""Teacher distillation round on unsolved real parts.

For every key in an unsolved list: send the rendered sheet to a hub model
(Anthropic Messages API on the lab router), take the last ```python block,
execute it to STL, score exact centered IoU against the GT mesh, and keep
samples with IoU >= --accept in the standard RFT tier format
({key, iou, ok, think, code, sample}); everything scored goes to scored-*.jsonl.
Optional one repair turn (traceback -> corrected script) for failed executions.
Resumable: keys already present in the output are skipped.

    python teacher_round.py --keys unsolved_keys.json --png-dir <render/png> \
        --gt-dir <gt_meshes_v15> --out <tier_dir> [--model claude-moonshotai/Kimi-K3[1m]] \
        [--samples 2] [--concurrency 8] [--limit 50] [--repair]

Run on serv-19 (where the corpus PNGs/meshes live) with the drawing_vlm venv.
Key: $ANTHROPIC_API_KEY, else ~/.claude-hub/my.key, else router default.
"""
from __future__ import annotations

import argparse
import base64
import glob
import json
import os
import re
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
for p in (os.path.join(HERE, "..", "..", "geom"), os.path.join(HERE, "..", "..")):
    sys.path.insert(0, os.path.abspath(p))
from hub_smoke import SYSTEM, USER, hub_key, ROUTER  # noqa: E402
from iou import iou_pair  # noqa: E402
from rft_generate import exec_to_stl  # noqa: E402

CODE_RE = re.compile(r"```(?:python)?\s*\n(.*?)```", re.S)
LOCK = threading.Lock()


def call(model, content, max_tokens, timeout=900):
    body = {"model": model, "max_tokens": max_tokens, "system": SYSTEM, "messages": [{"role": "user", "content": content}]}
    req = urllib.request.Request(f"{ROUTER}/v1/messages", data=json.dumps(body).encode(),
                                 headers={"content-type": "application/json", "x-api-key": hub_key(),
                                          "anthropic-version": "2023-06-01", "x-hub-user": os.environ.get("USER", "bimrose2")})
    for attempt in range(4):
        try:
            r = json.load(urllib.request.urlopen(req, timeout=timeout))
            txt = "".join(b.get("text", "") for b in r.get("content", []) if b.get("type") == "text")
            think = "".join(b.get("thinking", "") for b in r.get("content", []) if b.get("type") == "thinking")
            return txt, think, r.get("usage") or {}
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(15 * (attempt + 1)); continue
            raise
        except Exception:  # noqa: BLE001
            if attempt < 3:
                time.sleep(10 * (attempt + 1)); continue
            raise


def split(txt, think):
    blocks = CODE_RE.findall(txt)
    code = blocks[-1].strip() if blocks else None
    if not think:
        think = txt.split("```")[0].strip() if blocks else txt.strip()
    return think, code


def one(key, a, png, gt, out_scored, out_acc, stats):
    img = base64.b64encode(open(png, "rb").read()).decode()
    content = [{"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": img}},
               {"type": "text", "text": USER}]
    with tempfile.TemporaryDirectory(prefix="tch_") as td:
        for s in range(a.samples):
            try:
                txt, think, usage = call(a.model, content, a.max_tokens)
            except Exception as e:  # noqa: BLE001
                with LOCK:
                    stats["api_err"] += 1
                    print(f"[teacher] {key}#{s} API error: {repr(e)[:120]}", flush=True)
                continue
            think, code = split(txt, think)
            rec = {"key": key, "sample": s, "model": a.model, "usage": usage, "think": think, "code": code,
                   "exec": False, "iou": 0.0, "ok": False, "repair": False}
            if code:
                stl = os.path.join(td, f"{key}_{s}.stl")
                ok = exec_to_stl(code, stl, td, f"{key}_{s}")
                if not ok and a.repair:
                    tb = open(os.path.join(td, f"{key}_{s}.stderr")).read()[-1500:] if os.path.exists(os.path.join(td, f"{key}_{s}.stderr")) else "execution failed"
                    fix = content + [{"type": "text", "text": f"Your previous script failed to execute:\n```\n{tb}\n```\nReturn the full corrected script in a single ```python block."}]
                    try:
                        txt2, think2, usage2 = call(a.model, [{"type": "text", "text": "Previous answer:\n" + txt}] + fix, a.max_tokens)
                        _, code2 = split(txt2, think2)
                        if code2:
                            ok = exec_to_stl(code2, stl, td, f"{key}_{s}r")
                            if ok:
                                rec.update(code=code2, repair=True)
                    except Exception:  # noqa: BLE001
                        pass
                if ok:
                    rec["exec"] = True
                    rec["iou"] = float(iou_pair(stl, gt)["iou_centered"])
                    rec["ok"] = rec["iou"] >= a.accept
            with LOCK:
                out_scored.write(json.dumps(rec) + "\n"); out_scored.flush()
                stats["cands"] += 1; stats["exec"] += rec["exec"]; stats["acc"] += rec["ok"]
                if rec["ok"]:
                    out_acc.write(json.dumps({k: rec[k] for k in ("key", "iou", "ok", "think", "code", "sample")}) + "\n"); out_acc.flush()
                    stats["keys"].add(key)
                if stats["cands"] % 25 == 0:
                    print(f"[teacher] {stats['cands']} cands, exec {stats['exec']}, accepted {stats['acc']} on {len(stats['keys'])} keys, api_err {stats['api_err']}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keys", required=True); ap.add_argument("--png-dir", required=True, nargs="+")
    ap.add_argument("--gt-dir", required=True, nargs="+"); ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="claude-moonshotai/Kimi-K3[1m]"); ap.add_argument("--samples", type=int, default=2)
    ap.add_argument("--max-tokens", type=int, default=8000); ap.add_argument("--accept", type=float, default=0.8)
    ap.add_argument("--concurrency", type=int, default=8); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--repair", action="store_true")
    a = ap.parse_args()
    keys = json.load(open(a.keys)); keys = keys.get("unsolved", keys) if isinstance(keys, dict) else keys
    if a.limit:
        keys = keys[:a.limit]
    os.makedirs(a.out, exist_ok=True)
    done = set()
    sp = os.path.join(a.out, "scored-000.jsonl")
    if os.path.exists(sp):
        for l in open(sp):
            try: done.add(json.loads(l)["key"])
            except Exception: pass
    todo = []
    for k in keys:
        if k in done: continue
        png = next((p for d in a.png_dir for p in glob.glob(os.path.join(d, f"{k}_v*.png")) + glob.glob(os.path.join(d, f"{k}.png"))), None)
        gt = next((p for d in a.gt_dir for p in [os.path.join(d, f"{k}.stl")] if os.path.exists(p)), None)
        if png and gt: todo.append((k, png, gt))
    print(f"[teacher] model={a.model} keys={len(keys)} done={len(done)} todo={len(todo)} samples={a.samples}", flush=True)
    stats = {"cands": 0, "exec": 0, "acc": 0, "keys": set(), "api_err": 0}
    with open(sp, "a") as out_scored, open(os.path.join(a.out, "accepted-000.jsonl"), "a") as out_acc, ThreadPoolExecutor(a.concurrency) as ex:
        list(ex.map(lambda t: one(t[0], a, t[1], t[2], out_scored, out_acc, stats), todo))
    print(f"[teacher] DONE {stats['cands']} cands, exec {stats['exec']}, accepted {stats['acc']} rows on {len(stats['keys'])} keys, api_err {stats['api_err']}", flush=True)
    json.dump({k: (len(v) if isinstance(v, set) else v) for k, v in stats.items()}, open(os.path.join(a.out, "stats.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
