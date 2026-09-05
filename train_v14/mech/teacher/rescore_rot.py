"""Re-score teacher candidates under frame-tolerant metrics.

For each row of a teacher scored-*.jsonl with code: re-execute to STL and report
centered IoU (the metric), best of the 24 proper axis-aligned rotations, and
rotation + bbox rescale. Tells whether low teacher scores are frame/scale
conventions (fixable by prompt) or real geometry errors.

    python rescore_rot.py <scored.jsonl> <gt_dir>[,<gt_dir2>] [--max N]
"""
import json, os, sys, tempfile, itertools, warnings
import numpy as np
warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "geom")))
from iou import center_mesh, load_mesh, mesh_iou  # noqa: E402
from rft_generate import exec_to_stl  # noqa: E402

ROT = []
for perm in itertools.permutations(range(3)):
    for signs in itertools.product([1, -1], repeat=3):
        M = np.zeros((3, 3))
        for i, p in enumerate(perm):
            M[i, p] = signs[i]
        if np.linalg.det(M) > 0:
            ROT.append(M)


def tf(m, M):
    mm = m.copy(); T = np.eye(4); T[:3, :3] = M; mm.apply_transform(T); return center_mesh(mm)


scored, gtdirs = sys.argv[1], sys.argv[2].split(",")
mx = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 10**9
rows = [json.loads(l) for l in open(scored)][:mx]
out = []
with tempfile.TemporaryDirectory(prefix="rsc_") as td:
    for r in rows:
        if not r.get("code"):
            continue
        gtp = next((f"{d}/{r['key']}.stl" for d in gtdirs if os.path.exists(f"{d}/{r['key']}.stl")), None)
        if not gtp:
            continue
        stl = f"{td}/{r['key']}_{r['sample']}.stl"
        if not exec_to_stl(r["code"], stl, td, f"{r['key']}_{r['sample']}"):
            out.append({"key": r["key"], "sample": r["sample"], "exec": False}); continue
        m, gt = load_mesh(stl), load_mesh(gtp)
        if m is None or gt is None or len(m.faces) > 300_000:
            continue
        c, gt = center_mesh(m), center_mesh(gt)
        base = mesh_iou(c, gt)
        per = [mesh_iou(tf(c, M), gt) for M in ROT]
        best = ROT[int(np.argmax(per))]; cc = tf(c, best)
        sc = (gt.bounds[1] - gt.bounds[0]) / np.maximum(cc.bounds[1] - cc.bounds[0], 1e-6)
        ss = cc.copy(); ss.apply_scale(sc)
        rs = mesh_iou(center_mesh(ss), gt)
        ext_p = (c.bounds[1] - c.bounds[0]); ext_g = (gt.bounds[1] - gt.bounds[0])
        out.append({"key": r["key"], "sample": r["sample"], "exec": True, "centered": base, "rot24": max(per),
                    "rot_rescale": rs, "extent_pred": ext_p.round(1).tolist(), "extent_gt": ext_g.round(1).tolist(),
                    "vol_ratio": float(c.volume / max(gt.volume, 1e-9))})
        print(json.dumps(out[-1]), flush=True)
ex = [o for o in out if o.get("exec")]
if ex:
    print(f"\n{len(ex)} executed: centered {np.mean([o['centered'] for o in ex]):.3f}  rot24 {np.mean([o['rot24'] for o in ex]):.3f}  rot+rescale {np.mean([o['rot_rescale'] for o in ex]):.3f}; >=0.8 under rot+rescale: {sum(o['rot_rescale']>=0.8 for o in ex)}")
