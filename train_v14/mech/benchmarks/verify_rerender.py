#!/usr/bin/env python3
"""Spot-check a re-rendered tar set against the original (RECIPE "Training sheets
re-rendered with draftwright 0.4.23"): for N random keys present in both, compare
PNG size / dimensions / aspect and the sidecars' dimension labels (same geometry
=> same annotation values), and extract the old/new PNG pairs for visual review.

    python verify_rerender.py --old <tars_v14> --new <tars_v14_dw423> --n 20 --out <dir> [--shards 50]
"""
import argparse
import glob
import io
import json
import os
import random
import tarfile

from PIL import Image


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--shards", type=int, default=50, help="only the first N completed new shards")
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    new_tars = sorted(glob.glob(os.path.join(a.new, "shard_*.tar")))[: a.shards]
    rng = random.Random(a.seed)
    picks = []
    for t in rng.sample(new_tars, min(len(new_tars), a.n)):
        side = json.load(open(t[:-4] + ".renderers.json"))
        picks.append((os.path.basename(t), rng.choice(sorted(side))))
    rows = []
    n_dims_same = n_labels_same = 0
    for shard, key in sorted(picks):
        rec = {"shard": shard, "key": key}
        for tag, root in (("old", a.old), ("new", a.new)):
            with tarfile.open(os.path.join(root, shard)) as tf:
                png = tf.extractfile(key + ".png").read()
                py = tf.extractfile(key + ".py").read()
            im = Image.open(io.BytesIO(png))
            rec[tag] = {"bytes": len(png), "size": im.size, "mode": im.mode,
                        "aspect": round(im.size[0] / im.size[1], 4), "code_sha": hash(py) & 0xFFFFFFFF}
            with open(os.path.join(a.out, f"{key}.{tag}.png"), "wb") as f:
                f.write(png)
            side = json.load(open(os.path.join(root, shard[:-4] + ".renderers.json"))).get(key, {})
            ann = side.get("annotations") or {}
            rec[tag]["labels"] = sorted(str(v.get("label")) for v in ann.values() if isinstance(v, dict))
            rec[tag]["dims_placed"] = sorted(side.get("dims_placed") or [])
            rec[tag]["dims_unplaced"] = sorted(side.get("dims_unplaced") or [])
            rec[tag]["renderer"] = side.get("renderer")
        rec["code_identical"] = rec["old"]["code_sha"] == rec["new"]["code_sha"]
        rec["same_size"] = rec["old"]["size"] == rec["new"]["size"]
        old_l, new_l = set(rec["old"]["labels"]), set(rec["new"]["labels"])
        rec["label_overlap"] = round(len(old_l & new_l) / max(len(old_l | new_l), 1), 3)
        rec["labels_only_old"] = sorted(old_l - new_l)
        rec["labels_only_new"] = sorted(new_l - old_l)
        n_dims_same += rec["old"]["dims_placed"] == rec["new"]["dims_placed"]
        n_labels_same += old_l == new_l
        rows.append(rec)
        print(f"{key}: code_identical={rec['code_identical']} size old {rec['old']['size']} new {rec['new']['size']} "
              f"bytes {rec['old']['bytes']}->{rec['new']['bytes']} placed {len(rec['old']['dims_placed'])}->{len(rec['new']['dims_placed'])} "
              f"unplaced {len(rec['old']['dims_unplaced'])}->{len(rec['new']['dims_unplaced'])} label overlap {rec['label_overlap']}"
              + (f" only_old={rec['labels_only_old']} only_new={rec['labels_only_new']}" if rec['label_overlap'] < 1 else ""))
    print(f"\n{len(rows)} pairs: identical code {sum(r['code_identical'] for r in rows)}, same PNG size "
          f"{sum(r['same_size'] for r in rows)}, identical placed-dim sets {n_dims_same}, identical label sets {n_labels_same}, "
          f"mean label overlap {sum(r['label_overlap'] for r in rows) / max(len(rows), 1):.3f}")
    json.dump(rows, open(os.path.join(a.out, "verify.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
