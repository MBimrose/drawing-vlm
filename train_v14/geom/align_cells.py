"""Rigid-alignment column for every results-table cell (2026-10-29, user: "add it to all the metrics").

Each cell's per-part program is reproduced from the stored eval files (no generation):
  d0     draw 0 of a score_partials candidates file (the one-draw rows: off-the-shelf, LoRA, FFT, ablations)
  vote   the candidate the K=8 consistency vote served (<bench>_<name>_consistency.json per_part, matched to the
         executing candidate with that stored IoU, highest agreement on ties)
  chain  the multi-start repair pick: per part the chain final (last adopted program) with the highest v3 over the 3
         chains (summary_b.py / summary_am.py rules); cells whose chains are still running are reported as partial
Every unique (bench, key, program) is executed once (exec_harness.py, 60 s) and scored by align_once.py under
venv_meshalign (bbox-centred exact IoU = the tables' metric, then wpklab/meshalign rigid ICP, aligned = max(centered,
icp)). The recomputed centred IoU is checked against the stored one. Cache: results/alignment/align_cache.jsonl
(resumable); table: results/alignment/aligned_cells.md + .json. Selection is unchanged everywhere (the vote and the
repair pick still use centred agreement / v3): only the final GT comparison gains an aligned column.

    python align_cells.py [--workers 96] [--only <cell-substring>] [--summary-only]
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from score_partials import execute  # noqa: E402

DV = os.path.dirname(os.path.dirname(HERE)); RES = f"{DV}/results"; OUT = f"{RES}/alignment"
MA_PY = os.environ.get("MA_PY", "/projects/illinois/eng/ece/wpk/bimrose2/venv_meshalign/bin/python")
GT = {"full": f"{DV}/train_v14/mech/benchmarks/data/fullpool_dw423/gt_meshes_v15",
      "benchb": f"{RES}/bench_b/bench/gt_meshes_v15"}
AB, AM, NM = f"{RES}/ablations", f"{RES}/american_vlm", f"{RES}/nemotron"
GE, BE, FG = f"{RES}/grpo_eval", f"{RES}/bench_b/eval", f"{RES}/flashnext/grpo"
REF = {"benchb": f"{RES}/bench_b/pipeline", "full": f"{RES}/indist_pipeline"}
FNEI = open(f"{FG}/FNEI_BEST").read().strip() if os.path.exists(f"{FG}/FNEI_BEST") else "40"


def ev(d, n, m, dfull=None):   # an eval-file cell; dfull = another dir for the synthetic bench
    return {"full": ("file", dfull or d, n, m), "benchb": ("file", d, n, m)}


def ref(sysname):              # 27B chains: bench_b/pipeline + indist_pipeline chain_<sys>_rp3_c{1,2,3}.jsonl
    return {b: ("ref", sysname) for b in ("full", "benchb")}


def am(pdir, name):            # multi-host chains (summary_am.py / summary_fn.py globs)
    return {b: ("glob", pdir, f"{name}_{b}") for b in ("full", "benchb")}


# (column, row, sources) in table order; the paper rows first, then the ablation-table one-draw / vote rows
CELLS = [
    ("Qwen3.8-27B", "Off-the-shelf", ev(BE, "qwenbase", "d0", GE)),
    ("Qwen3.8-27B", "LoRA r64, attention only", ev(AB, "e10", "d0")),
    ("Qwen3.8-27B", "FFT", ev(AB, "e55ctl", "d0")),
    ("Qwen3.8-27B", "FFT + vote", ev(AB, "e55ctl", "vote")),
    ("Qwen3.8-27B", "FFT + vote + GRPO", ev(BE, "rft2_rl_s60", "vote", GE)),
    ("Qwen3.8-27B", "FFT + vote + repair", ref("e55")),
    ("Qwen3.8-27B", "FFT + vote + GRPO + repair (verifier starts)", ref("rl2s60")),
    ("Muse-Glimmer-30B", "Off-the-shelf", ev(AM, "glimmer_zs", "d0")),
    ("Muse-Glimmer-30B", "LoRA", ev(AM, "gllora", "d0")),
    ("Muse-Glimmer-30B", "FFT", ev(AM, "glftpf", "d0")),
    ("Muse-Glimmer-30B", "FFT + vote", ev(AM, "glftpf", "vote")),
    ("Muse-Glimmer-30B", "FFT + vote + GRPO", ev(AM, "gl1s180", "vote")),
    ("Muse-Glimmer-30B", "FFT + vote + repair", am(f"{AM}/pipeline", "glS2")),
    ("Muse-Glimmer-30B", "FFT + vote + GRPO + repair", am(f"{AM}/pipeline_glgrpo", "glgS2")),
    ("Gemma 4 31B", "Off-the-shelf", ev(AM, "gemma4_31b_zs", "d0")),
    ("Gemma 4 31B", "LoRA", ev(AM, "gmlora", "d0")),
    ("Gemma 4 31B", "FFT", ev(AM, "gmftpf", "d0")),
    ("Gemma 4 31B", "FFT + vote", ev(AM, "gmftpf", "vote")),
    ("Gemma 4 31B", "FFT + vote + GRPO", ev(AM, "gm1s40", "vote")),
    ("Gemma 4 31B", "FFT + vote + repair", am(f"{AM}/pipeline_gemma", "gmS2")),
    ("Gemma 4 31B", "FFT + vote + GRPO + repair", am(f"{AM}/pipeline_gmgrpo", "gmgS2")),
    ("Nemotron 3.5 Super VL", "Off-the-shelf", ev(NM, "nemobase", "d0")),
    ("Nemotron 3.5 Super VL", "LoRA", ev(AM, "nmlora", "d0")),
    ("Nemotron 3.5 Super VL", "FFT", ev(AB, "nemoft_pf", "d0")),
    ("Nemotron 3.5 Super VL", "FFT + vote", ev(AB, "nemoft_pf", "vote")),
    ("Nemotron 3.5 Super VL", "FFT + vote + repair", am(f"{AM}/pipeline_nemo", "nmS2")),
    ("Qwen3.8-Flash-Next", "LoRA", ev(AB, "e26fl", "d0")),
    ("Qwen3.8-Flash-Next", "FFT", ev(AB, "e59", "d0")),
    ("Qwen3.8-Flash-Next", "FFT + vote", ev(AB, "e59", "vote")),
    ("Qwen3.8-Flash-Next", "FFT + vote + GRPO", ev(FG, f"fneis{FNEI}", "vote")),
    ("Qwen3.8-Flash-Next", "FFT + vote + repair", am(f"{RES}/flashnext/pipeline", "fnS2")),
    ("Qwen3.8-Flash-Next", "FFT + vote + GRPO + repair", am(f"{RES}/flashnext/pipeline", "fnS1")),
]
for n in ("e1", "e10", "e3", "e4", "e9", "e12", "e2", "e16", "e22", "e24", "e55ctl", "e32fn", "e26fl", "e35fn", "e59",
          "e59best", "nemoft_pf"):
    for m in ("d0", "vote"):
        CELLS.append(("ablation", f"{n} {m}", ev(AB, n, m)))


def final(r):
    x = r["hist"][0]
    for y in r["hist"][1:]:
        if y.get("adopted"):
            x = y
    return x


def picks(b, src):
    """{key: (code or None, stored iou)} for one cell on bench b, or None when its files are missing."""
    if src[0] == "file":
        _, d, n, m = src
        f = f"{d}/{b}_{n}.json"
        if not os.path.exists(f):
            return None
        cands = {p["key"]: sorted(p["cands"], key=lambda c: c.get("draw", 0)) for p in json.load(open(f))["candidates"]}
        if m == "d0":
            return {k: ((c[0].get("code") if c[0].get("exec") else None), float(c[0].get("iou") or 0)) for k, c in cands.items()}
        cf = f"{d}/{b}_{n}_consistency.json"
        if not os.path.exists(cf):
            return None
        C = json.load(open(cf)); pp = C["per_part"]; out = {}
        for p in C["parts"]:
            k = p["key"]; v = float(pp[k]["consistency"]); cs = cands[k]
            ex = [j for j, e in enumerate(p["exec"]) if e]
            if not ex:
                out[k] = (None, 0.0); continue
            M = p["pair_iou"]
            agree = {j: sum(M[j][i] or 0 for i in ex if i != j) / max(1, len(ex) - 1) for j in ex}
            match = [j for j in ex if abs(float(cs[j].get("iou") or 0) - v) < 1e-9]
            j = max(match or ex, key=lambda j: agree[j])
            out[k] = (cs[j].get("code"), v)
        return out
    if src[0] == "ref":
        files = [f"{REF[b]}/chain_{src[1]}_rp3_c{c}.jsonl" for c in (1, 2, 3)]
        if not all(os.path.exists(f) for f in files):
            return None
        ch = [{json.loads(l)["key"]: json.loads(l) for l in open(f)} for f in files]
    else:
        _, d, name = src; ch = []
        for c in (1, 2, 3):
            m = {}
            for f in sorted(glob.glob(f"{d}/out/{name}_c{c}.*jsonl") + glob.glob(f"{d}/out_s19/{name}_c{c}.*jsonl")
                            + glob.glob(f"{d}/h*/out/{name}_c{c}.*jsonl") + glob.glob(f"{d}/r*/out/{name}_c{c}.*jsonl")):
                if f.endswith(".dropped.jsonl"):
                    continue
                for l in open(f):
                    r = json.loads(l); m.setdefault(r["key"], r)
            ch.append(m)
    keys = set.intersection(*[set(c) for c in ch])
    out = {}
    for k in keys:
        x = max((final(c[k]) for c in ch), key=lambda x: x.get("v3", 0))
        out[k] = ((x.get("code") if x.get("exec", True) else None), float(x.get("iou") or 0))
    return out


def hkey(b, k, code):
    return hashlib.sha1(f"{b}|{k}|{code}".encode()).hexdigest()


def load_cache():
    C = {}
    if os.path.exists(f"{OUT}/align_cache.jsonl"):
        for l in open(f"{OUT}/align_cache.jsonl"):
            try:
                r = json.loads(l); C[r["h"]] = r
            except Exception:
                pass
    return C


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=96)
    ap.add_argument("--only", default="")
    ap.add_argument("--summary-only", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    full_n = {"full": 1027, "benchb": 280}
    cells = []
    for col, row, srcs in CELLS:
        if a.only and a.only not in f"{col} {row}":
            continue
        for b in ("full", "benchb"):
            P = picks(b, srcs[b])
            cells.append((col, row, b, P))
            print(f"[cells] {col} | {row} | {b}: {'missing' if P is None else len(P)}", flush=True)
    cache = load_cache()
    todo = {}
    for *_, b, P in cells:
        for k, (code, _) in (P or {}).items():
            if code:
                h = hkey(b, k, code)
                if h not in cache:
                    todo[h] = (b, k, code)
    print(f"[align] {len(todo)} programs to score ({len(cache)} cached)", flush=True)
    if todo and not a.summary_only:
        lock = threading.Lock(); f_out = open(f"{OUT}/align_cache.jsonl", "a"); n = [0]; t0 = time.time()
        with tempfile.TemporaryDirectory(prefix="align_") as td:
            def run(item):
                h, (b, k, code) = item
                stl = f"{td}/{h}.stl"
                rec = {"h": h, "bench": b, "key": k}
                if not execute(code, stl, td, h, 60):
                    rec.update(exec=False, centered=0.0, icp=0.0)
                else:
                    rec["exec"] = True
                    try:
                        p = subprocess.run([MA_PY, f"{HERE}/align_once.py", stl, f"{GT[b]}/{k}.stl"], capture_output=True,
                                           text=True, timeout=300, env={**os.environ, "OMP_NUM_THREADS": "1",
                                                                        "OPENBLAS_NUM_THREADS": "1"})
                        rec.update(json.loads(p.stdout.strip().splitlines()[-1]))
                    except subprocess.TimeoutExpired:
                        rec.update(centered=None, icp=None, error="timeout")
                    except Exception as e:  # noqa: BLE001
                        rec.update(centered=None, icp=None, error=f"{type(e).__name__}"[:80])
                for x in (stl, f"{td}/{h}.py"):
                    if os.path.exists(x):
                        os.remove(x)
                with lock:
                    f_out.write(json.dumps(rec) + "\n"); cache[h] = rec; n[0] += 1
                    if n[0] % 500 == 0:
                        f_out.flush(); r = n[0] / (time.time() - t0)
                        print(f"[align] {n[0]}/{len(todo)} {r:.2f}/s eta {(len(todo) - n[0]) / r / 60:.0f} min", flush=True)
            with ThreadPoolExecutor(a.workers) as ex:
                list(ex.map(run, todo.items()))
        f_out.close()
    # --- summary
    rows, js = [], []
    for col, row, b, P in cells:
        if not P:
            continue
        cen, ali, icp, sto, flips, mism, miss = [], [], [], [], 0, 0, 0
        for k, (code, stored) in P.items():
            r = cache.get(hkey(b, k, code)) if code else {"exec": False, "centered": 0.0, "icp": 0.0}
            if r is None or r.get("centered") is None:      # not scored yet / timed out: keep the stored value, no gain
                miss += 1; c = i = stored
            else:
                c = float(r["centered"]); i = float(r["icp"] if r.get("icp") is not None else c)
                mism += abs(c - stored) > 0.02
                flips += (r.get("rot_deg") or 0) >= 90 and i > c
            sto.append(stored); cen.append(c); icp.append(i); ali.append(max(c, i))
        js.append({"column": col, "row": row, "bench": b, "n": len(P), "complete": len(P) >= full_n[b],
                   "stored": float(np.mean(sto)), "centered": float(np.mean(cen)), "aligned": float(np.mean(ali)),
                   "icp_raw": float(np.mean(icp)), "flip_gains": flips, "mismatch_gt_0.02": mism, "unscored": miss})
    json.dump(js, open(f"{OUT}/aligned_cells.json", "w"), indent=1)
    by = {}
    for r in js:
        by.setdefault((r["column"], r["row"]), {})[r["bench"]] = r
    L = ["# Rigid-alignment column (wpklab/meshalign) for every table cell", "",
         "Centered = the tables' metric (bbox-centred exact IoU, stored value); aligned = max(centered, IoU after meshalign "
         "rigid ICP of the centred prediction onto the centred GT). Selection unchanged. flips = parts whose gain came from a "
         ">=90 deg rotation. (partial n) = repair chains still running.", "",
         "| Model | Row | Synthetic centered | Synthetic aligned | Held-out centered | Held-out aligned | flips (syn / held-out) |",
         "|---|---|---|---|---|---|---|"]
    for (col, row), d in by.items():
        cell = []
        for b in ("full", "benchb"):
            r = d.get(b)
            if not r:
                cell += ["—", "—"]; continue
            tag = "" if r["complete"] else f" (partial {r['n']})"
            cell += [f"{r['stored']:.3f}{tag}", f"{r['aligned']:.3f} ({r['aligned'] - r['stored']:+.3f})"]
        fl = " / ".join(str(d[b]["flip_gains"]) if b in d else "—" for b in ("full", "benchb"))
        L.append(f"| {col} | {row} | " + " | ".join(cell) + f" | {fl} |")
    chk = [r for r in js if r["mismatch_gt_0.02"] or r["unscored"]]
    L += ["", "Checks (recomputed centred IoU vs stored, |diff| > 0.02; unscored = exec/align timeout or not yet run):"]
    L += [f"- {r['column']} | {r['row']} | {r['bench']}: mismatch {r['mismatch_gt_0.02']}, unscored {r['unscored']}, "
          f"centred recomputed {r['centered']:.3f} vs stored {r['stored']:.3f}" for r in chk] or ["- none"]
    open(f"{OUT}/aligned_cells.md", "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
