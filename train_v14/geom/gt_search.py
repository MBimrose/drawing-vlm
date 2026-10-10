"""GT-selected repair search on TRAINING parts -> guide-bank entries (2026-10-07, expert iteration for guided GRPO).

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

    S = pickle.load(open(os.path.join(a.bench, "eval_cache_v15.pkl"), "rb"))["samples"]
    gt_dir = os.path.join(a.bench, "gt_meshes_v15")
    start = {}
    if a.starts:   # best scored draw per part (GT selection is legitimate on training parts)
        for p in json.load(open(a.starts))["candidates"]:
            best = max((c for c in p["cands"] if c.get("code") and c.get("exec")), key=lambda c: float(c.get("iou") or 0),
                       default=None)
            if best is not None:
                start[p.get("key") or p.get("part")] = (best["code"], float(best.get("iou") or 0))
    if a.bank:     # an existing bank entry is a better start when it beats the draws
        for k, v in json.load(open(a.bank)).items():
            if k not in start or v["iou"] > start[k][1]:
                start[k] = (v["code"], float(v["iou"]))
    keys = [l.strip() for l in open(a.keys) if l.strip()] if a.keys else sorted(start)
    keys = [k for k in keys if k in start and k in S and os.path.exists(os.path.join(gt_dir, k + ".stl"))]
    done = {json.loads(l)["key"] for l in open(a.out)} if os.path.exists(a.out) else set()
    todo = [k for k in keys if k not in done]
    print(f"[gts] {len(keys)} parts with a start, {len(done)} done, {len(todo)} to search", flush=True)
    lock = threading.Lock()

    def score(code, k):
        with tempfile.TemporaryDirectory(prefix="gts_", dir="/dev/shm") as td:
            cp, stl, stp = (os.path.join(td, "c" + e) for e in (".py", ".stl", ".step"))
            open(cp, "w").write(code)
            try:
                if subprocess.run([a.py, os.path.join(HERE, "exec_harness.py"), cp, stl, stp], capture_output=True,
                                  timeout=60, env=ENV1).returncode or not os.path.exists(stl):
                    return 0.0
                p = subprocess.run([a.py, IOU_ONCE, stl, os.path.join(gt_dir, k + ".stl")], capture_output=True,
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
        row = {"key": k, "start_iou": start[k][1], "best_iou": iou, "code": code, "hist": hist}
        with lock:
            with open(a.out, "a") as f:
                f.write(json.dumps(row) + "\n")

    def safe(k):
        try:
            one(k)
        except Exception as ex:
            print(f"[gts] error {k}: {str(ex)[:200]}", flush=True)

    with ThreadPoolExecutor(a.workers) as ex:
        list(ex.map(safe, todo))
    print("[gts] DONE", flush=True)


if __name__ == "__main__":
    main()
