"""gt_search2 (2026-10-09, expert iteration round 2): gt_search.py with SEVERAL benches in one worker pool and a global,
re-read priority key list, so one pool stays busy across corpora and picks up parts whose starts appear later
(--bench c4=<dir>,c2=<dir> --starts c4=<json>,c2=<json> --keys <global keys file>; rescans every 120 s until
--until-file exists). Rows carry "bench". Everything else (rp3 repairs, adopt by true IoU, render only the adopted
program, patience) is gt_search.py unchanged. Original docstring:

GT-selected repair search on TRAINING parts -> guide-bank entries (2026-10-07, expert iteration for guided GRPO).

Training parts carry ground truth, so the search may select by true IoU instead of the label-free v3 render score.
Per part: start = the best known program (bank entry or the best of e55's scored draws); each round the repairer
proposes K repairs of the current program from [target sheet, current sheet]; every repair is executed and scored
against GT; the best is adopted if it beats the current IoU by --min-gain; only the ADOPTED program is rendered
(for the next round's image 2), so rendering costs one sheet per part-round. Stops after --patience flat rounds.

    python gt_search.py --bench <bench dir> --starts <scored bo-K json> [--bank <existing bank json>] --keys <file>
        --base-url http://127.0.0.1:8300/v1 --model rp3 --out <jsonl> [--k 8 --rounds 4 --workers 16]
        --py <.venv python> --rpy <dw_venv python> --script-dir <mech_step_to_drw>
Output jsonl rows {key, start_iou, best_iou, code, hist}; build the bank with --emit-targets <json> afterwards
(-> {key: {code, iou}} for parts whose best beats the start by --emit-gain), then build_guide_bank.py.
"""
import argparse
import base64
import json
import os
import pickle
import subprocess
import sys
import tempfile
import threading
import urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from collate_v14 import REPAIR_PROMPT, SYSTEM_PROMPTS  # noqa: E402
from geom_eval_worker import extract_code  # noqa: E402
from render_compare import render_candidate  # noqa: E402

