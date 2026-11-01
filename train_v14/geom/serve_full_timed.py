"""Wall-clock latency of the FULL served system, one drawing at a time, by stage (the S1 / bench-B protocol):

  1 generate   K=16 candidates from the generator (draw 0 greedy + 15 at T 0.7, think, 2,400 tokens), vLLM
  2 execute    every candidate -> STEP + STL (exec_harness.py), in parallel
  3 select     in parallel: render each executing candidate as a drawing (draftwright 0.4.23) + render-compare
               v3 vs the input sheet; verifier v3b expected IoU (HF, one batched forward pass); then rank by
               verifier + v3 (pg_make_starts / sel_study "ver+v3") and take the top-3 DISTINCT (pairwise IoU < 0.95)
  4 repair     3 chains in parallel; each round: rp3 proposes 16 repairs (no-think, T 0.7, 6,000 tokens), each is
               executed + rendered + v3-scored, the best is adopted if its v3 beats the chain's by 0.1; 6 rounds
               (vr_serve.py protocol: every round runs)
  5 pick       final = chain final with the highest v3
Every model stays loaded (generator and repairer behind vLLM servers, verifier in this process on its own GPU), so
the numbers are per-part serving latency, not job start-up. Ground-truth IoU of the chosen program is computed after
the clock stops (evaluation only).

    CUDA_VISIBLE_DEVICES=<verifier gpu> python serve_full_timed.py --bench <bench> --gen-url .../v1 --gen-model gen \
        --rp-url .../v1 --rp-model rp3 --verifier runs/v3b-verifier-real-reg/final --rpy dw_venv/bin/python \
        --script-dir mech_benchmarks/step_to_drw --n 30 --out full_timed.jsonl
"""
import argparse, base64, glob, json, os, pickle, random, subprocess, sys, tempfile, threading, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor

os.environ.setdefault("IOU_MC_POINTS", "20000")      # candidate-vs-candidate agreement (as consistency_rerank.py)
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from collate_v14 import SYSTEM_PROMPTS, REPAIR_PROMPT  # noqa: E402
from geom_eval_worker import USER_PROMPT, extract_code  # noqa: E402
from rc_metric2 import sheet_score_v3  # noqa: E402
from render_compare import HARNESS, RENDER_EXT  # noqa: E402
from iou import iou_pair  # noqa: E402
IOU_ONCE = os.path.join(HERE, "iou_once.py")


def img(png):
    return {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(png).decode()}}


def run_group(cmd, timeout, **kw):
    """subprocess.run in its own process group; on timeout kill the whole group (render_ext.py's pool workers otherwise
    survive as orphans at 100% CPU forever: 19 of them had piled up on serv-05 by 2026-10-21)."""
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True, **kw)
    try:
        out, err = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, 9)
        except ProcessLookupError:
            pass
        p.communicate(); raise
    return subprocess.CompletedProcess(cmd, p.returncode, out, err)


def chat(url, body, timeout=3600):
    rq = urllib.request.Request(url.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(),
                                headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(rq, timeout=timeout))["choices"]


