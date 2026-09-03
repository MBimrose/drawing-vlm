"""How much IoU does the centered (translation-only) metric lose to frame choices?

For every executing candidate of the 96-pool parts (STLs from the self-check
prestage), compare: centered IoU (the metric), best over the 24 proper
axis-aligned rotations, best over 48 (with reflections), and bbox rescale after
the best rotation. Writes per-candidate rows + a summary.

    python align_study.py <prestage_dir> <out_json>
"""
import itertools
import json
import os
import sys
import warnings
from concurrent.futures import ThreadPoolExecutor

import numpy as np

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from iou import center_mesh, load_mesh, mesh_iou  # noqa: E402

P, OUT = sys.argv[1], sys.argv[2]
GT = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/step_to_drw/wds_dataset/gt_meshes_v15"


def rotations():
    ms = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product([1, -1], repeat=3):
            M = np.zeros((3, 3))
            for i, p in enumerate(perm):
                M[i, p] = signs[i]
            ms.append(M)
    return ms


ALL = rotations()
PROPER = [M for M in ALL if np.linalg.det(M) > 0]


def tf(m, M):
    mm = m.copy()
    T = np.eye(4); T[:3, :3] = M
    mm.apply_transform(T)
    return center_mesh(mm)


def study(key):
    gt = load_mesh(f"{GT}/{key}.stl")
    if gt is None:
        return []
    gt = center_mesh(gt); out = []
    for j in range(8):
        p = f"{P}/{key}/cand{j}.stl"
        if not os.path.exists(p):
            continue
        m = load_mesh(p)
        if m is None or len(m.faces) > 200_000:
            continue
        c = center_mesh(m)
        base = mesh_iou(c, gt)
        per = [mesh_iou(tf(c, M), gt) for M in ALL]
        r48 = max(per)
        proper_scores = [s for s, M in zip(per, ALL) if np.linalg.det(M) > 0]
        r24 = max(proper_scores)
        best = PROPER[int(np.argmax(proper_scores))]
        cc = tf(c, best)
        sc = (gt.bounds[1] - gt.bounds[0]) / np.maximum(cc.bounds[1] - cc.bounds[0], 1e-6)
        ss = cc.copy(); ss.apply_scale(sc)
        rs = mesh_iou(center_mesh(ss), gt)
        out.append({"key": key, "cand": j, "centered": base, "rot24": r24, "rot48": r48, "rot_rescale": rs})
    return out


keys = sorted(k for k in os.listdir(P) if os.path.isdir(f"{P}/{k}"))
with ThreadPoolExecutor(int(os.environ.get("WORKERS", "16"))) as ex:
    rows = [r for rs in ex.map(study, keys) for r in rs]
json.dump(rows, open(OUT, "w"))

byk = {}
for r in rows:
    byk.setdefault(r["key"], []).append(r)


def agg(field):
    v = [max(r[field] for r in rs) for rs in byk.values()]
    return float(np.mean(v)), float(np.mean([x >= 0.85 for x in v]))


print(f"candidates: {len(rows)} over {len(byk)} parts")
print("per-part best candidate      mean    >=0.85")
for name, f in [("centered (current metric)", "centered"), ("best of 24 rotations", "rot24"),
                ("best of 48 (+reflections)", "rot48"), ("rotation + bbox rescale", "rot_rescale")]:
    m, fr = agg(f); print(f"{name:28s} {m:.4f}  {fr:.3f}")
g = np.array([r["rot24"] - r["centered"] for r in rows])
print(f"\nper-candidate rotation gain: mean {g.mean():.4f}; >0.05 in {np.mean(g > 0.05):.1%}; >0.2 in {np.mean(g > 0.2):.1%}")
g = np.array([r["rot48"] - r["rot24"] for r in rows])
print(f"reflection extra gain:      mean {g.mean():.4f}; >0.05 in {np.mean(g > 0.05):.1%}")
g = np.array([r["rot_rescale"] - r["rot24"] for r in rows])
print(f"bbox-rescale extra gain:    mean {g.mean():.4f}; >0.05 in {np.mean(g > 0.05):.1%}")
print("DONE")