IOU_ONCE = os.path.join(HERE, "iou_once.py")
ENV1 = {**os.environ, **{v: "1" for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")}}


def b64(png):
    return {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(png).decode()}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bench"); ap.add_argument("--starts", default=""); ap.add_argument("--bank", default="")
    ap.add_argument("--keys", default=""); ap.add_argument("--base-url"); ap.add_argument("--model", default="rp3")
    ap.add_argument("--out"); ap.add_argument("--k", type=int, default=8); ap.add_argument("--rounds", type=int, default=4)
    ap.add_argument("--patience", type=int, default=2); ap.add_argument("--min-gain", type=float, default=0.01)
    ap.add_argument("--temperature", type=float, default=0.8); ap.add_argument("--max-tokens", type=int, default=2400)
    ap.add_argument("--workers", type=int, default=16); ap.add_argument("--py", default=sys.executable)
    ap.add_argument("--rpy"); ap.add_argument("--script-dir")
    ap.add_argument("--emit-targets", default="", help="only convert --out into a {key: {code, iou}} targets json")
    ap.add_argument("--emit-gain", type=float, default=0.03)
    ap.add_argument("--until-file", default="", help="keep rescanning --keys/--starts every 120 s until this file exists")
    a = ap.parse_args()

    if a.emit_targets:
        tg = {}
        for line in open(a.out):
            r = json.loads(line)
            if r.get("code") and r["best_iou"] >= r["start_iou"] + a.emit_gain:
                tg[r["key"]] = {"code": r["code"], "iou": r["best_iou"], "start_iou": r["start_iou"]}
        json.dump(tg, open(a.emit_targets, "w"))
        print(f"[gts] {len(tg)} targets (gain >= {a.emit_gain}) -> {a.emit_targets}")
        return

    benches = dict(x.split("=", 1) for x in a.bench.split(","))
    starts_f = dict(x.split("=", 1) for x in a.starts.split(","))
    S, GTD, B_OF = {}, {}, {}
    for b, d in benches.items():
        for k, v in pickle.load(open(os.path.join(d, "eval_cache_v15.pkl"), "rb"))["samples"].items():
            S[k] = v; GTD[k] = os.path.join(d, "gt_meshes_v15"); B_OF[k] = b
    print(f"[gts2] {len(S)} sheets from {list(benches)}", flush=True)
    start = {}
    loaded = set()

    def load_starts():
        for b, f in starts_f.items():
            if b in loaded or not os.path.exists(f):
                continue
            for p in json.load(open(f))["candidates"]:
                best = max((c for c in p["cands"] if c.get("code") and c.get("exec")), key=lambda c: float(c.get("iou") or 0),
                           default=None)
                if best is not None:
                    start[p.get("key") or p.get("part")] = (best["code"], float(best.get("iou") or 0))
            loaded.add(b); print(f"[gts2] starts {b} loaded ({len(start)} total)", flush=True)

    def todo_now():
        load_starts()
        keys = [l.strip() for l in open(a.keys) if l.strip()] if os.path.exists(a.keys) else []
        done = {json.loads(l)["key"] for l in open(a.out)} if os.path.exists(a.out) else set()
        return [k for k in keys if k in start and k in S and k not in done and k not in queued
                and os.path.exists(os.path.join(GTD[k], k + ".stl"))]
    queued = set()
    lock = threading.Lock()

    def score(code, k):
        with tempfile.TemporaryDirectory(prefix="gts_", dir="/dev/shm") as td:
            cp, stl, stp = (os.path.join(td, "c" + e) for e in (".py", ".stl", ".step"))
            open(cp, "w").write(code)
            try:
                if subprocess.run([a.py, os.path.join(HERE, "exec_harness.py"), cp, stl, stp], capture_output=True,
                                  timeout=60, env=ENV1).returncode or not os.path.exists(stl):
                    return 0.0
                p = subprocess.run([a.py, IOU_ONCE, stl, os.path.join(GTD[k], k + ".stl")], capture_output=True,
                                   text=True, timeout=90, env=ENV1)
                return float(json.loads(p.stdout)["iou_centered"])
            except Exception:
                return 0.0

    def one(k):
        code, iou = start[k]
        hist = [{"round": 0, "iou": iou}]
        flat = 0
        for rd in range(1, a.rounds + 1):
            png, _ = render_candidate(code, k, a.py, a.rpy, a.script_dir, 120, 300)
            if png is None:
                break
            body = {"model": a.model, "temperature": a.temperature, "top_p": 0.95, "n": a.k, "max_tokens": a.max_tokens,
                    "messages": [{"role": "system", "content": SYSTEM_PROMPTS["detailed"]},
                                 {"role": "user", "content": [b64(S[k]["png"]), b64(png),
                                                              {"type": "text", "text": REPAIR_PROMPT.format(code=code)}]}],
                    "chat_template_kwargs": {"enable_thinking": False, "thinking": False}}
            try:
                rq = urllib.request.Request(a.base_url.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(),
                                            headers={"Content-Type": "application/json"})
                chs = json.load(urllib.request.urlopen(rq, timeout=1800))["choices"]
            except Exception as ex:
                print(f"[gts] {k} round {rd}: {str(ex)[:120]}", flush=True)
                break
            cands = []
            for ch in chs:
                c = extract_code(ch["message"].get("content") or "")
                if c and c != code and all(c != x for x in cands):
                    cands.append(c)
            scored = [(score(c, k), c) for c in cands]
            best = max(scored, default=(0.0, None))
            hist.append({"round": rd, "n": len(cands), "best": best[0]})
            if best[1] is not None and best[0] > iou + a.min_gain:
                code, iou, flat = best[1], best[0], 0
            else:
                flat += 1
                if flat >= a.patience:
                    break
        row = {"key": k, "bench": B_OF[k], "start_iou": start[k][1], "best_iou": iou, "code": code, "hist": hist}
        with lock:
            with open(a.out, "a") as f:
                f.write(json.dumps(row) + "\n")

    def safe(k):
        try:
            one(k)
        except Exception as ex:
            print(f"[gts] error {k}: {str(ex)[:200]}", flush=True)

    # worker threads pull the highest-priority pending key (rank = position in the re-read global keys file), so parts
    # whose starts appear later (another corpus finished scoring) still run in global priority order
    import time
    rank, pending, cv = {}, [], threading.Condition()
    state = {"closed": False}

    def worker():
        while True:
            with cv:
                while not pending and not state["closed"]:
                    cv.wait(30)
                if not pending:
                    return
                pending.sort(key=lambda k: rank.get(k, 1e9))
                k = pending.pop(0)
            safe(k)

    th = [threading.Thread(target=worker, daemon=True) for _ in range(a.workers)]
    for t in th:
        t.start()
    while True:
        if os.path.exists(a.keys):
            rank.update({k: i for i, k in enumerate(l.strip() for l in open(a.keys) if l.strip())})
        todo = todo_now()
        with cv:
            for k in todo:
                queued.add(k); pending.append(k)
            cv.notify_all()
            npend = len(pending)
        print(f"[gts2] {time.strftime('%H:%M')} queued {len(todo)} new, {npend} pending, {len(queued)} total", flush=True)
        if a.until_file and not os.path.exists(a.until_file):
            time.sleep(120); continue
        if npend == 0 and not todo:
            break
        time.sleep(60)
    with cv:
        state["closed"] = True; cv.notify_all()
    for t in th:
        t.join()
    print("[gts] DONE", flush=True)


if __name__ == "__main__":
    main()
