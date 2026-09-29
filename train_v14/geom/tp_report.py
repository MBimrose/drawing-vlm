"""Score start / final programs of a vr_serve run against the reference: absolute centred IoU and shape IoU (both meshes
scaled so the longest bbox edge = 100). Writes final STEP/STL/code per key into <outdir>."""
import json, os, subprocess, sys, tempfile
import trimesh
HERE = os.path.dirname(os.path.abspath(__file__)); PY = sys.executable; sys.path.insert(0, HERE)
from iou import iou_pair
log, ref, outdir = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(outdir, exist_ok=True)
def mesh(code, stem):
    cp, stl, stp = f"{outdir}/{stem}.py", f"{outdir}/{stem}.stl", f"{outdir}/{stem}.step"; open(cp, "w").write(code)
    r = subprocess.run([PY, os.path.join(HERE, "exec_harness.py"), cp, stl, stp], capture_output=True, text=True, timeout=180)
    return stl if r.returncode == 0 and os.path.exists(stl) else None
def norm(p, tag):
    m = trimesh.load(p); m.apply_scale(100.0 / max(m.extents)); q = f"{outdir}/_{tag}_n.stl"; m.export(q); return q
rn = norm(ref, "ref")
for l in open(log):
    r = json.loads(l); k = r["key"]; h = r["hist"]; fin = h[-1]
    for tag, x in (("start", h[0]), ("final", fin)):
        s = mesh(x["code"], f"{k}_{tag}")
        if not s: print(k, tag, "does not execute"); continue
        m = trimesh.load(s); a = iou_pair(s, ref)["iou_centered"]; b = iou_pair(norm(s, f"{k}{tag}"), rn)["iou_centered"]
        print(f"{k} {tag:5s} extents {[round(e,1) for e in m.extents]} mm  IoU {a:.3f}  shape-IoU {b:.3f}  v3 {x.get('v3', 0):.3f}  adopted rounds {[y['round'] for y in h[1:]]}")
