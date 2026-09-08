#!/usr/bin/env python3
"""Render external STEP parts into the v14 draftwright sheet format by calling
worker_v11._process_one_part exactly as the v14 dataset workers do (VLM_MODE=1:
one variant per part, 1920x1280 PNG, same timeouts / precompute / variant specs).
No tar, no sqlite, no GPU. Output: <out>/png/<key>_v<N>.png + <out>/renderers.json
(the same sidecar schema as tars_v14/*.renderers.json: dims_placed/dims_unplaced/...).

  SCRIPT_DIR=.../step_to_drw <python: /software/python-3.11.1/bin/python3 (draftwright 0.4.0+patch)
      or /srv/scratch/bimrose2/dw_venv/bin/python (0.4.23+patch)> render_ext.py \
      --src <dir of *.step> [--src ...] --out <dir> --workers 32 [--limit N]
"""
import os, sys, glob, json, time, zlib, hashlib, argparse, concurrent.futures
ROOT = os.environ.get("SCRIPT_DIR", "/srv/scratch/bimrose2/mech_benchmarks/step_to_drw")
os.environ["SCRIPT_DIR"] = ROOT
os.environ["VLM_MODE"] = "1"
for k, v in (("OMP_NUM_THREADS", "2"), ("TBB_NUM_THREADS", "2"), ("MKL_NUM_THREADS", "1"), ("OPENBLAS_NUM_THREADS", "1")):
    os.environ.setdefault(k, v)
_CWD = os.getcwd()
sys.path.insert(0, ROOT)
os.chdir(ROOT)
try:  # worker_v11 imports sqlite3 for its dataset db; a venv on a python built without _sqlite3
    import sqlite3  # noqa: F401   (dw_venv on serv-19) only needs the import to succeed
except ImportError:
    import types
    sys.modules["sqlite3"] = types.ModuleType("sqlite3")
import worker_v11 as w  # noqa: E402  (module import only builds variant specs)


def _run(args):
    return w._process_one_part(args)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    a.src = [os.path.join(_CWD, s) for s in a.src]
    a.out = os.path.join(_CWD, a.out)
    files = sorted(f for s in a.src for f in glob.glob(os.path.join(s, "*.step")))
    if a.limit:
        files = files[: a.limit]
    png_dir = os.path.join(a.out, "png")
    os.makedirs(png_dir, exist_ok=True)
    side_path = os.path.join(a.out, "renderers.json")
    sidecar = json.load(open(side_path)) if os.path.exists(side_path) else {}
    done = {k.rsplit("_v", 1)[0] for k in sidecar}
    todo = [f for f in files if os.path.splitext(os.path.basename(f))[0] not in done]
    print(f"[render] {len(files)} parts, {len(todo)} to do, workers={a.workers}", flush=True)
    t0 = time.time()
    fails = {}
    pool = concurrent.futures.ProcessPoolExecutor(max_workers=a.workers)
    futs = {}
    for f in todo:
        key = os.path.splitext(os.path.basename(f))[0]
        step_bytes = open(f, "rb").read()
        seed = zlib.crc32(key.encode()) % (2 ** 31)  # worker uses hash(uuid); crc32 for determinism
        ruuid = hashlib.md5(key.encode()).hexdigest()  # renderer needs a hex uuid (int(uuid[:8],16))
        args = (step_bytes, None, ruuid, w._variant_specs, seed, w.PNG_WIDTH, w.PNG_HEIGHT,
                w._PRECOMPUTE_VIEWS, w._HLR_TIMEOUT_PER_VIEW, w._DRAWING_TIMEOUT, ROOT)
        futs[pool.submit(_run, args)] = key
    n = 0
    try:
        for fut in concurrent.futures.as_completed(futs, timeout=None):
            key = futs[fut]
            n += 1
            try:
                r = fut.result(timeout=w._PART_TIMEOUT + 60)
            except Exception as e:  # BrokenProcessPool / timeout
                fails[key] = f"{type(e).__name__}: {str(e)[:80]}"
                continue
            if not r["examples"]:
                fails[key] = "no_variant"
            for (_, png, _, vi) in r["examples"]:
                with open(os.path.join(png_dir, f"{key}_v{vi+1}.png"), "wb") as fh:
                    fh.write(png)
                meta = dict((r.get("render_meta") or {}).get(vi, {}))
                meta["render_uuid"] = hashlib.md5(key.encode()).hexdigest()
                sidecar[f"{key}_v{vi+1}"] = meta
            if n % 10 == 0 or n == len(todo):
                json.dump(sidecar, open(side_path, "w"), indent=1, sort_keys=True)
                print(f"[render] {n}/{len(todo)} ok={len(sidecar)} fail={len(fails)} {time.time()-t0:.0f}s", flush=True)
    finally:
        json.dump(sidecar, open(side_path, "w"), indent=1, sort_keys=True)
        json.dump(fails, open(os.path.join(a.out, "failures.json"), "w"), indent=1)
        for p in getattr(pool, "_processes", {}).values():
            try:
                p.kill()
            except Exception:
                pass
        pool.shutdown(wait=False)
    print(f"[render] done ok={len(sidecar)} fail={len(fails)} in {time.time()-t0:.0f}s -> {a.out}", flush=True)


if __name__ == "__main__":
    main()
