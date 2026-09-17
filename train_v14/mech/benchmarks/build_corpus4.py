"""Stage 1a of real corpus 4: every CADBench part with a STEP body that no earlier corpus or
bench has used (corpora 1-3, abccode, the held-out ext benches), all labels, all six subsets.
Exclusion = file_ids found in any data/*/manifest.json key (<FAM>_<file_id>_<label>), so the
146 held-out bench parts stay held out. STEPs land in <out>/src/<chunk>/<fam>_<file_id>_<label>.step.
    python build_corpus4.py --out train_v14/mech/benchmarks/data/rft_corpus4 --inventory data/cadbench_inventory/rows.json
"""
import argparse, collections, glob, json, os, re, time
import fsspec, pyarrow.parquet as pq
BASE = "https://huggingface.co/datasets/DeCoDELab/CADBench/resolve/main/"
FAM = {"bench0": "B", "bench0F": "F", "bench1A": "E", "bench1B": "A", "bench2": "M", "bench3": "O"}   # DeepCAD, Fusion, ?, ABC, MCB, Objaverse
ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--inventory", required=True)
ap.add_argument("--data-root", default="train_v14/mech/benchmarks/data"); ap.add_argument("--chunk", type=int, default=250)
a = ap.parse_args()
used = set()
for m in glob.glob(os.path.join(a.data_root, "*", "manifest.json")):
    if os.path.abspath(os.path.dirname(m)) == os.path.abspath(a.out): continue
    try: parts = json.load(open(m)).get("parts", {})
    except Exception: continue
    for k in (parts if isinstance(parts, dict) else []):
        mm = re.match(r"^[A-Z]_(.+)_(easy|medium|hard|code|x)$", k)
        if mm: used.add(mm.group(1))
rows = json.load(open(a.inventory)); files = sorted({r["_file"] for r in rows})
print(f"[corpus4] {len(used)} used file_ids excluded; {len(files)} parquet files", flush=True)
fs = fsspec.filesystem("https"); stats = collections.Counter(); chunk_i = 0; in_chunk = 0
os.makedirs(a.out, exist_ok=True); done_f = os.path.join(a.out, "download_done.txt")
done = set(open(done_f).read().split()) if os.path.exists(done_f) else set()
if done: chunk_i = len(glob.glob(os.path.join(a.out, "src", "*")))
for f in files:
    if f in done: continue
    pre = re.sub(r"-\d+-of-\d+\.parquet$", "", f.split("/")[-1]); fam = FAM.get(pre, "X"); t = time.time()
    try:
        with fs.open(BASE + f, "rb", block_size=8 << 20) as fh:
            tb = pq.ParquetFile(fh).read(columns=["file_id", "label", "step"])
    except Exception as e:
        print(f"[corpus4] {f} FAILED {type(e).__name__}: {str(e)[:100]}", flush=True); stats[f"{fam}_shard_fail"] += 1; continue
    for fid, lab, st in zip(tb.column("file_id").to_pylist(), tb.column("label").to_pylist(), tb.column("step").to_pylist()):
        fid = str(fid); lab = lab or "x"
        if fid in used: stats[f"{fam}_excluded"] += 1; continue
        if not st or len(st) < 200: stats[f"{fam}_nostep"] += 1; continue
        if in_chunk >= a.chunk: chunk_i += 1; in_chunk = 0
        d = os.path.join(a.out, "src", f"{chunk_i:03d}"); os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, f"{fam}_{fid}_{lab}.step"), "wb") as fo: fo.write(st if isinstance(st, bytes) else st.encode())
        in_chunk += 1; stats[f"{fam}_{lab}"] += 1
    open(done_f, "a").write(f + "\n")
    print(f"[corpus4] {f}: {tb.num_rows} rows {time.time()-t:.0f}s  kept so far {sum(v for k, v in stats.items() if k.split('_')[-1] in ('easy','medium','hard','x'))}", flush=True)
stats["chunks"] = chunk_i + 1
json.dump(dict(stats), open(os.path.join(a.out, "download_stats.json"), "w"), indent=1)
print("[corpus4] DOWNLOAD DONE", dict(stats), flush=True)
