"""One-time assets for the v2 (certified-manifest) data era.

1. legacy_keys_v14.txt — tar_keys with renderer=="legacy" from the sidecars
   (handoff §5: filter them out of training).
2. eval_cache_v15.pkl — the frozen manifest's eval split (1,072 certified
   samples: png + code + trace) from the bundle's eval shard.
3. gt_meshes_v15/<uuid>.stl — GT meshes tessellated DIRECTLY from the
   bundle's generated.step files (no code execution -> no failures; every
   eval sample has valid GT).

Usage: python build_v15_assets.py
"""
from __future__ import annotations

import glob
import json
import os
import pickle
import sys
import tarfile
from concurrent.futures import ProcessPoolExecutor, as_completed

WDS = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/step_to_drw/wds_dataset"
BUNDLE = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/v14_bundle"
GT_DIR = os.path.join(WDS, "gt_meshes_v15")


def build_legacy_keys():
    out = os.path.join(WDS, "legacy_keys_v14.txt")
    keys = []
    sidecars = sorted(glob.glob(os.path.join(WDS, "tars_v14", "*.renderers.json")))
    for sc in sidecars:
        try:
            with open(sc) as f:
                entries = json.load(f)
        except Exception:
            continue
        keys.extend(k for k, meta in entries.items()
                    if meta.get("renderer") == "legacy")
    with open(out + ".tmp", "w") as f:
        f.write("\n".join(sorted(keys)) + "\n")
    os.replace(out + ".tmp", out)
    print(f"[assets] {len(keys)} legacy keys from {len(sidecars)} sidecars -> {out}")


def build_eval_cache():
    out = os.path.join(WDS, "eval_cache_v15.pkl")
    samples, order = {}, []
    with tarfile.open(os.path.join(BUNDLE, "shards", "eval-000000.tar")) as tf:
        groups: dict[str, dict] = {}
        for m in tf.getmembers():
            base, _, ext = m.name.partition(".")
            groups.setdefault(base, {})[ext] = tf.extractfile(m).read()
    for uuid in sorted(groups):
        g = groups[uuid]
        if not {"png", "trace.txt", "code.py"} <= set(g):
            continue
        samples[uuid] = {
            "png": g["png"],
            "code": g["code.py"].decode("utf-8", errors="replace"),
            "trace": g["trace.txt"].decode("utf-8", errors="replace").strip(),
        }
        order.append(uuid)
        if "step" in g:
            os.makedirs(GT_DIR, exist_ok=True)
            with open(os.path.join(GT_DIR, f"{uuid}.step"), "wb") as f:
                f.write(g["step"])
    with open(out + ".tmp", "wb") as f:
        pickle.dump({"samples": samples, "pools": {"certified": order}}, f)
    os.replace(out + ".tmp", out)
    print(f"[assets] eval cache: {len(order)} certified eval samples -> {out}")
    return order


def _mesh_one(uuid: str) -> tuple[str, bool, str]:
    stl = os.path.join(GT_DIR, f"{uuid}.stl")
    if os.path.exists(stl) and os.path.getsize(stl) > 0:
        return uuid, True, "cached"
    step = os.path.join(GT_DIR, f"{uuid}.step")
    try:
        from build123d import Mesher, import_step
        shape = import_step(step)
        m = Mesher()
        m.add_shape(shape, angular_deflection=0.5)
        m.write(stl)
        ok = os.path.exists(stl) and os.path.getsize(stl) > 0
        return uuid, ok, "" if ok else "empty"
    except Exception as e:
        return uuid, False, f"{type(e).__name__}: {str(e)[:80]}"


def build_gt_meshes(order: list[str], n_workers: int = 16):
    ok = 0
    failures = []
    with ProcessPoolExecutor(max_workers=n_workers) as ex:
        futs = {ex.submit(_mesh_one, u): u for u in order}
        for fut in as_completed(futs):
            uuid, success, msg = fut.result()
            if success:
                ok += 1
            else:
                failures.append((uuid, msg))
    with open(os.path.join(GT_DIR, "failed.txt"), "w") as f:
        for uuid, msg in failures:
            f.write(f"{uuid}\t{msg}\n")
    print(f"[assets] GT meshes: {ok}/{len(order)} ok, {len(failures)} failed")


if __name__ == "__main__":
    build_legacy_keys()
    order = build_eval_cache()
    build_gt_meshes(order)
    sys.exit(0)
