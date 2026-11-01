"""One centered IoU and one rigid-aligned IoU for a (prediction, ground truth) pair, as a subprocess (venv_meshalign).

As align_study_meshalign.py (2026-09-03): both meshes bbox-centred (iou.center_mesh), "centered" = the exact IoU the
tables report, then wpklab/meshalign rigid registration (no scale, seed 0, mode "fast") of the centred prediction onto
the centred ground truth and the exact IoU again after its transform ("icp"). The caller reports
aligned = max(centered, icp): the aligner minimises surface distance, so on a few parts its pose overlaps less than
the centred one, and an alignment column should not score below the unaligned metric.

    venv_meshalign/bin/python align_once.py <pred.stl> <gt.stl>
      -> {"centered": .., "icp": .., "rot_deg": .., "shift_mm": .., "secs_icp": ..}
"""
import json
import os
import sys
import tempfile
import time
import warnings

import numpy as np

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from iou import center_mesh, load_mesh, mesh_iou  # noqa: E402


def main(pred_path, gt_path):
    import meshalign as ma
    pred, gt = load_mesh(pred_path), load_mesh(gt_path)
    if pred is None or gt is None:
        return {"centered": 0.0, "icp": 0.0, "error": "mesh load"}
    c, g = center_mesh(pred), center_mesh(gt)
    out = {"centered": float(mesh_iou(c, g))}
    with tempfile.TemporaryDirectory(prefix="al_") as td:
        gp, cp = os.path.join(td, "gt.stl"), os.path.join(td, "pred.stl")
        g.export(gp); c.export(cp)
        t0 = time.time()
        T = np.asarray(ma.register(ma.load_mesh(gp), ma.load_mesh(cp), verbose=False, seed=0, mode="fast"))
        out["secs_icp"] = time.time() - t0
    a = c.copy(); a.apply_transform(T)
    out["icp"] = float(mesh_iou(a, g))
    out["rot_deg"] = float(np.degrees(np.arccos(np.clip((np.trace(T[:3, :3]) - 1) / 2, -1, 1))))
    out["shift_mm"] = float(np.linalg.norm(T[:3, 3]))
    return out


if __name__ == "__main__":
    try:
        r = main(sys.argv[1], sys.argv[2])
    except Exception as e:  # noqa: BLE001
        r = {"centered": None, "icp": None, "error": f"{type(e).__name__}: {e}"[:200]}
    print(json.dumps(r))
