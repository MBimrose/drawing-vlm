#!/usr/bin/env python
"""Corpus 2: CADBench benchB (DeepCAD) medium+hard and the F/A/E hard tiers, `step` column only via
HTTP range reads. Per shard the tiny `label` column is read first and the shard is skipped when it has
no medium/hard rows. Excludes file_ids in --exclude (corpus-1 keys + held-out bench).
  python build_corpus2.py --out rft_corpus2 --exclude exclude_ids_corpus2.txt [--chunk 120]
"""
import argparse, os, json, time, collections
import pyarrow.parquet as pq, fsspec
BASE = "https://huggingface.co/datasets/DeCoDELab/CADBench/resolve/main/data/"
PLAN = {"B": ("bench0", 18, list(range(18)), {"medium", "hard"}),      # DeepCAD: tiers unknown -> scan labels
        "F": ("bench0F", 20, list(range(6, 14)), {"hard"}),            # hard 6(partial)-13(partial)
        "A": ("bench1B", 31, list(range(10, 21)), {"hard"}),           # hard 10(partial)-20(partial)
        "E": ("bench1A", 30, list(range(10, 20)), {"hard"})}           # hard 10-19
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
                    stats[f"{fam}_shard_skipped_easy"] += 1; print(f"[corpus2] {name}: no {want} rows, skipped", flush=True); continue
                tb = pf.read(columns=["file_id", "label", "step"])
        except Exception as e:
            print(f"[corpus2] {name} FAILED {e}", flush=True); stats[f"{fam}_shard_fail"] += 1; continue
        total_bytes += tb.nbytes
        for fid, lab, st in zip(tb.column("file_id").to_pylist(), tb.column("label").to_pylist(), tb.column("step").to_pylist()):
            if lab not in want: stats[f"{fam}_{lab}_skipped"] += 1; continue
            if fid in excl: stats[f"{fam}_excluded"] += 1; continue
            if in_chunk >= a.chunk: chunk_i += 1; in_chunk = 0
            with open(os.path.join(chunk_dir(), f"{fam}_{fid}_{lab}.step"), "wb") as f: f.write(st)
            in_chunk += 1; stats[f"{fam}_{lab}"] += 1
        print(f"[corpus2] {name}: {tb.num_rows} rows {tb.nbytes/1e6:.0f} MB {time.time()-t:.0f}s labels={dict(collections.Counter(labels))}", flush=True)
stats["total_MB"] = int(total_bytes / 1e6); stats["chunks"] = chunk_i + 1
json.dump(dict(stats), open(os.path.join(a.out, "download_stats.json"), "w"), indent=1); print("[corpus2] done", dict(stats), flush=True)
