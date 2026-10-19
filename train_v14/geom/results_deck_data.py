"""Per-part table for the results-section figures (e55 best-of-8 on the synthetic test pool): medoid / first
executing draw / oracle IoU, medoid agreement, GT B-rep face count, and the wall time to execute the medoid's
build123d program (build123d already imported; includes the STEP export the program ends with).

    bash train_v14/serv19/cpu_run.sh -c 32 -- .venv/bin/python train_v14/geom/results_deck_data.py
Writes results/figures/results_deck/data/parts.json
"""
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

import numpy as np

DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
BO8 = f"{DV}/results/ext/bo8_full_e55-rft-real-u5-gt-dw423.json"
CONS = f"{DV}/results/ext/bo8_full_e55-rft-real-u5-gt-dw423_consistency.json"
FACES = f"{DV}/results/figures/results_deck/data/faces_all.json"
OUT = f"{DV}/results/figures/results_deck/data/parts.json"
WORKERS = 12   # well below the core count so timings are not inflated by contention

TIMER = r'''
import json, os, sys, tempfile, time
import build123d  # noqa: F401  (import cost excluded from the timing)
code = open(sys.argv[1]).read(); os.chdir(tempfile.mkdtemp(prefix="t_"))
t0 = time.perf_counter()
exec(compile(code, "<gen>", "exec"), {"__name__": "__main__", "OUTPUT_PATH": "output.step"})
print(json.dumps({"sec": time.perf_counter() - t0}))
'''


def main():
    if "--retime" in sys.argv:   # re-measure listed keys (warm) in an existing parts.json
        return retime(sys.argv[sys.argv.index("--retime") + 1:])
    if os.path.exists(OUT) and any(r.get("exec_sec") is not None for r in json.load(open(OUT))):
        print(f"[data] {OUT} already has execution times; skipping")   # a duplicate queued run is a no-op
        return
    bo8 = {p["key"]: p for p in json.load(open(BO8))["candidates"]}
    cons = json.load(open(CONS)); faces = {r["key"]: r for r in json.load(open(FACES))}
    rows = []
    for p in cons["parts"]:
        k, M, ex, iou = p["key"], p["pair_iou"], p["exec"], p["iou"]
        idx = [i for i in range(len(iou)) if ex[i]]
        r = {"key": k, "n_exec": len(idx), "first": iou[idx[0]] if idx else 0.0, "draw0": iou[0] if ex[0] else 0.0,
             "oracle": max(iou) if idx else 0.0, "faces": faces[k]["faces"], "medoid": None, "agree": None}
        if len(idx) >= 2:
            ag = {i: float(np.mean([M[i][j] if M[i][j] is not None else 0.0 for j in idx if j != i])) for i in idx}
            m = max(idx, key=lambda i: ag[i]); r.update(medoid_idx=m, agree=ag[m])
        elif idx:
            m = idx[0]; r.update(medoid_idx=m)
        else:
            m = None
        r["medoid"] = iou[m] if m is not None else 0.0
        r["code"] = bo8[k]["cands"][m]["code"] if m is not None else None
        rows.append(r)

    td = tempfile.mkdtemp(prefix="rdd_"); tp = os.path.join(td, "timer.py"); open(tp, "w").write(TIMER)

    def time_one(r):
        if not r["code"]:
            return None
        cp = os.path.join(td, r["key"] + ".py"); open(cp, "w").write(r["code"])
        try:
            out = subprocess.run([sys.executable, tp, cp], capture_output=True, text=True, timeout=300)
            return json.loads(out.stdout.strip().splitlines()[-1])["sec"]
        except Exception:
            return None

    warm_up(tp, td)
    with ThreadPoolExecutor(WORKERS) as ex:
        secs = list(ex.map(time_one, rows))
    for r, s in zip(rows, secs):
        r["exec_sec"] = s; r.pop("code")
    json.dump(rows, open(OUT, "w"), indent=1)
    t = [s for s in secs if s is not None]
    print(f"[data] {len(rows)} parts, timed {len(t)}: median {np.median(t):.2f}s p95 {np.percentile(t, 95):.2f}s -> {OUT}")


def warm_up(tp, td, n=WORKERS):
    """The first batch of programs absorbs a one-off ~1 s cold start (shared libraries loading from the network
    filesystem): run throwaway programs first so no timed part pays it."""
    cp = os.path.join(td, "warm.py")
    open(cp, "w").write('from build123d import *\npart = Box(1, 1, 1) - Cylinder(0.2, 1)\nexport_step(part, "output.step")\n')
    with ThreadPoolExecutor(n) as ex:
        list(ex.map(lambda _: subprocess.run([sys.executable, tp, cp], capture_output=True, timeout=300), range(n)))


def retime(prefixes):
    rows = json.load(open(OUT)); bo8 = {p["key"]: p for p in json.load(open(BO8))["candidates"]}
    td = tempfile.mkdtemp(prefix="rdd_"); tp = os.path.join(td, "timer.py"); open(tp, "w").write(TIMER)
    warm_up(tp, td)
    for r in rows:
        if any(r["key"].startswith(p) for p in prefixes) and r.get("medoid_idx") is not None:
            cp = os.path.join(td, r["key"] + ".py"); open(cp, "w").write(bo8[r["key"]]["cands"][r["medoid_idx"]]["code"])
            out = subprocess.run([sys.executable, tp, cp], capture_output=True, text=True, timeout=300)
            new = json.loads(out.stdout.strip().splitlines()[-1])["sec"]
            print(f"[retime] {r['key'][:8]} {r['exec_sec']:.3f}s -> {new:.3f}s"); r["exec_sec"] = new
    json.dump(rows, open(OUT, "w"), indent=1)


if __name__ == "__main__":
    main()
