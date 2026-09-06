"""Pack REAL-PART verifier training data: every scored candidate from the
real-geometry corpus passes (best-of-N JSONs from bestofn_verifier_eval /
merge_bo_shards and scored-*.jsonl from gt_feedback_gen) with its drawing PNG
into the exact member layout build_verifier_dataset expects (see
pack_scored_shards.py):

    <key>-s<j>.png  <key>-s<j>.code.py  <key>-s<j>.meta.json({iou, exec})
    scored-train-NNNNNN.tar / scored-eval-NNNNNN.tar   (~2% of PARTS in eval)

Differences from pack_scored_shards.py: PNGs come from directories
(<png_dir>/<key>.png or <key>_v<N>.png, the sheet variant the corpus was
rendered with) rather than the synthetic tars_v14 shards; parts whose file_id
is in the held-out external bench are excluded; candidates without code are
dropped; execution failures kept with iou=0. Duplicate scripts per part
(e.g. the greedy draw repeated across passes) are packed once.

    python pack_scored_real.py --out rft_scored_real/shards \
        --png <dir> [--png <dir> ...] \
        --src <bo_json_or_scored_dir> [--src ...] \
        [--heldout heldout_file_ids.txt] [--pos-threshold 0.85 --pos-max 0.4]
        [--neg-keep 1.0]

--pos-max: if the share of candidates with iou >= --pos-threshold exceeds
this, positives are subsampled down to it (v1 collapsed on a positives-heavy
pool). --neg-keep: keep this fraction of NON-executing candidates (1.0 = all).
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import io
import json
import os
import random
import re
import tarfile

PER_SHARD = 4000


def file_id(key: str) -> str:
    """'A_00917205_..._step_001_medium' -> '00917205_..._step_001' (drop family
    prefix and tier suffix; matches heldout_file_ids.txt)."""
    fam, rest = key.split("_", 1)
    return rest.rsplit("_", 1)[0]


def is_eval(key: str) -> bool:
    return int(hashlib.md5(key.encode()).hexdigest(), 16) % 50 == 1


def load_source(path: str) -> list[dict]:
    rows = []
    if os.path.isdir(path):
        for p in sorted(glob.glob(os.path.join(path, "scored-*.jsonl"))):
            for line in open(p):
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                rows.append({"key": r["key"], "code": r.get("code") or "",
                             "exec": bool(r.get("exec", False)), "iou": float(r.get("iou") or 0.0),
                             "src": os.path.basename(path.rstrip("/"))})
    else:
        d = json.load(open(path))
        tag = os.path.basename(path).replace(".json", "")
        for part in d["candidates"]:
            for c in part["cands"]:
                rows.append({"key": part["key"], "code": c.get("code") or "",
                             "exec": bool(c.get("exec", False)), "iou": float(c.get("iou") or 0.0),
                             "src": tag})
    return rows


class Writer:
    def __init__(self, out, split):
        self.out, self.split, self.idx, self.n, self.tf, self.total = out, split, -1, 0, None, 0
        self._next()

    def _next(self):
        if self.tf:
            self.tf.close()
        self.idx += 1
        self.n = 0
        self.tf = tarfile.open(os.path.join(self.out, f"scored-{self.split}-{self.idx:06d}.tar"), "w")

    def add(self, name, data: bytes):
        ti = tarfile.TarInfo(name); ti.size = len(data)
        self.tf.addfile(ti, io.BytesIO(data))

    def sample(self, base, png, rec):
        self.add(f"{base}.png", png)
        self.add(f"{base}.code.py", rec["code"].encode())
        self.add(f"{base}.meta.json", json.dumps(
            {"iou": float(rec["iou"]), "exec": bool(rec["exec"])}).encode())
        self.n += 1; self.total += 1
        if self.n >= PER_SHARD:
            self._next()

    def close(self):
        self.tf.close()
        if self.n == 0:   # drop the trailing empty shard
            os.remove(os.path.join(self.out, f"scored-{self.split}-{self.idx:06d}.tar"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--png", action="append", default=[], help="PNG directory (repeatable)")
    ap.add_argument("--src", action="append", default=[], help="best-of-N JSON or dir of scored-*.jsonl (repeatable)")
    ap.add_argument("--heldout", default="")
    ap.add_argument("--pos-threshold", type=float, default=0.85)
    ap.add_argument("--pos-max", type=float, default=0.40)
    ap.add_argument("--neg-keep", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    os.makedirs(args.out, exist_ok=True)

    # --- PNG index: key -> path (first dir wins; <key>.png or <key>_v<N>.png)
    pngs: dict[str, str] = {}
    pat = re.compile(r"^(.*?)(?:_v\d+)?\.png$")
    for d in args.png:
        for f in sorted(os.listdir(d)):
            m = pat.match(f)
            if m:
                pngs.setdefault(m.group(1), os.path.join(d, f))
    print(f"[pack-real] {len(pngs)} drawings indexed from {len(args.png)} dirs", flush=True)

    held = set(l.strip() for l in open(args.heldout)) if args.heldout else set()

    # --- collect candidates, dedup by code per key
    cands: dict[str, list] = {}
    stats = {"rows": 0, "no_code": 0, "heldout": 0, "no_png": 0, "dup": 0}
    per_src: dict[str, int] = {}
    for s in args.src:
        rows = load_source(s)
        print(f"[pack-real] {s}: {len(rows)} rows", flush=True)
        for r in rows:
            stats["rows"] += 1
            if not r["code"]:
                stats["no_code"] += 1; continue
            if file_id(r["key"]) in held:
                stats["heldout"] += 1; continue
            if r["key"] not in pngs:
                stats["no_png"] += 1; continue
            lst = cands.setdefault(r["key"], [])
            if any(x["code"] == r["code"] for x in lst):
                stats["dup"] += 1; continue
            lst.append(r)
            per_src[r["src"]] = per_src.get(r["src"], 0) + 1
    n_all = sum(map(len, cands.values()))
    print(f"[pack-real] {n_all} distinct candidates over {len(cands)} parts; {stats}", flush=True)
    print(f"[pack-real] per source (after dedup): {json.dumps(per_src, indent=1)}", flush=True)
    if stats["heldout"]:
        print(f"[pack-real] WARNING: {stats['heldout']} rows were on held-out parts and were excluded", flush=True)

    # --- label balance and optional rebalancing
    def balance(tag):
        allc = [c for v in cands.values() for c in v]
        n = len(allc)
        ex = sum(c["exec"] for c in allc)
        p80 = sum(c["iou"] >= 0.8 for c in allc)
        pth = sum(c["iou"] >= args.pos_threshold for c in allc)
        print(f"[pack-real] {tag}: n={n} exec={ex/n:.3f} iou>=0.8={p80/n:.3f} "
              f"iou>={args.pos_threshold}={pth/n:.3f} parts_with_pos={sum(any(c['iou']>=args.pos_threshold for c in v) for v in cands.values())}",
              flush=True)
        return pth / n
    share = balance("balance before rebalancing")
    if args.neg_keep < 1.0:
        for k in list(cands):
            cands[k] = [c for c in cands[k] if c["exec"] or rng.random() < args.neg_keep]
        balance(f"after dropping non-executing at keep={args.neg_keep}")
        share = sum(c["iou"] >= args.pos_threshold for v in cands.values() for c in v) / \
            max(1, sum(map(len, cands.values())))
    if share > args.pos_max:
        keep = args.pos_max * (1 - share) / (share * (1 - args.pos_max))
        print(f"[pack-real] positives {share:.3f} > {args.pos_max}: keeping {keep:.3f} of them", flush=True)
        for k in list(cands):
            cands[k] = [c for c in cands[k] if c["iou"] < args.pos_threshold or rng.random() < keep]
        balance("after positive subsampling")
    cands = {k: v for k, v in cands.items() if v}

    # --- write shards (eval split by part hash, PNG cached per key)
    w = {"train": Writer(args.out, "train"), "eval": Writer(args.out, "eval")}
    n_parts = {"train": 0, "eval": 0}
    for key in sorted(cands):
        png = open(pngs[key], "rb").read()
        split = "eval" if is_eval(key) else "train"
        n_parts[split] += 1
        for j, r in enumerate(cands[key]):
            w[split].sample(f"{key}-s{j}", png, r)
    for x in w.values():
        x.close()
    print(f"[pack-real] DONE train={w['train'].total} ({n_parts['train']} parts) "
          f"eval={w['eval'].total} ({n_parts['eval']} parts) -> {args.out}", flush=True)
    json.dump({"train": w["train"].total, "eval": w["eval"].total, "parts": n_parts,
               "sources": per_src, "stats": stats, "pos_threshold": args.pos_threshold},
              open(os.path.join(args.out, "pack_stats.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
