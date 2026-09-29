"""Serve a trained visual-repair model on a bench (2026-09-29): per part, render the starting program (e55's vote
pick), send [target sheet, candidate sheet] + collate_v14.REPAIR_PROMPT to the vLLM server in no-think mode, draw K
repairs, execute + score each (centred IoU vs GT, evaluation only). Optional further rounds repair the round's
medoid-free first executing draw. Output jsonl like vis_repair.py ({key, hist:[{round, iou, exec, code}...]}), plus
all K draws per round under "draws".
    python vr_serve.py --bench <bench> --picks e55_vote_picks.json --base-url http://127.0.0.1:8100/v1 --model rp1 --k 8 --out x.jsonl"""
import argparse, base64, json, os, pickle, subprocess, sys, tempfile, threading, urllib.request
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from collate_v14 import SYSTEM_PROMPTS, REPAIR_PROMPT
from geom_eval_worker import extract_code
from render_compare import render_candidate
IOU_ONCE = os.path.join(HERE, "iou_once.py")

def b64(png): return {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(png).decode()}}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--bench"); ap.add_argument("--picks"); ap.add_argument("--base-url"); ap.add_argument("--model")
    ap.add_argument("--k", type=int, default=8); ap.add_argument("--temperature", type=float, default=0.7); ap.add_argument("--max-tokens", type=int, default=2400)
    ap.add_argument("--out"); ap.add_argument("--workers", type=int, default=24); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--py", default=sys.executable); ap.add_argument("--rpy"); ap.add_argument("--script-dir")
    a = ap.parse_args()
    S = pickle.load(open(os.path.join(a.bench, "eval_cache_v15.pkl"), "rb"))["samples"]; picks = json.load(open(a.picks))
    keys = sorted(k for k in picks if k in S)[: a.limit or None]
    done = {json.loads(l)["key"] for l in open(a.out)} if os.path.exists(a.out) else set(); lock = threading.Lock()
    def score(code, k):
        with tempfile.TemporaryDirectory(prefix="vs_", dir="/dev/shm") as td:
            cp, stl, stp = [os.path.join(td, "c" + e) for e in (".py", ".stl", ".step")]; open(cp, "w").write(code)
            try:
                if subprocess.run([a.py, os.path.join(HERE, "exec_harness.py"), cp, stl, stp], capture_output=True, timeout=120).returncode or not os.path.exists(stl): return 0.0, False
                p = subprocess.run([a.py, IOU_ONCE, stl, os.path.join(a.bench, "gt_meshes_v15", k + ".stl")], capture_output=True, text=True, timeout=300)
                return float(json.loads(p.stdout)["iou_centered"]), True
            except Exception: return 0.0, False
    def one(k):
        if k in done: return
        code = picks[k]["code"]; s, e = score(code, k); hist = [{"round": 0, "iou": s, "exec": e, "code": code}]
        png, info = render_candidate(code, k, a.py, a.rpy, a.script_dir, 120, 300)
        rec = {"key": k, "hist": hist, "render": info}
        if png is not None:
            body = {"model": a.model, "temperature": a.temperature, "top_p": 0.95, "n": a.k, "max_tokens": a.max_tokens,
                    "messages": [{"role": "system", "content": SYSTEM_PROMPTS["detailed"]},
                                 {"role": "user", "content": [b64(S[k]["png"]), b64(png), {"type": "text", "text": REPAIR_PROMPT.format(code=code)}]}],
                    "chat_template_kwargs": {"enable_thinking": False}}
            rq = urllib.request.Request(a.base_url.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
            d = json.load(urllib.request.urlopen(rq, timeout=1800))
            draws = []
            for ch in d["choices"]:
                c = extract_code(ch["message"].get("content") or "")
                if c: si, ei = score(c, k); draws.append({"iou": si, "exec": ei, "code": c})
                else: draws.append({"iou": 0.0, "exec": False, "code": ""})
            rec["draws"] = draws
            if draws: hist.append({"round": 1, **draws[0]})
        with lock:
            with open(a.out, "a") as f: f.write(json.dumps(rec) + "\n")
    def safe(k):
        try: one(k)
        except Exception:
            import traceback; print("[vs] error", k, traceback.format_exc()[-400:], flush=True)
    with ThreadPoolExecutor(a.workers) as ex: list(ex.map(safe, keys))
    print("VS DONE", flush=True)

if __name__ == "__main__":
    main()
