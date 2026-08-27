"""Generate visualization assets for a checkpoint: for N eval samples, save
the input drawing, the model's predicted part (executed -> STL -> rendered),
the GT part render, and per-sample IoU.

    python visualize_best.py --ckpt runs/e15-full-notrace/final --kind hf \
        --run e15-full-notrace --n 16 --out viz_e15

Renders use matplotlib 3D (headless-safe). One repair round is applied to
failed samples, mirroring the deployable eval.
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

from data_v14 import EVAL_CACHE, _decode_png  # noqa: E402
from geom_eval_worker import (  # noqa: E402
    GT_DIR, HARNESS, PYTHON, build_gen_messages, build_repair_messages,
    extract_code, feedback_text, generate_all, load_model, run_config,
)
from iou import iou_pair, load_mesh  # noqa: E402


def render_mesh(stl_path: str, out_png: str, color: str) -> bool:
    mesh = load_mesh(stl_path)
    if mesh is None:
        return False
    v, f = np.asarray(mesh.vertices), np.asarray(mesh.faces)
    fig = plt.figure(figsize=(5, 5), dpi=110)
    ax = fig.add_subplot(111, projection="3d")
    tris = v[f]
    pc = Poly3DCollection(tris, facecolor=color, edgecolor="k",
                          linewidths=0.05, alpha=1.0)
    # simple lambert-ish shading by face normal
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    n = n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)
    light = np.array([0.4, 0.3, 0.85])
    shade = 0.45 + 0.55 * np.clip(n @ light, 0, 1)
    base = np.array(matplotlib.colors.to_rgb(color))
    pc.set_facecolor(np.clip(base[None, :] * shade[:, None], 0, 1))
    ax.add_collection3d(pc)
    lo, hi = v.min(0), v.max(0)
    c, r = (lo + hi) / 2, (hi - lo).max() / 2 + 1e-6
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r, c[2] + r)
    ax.view_init(elev=28, azim=-55)
    ax.set_axis_off()
    fig.tight_layout(pad=0)
    fig.savefig(out_png, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--kind", default="hf")
    ap.add_argument("--run", required=True)
    ap.add_argument("--n", type=int, default=16)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-new-tokens", type=int, default=2400)
    ap.add_argument("--pool", choices=["v1", "v2"], default="v1",
                    help="v2 = frozen certified eval split + STEP-derived GT")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    cfg = run_config(args.run)
    global GT_DIR
    if args.pool == "v2":
        from data_v14 import EVAL_CACHE_V15
        cache_path = EVAL_CACHE_V15
        pool_name = "certified"
        GT_DIR = os.path.join(os.path.dirname(EVAL_CACHE), "gt_meshes_v15")
    else:
        cache_path = EVAL_CACHE
        pool_name = "all"
    with open(cache_path, "rb") as f:
        cache = pickle.load(f)
    keys = [k for k in cache["pools"][pool_name]
            if os.path.exists(os.path.join(GT_DIR, f"{k}.stl"))][: args.n]
    samples = [{"uuid": k, "image": _decode_png(cache["samples"][k]["png"])}
               for k in keys]
    print(f"[viz] {len(samples)} samples with GT", flush=True)

    model, processor = load_model(args.ckpt, args.kind, cfg)
    msgs = [build_gen_messages(s["image"], cfg) for s in samples]
    outs = generate_all(model, processor, cfg, msgs, args.batch,
                        args.max_new_tokens, "viz r0")

    results = []
    with tempfile.TemporaryDirectory(prefix="viz_") as td:
        state = []
        for s, text in zip(samples, outs):
            code = extract_code(text)
            rec = {"key": s["uuid"], "code": code, "exec_ok": False,
                   "stderr_tail": "", "exec_rc": None, "repaired": False,
                   "reply": (code and f"```python\n{code}\n```") or text[-1200:]}
            state.append(rec)

        def run_exec(rec):
            if not rec["code"]:
                return
            cp = os.path.join(td, rec["key"] + ".py")
            with open(cp, "w") as f:
                f.write(rec["code"])
            stl = os.path.join(td, rec["key"] + ".stl")
            try:
                p = subprocess.run([PYTHON, HARNESS, cp, stl],
                                   capture_output=True, text=True, timeout=120)
                rec["exec_rc"] = p.returncode
                rec["exec_ok"] = p.returncode == 0
                rec["stderr_tail"] = p.stderr[-1200:] if p.returncode else ""
            except subprocess.TimeoutExpired:
                rec["exec_rc"] = -9

        for rec in state:
            run_exec(rec)

        # one repair round for failures
        fail_idx = [i for i, r in enumerate(state) if not r["exec_ok"]]
        if fail_idx:
            rmsgs = [build_repair_messages(samples[i]["image"], cfg,
                                           state[i]["reply"],
                                           feedback_text(state[i]))
                     for i in fail_idx]
            routs = generate_all(model, processor, cfg, rmsgs, args.batch,
                                 args.max_new_tokens, "viz r1")
            for i, text in zip(fail_idx, routs):
                code = extract_code(text)
                if code:
                    state[i]["code"] = code
                    run_exec(state[i])
                    state[i]["repaired"] = state[i]["exec_ok"]

        for s, rec in zip(samples, state):
            key = rec["key"]
            s["image"].convert("RGB").resize((768, 512)).save(
                os.path.join(args.out, f"{key}_drawing.jpg"), quality=88)
            gt_stl = os.path.join(GT_DIR, f"{key}.stl")
            render_mesh(gt_stl, os.path.join(args.out, f"{key}_gt.png"),
                        "#8fb7dd")
            entry = {"key": key, "exec_ok": rec["exec_ok"],
                     "repaired": rec["repaired"], "iou": 0.0}
            if rec["exec_ok"]:
                pred_stl = os.path.join(td, key + ".stl")
                entry["iou"] = iou_pair(pred_stl, gt_stl)["iou_centered"]
                render_mesh(pred_stl,
                            os.path.join(args.out, f"{key}_pred.png"),
                            "#e8a87c")
                with open(os.path.join(args.out, f"{key}_pred.py"), "w") as f:
                    f.write(rec["code"] or "")
            results.append(entry)
            print(f"[viz] {key}: exec={entry['exec_ok']} iou={entry['iou']:.3f}"
                  f"{' (repaired)' if entry['repaired'] else ''}", flush=True)

    with open(os.path.join(args.out, "results.json"), "w") as f:
        json.dump({"ckpt": args.ckpt, "run": args.run, "results": results}, f,
                  indent=1)
    print(f"[viz] done -> {args.out}", flush=True)


if __name__ == "__main__":
    main()
