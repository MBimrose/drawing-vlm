"""DeepSeek "T0" regime episodes (2026-10-07) -- an exact re-implementation of the hub run that scored 0.308 on the
real bench (RECIPE "T0 result"; results/visrepair/ds_scratch_real.jsonl; geom/vis_repair.py --arm scratch round 0
via family_synth.call): Anthropic /v1/messages request, system = vis_repair.SYS, user = [sheet, vis_repair.SCRATCH],
max_tokens 30000, thinking {enabled, budget 6000} (ignored by vLLM), output_config.effort "low", no temperature
(vLLM default 1.0), and up to 3 calls per part:
  - reply without a code block -> append assistant (text or "(empty)") + "Answer now with the complete program in a
    single ```python block; do not deliberate." and call again;
  - code that fails to execute -> append assistant ```python code``` + "This program fails to execute:\\n<last 15 lines>
    \\nFix it and answer with the complete program in a single ```python block." and call again;
  - code that executes -> stop.
The final program is scored like vis_repair (exec_harness 120 s, iou_once centred IoU 300 s), single-thread env,
<= --score-workers concurrent scoring subprocesses. The whole episode (every call's context, reasoning, text, stop
reason, token usage) is saved, so the trainer can rebuild the final call's exact conversation.
Here it is pointed at OUR server (serv-19 :8200, the same vLLM image as the hub replica) -- the hub itself is never used.
2026-10-10: --hub-user bimrose2 + --base-url http://wpk-serv-07.mechse.illinois.edu:3456 --model
"claude-deepseek-ai/DeepSeek-V4.1-Flash[1m]" runs the same regime against the lab hub (vanilla baseline; keep
--workers within the hub cap).

    python dsv41_t0_rollout.py --parts parts.tsv --base-url http://wpk-serv-19...:8200 --k 4 --out runs/r00/ep
"""
from __future__ import annotations

