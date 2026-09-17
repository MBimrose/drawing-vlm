"""List every CADBench row (file_id, label, parquet file) without downloading the STEP column,
so new real-part corpora can exclude what corpora 1-3 / abccode / the held-out bench already used.
    python cadbench_inventory.py --out data/cadbench_inventory/rows.json
"""
import argparse, collections, json, time, urllib.request
import fsspec, pyarrow.parquet as pq
ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args()
r = json.load(urllib.request.urlopen("https://huggingface.co/api/datasets/DeCoDELab/CADBench/tree/main/data"))
files = sorted(x["path"] for x in r if x["path"].endswith(".parquet"))
print(len(files), "parquet files; e.g.", files[:2], flush=True)
fs = fsspec.filesystem("https"); rows = []; t0 = time.time()
for i, f in enumerate(files):
    url = "https://huggingface.co/datasets/DeCoDELab/CADBench/resolve/main/" + f
    try:
        with fs.open(url, "rb") as fh:
            pf = pq.ParquetFile(fh)
            if i == 0: print("schema:", pf.schema.names, flush=True)
            cols = [c for c in ("file_id", "label", "split", "family", "source") if c in pf.schema.names]
            for rec in pf.read(columns=cols).to_pylist():
                rec["_file"] = f; rows.append(rec)
    except Exception as e:
        print("skip", f, type(e).__name__, str(e)[:80], flush=True)
    if i % 10 == 0:
        print(f"{i}/{len(files)} files, {len(rows)} rows, {time.time()-t0:.0f}s", flush=True)
        json.dump(rows, open(a.out, "w"))
json.dump(rows, open(a.out, "w"))
print("INVENTORY DONE rows", len(rows), "labels", collections.Counter(x.get("label") for x in rows).most_common(8), flush=True)
