"""Kimi-trace A/B (2026-10-29): sampling sets for each arm's own RFT tier, in the bench format gen_openai_bo.py and
score_partials.py read (eval_cache_v15.pkl {"pools": {"certified": keys}, "samples": {key: {"png": bytes}}} +
gt_meshes_v15/<key>.stl).

Synthetic parts: N training keys drawn uniformly (seed 29) from every key whose GT program the earlier RFT rounds
executed (rft_v1/v2/v3 gt_stl_cache: the training pool they streamed, solved or not, so the pick is not filtered by any
model's success), minus data_v14's training filters (exec-bad, legacy renderer, val residue 7, manifest-eval residue 0).
PNGs are the tars_v14_dw423 sheets the plain tier trains on; GT meshes are the cached STLs of the GT programs.
Split round-robin into NB benches of ~N/NB parts.

    python ab_build_benches.py --n 42000 --nb 8 --out /projects/illinois/eng/ece/wpk/bimrose2/srvmirror/amvlm/ab/syn
    round 2 (2026-10-31): --seed 31 --exclude <ab>/syn_s{0..7} --out <ab>/syn2   (42k parts disjoint from round 1)
"""
from __future__ import annotations

import argparse
import glob
import os
import pickle
import random
import shutil
import sys
import tarfile
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import data_v14 as dv  # noqa: E402

DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
CACHES = [f"{DV}/rft_v{i}/gt_stl_cache" for i in (3, 2, 1)]   # first hit wins


def scan(args):
    tp, want = args
    out = {}
    with tarfile.open(tp) as t:
        for m in t:
            b = os.path.basename(m.name)
            k, _, ext = b.partition(".")
            if ext == "png" and k in want:
                out[k] = t.extractfile(m).read()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=42000)
    ap.add_argument("--nb", type=int, default=8)
    ap.add_argument("--seed", type=int, default=29)
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--out", required=True)
    ap.add_argument("--exclude", nargs="*", default=[], help="bench dirs whose parts to leave out (round 2: a fresh set)")
    a = ap.parse_args()

    stl = {}
    for c in CACHES:
        for f in os.listdir(c):
            if f.endswith(".stl"):
                stl.setdefault(f[:-4], os.path.join(c, f))
    bad, legacy = dv.bad_keys(), dv.legacy_keys()
    pool = sorted(k for k, p in stl.items() if os.path.getsize(p) > 0 and k not in bad and k not in legacy
                  and not dv.is_val_uuid(dv.uuid_of_key(k)) and not dv.is_manifest_eval_uuid(dv.uuid_of_key(k)))
    print(f"[ab] {len(stl)} cached GT meshes, {len(pool)} pass the training filters", flush=True)
    if a.exclude:
        ex = {f[:-4] for d in a.exclude for f in os.listdir(f"{d}/gt_meshes_v15") if f.endswith(".stl")}
        pool = [k for k in pool if k not in ex]
        print(f"[ab] {len(pool)} after excluding {len(ex)} parts of {len(a.exclude)} benches", flush=True)
    keys = random.Random(a.seed).sample(pool, min(a.n + a.n // 20, len(pool)))   # 5% spare for keys with no sheet
    want = frozenset(keys)
    tars = dv.all_shards()
    png = {}
    with Pool(a.workers) as p:
        for i, d in enumerate(p.imap_unordered(scan, [(t, want) for t in tars], chunksize=4)):
            png.update(d)
            if i % 500 == 0:
                print(f"[ab] scanned {i}/{len(tars)} tars, {len(png)} sheets", flush=True)
    keys = [k for k in keys if k in png][: a.n]
    print(f"[ab] {len(keys)} parts with a sheet", flush=True)
    for b in range(a.nb):
        bk = keys[b::a.nb]
        d = f"{a.out}_s{b}"
        os.makedirs(f"{d}/gt_meshes_v15", exist_ok=True)
        for k in bk:
            shutil.copyfile(stl[k], f"{d}/gt_meshes_v15/{k}.stl")
        cache = {"pools": {"certified": bk, "all": bk}, "samples": {k: {"png": png[k], "code": "", "trace": ""} for k in bk}}
        with open(f"{d}/eval_cache_v15.pkl.tmp", "wb") as f:
            pickle.dump(cache, f)
        os.replace(f"{d}/eval_cache_v15.pkl.tmp", f"{d}/eval_cache_v15.pkl")
        print(f"[ab] bench {d}: {len(bk)} parts", flush=True)
    print("[ab] DONE", flush=True)


if __name__ == "__main__":
    main()