class Worker:
    """Execute + render + v3 for one program; each call owns a temp dir under /dev/shm."""

    def __init__(self, a, target_png, key):
        self.a, self.target, self.key = a, target_png, key

    def execute(self, code, td):
        cp, stl, step = os.path.join(td, "c.py"), os.path.join(td, "c.stl"), os.path.join(td, "src", self.key + ".step")
        os.makedirs(os.path.dirname(step), exist_ok=True); open(cp, "w").write(code)
        try:
            p = run_group([self.a.py, HARNESS, cp, stl, step], timeout=120)
            ok = p.returncode == 0 and os.path.exists(step) and os.path.exists(stl)
        except subprocess.TimeoutExpired:
            ok = False
        return ok, stl

    def render_v3(self, td):
        env = dict(os.environ, SCRIPT_DIR=self.a.script_dir, VLM_MODE="1", OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
        try:
            run_group([self.a.rpy, RENDER_EXT, "--src", os.path.join(td, "src"), "--out", os.path.join(td, "out"),
                       "--workers", "1"], timeout=300, env=env, cwd=td)
        except subprocess.TimeoutExpired:
            return None, 0.0
        pngs = glob.glob(os.path.join(td, "out", "png", self.key + "_v*.png"))
        if not pngs:
            return None, 0.0
        png = open(pngs[0], "rb").read()
        try:
            return png, float(sheet_score_v3(self.target, png)["v3"])
        except Exception:
            return png, 0.0


DIGITS = [str(d) for d in range(10)]
VER_RETRIES = [0]


def ver_vllm(url, model, png, code, effort="medium"):
    """reg_ev expected IoU of the v3b verifier served by vLLM (same prompt as verifier_select_offline.build_prompt)."""
    from collate_v14 import VERIFIER_SYSTEM, VERIFIER_USER, wrap_python
    import math
    body = {"model": model, "max_tokens": 1, "temperature": 0.0, "logprobs": True, "top_logprobs": 20, "prompt_logprobs": 20,
            "add_generation_prompt": False, "continue_final_message": True,
            "chat_template_kwargs": {"enable_thinking": True, "reasoning_effort": effort},
            "messages": [{"role": "system", "content": [{"type": "text", "text": VERIFIER_SYSTEM}]},
                         {"role": "user", "content": [img(png), {"type": "text", "text": VERIFIER_USER.format(code=wrap_python(code))}]},
                         {"role": "assistant", "content": "0."}]}
    rq = urllib.request.Request(url.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(),
                                headers={"Content-Type": "application/json"})
    for attempt in range(6):   # under load vLLM occasionally hits a NaN prompt logprob and rejects its own response (400); retry
        try:
            d = json.load(urllib.request.urlopen(rq, timeout=600)); break
        except urllib.error.HTTPError as e:
            if e.code != 400 or attempt == 5:
                raise
            VER_RETRIES[0] += 1; time.sleep(0.5 * (attempt + 1))
    first = d["prompt_logprobs"][-2]                       # distribution at the "0" token position
    p01 = [math.exp(first[t]["logprob"]) if t in first else 0.0 for t in
           [next((k for k, v in first.items() if v.get("decoded_token") == c), None) for c in ("0", "1")]]
    tops = d["choices"][0]["logprobs"]["content"][0]["top_logprobs"]
    pd = {t["token"]: math.exp(t["logprob"]) for t in tops if t["token"] in DIGITS}
    z1 = sum(p01) or 1.0; z2 = sum(pd.values()) or 1.0
    return p01[1] / z1 + p01[0] / z1 * sum(pd.get(str(k), 0.0) / z2 * (k / 10 + 0.05) for k in range(10))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bench", required=True); ap.add_argument("--keys", default="")
    ap.add_argument("--n", type=int, default=30); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--gen-url", required=True); ap.add_argument("--gen-model", required=True)
    ap.add_argument("--rp-url", required=True); ap.add_argument("--rp-model", required=True)
    ap.add_argument("--verifier", default="runs/v3b-verifier-real-reg/final"); ap.add_argument("--verifier-run", default="v3b-verifier-real-reg")
    ap.add_argument("--base", default=""); ap.add_argument("--vbatch", type=int, default=16)
    ap.add_argument("--k", type=int, default=16); ap.add_argument("--rk", type=int, default=16)
    ap.add_argument("--rounds", type=int, default=6); ap.add_argument("--chains", type=int, default=3)
    ap.add_argument("--margin", type=float, default=0.1); ap.add_argument("--distinct", type=float, default=0.95)
    ap.add_argument("--py", default=sys.executable); ap.add_argument("--rpy", required=True); ap.add_argument("--script-dir", required=True)
    ap.add_argument("--workers", type=int, default=64); ap.add_argument("--out", required=True)
    ap.add_argument("--concurrency", type=int, default=1, help="drawings in flight (throughput deployment)")
    ap.add_argument("--all", action="store_true", help="every part of the bench (ignore --n)")
    ap.add_argument("--ver-url", default="", help="vLLM endpoint serving the verifier LoRA (lean setup; no HF verifier)")
    ap.add_argument("--ver-model", default="ver")
    ap.add_argument("--select", choices=["both", "ver", "v3"], default="both",
                    help="both = verifier + render-compare (render every candidate); ver = verifier only (no renders); "
                         "v3 = render-compare only (no verifier model)")
    ap.add_argument("--no-eval", action="store_true", help="skip ground-truth IoU (throughput runs; score offline from codes)")
    a = ap.parse_args()
    for f in ("bench", "rpy", "script_dir", "py", "verifier", "out"):   # renders run with cwd = a temp dir
        setattr(a, f, os.path.abspath(getattr(a, f)))

    from geom_eval_worker import classify_ckpt, load_model, run_config
    from verifier_select_offline import reg_ev_scores
    from data_v14 import _decode_png
    if not a.ver_url and a.select != "v3":
        vcfg = run_config(a.verifier_run)
        if a.base:
            vcfg["model_id"] = a.base
        vmodel, vproc = load_model(a.verifier, classify_ckpt(a.verifier), vcfg); vmodel.eval()

    cache = pickle.load(open(os.path.join(a.bench, "eval_cache_v15.pkl"), "rb"))["samples"]
    if a.keys:
        keys = [l.strip() for l in open(a.keys) if l.strip()]
    else:
        keys = sorted(k for k in cache if os.path.exists(os.path.join(a.bench, "gt_meshes_v15", k + ".stl")))
        random.Random(a.seed).shuffle(keys); keys = keys if a.all else keys[: a.n]
    done = {json.loads(l)["key"] for l in open(a.out)} if os.path.exists(a.out) else set()
    pool = ThreadPoolExecutor(a.workers); lock = threading.Lock(); vlock = threading.Lock()
    sysmsg = SYSTEM_PROMPTS["detailed"]

    def run_part(key):
        target = cache[key]["png"]; W = Worker(a, target, key); T = {}
        tds = []

        def newdir():
            td = tempfile.mkdtemp(prefix="sft_", dir="/dev/shm"); tds.append(td); return td

        t0 = time.perf_counter()
        # 1. generate K candidates (greedy request + sampled request, concurrently, as gen_openai_bo.py)
        gbody = {"model": a.gen_model, "max_tokens": 2400, "chat_template_kwargs": {"enable_thinking": True},
                 "messages": [{"role": "system", "content": sysmsg},
                              {"role": "user", "content": [img(target), {"type": "text", "text": USER_PROMPT}]}]}
        f_g = pool.submit(chat, a.gen_url, dict(gbody, temperature=0.0, top_p=1.0, n=1))
        f_s = pool.submit(chat, a.gen_url, dict(gbody, temperature=0.7, top_p=0.95, n=a.k - 1))
        codes = [extract_code(ch["message"].get("content") or "") for ch in f_g.result() + f_s.result()]
        T["generate"] = time.perf_counter() - t0

        # 2. execute every candidate
        t1 = time.perf_counter()
        dirs = [newdir() for _ in codes]
        ex = list(pool.map(lambda i: W.execute(codes[i], dirs[i]) if codes[i] else (False, None), range(len(codes))))
        T["execute"] = time.perf_counter() - t1

        # 3. selection: renders + v3 (CPU) in parallel with the verifier (GPU); then distinct top-3
        t2 = time.perf_counter()
        idx = [i for i, (ok, _) in enumerate(ex) if ok]
        f_r = {i: pool.submit(W.render_v3, dirs[i]) for i in idx} if a.select != "ver" else {}
        tv = time.perf_counter()
        if a.select == "v3":
            ver = {i: 0.0 for i in idx}
        elif a.ver_url:   # lean: verifier LoRA served next to the generator, requests in parallel
            ver = dict(zip(idx, pool.map(lambda i: ver_vllm(a.ver_url, a.ver_model, target, codes[i]), idx)))
        else:
            with vlock:   # one HF verifier on one GPU, shared by the drawings in flight
                ver = dict(zip(idx, reg_ev_scores(vmodel, vproc, [_decode_png(target)] * len(idx), [codes[i] for i in idx], vcfg,
                                                  batch=a.vbatch, log=None))) if idx else {}
        T["verifier"] = time.perf_counter() - tv
        rv = {i: f.result() for i, f in f_r.items()}
        T["render_compare"] = time.perf_counter() - t2   # renders finish after the verifier (both started at t2)
        score = {i: ver[i] + (rv[i][1] if i in rv else 0.0) for i in idx}
        ranked = sorted(idx, key=lambda i: (-score[i], i)) or [0]
        chosen = []
        for i in ranked:   # distinctness only needs pairs against the picks so far
            if all(iou_pair(ex[i][1], ex[j][1])["iou_centered"] < a.distinct for j in chosen):
                chosen.append(i)
            if len(chosen) == a.chains:
                break
        while len(chosen) < a.chains:
            chosen.append(chosen[-1])
        T["select"] = time.perf_counter() - t2

        # 4. repair chains, in parallel
        t3 = time.perf_counter()

        def chain(i):
            code, png, v3 = codes[i], rv.get(i, (None, 0.0))[0], rv.get(i, (None, 0.0))[1]; rtimes = []
            hist = [{"round": 0, "code": code, "v3": v3}]
            for rd in range(a.rounds):
                if png is None:
                    break
                tr = time.perf_counter()
                body = {"model": a.rp_model, "temperature": 0.7, "top_p": 0.95, "n": a.rk, "max_tokens": 6000,
                        "chat_template_kwargs": {"enable_thinking": False, "thinking": False},
                        "messages": [{"role": "system", "content": sysmsg},
                                     {"role": "user", "content": [img(target), img(png), {"type": "text", "text": REPAIR_PROMPT.format(code=code)}]}]}
                reps = []
                for ch in chat(a.rp_url, body):
                    c = extract_code(ch["message"].get("content") or "")
                    if c and c not in reps:
                        reps.append(c)
                rdirs = [newdir() for _ in reps]

                def score_rep(j):
                    ok, _ = W.execute(reps[j], rdirs[j])
                    return W.render_v3(rdirs[j]) if ok else (None, 0.0)
                res = list(pool.map(score_rep, range(len(reps))))
                best = max((j for j in range(len(reps)) if res[j][0] is not None), key=lambda j: res[j][1], default=None)
                if best is not None and res[best][1] > v3 + a.margin:
                    code, png, v3 = reps[best], res[best][0], res[best][1]
                    hist.append({"round": rd + 1, "code": code, "v3": v3})
                rtimes.append(time.perf_counter() - tr)
            return code, v3, rtimes, hist
        chains = list(ThreadPoolExecutor(a.chains).map(chain, chosen))
        T["repair"] = time.perf_counter() - t3
        best_chain = max(range(len(chains)), key=lambda c: chains[c][1]); final_code = chains[best_chain][0]
        T["total"] = time.perf_counter() - t0

        # evaluation only (clock stopped): GT IoU of the served program and of the selected start
        def gt_iou(code):
            with tempfile.TemporaryDirectory(prefix="sfe_", dir="/dev/shm") as td:
                ok, stl = W.execute(code, td)
                if not ok:
                    return 0.0
                p = subprocess.run([a.py, IOU_ONCE, stl, os.path.join(a.bench, "gt_meshes_v15", key + ".stl")],
                                   capture_output=True, text=True, timeout=600)
                try:
                    return float(json.loads(p.stdout)["iou_centered"])
                except Exception:
                    return 0.0
        rec = {"key": key, "times": T, "n_exec": len(idx), "round_times": [c[2] for c in chains], "t_start": t0, "t_end": t0 + T["total"],
               "iou_final": None if a.no_eval else gt_iou(final_code), "iou_start": None if a.no_eval else gt_iou(codes[chosen[0]]),
               # for candidate visualisations (codes re-executed offline; no meshes stored)
               "codes": codes, "exec": [ok for ok, _ in ex], "ver": {str(i): v for i, v in ver.items()},
               "v3": {str(i): rv[i][1] for i in rv}, "chosen": chosen, "best_chain": best_chain,
               "chains": [c[3] for c in chains], "final_code": final_code}
        for td in tds:
            subprocess.run(["rm", "-rf", td])
        with lock:
            with open(a.out, "a") as f:
                f.write(json.dumps(rec) + "\n")
        print(f"[full] {key[:16]} " + " ".join(f"{k} {v:.1f}s" for k, v in T.items()) +
              f"  exec {len(idx)}/{len(codes)}" + ("" if a.no_eval else f"  IoU start {rec['iou_start']:.3f} -> final {rec['iou_final']:.3f}"), flush=True)

    def safe(key):
        if key in done:
            return
        try:
            run_part(key)
        except Exception as e:
            import traceback
            body = e.read().decode(errors="replace")[:500] if isinstance(e, urllib.error.HTTPError) else ""
            print(f"[full] ERROR {key}: {traceback.format_exc()[-600:]} {body}", flush=True)
    with ThreadPoolExecutor(a.concurrency) as ex:
        list(ex.map(safe, keys))
    print(f"FULL DONE (verifier 400 retries: {VER_RETRIES[0]})", flush=True)


if __name__ == "__main__":
    main()
