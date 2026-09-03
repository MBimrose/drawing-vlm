"""Does a rigid ICP alignment (wpklab/meshalign) change the exact-IoU verdict?

For every executing candidate of the 96-pool parts: centered IoU (the metric)
vs IoU after meshalign.register (rigid, no scale, identity kept as a candidate
so it cannot regress) applied to the centered candidate. The exact boolean IoU
is used for both so only the alignment differs.

    python align_study_meshalign.py <prestage_dir> <out_json>     (venv_meshalign)
"""
import json
import os
import sys
import tempfile
import time
import warnings
from concurrent.futures import ProcessPoolExecutor

import numpy as np

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from iou import center_mesh, load_mesh, mesh_iou  # noqa: E402

P, OUT = sys.argv[1], sys.argv[2]
GT = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/step_to_drw/wds_dataset/gt_meshes_v15"


def one(key):
    import meshalign as ma
    gt_t = load_mesh(f"{GT}/{key}.stl")
    if gt_t is None:
        return []
    gt_t = center_mesh(gt_t); out = []
    with tempfile.TemporaryDirectory(prefix="ma_") as td:
        gt_path = os.path.join(td, "gt.stl"); gt_t.export(gt_path)
        ref = ma.load_mesh(gt_path)
        for j in range(8):
            p = f"{P}/{key}/cand{j}.stl"
            if not os.path.exists(p):
                continue
            m = load_mesh(p)
            if m is None or len(m.faces) > 200_000:
                continue
            c = center_mesh(m)
            base = mesh_iou(c, gt_t)
            cp = os.path.join(td, f"c{j}.stl"); c.export(cp)
            t0 = time.time()
            try:
                T = np.asarray(ma.register(ref, ma.load_mesh(cp), verbose=False, seed=0, mode="fast"))
                aligned = c.copy(); aligned.apply_transform(T)
                al = mesh_iou(aligned, gt_t)
                rot = float(np.degrees(np.arccos(np.clip((np.trace(T[:3, :3]) - 1) / 2, -1, 1))))
                shift = float(np.linalg.norm(T[:3, 3]))
                err = ""
            except Exception as e:  # noqa: BLE001
                al, rot, shift, err = base, 0.0, 0.0, repr(e)[:80]
            out.append({"key": key, "cand": j, "centered": base, "meshalign": al,
                        "rot_deg": rot, "shift_mm": shift, "secs": time.time() - t0, "err": err})
    return out


if __name__ == "__main__":
    keys = sorted(k for k in os.listdir(P) if os.path.isdir(f"{P}/{k}"))
    with ProcessPoolExecutor(int(os.environ.get("WORKERS", "16"))) as ex:
        rows = [r for rs in ex.map(one, keys) for r in rs]
    json.dump(rows, open(OUT, "w"))
    byk = {}
    for r in rows:
        byk.setdefault(r["key"], []).append(r)
    for name, f in [("centered (metric)", "centered"), ("meshalign rigid", "meshalign")]:
        v = [max(r[f] for r in rs) for rs in byk.values()]
        print(f"{name:20s} per-part best: mean {np.mean(v):.4f}  >=0.85 {np.mean([x >= 0.85 for x in v]):.3f}")
    g = np.array([r["meshalign"] - r["centered"] for r in rows])
    print(f"per-candidate gain: mean {g.mean():+.4f}; >0.02 in {np.mean(g > 0.02):.1%}; >0.05 in {np.mean(g > 0.05):.1%}; <-0.01 in {np.mean(g < -0.01):.1%}")
    rot = np.array([r["rot_deg"] for r in rows]); sh = np.array([r["shift_mm"] for r in rows])
    print(f"pose change: rotation median {np.median(rot):.2f} deg (p95 {np.percentile(rot, 95):.1f}); shift median {np.median(sh):.2f} mm (p95 {np.percentile(sh, 95):.2f})")
    print(f"time per pair: median {np.median([r['secs'] for r in rows]):.2f}s; errors: {sum(bool(r['err']) for r in rows)}")
    print("DONE")
