"""Offline evaluation of CONSISTENCY (medoid) selection on stored best-of-N
candidates: re-execute every candidate, compute pairwise volumetric IoU among
each part's executing candidates, and pick the one with the highest mean
agreement with the others. No learned verifier, no GT signal in selection —
majority voting in shape space. Compares vs first_exec / oracle on the same
candidate sets, plus a consistency+greedy hybrid.

    python consistency_rerank.py results/bo8_verifier2_e24.json results/bo8_consistency.json
"""
import json
import os
import sys
# Candidate-vs-candidate agreement only needs a coarse IoU when both boolean
# engines fail on a non-watertight candidate: 20k points (~±0.01) instead of
# the 150k used against ground truth (a 7x speed-up on the rare fallback path).
os.environ.setdefault("IOU_MC_POINTS", "20000")
import tempfile
from concurrent.futures import ThreadPoolExecutor
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from iou import iou_pair  # noqa: E402
from rft_generate import exec_to_stl  # noqa: E402

src, out_path = sys.argv[1], sys.argv[2]
data = json.load(open(src))
parts = data["candidates"]
print(f"[cons] {len(parts)} parts, k={data['metrics']['k']}", flush=True)

with tempfile.TemporaryDirectory(prefix="cons_") as td:
    def run_one(a):
        pi, j = a
        c = parts[pi]["cands"][j]
        if not c.get("code") or not c.get("exec"):
            return
        stl = os.path.join(td, f"{pi}_{j}.stl")
        c["stl"] = stl if exec_to_stl(c["code"], stl, td, f"{pi}_{j}") else None
    with ThreadPoolExecutor(max_workers=24) as ex:
        list(ex.map(run_one, [(pi, j) for pi in range(len(parts))
                              for j in range(len(parts[pi]["cands"]))]))
    n_ok = sum(1 for p in parts for c in p["cands"] if c.get("stl"))
    print(f"[cons] re-executed {n_ok} candidates", flush=True)

    def score_part(p):
        cs = [c for c in p["cands"] if c.get("stl")]
        for c in cs:
            c["agree"] = 0.0
        for a, b in combinations(range(len(cs)), 2):
            try:
                v = iou_pair(cs[a]["stl"], cs[b]["stl"])["iou_centered"]
            except Exception:
                v = 0.0
            cs[a]["agree"] += v
            cs[b]["agree"] += v
        for c in cs:
            c["agree"] /= max(1, len(cs) - 1)
    with ThreadPoolExecutor(max_workers=24) as ex:
        list(ex.map(score_part, parts))

def metrics(select):
    ious = []
    for p in parts:
        cs = [c for c in p["cands"] if c.get("stl")]
        ious.append(select(cs, p)["iou"] if cs else 0.0)
    n = len(ious); s = sorted(ious)
    return {"iou_mean": sum(ious) / n, "iou_median": s[n // 2],
            "frac_iou85": sum(i >= 0.85 for i in ious) / n,
            "frac_iou50": sum(i >= 0.5 for i in ious) / n}

pols = {
    "first_exec": lambda cs, p: cs[0],
    "consistency": lambda cs, p: max(cs, key=lambda c: c["agree"]),
    # greedy candidate unless its agreement is far below the medoid's
    "cons_hybrid": lambda cs, p: (cs[0] if cs[0]["agree"] >= max(c["agree"] for c in cs) - 0.10
                                  else max(cs, key=lambda c: c["agree"])),
    "verifier": lambda cs, p: max(cs, key=lambda c: c.get("pred", -1e9)),
    "oracle": lambda cs, p: max(cs, key=lambda c: c["iou"]),
}
res = {name: metrics(fn) for name, fn in pols.items()}
# per-part chosen IoU under every policy (enables offline slices, e.g. determinate-only)
res["per_part"] = {p["key"]: {name: (fn([c for c in p["cands"] if c.get("stl")], p)["iou"]
                                     if any(c.get("stl") for c in p["cands"]) else 0.0)
                              for name, fn in pols.items()} for p in parts}
for name, m in res.items():
    print(f"{name:12s} mean={m['iou_mean']:.3f} median={m['iou_median']:.3f} "
          f"iou85={m['frac_iou85']:.3f} iou50={m['frac_iou50']:.3f}", flush=True)
json.dump(res, open(out_path, "w"), indent=1)
