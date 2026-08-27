"""Pack RFT accepted samples into webdataset shards.

Reads rft_v1/accepted-*.jsonl ({key, iou, think, code}), pulls each key's
drawing PNG from tars_v14 (single index pass over tar members), and writes
shards rft_v1/shards/rft-%05d.tar with members:

    <key>.png  <key>.code.py  <key>.think.txt  <key>.meta.json

The model's own verified reasoning (think) is kept — STaR-style, rationales
that produced iou>=0.8 parts are trusted. Dedup on key (temperature
sampling can't duplicate a key here, but resumed workers can).
"""
from __future__ import annotations

import glob
import io
import json
import os
import sys
import tarfile

DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
RFT = sys.argv[1] if len(sys.argv) > 1 else f"{DV}/rft_v1"
TARS = f"{DV}/step_to_drw/wds_dataset/tars_v14"
OUT = os.path.join(RFT, "shards")
PER_SHARD = 2000

accepted: dict[str, dict] = {}
for p in sorted(glob.glob(os.path.join(RFT, "accepted-*.jsonl"))):
    for line in open(p):
        try:
            r = json.loads(line)
            accepted[r["key"]] = r
        except Exception:
            continue
print(f"[pack] {len(accepted)} unique accepted samples", flush=True)

os.makedirs(OUT, exist_ok=True)
shard_idx = n_in_shard = n_written = 0
tf_out = None


def add(name: str, data: bytes):
    info = tarfile.TarInfo(name)
    info.size = len(data)
    tf_out.addfile(info, io.BytesIO(data))


def next_shard():
    global tf_out, shard_idx, n_in_shard
    if tf_out is not None:
        tf_out.close()
        shard_idx += 1
    tf_out = tarfile.open(os.path.join(OUT, f"rft-{shard_idx:05d}.tar"), "w")
    n_in_shard = 0


next_shard()
todo = set(accepted)
for sp in sorted(glob.glob(os.path.join(TARS, "shard_*.tar"))):
    if not todo:
        break
    try:
        tf = tarfile.open(sp)
    except Exception:
        continue
    names = tf.getnames()
    hit = [n for n in names if n.endswith(".png") and n[:-4] in todo]
    for png_name in hit:
        key = png_name[:-4]
        rec = accepted[key]
        try:
            png = tf.extractfile(png_name).read()
        except Exception:
            continue
        add(f"{key}.png", png)
        add(f"{key}.code.py", rec["code"].encode())
        add(f"{key}.think.txt", (rec.get("think") or "").encode())
        add(f"{key}.meta.json", json.dumps({"iou": rec["iou"]}).encode())
        todo.discard(key)
        n_in_shard += 1
        n_written += 1
        if n_in_shard >= PER_SHARD:
            next_shard()
    tf.close()
    if n_written and n_written % 10000 < PER_SHARD // 2:
        print(f"[pack] {n_written} written, {len(todo)} to find", flush=True)

tf_out.close()
print(f"[pack] DONE: {n_written} samples in {shard_idx + 1} shards, "
      f"{len(todo)} unfound", flush=True)
