"""Kimi-trace A/B (2026-10-29): pack an arm's own verified samples into its RFT tier and build the round-1 mix.

Inputs: the scored jobs (score_partials.py JSON: candidates [{key, cands: [{draw, code, think, exec, iou}]}]) and their
benches (eval_cache_v15.pkl for the sheets). Acceptance as the 27B's tiers: synthetic jobs (syn_*) keep iou >= 0.9 like
rft_strict90 (up to 2 distinct programs per part), real jobs keep iou >= 0.8 like rft_real_union5 (up to 5). Members as
pack_rft_shards.py: <key>[-s<i>].png / .code.py / .think.txt / .meta.json, 2,000 per shard.

The mix replicates e55's rft_mix_u6_gt_dw423 layout with this arm's rows in place of the Qwen ones: the synthetic tier
x1, the real tier x5, and the model-free ABC ground-truth-code tier (rft_real_abccode_train, empty think) x8, as relative
symlinks so the same dir works on the cluster mirror and on serv-19.

    python ab_pack_tier.py --arm a --scored <dir> --jobs <amvlm/ab/jobs.txt> --root <amvlm/ab dir> --abc <abc shards dir>

Round 2 (2026-10-31): several --scored dirs with their --jobs files (same order); a part's candidates from every round
are pooled before the threshold, distinct-code and per-part cap, so round 1's accepted programs stay in the tier.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import pickle
import tarfile

PER_SHARD = 2000


def write_tier(rows, out):
    os.makedirs(out, exist_ok=True)
    n = 0
    tf = None
    for i, (name, png, rec) in enumerate(rows):
        if i % PER_SHARD == 0:
            if tf:
                tf.close()
            tf = tarfile.open(os.path.join(out, f"rft-{i // PER_SHARD:05d}.tar"), "w")
        for ext, data in (("png", png), ("code.py", rec["code"].encode()), ("think.txt", rec["think"].encode()),
                          ("meta.json", json.dumps({"iou": rec["iou"], "draw": rec["draw"]}).encode())):
            info = tarfile.TarInfo(f"{name}.{ext}")
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
        n += 1
    if tf:
        tf.close()
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True)
    ap.add_argument("--scored", nargs="+", required=True)
    ap.add_argument("--jobs", nargs="+", required=True)
    ap.add_argument("--root", required=True, help="amvlm/ab on this host (benches are <root>/.. relative paths)")
    ap.add_argument("--srv", default="/projects/illinois/eng/ece/wpk/bimrose2/srvmirror", help="this host's /srv/scratch/bimrose2")
    ap.add_argument("--abc", required=True)
    a = ap.parse_args()
    assert len(a.scored) == len(a.jobs), "one --jobs file per --scored dir"
    tiers = {"syn": [], "real": []}
    stats = {}
    pooled = {}   # (kind, key) -> [png, cands from every round]
    for rnd, (sdir, jobs) in enumerate(zip(a.scored, a.jobs)):
        for line in open(jobs):
            if not line.strip():
                continue
            name, bench = line.split()[:2]
            kind = "syn" if name.startswith("syn") else "real"
            sc = json.load(open(os.path.join(sdir, f"{name}.json")))["candidates"]
            cache = pickle.load(open(os.path.join(a.srv, bench, "eval_cache_v15.pkl"), "rb"))["samples"]
            for r in sc:
                pooled.setdefault((kind, r["key"]), [cache[r["key"]]["png"], []])[1].extend(r["cands"])
            stats[f"r{rnd}_{name}" if rnd else name] = {"parts": len(sc), "cands": sum(len(r["cands"]) for r in sc)}
    for kind in ("syn", "real"):
        thr, cap = (0.9, 2) if kind == "syn" else (0.8, 5)
        n_parts = n_acc = n_all = 0
        for (k_, key), (png, cands) in pooled.items():
            if k_ != kind:
                continue
            n_all += 1
            keep = []
            for c in sorted(cands, key=lambda c: -(c.get("iou") or 0)):
                if (c.get("iou") or 0) >= thr and c.get("code") and all(k["code"] != c["code"] for k in keep):
                    keep.append({"code": c["code"], "think": (c.get("think") or "").strip(), "iou": c["iou"], "draw": c["draw"]})
            keep = keep[:cap]
            n_parts += bool(keep)
            for i, rec in enumerate(keep):
                tiers[kind].append((key if i == 0 else f"{key}-s{i}", png, rec))
                n_acc += 1
        stats[f"{kind}_pooled"] = {"parts": n_all, "parts_accepted": n_parts, "rows": n_acc}
        print(f"[pack] {kind}: {n_parts}/{n_all} parts, {n_acc} rows (iou >= {thr}, <= {cap} per part)", flush=True)
    T = os.path.join(a.root, f"tier_{a.arm}")
    counts = {k: write_tier(v, os.path.join(T, k)) for k, v in tiers.items()}
    think = sum(bool(rec["think"]) for v in tiers.values() for _, _, rec in v)
    mix = os.path.join(T, "mix")
    os.makedirs(mix, exist_ok=True)
    j = 0
    abc = sorted(os.path.join(a.abc, f) for f in os.listdir(a.abc) if f.endswith(".tar"))
    srcs = [os.path.join(T, "syn", f) for f in sorted(os.listdir(os.path.join(T, "syn")))]
    srcs += [os.path.join(T, "real", f) for f in sorted(os.listdir(os.path.join(T, "real")))] * 5 + abc * 8
    for s in srcs:
        os.symlink(os.path.relpath(s, mix), os.path.join(mix, f"rft-{j:05d}.tar"))
        j += 1
    summary = {"arm": a.arm, "jobs": stats, "rows": counts, "rows_with_think": think, "mix_shards": j}
    json.dump(summary, open(os.path.join(T, "summary.json"), "w"), indent=1)
    print(f"[pack] DONE {json.dumps(summary)}", flush=True)


if __name__ == "__main__":
    main()
