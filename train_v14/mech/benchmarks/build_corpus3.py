#!/usr/bin/env python
"""Corpus 3: the CADBench EASY tiers of families F (Fusion 360), A (ABC) and E (ABC sketch-extrude),
`step` column only via HTTP range reads. Same layout/behaviour as build_corpus2.py: per shard the tiny
`label` column is read first and the shard is skipped when it has no wanted rows; rows whose `file_id`
is in --exclude (corpus-1 + corpus-2 keys + held-out bench) are dropped; STEPs are written as
<out>/src/<chunk>/<fam>_<file_id>_<label>.step in chunks of --chunk for parallel prep.
  python build_corpus3.py --out rft_corpus3 --exclude exclude_ids_corpus3.txt [--chunk 120]
Shard ranges from data/cadbench_tier_map.json (easy: F 0-6 (6 partial), A 0-10 (10 partial), E 0-9).
"""
import argparse, os, json, time, collections
import pyarrow.parquet as pq, fsspec
BASE = "https://huggingface.co/datasets/DeCoDELab/CADBench/resolve/main/data/"
TAG = "corpus3"
PLAN = {"F": ("bench0F", 20, list(range(0, 7)), {"easy"}),    # easy 0-5, 6 (100 easy + 50 hard)
        "A": ("bench1B", 31, list(range(0, 11)), {"easy"}),   # easy 0-9, 10 (30 easy + 67 hard)
        "E": ("bench1A", 30, list(range(0, 10)), {"easy"})}   # easy 0-9
ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--exclude", required=True)
ap.add_argument("--chunk", type=int, default=120); a = ap.parse_args()
excl = {l.strip() for l in open(a.exclude) if l.strip()}
fs = fsspec.filesystem("https"); stats = collections.Counter(); chunk_i = 0; in_chunk = 0; total_bytes = 0
def chunk_dir():
    d = os.path.join(a.out, "src", f"{chunk_i:03d}"); os.makedirs(d, exist_ok=True); return d
for fam, (pre, n, idxs, want) in PLAN.items():
    for i in idxs:
        name = f"{pre}-{i:05d}-of-{n:05d}.parquet"; t = time.time()
        try:
            with fs.open(BASE + name, "rb", block_size=4 << 20) as fh:
                pf = pq.ParquetFile(fh)
                labels = pf.read(columns=["label"]).column("label").to_pylist()
                if not any(l in want for l in labels):
                    stats[f"{fam}_shard_skipped_nowant"] += 1; print(f"[{TAG}] {name}: no {want} rows, skipped", flush=True); continue
                tb = pf.read(columns=["file_id", "label", "step"])
        except Exception as e:
            print(f"[{TAG}] {name} FAILED {e}", flush=True); stats[f"{fam}_shard_fail"] += 1; continue
        total_bytes += tb.nbytes
        for fid, lab, st in zip(tb.column("file_id").to_pylist(), tb.column("label").to_pylist(), tb.column("step").to_pylist()):
            if lab not in want: stats[f"{fam}_{lab}_skipped"] += 1; continue
            if fid in excl: stats[f"{fam}_excluded"] += 1; continue
            if in_chunk >= a.chunk: chunk_i += 1; in_chunk = 0
            with open(os.path.join(chunk_dir(), f"{fam}_{fid}_{lab}.step"), "wb") as f: f.write(st)
            in_chunk += 1; stats[f"{fam}_{lab}"] += 1
        print(f"[{TAG}] {name}: {tb.num_rows} rows {tb.nbytes/1e6:.0f} MB {time.time()-t:.0f}s labels={dict(collections.Counter(labels))}", flush=True)
stats["total_MB"] = int(total_bytes / 1e6); stats["chunks"] = chunk_i + 1
json.dump(dict(stats), open(os.path.join(a.out, "download_stats.json"), "w"), indent=1); print(f"[{TAG}] done", dict(stats), flush=True)
