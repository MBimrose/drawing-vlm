"""Pack RFT accepted samples whose drawings live in a PNG directory (not in the
tars_v14 shards) into webdataset shards with the same member layout as
pack_rft_shards.py:

    <key>.png  <key>.code.py  <key>.think.txt  <key>.meta.json

    python pack_rft_shards_dir.py <rft_dir> [<png_dir>] [--repeat N]

<rft_dir>/accepted-*.jsonl rows: {key, iou, think, code}. PNGs at
<png_dir>/<key>.png (default <rft_dir>/png). --repeat N writes every sample N
times (distinct member keys <key>__rK) so a small tier is oversampled by the
shard-level mixer without touching data_v14.py.
"""
from __future__ import annotations

import glob
import io
import json
import os
import sys
import tarfile

args = [a for a in sys.argv[1:] if not a.startswith("--")]
RFT = args[0]
PNG = args[1] if len(args) > 1 else os.path.join(RFT, "png")
REPEAT = int(sys.argv[sys.argv.index("--repeat") + 1]) if "--repeat" in sys.argv else 1
OUT = os.path.join(RFT, "shards")
PER_SHARD = 2000
os.makedirs(OUT, exist_ok=True)

accepted: dict[str, list] = {}
for p in sorted(glob.glob(os.path.join(RFT, "accepted-*.jsonl"))):
    for line in open(p):
        try:
            r = json.loads(line)
        except Exception:
            continue
        if not r.get("code"):
            continue
        lst = accepted.setdefault(r["key"], [])
        if all(x["code"] != r["code"] for x in lst):
            lst.append(r)
print(f"[pack] {len(accepted)} keys, {sum(len(v) for v in accepted.values())} distinct accepted samples, repeat={REPEAT}", flush=True)


def add(tf, name, data: bytes):
    info = tarfile.TarInfo(name)
    info.size = len(data)
    tf.addfile(info, io.BytesIO(data))


shard_idx, n_in_shard, written, missing = 0, 0, 0, 0
tf_out = tarfile.open(os.path.join(OUT, f"rft-{shard_idx:05d}.tar"), "w")
for key, recs in accepted.items():
    png_path = os.path.join(PNG, f"{key}.png")
    if not os.path.exists(png_path):
        missing += 1
        continue
    png = open(png_path, "rb").read()
    for i, rec in enumerate(recs):
        for rep in range(REPEAT):
            k = key if (i == 0 and rep == 0) else f"{key}__s{i}r{rep}"
            add(tf_out, f"{k}.png", png)
            add(tf_out, f"{k}.code.py", rec["code"].encode())
            add(tf_out, f"{k}.think.txt", (rec.get("think") or "").encode())
            add(tf_out, f"{k}.meta.json", json.dumps({"iou": rec.get("iou"), "src_key": key,
                                                       "sample": i, "repeat": rep}).encode())
            written += 1
            n_in_shard += 1
            if n_in_shard >= PER_SHARD:
                tf_out.close(); shard_idx += 1; n_in_shard = 0
                tf_out = tarfile.open(os.path.join(OUT, f"rft-{shard_idx:05d}.tar"), "w")
tf_out.close()
print(f"[pack] wrote {written} members into {shard_idx + 1} shards under {OUT}; {missing} keys had no PNG", flush=True)
