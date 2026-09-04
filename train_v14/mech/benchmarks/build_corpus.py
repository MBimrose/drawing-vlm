#!/usr/bin/env python
"""Stage 1a of the real-geometry RFT corpus: pull the `step` column of CADBench
shards by HTTP range reads (no images), skip held-out file_ids, write
<out>/src/<chunk>/<fam>_<file_id>_<label>.step in chunks for parallel prep.
  python build_corpus.py --out rft_corpus --exclude heldout_file_ids.txt [--chunk 120]
"""
import argparse, os, json, time, collections
import pyarrow.parquet as pq, fsspec
BASE = "https://huggingface.co/datasets/DeCoDELab/CADBench/resolve/main/data/"
# family -> (parquet prefix, n shards, shard indices to pull)  [tiers from data/cadbench_tier_map.json]
PLAN = {"F": ("bench0F", 20, list(range(13, 20)) + list(range(7, 13))),   # medium 13-19, hard 7-12
        "A": ("bench1B", 31, list(range(20, 31))),                          # medium 20-30 (hard passes 0%)
        "E": ("bench1A", 30, list(range(20, 30)) + list(range(10, 20)))}   # medium 20-29, hard 10-19
ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--exclude", required=True)
ap.add_argument("--chunk", type=int, default=120); a = ap.parse_args()
excl = {l.strip() for l in open(a.exclude) if l.strip()}
fs = fsspec.filesystem("https"); stats = collections.Counter(); chunk_i = 0; in_chunk = 0; total_bytes = 0
def chunk_dir():
    d = os.path.join(a.out, "src", f"{chunk_i:03d}"); os.makedirs(d, exist_ok=True); return d
for fam, (pre, n, idxs) in PLAN.items():
    for i in idxs:
        name = f"{pre}-{i:05d}-of-{n:05d}.parquet"; t = time.time()
        try:
            with fs.open(BASE + name, "rb", block_size=4 << 20) as fh:
                tb = pq.ParquetFile(fh).read(columns=["file_id", "label", "step"])
        except Exception as e:
            print(f"[corpus] {name} FAILED {e}", flush=True); stats[f"{fam}_shard_fail"] += 1; continue
        total_bytes += tb.nbytes
        for fid, lab, st in zip(tb.column("file_id").to_pylist(), tb.column("label").to_pylist(), tb.column("step").to_pylist()):
            if fid in excl:
                stats[f"{fam}_heldout_skipped"] += 1; continue
            if in_chunk >= a.chunk:
                chunk_i += 1; in_chunk = 0
            with open(os.path.join(chunk_dir(), f"{fam}_{fid}_{lab}.step"), "wb") as f:
                f.write(st)
            in_chunk += 1; stats[f"{fam}_{lab}"] += 1
        print(f"[corpus] {name}: {tb.num_rows} rows {tb.nbytes/1e6:.0f} MB {time.time()-t:.0f}s", flush=True)
stats["total_MB"] = int(total_bytes / 1e6); stats["chunks"] = chunk_i + 1
json.dump(dict(stats), open(os.path.join(a.out, "download_stats.json"), "w"), indent=1)
print("[corpus] done", dict(stats), flush=True)