import argparse, base64, json, os, pickle, re, subprocess, sys, tempfile, threading, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = """You are an expert CAD engineer. You write build123d (Python) programs that reproduce parts from engineering drawings exactly.
Program conventions: `from build123d import *`, named dimension variables, final solid in `part`, end with `export_step(part, "output.step")`."""
SCRATCH = """The image is an engineering drawing of one part. Read every view and printed dimension, then write the build123d program that reproduces the part exactly, in a single ```python block. Do not deliberate at length."""
ANSWER_NOW = "Answer now with the complete program in a single ```python block; do not deliberate."
FIX = "This program fails to execute:\n{err}\nFix it and answer with the complete program in a single ```python block."
ENV1 = {**os.environ, **{v: "1" for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")}}


def code_of(txt):   # family_synth.code_of: the LONGEST fenced block
    m = re.findall(r"```(?:python)?\s*\n(.*?)```", txt or "", re.S)
    return max(m, key=len) if m else None


def img_block(png):
    return {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": base64.b64encode(png).decode()}}


HUB_USER = None   # --hub-user: lab-hub attribution header (x-hub-user), required when --base-url is the hub router


def call(base_url, model, messages, max_tokens, temperature, timeout=7200):
    body = {"model": model, "max_tokens": max_tokens, "messages": messages, "system": SYS,
            "thinking": {"type": "enabled", "budget_tokens": 6000}, "output_config": {"effort": "low"}}
    if temperature is not None:
        body["temperature"] = temperature
    req = urllib.request.Request(base_url.rstrip("/") + "/v1/messages", data=json.dumps(body).encode(),
                                 headers={"content-type": "application/json", "x-api-key": "none", "anthropic-version": "2023-06-01",
                                          **({"x-hub-user": HUB_USER} if HUB_USER else {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.load(r)
    think = "".join(b.get("thinking", "") for b in d.get("content", []) if b.get("type") == "thinking")
    text = "".join(b.get("text", "") for b in d.get("content", []) if b.get("type") == "text")
    return think, text, d.get("stop_reason"), d.get("usage", {})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts", required=True); ap.add_argument("--base-url", required=True); ap.add_argument("--model", default="pol")
    ap.add_argument("--out", required=True, help="<out>.jsonl, one episode per line (resumable)")
    ap.add_argument("--k", type=int, default=1); ap.add_argument("--max-tokens", type=int, default=30000)
    ap.add_argument("--temperature", type=float, default=None, help="default: unset = server default (T0)")
    ap.add_argument("--attempts", type=int, default=3); ap.add_argument("--workers", type=int, default=48)
    ap.add_argument("--score-workers", type=int, default=16)
    ap.add_argument("--py", default=sys.executable)
    ap.add_argument("--hub-user", default=None, help="send x-hub-user (lab hub router, e.g. bimrose2)")
    a = ap.parse_args()
    global HUB_USER
    HUB_USER = a.hub_user
    parts = [tuple(l.rstrip("\n").split("\t")) for l in open(a.parts) if l.strip()]
    pngs = {}
    for b in sorted({b for b, _ in parts}):
        c = pickle.load(open(os.path.join(b, "eval_cache_v15.pkl"), "rb"))["samples"]
        for bb, k in parts:
            if bb == b:
                pngs[(b, k)] = c[k]["png"]
        del c
    done = set()
    if os.path.exists(a.out + ".jsonl"):
        for l in open(a.out + ".jsonl"):
            try:
                r = json.loads(l); done.add((r["bench"], r["key"], r["draw"]))
            except Exception:
                pass
    todo = [(b, k, d) for b, k in parts for d in range(a.k) if (b, k, d) not in done]
    print(f"[t0] {len(parts)} parts x {a.k}, {len(todo)} episodes to run, max_tokens {a.max_tokens}, T {a.temperature}", flush=True)
    sem = threading.Semaphore(a.score_workers); lock = threading.Lock(); f = open(a.out + ".jsonl", "a"); t0 = time.time(); n = [0]

    def score(code, bench, key):
        """vis_repair.score: -> (iou, exec ok, error text)"""
        with sem, tempfile.TemporaryDirectory(prefix="t0_", dir="/dev/shm") as td:
            cp, stl, stp = [os.path.join(td, "c" + e) for e in (".py", ".stl", ".step")]; open(cp, "w").write(code)
            try:
                q = subprocess.run([a.py, os.path.join(HERE, "exec_harness.py"), cp, stl, stp], capture_output=True, text=True, timeout=120, env=ENV1)
                if q.returncode or not os.path.exists(stl):
                    return 0.0, False, "\n".join((q.stderr or q.stdout or "no output").strip().splitlines()[-15:])
                p = subprocess.run([a.py, os.path.join(HERE, "iou_once.py"), stl, os.path.join(bench, "gt_meshes_v15", key + ".stl")],
                                   capture_output=True, text=True, timeout=300, env=ENV1)
                return float(json.loads(p.stdout)["iou_centered"]), True, ""
            except subprocess.TimeoutExpired:
                return 0.0, False, "execution timed out"
            except Exception as ex:
                return 0.0, True, str(ex)[:200]

    def episode(item):
        b, k, d = item
        msgs = [{"role": "user", "content": [img_block(pngs[(b, k)]), {"type": "text", "text": SCRATCH}]}]
        turns, new, s_, e, err = [], None, 0.0, False, ""
        for attempt in range(a.attempts):
            ctx = [{"role": m["role"], "text": m["content"] if isinstance(m["content"], str) else None} for m in msgs[1:]]
            try:
                think, txt, stop, usage = call(a.base_url, a.model, msgs, a.max_tokens, a.temperature)
            except Exception as ex:
                turns.append({"context": ctx, "error": f"{type(ex).__name__}: {str(ex)[:200]}"}); break
            new = code_of(txt)
            turn = {"context": ctx, "think": think, "text": txt, "stop": stop, "input_tokens": usage.get("input_tokens"),
                    "output_tokens": usage.get("output_tokens"), "code": new or ""}
            turns.append(turn)
            if not new:
                msgs += [{"role": "assistant", "content": txt or "(empty)"}, {"role": "user", "content": ANSWER_NOW}]
                continue
            s_, e, err = score(new, b, k)
            turn.update(exec=e, iou=s_, err=err[-1500:])
            if e:
                break
            msgs += [{"role": "assistant", "content": f"```python\n{new}\n```"}, {"role": "user", "content": FIX.format(err=err)}]
        rec = {"bench": b, "key": k, "draw": d, "turns": turns, "code": new or "", "exec": bool(new) and e, "iou": s_ if new else 0.0,
               "n_calls": len(turns), "output_tokens": sum(t.get("output_tokens") or 0 for t in turns)}
        with lock:
            f.write(json.dumps(rec) + "\n"); f.flush(); n[0] += 1
            if n[0] % 10 == 0:
                print(f"[t0] {n[0]}/{len(todo)} {(time.time() - t0) / 60:.1f} min", flush=True)

    def safe(item):
        try:
            episode(item)
        except Exception:
            import traceback; print("[t0] error", item, traceback.format_exc()[-400:], flush=True)

    with ThreadPoolExecutor(a.workers) as ex:
        list(ex.map(safe, todo))
    recs = [json.loads(l) for l in open(a.out + ".jsonl")]
    m = sum(r["iou"] for r in recs) / max(1, len(recs))
    print(f"[t0] done: {len(recs)} episodes, mean IoU {m:.3f}, executed {sum(r['exec'] for r in recs)}, "
          f"calls/episode {sum(r['n_calls'] for r in recs) / max(1, len(recs)):.2f}, {(time.time() - t0) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
