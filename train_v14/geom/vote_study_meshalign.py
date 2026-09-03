"""Does a rigid-aligned agreement estimate improve the consistency vote?

For each 96-pool part: candidates cand0..7 (prestage dir). Two pairwise
agreement matrices: centered exact IoU (deployed) and exact IoU after
meshalign.register (rigid). Medoid under each; the served candidate is scored
against GT with the STRICT centered metric in both cases, so only the
selection changes.

    python vote_study_meshalign.py <prestage_dir> <out_json>     (venv_meshalign)
"""
import json
import os
import sys
import tempfile
import warnings
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations

import numpy as np

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from iou import center_mesh, load_mesh, mesh_iou  # noqa: E402

P, OUT = sys.argv[1], sys.argv[2]
GT = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/step_to_drw/wds_dataset/gt_meshes_v15"


def one(key):
    import meshalign as ma
    gt = load_mesh(f"{GT}/{key}.stl")
    if gt is None:
        return None
    gt = center_mesh(gt)
    cands = []
    for j in range(8):
        p = f"{P}/{key}/cand{j}.stl"
        if os.path.exists(p):
            m = load_mesh(p)
            if m is not None and len(m.faces) <= 200_000:
                cands.append((j, center_mesh(m)))
    if not cands:
        return {"key": key, "n": 0}
    truth = {j: mesh_iou(c, gt) for j, c in cands}
    n = len(cands)
    A_c = np.zeros((n, n)); A_m = np.zeros((n, n))
    with tempfile.TemporaryDirectory(prefix="mv_") as td:
        paths = []
        for j, c in cands:
            pth = os.path.join(td, f"c{j}.stl"); c.export(pth); paths.append(pth)
        refs = [ma.load_mesh(pth) for pth in paths]
        for a, b in combinations(range(n), 2):
            ca, cb = cands[a][1], cands[b][1]
            v = mesh_iou(ca, cb); A_c[a, b] = A_c[b, a] = v
            try:
                T = np.asarray(ma.register(refs[a], ma.load_mesh(paths[b]), verbose=False, seed=0, mode="fast"))
                bb = cb.copy(); bb.apply_transform(T)
                vm = max(v, mesh_iou(bb, ca))   # identity is always a candidate
            except Exception:
                vm = v
            A_m[a, b] = A_m[b, a] = vm
    def medoid(A):
        s = A.sum(1) / max(1, n - 1); return int(np.argmax(s)), float(s.max())
    ic, ac = medoid(A_c); im, am = medoid(A_m)
    return {"key": key, "n": n, "served_centered": truth[cands[ic][0]], "served_meshalign": truth[cands[im][0]],
            "agree_centered": ac, "agree_meshalign": am, "oracle": max(truth.values()),
            "first_exec": truth[cands[0][0]], "changed": ic != im}


if __name__ == "__main__":
    keys = sorted(k for k in os.listdir(P) if os.path.isdir(f"{P}/{k}"))
    with ProcessPoolExecutor(int(os.environ.get("WORKERS", "16"))) as ex:
        rows = [r for r in ex.map(one, keys) if r and r.get("n")]
    json.dump(rows, open(OUT, "w"))
    N = len(rows)
    for f in ("first_exec", "served_centered", "served_meshalign", "oracle"):
        v = [r[f] for r in rows]; print(f"{f:18s} mean {np.mean(v):.4f}  >=0.85 {np.mean([x >= 0.85 for x in v]):.3f}")
    ch = [r for r in rows if r["changed"]]
    d = [r["served_meshalign"] - r["served_centered"] for r in ch]
    print(f"selection changed on {len(ch)}/{N} parts; on those: mean delta {np.mean(d) if d else 0:+.4f}, better {sum(x > 0.01 for x in d)}, worse {sum(x < -0.01 for x in d)}")
    print("DONE")
