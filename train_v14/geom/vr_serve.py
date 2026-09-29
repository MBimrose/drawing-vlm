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
from rc_metric2 import sheet_score_v3
IOU_ONCE = os.path.join(HERE, "iou_once.py")

def b64(png): return {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(png).decode()}}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--bench"); ap.add_argument("--picks"); ap.add_argument("--base-url"); ap.add_argument("--model")
    ap.add_argument("--k", type=int, default=8); ap.add_argument("--temperature", type=float, default=0.7); ap.add_argument("--max-tokens", type=int, default=2400)
    ap.add_argument("--out"); ap.add_argument("--workers", type=int, default=24); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--rounds", type=int, default=1); ap.add_argument("--margin", type=float, default=0.1)
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
    def rv3(code, k):
        png, info = render_candidate(code, k, a.py, a.rpy, a.script_dir, 120, 300)
        if png is None: return None, 0.0
        try: return png, float(sheet_score_v3(S[k]["png"], png)["v3"])
        except Exception: return png, 0.0
    def one(k):
        if k in done: return
        code = picks[k]["code"]; s, e = score(code, k); png, v3 = rv3(code, k)
        hist = [{"round": 0, "iou": s, "exec": e, "code": code, "v3": v3}]; rec = {"key": k, "hist": hist, "rounds": []}
        for rd in range(1, a.rounds + 1):
            if png is None: break
            body = {"model": a.model, "temperature": a.temperature, "top_p": 0.95, "n": a.k, "max_tokens": a.max_tokens,
                    "messages": [{"role": "system", "content": SYSTEM_PROMPTS["detailed"]},
                                 {"role": "user", "content": [b64(S[k]["png"]), b64(png), {"type": "text", "text": REPAIR_PROMPT.format(code=code)}]}],
                    "chat_template_kwargs": {"enable_thinking": False}}
            rq = urllib.request.Request(a.base_url.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
            d = json.load(urllib.request.urlopen(rq, timeout=1800))
            draws = []
            for ch in d["choices"]:
                c = extract_code(ch["message"].get("content") or "")
                if not c or any(c == x["code"] for x in draws): continue
                si, ei = score(c, k)
                if not ei: draws.append({"iou": si, "exec": False, "code": c, "v3": 0.0}); continue
                p2, v = rv3(c, k); draws.append({"iou": si, "exec": True, "code": c, "v3": v, "_png": p2})
            rec["rounds"].append([{kk: vv for kk, vv in x.items() if kk != "_png"} for x in draws])
            best = max((x for x in draws if x["exec"] and x.get("_png") is not None), key=lambda x: x["v3"], default=None)
            if best and best["v3"] > v3 + a.margin:      # label-free adoption (render matches the target better)
                code, png, v3 = best["code"], best["_png"], best["v3"]
                hist.append({"round": rd, "iou": best["iou"], "exec": True, "code": code, "v3": v3, "adopted": True})
        rec["draws"] = rec["rounds"][0] if rec["rounds"] else []
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
