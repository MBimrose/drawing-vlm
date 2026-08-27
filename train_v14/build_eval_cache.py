"""One-time: build the validation-sample cache from shard sidecars.

Scanning tars blindly for val-hash samples is brutal (0.1% yield for the
pass-gated pool -> hundreds of GB of Lustre reads per rank). The
shard_XXXXXX.renderers.json sidecars list every key in a shard, so we can
locate the needed samples first and open only the tars that contain them.

Pools (each up to POOL_N keys, in shard order):
    pass — val-hash uuids with a gate-passing trace   (required/pass_only)
    any  — val-hash uuids with any trace              (required/any)
    all  — every val-hash uuid                        (optional / none)

Output: eval_cache_v14.pkl  {"pools": {name: [keys]},
                             "samples": {key: {"png": bytes, "code": str}}}
"""
import glob
import json
import os
import pickle
import sys
import tarfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_v14 import TARS_ROOT, is_val_uuid, trace_index, uuid_of_key

OUT = os.environ.get(
    "DRAWING_VLM_EVAL_CACHE",
    "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/step_to_drw/wds_dataset/eval_cache_v14.pkl",
)
POOL_N = 256


def main():
    idx = trace_index()
    pools = {"pass": [], "any": [], "all": []}
    by_shard: dict[str, set] = {}

    sidecars = sorted(glob.glob(os.path.join(TARS_ROOT, "shard_*.renderers.json")))
    print(f"[eval-cache] scanning {len(sidecars)} sidecars", flush=True)
    for sc in sidecars:
        if all(len(v) >= POOL_N for v in pools.values()):
            break
        try:
            with open(sc) as f:
                entries = json.load(f)
        except Exception:
            continue
        tar = sc[: -len(".renderers.json")] + ".tar"
        for key in sorted(entries):
            uuid = uuid_of_key(key)
            if not is_val_uuid(uuid):
                continue
            rec = idx.get(uuid)
            wanted = False
            if len(pools["all"]) < POOL_N:
                pools["all"].append(key)
                wanted = True
            if rec is not None and len(pools["any"]) < POOL_N:
                pools["any"].append(key)
                wanted = True
            if rec is not None and rec.get("p") is True and len(pools["pass"]) < POOL_N:
                pools["pass"].append(key)
                wanted = True
            if wanted:
                by_shard.setdefault(tar, set()).add(key)

    print(f"[eval-cache] pools: " + "  ".join(f"{k}={len(v)}" for k, v in pools.items())
          + f"  across {len(by_shard)} tars", flush=True)

    samples: dict[str, dict] = {}
    for i, (tar, keys) in enumerate(sorted(by_shard.items())):
        try:
            with tarfile.open(tar, "r") as tf:
                for m in tf.getmembers():
                    base, dot, ext = m.name.partition(".")
                    if base in keys:
                        data = tf.extractfile(m).read()  # type: ignore[union-attr]
                        s = samples.setdefault(base, {})
                        if ext == "png":
                            s["png"] = data
                        elif ext == "py":
                            s["code"] = data.decode("utf-8", errors="replace")
        except Exception as e:
            print(f"[eval-cache] skipping {tar}: {type(e).__name__}: {e}", flush=True)
        if (i + 1) % 25 == 0:
            print(f"[eval-cache] {i + 1}/{len(by_shard)} tars read", flush=True)

    # Drop incomplete samples from pools.
    complete = {k for k, v in samples.items() if "png" in v and "code" in v}
    pools = {name: [k for k in ks if k in complete] for name, ks in pools.items()}
    samples = {k: v for k, v in samples.items() if k in complete}

    with open(OUT + ".tmp", "wb") as f:
        pickle.dump({"pools": pools, "samples": samples}, f)
    os.replace(OUT + ".tmp", OUT)
    sz = os.path.getsize(OUT) / 1e6
    print(f"[eval-cache] wrote {len(samples)} samples ({sz:.0f} MB) -> {OUT}")
    print("[eval-cache] final pools: " + "  ".join(f"{k}={len(v)}" for k, v in pools.items()))


if __name__ == "__main__":
    main()
