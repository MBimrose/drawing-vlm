"""Translation-only alternative to bbox centering: centre both meshes on their
volume centroid (robust to a missing/extra feature shifting the bbox), exact IoU.
    python centroid_study.py <prestage_dir> <out_json>"""
import json, os, sys, warnings; warnings.filterwarnings("ignore")
import numpy as np
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iou import center_mesh, load_mesh, mesh_iou
P, OUT = sys.argv[1], sys.argv[2]
GT = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/step_to_drw/wds_dataset/gt_meshes_v15"
def cm(m):
    mm = m.copy()
    try: c = mm.center_mass
    except Exception: c = (mm.bounds[0] + mm.bounds[1]) / 2
    mm.apply_translation(-np.asarray(c)); return mm
def one(key):
    gt = load_mesh(f"{GT}/{key}.stl")
    if gt is None: return []
    gb, gc = center_mesh(gt), cm(gt); out = []
    for j in range(8):
        p = f"{P}/{key}/cand{j}.stl"
        if not os.path.exists(p): continue
        m = load_mesh(p)
        if m is None or len(m.faces) > 200_000: continue
        out.append({"key": key, "cand": j, "bbox": mesh_iou(center_mesh(m), gb), "centroid": mesh_iou(cm(m), gc)})
    return out
keys = sorted(k for k in os.listdir(P) if os.path.isdir(f"{P}/{k}"))
with ThreadPoolExecutor(int(os.environ.get("WORKERS", "16"))) as ex: rows = [r for rs in ex.map(one, keys) for r in rs]
json.dump(rows, open(OUT, "w")); byk = {}
for r in rows: byk.setdefault(r["key"], []).append(r)
for f in ("bbox", "centroid"):
    v = [max(r[f] for r in rs) for rs in byk.values()]; print(f"{f:9s} per-part best mean {np.mean(v):.4f} >=0.85 {np.mean([x>=0.85 for x in v]):.3f}")
g = np.array([r["centroid"] - r["bbox"] for r in rows]); print(f"per-candidate gain mean {g.mean():+.4f}; >0.02 {np.mean(g>0.02):.1%}; <-0.02 {np.mean(g<-0.02):.1%}")
for lo, hi in [(0,0.5),(0.5,0.85),(0.85,0.95),(0.95,1.01)]:
    m = np.array([(lo<=r["bbox"]<hi) for r in rows]); print(f"  bbox in [{lo},{hi}): n={m.sum():3d} gain {g[m].mean():+.4f}")
print("DONE")
