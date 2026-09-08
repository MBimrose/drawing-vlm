#!/usr/bin/env python3
"""Re-render sheets with another draftwright build, keeping member names.

Two modes (serv-19 paths by default; stdlib only, run with any python3):

  tars  — every tars_v14/shard_XXXXXX.tar: each {uuid}_v{N}.py is executed to STEP
          (rerender_exec.py under --exec-py, build123d 0.11.1) and the STEP is rendered
          with the sheet variant FORCED to N (rerender_one.py under --render-py), so
          <out>/shard_XXXXXX.tar holds {uuid}_v{N}.png (new sheet) + the unchanged
          {uuid}_v{N}.py, plus shard_XXXXXX.renderers.json in the tars_v14 sidecar
          schema. Parts that fail keep NO member. Resumable per shard (an existing
          output tar + sidecar is skipped), one worker process per shard, one
          subprocess per exec / render so a crash or timeout is confined to a part.
  retry — for every COMPLETED output shard, re-attempt the keys recorded in
          <out>/failures/<shard>.json with a retryable reason (render_legacy / render_fail /
          render_timeout by default) after an adapter fix, append recovered members to the
          existing tar + sidecar, and move them to "recovered" in the failures file.
  dir   — every <src>/*.step rendered into <out>/png/<key>_v<N>.png + <out>/renderers.json
          with render_ext.py's conventions (seed crc32(key), uuid md5(key), variant from
          the seed) — the corpora / benches path, one process per part. With
          --variants {key: N} the variant is forced and the key is the renderer uuid
          (the certified eval sheets from gt_meshes_v15/<uuid>.step).

  python rerender_tars.py tars --tars /srv/scratch/bimrose2/tars_v14 \
      --out /srv/scratch/bimrose2/tars_v14_dw423 --workers 288 --log <jsonl> \
      [--shards 0-49] [--skip-keys exec_bad_keys_v14.txt --keep-keys certified.txt]
  python rerender_tars.py dir --src <corpus>/step_mm --out <corpus>/render_dw423 --workers 32 --log <jsonl>

Log: one JSON line per shard (tars) / part (dir): counts, failures by reason
(exec_error / exec_timeout / exec_nostep / render_fail / render_timeout /
skipped_known_bad; render_legacy only existed before the legacy fallback was removed), timings.
render_fail carries the draftwright exception text. Failure reasons per key are kept in
<out>/failures/<shard>.json (tars) or <out>/failures.json (dir).
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import io
import json
import multiprocessing as mp
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import zlib

M = "/srv/scratch/bimrose2/mech_benchmarks"
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULTS = dict(
    exec_py="/srv/scratch/bimrose2/.venv/bin/python",
    render_py="/srv/scratch/bimrose2/dw_venv/bin/python",
    script_dir=f"{M}/step_to_drw",
    tmp="/dev/shm/bimrose2_rerender",
)
THREAD_ENV = {"OMP_NUM_THREADS": "1", "TBB_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
              "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "PYTHONUNBUFFERED": "1"}

_CFG: dict = {}


def _run(cmd, timeout, cwd, env):
    """subprocess with a hard timeout that also kills the child's process group."""
    p = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=subprocess.DEVNULL,
                         stderr=subprocess.PIPE, start_new_session=True)
    try:
        _, err = p.communicate(timeout=timeout)
        return p.returncode, err.decode("utf-8", "replace")[-400:]
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, 9)
        except Exception:
            pass
        p.communicate()
        return -9, "timeout"


def exec_to_step(cfg, py_path, step_path, wd):
    env = dict(os.environ, **THREAD_ENV, TMPDIR=wd)
    rc, err = _run([cfg["exec_py"], os.path.join(HERE, "rerender_exec.py"), py_path, step_path],
                   cfg["exec_timeout"], wd, env)
    if rc == 0 and os.path.exists(step_path) and os.path.getsize(step_path) > 0:
        return None
    if rc == -9:
        return "exec_timeout", ""
    if rc == 3:
        return "exec_nostep", ""
    return "exec_error", err.strip().splitlines()[-1][:160] if err.strip() else f"rc={rc}"


def render_step(cfg, step_path, uuid, seed, variant, png_path, meta_path, wd):
    env = dict(os.environ, **THREAD_ENV, TMPDIR=wd, SCRIPT_DIR=cfg["script_dir"], VLM_MODE="1")
    cmd = [cfg["render_py"], os.path.join(HERE, "rerender_one.py"), "--step", step_path,
           "--out-png", png_path, "--out-meta", meta_path, "--uuid", uuid, "--seed", str(seed),
           "--variant", str(variant)]
    rc, err = _run(cmd, cfg["render_timeout"], wd, env)
    if rc == 0 and os.path.exists(png_path) and os.path.getsize(png_path) > 0:
        meta = json.load(open(meta_path))
        if meta.get("renderer") == "legacy" and not cfg["allow_legacy"]:
            return "render_legacy", str(meta.get("fallback", ""))[:200], meta  # dispatcher's reason
        return None, "", meta
    if rc == -9:
        return "render_timeout", "", None
    last = err.strip().splitlines()[-1][:300] if err.strip() else f"rc={rc}"
    if rc == 5 and os.path.exists(meta_path):  # failure meta from rerender_one (renderer="failed")
        try:
            last = str(json.load(open(meta_path)).get("render_error", last))[:300]
        except Exception:
            pass
    return "render_fail", last, None


# ----------------------------------------------------------------------------- tars mode
def do_shard(shard_path):
    cfg = _CFG
    name = os.path.basename(shard_path)[:-4]  # shard_XXXXXX
    out_tar = os.path.join(cfg["out"], name + ".tar")
    out_side = os.path.join(cfg["out"], name + ".renderers.json")
    if os.path.exists(out_tar) and os.path.exists(out_side):
        return {"shard": name, "skipped": True}
    t_start = time.time()
    wd = os.path.join(cfg["tmp"], name)
    shutil.rmtree(wd, ignore_errors=True)
    os.makedirs(wd)
    members: dict[str, dict] = {}
    try:
        with tarfile.open(shard_path) as tf:
            for m in tf.getmembers():
                if not m.isfile():
                    continue
                base, dot, ext = m.name.partition(".")
                if ext in ("py", "png"):
                    members.setdefault(base, {})[ext] = tf.extractfile(m).read()
    except Exception as e:
        shutil.rmtree(wd, ignore_errors=True)
        return {"shard": name, "error": f"{type(e).__name__}: {e}", "elapsed": time.time() - t_start}
    keys = sorted(k for k, v in members.items() if "py" in v and "png" in v)
    fails: dict[str, list] = {}
    sidecar: dict[str, dict] = {}
    ok: list[tuple[str, bytes, bytes]] = []
    t_exec = t_render = 0.0
    n_exec = n_render = 0
    for key in keys:
        if key in cfg["skip_keys"] and key not in cfg["keep_keys"]:
            fails[key] = ["skipped_known_bad", ""]
            continue
        uuid, _, vs = key.rpartition("_v")
        try:
            variant = int(vs)
        except ValueError:
            fails[key] = ["bad_key", ""]
            continue
        py_path = os.path.join(wd, key + ".py")
        step_path = os.path.join(wd, key + ".step")
        png_path = os.path.join(wd, key + ".png")
        meta_path = os.path.join(wd, key + ".json")
        with open(py_path, "wb") as f:
            f.write(members[key]["py"])
        t0 = time.time()
        r = exec_to_step(cfg, py_path, step_path, wd)
        t_exec += time.time() - t0
        n_exec += 1
        if r is not None:
            fails[key] = list(r)
            continue
        seed = zlib.crc32(uuid.encode()) % (2 ** 31)
        t0 = time.time()
        reason, msg, meta = render_step(cfg, step_path, uuid, seed, variant, png_path, meta_path, wd)
        t_render += time.time() - t0
        n_render += 1
        if reason is not None:
            fails[key] = [reason, msg]
            continue
        with open(png_path, "rb") as f:
            png = f.read()
        ok.append((key, png, members[key]["py"]))
        sidecar[key] = meta
        for p in (py_path, step_path, png_path, meta_path):
            try:
                os.unlink(p)
            except OSError:
                pass
    # write the shard atomically (tmp name in the output dir, then rename)
    os.makedirs(cfg["out"], exist_ok=True)
    tmp_tar = os.path.join(cfg["out"], f".tmp_{name}_{os.getpid()}.tar")
    with tarfile.open(tmp_tar, "w") as tf:
        for key, png, py in ok:
            for ext, data in (("png", png), ("py", py)):
                info = tarfile.TarInfo(f"{key}.{ext}")
                info.size = len(data)
                info.mtime = int(time.time())
                tf.addfile(info, io.BytesIO(data))
    os.makedirs(os.path.join(cfg["out"], "failures"), exist_ok=True)
    with open(os.path.join(cfg["out"], "failures", name + ".json"), "w") as f:
        json.dump(fails, f, indent=1, sort_keys=True)
    with open(out_side + ".tmp", "w") as f:
        json.dump(sidecar, f, indent=1, sort_keys=True)
    os.replace(out_side + ".tmp", out_side)
    os.replace(tmp_tar, out_tar)
    shutil.rmtree(wd, ignore_errors=True)
    by_reason: dict[str, int] = {}
    for reason, _ in fails.values():
        by_reason[reason] = by_reason.get(reason, 0) + 1
    return {"shard": name, "n_in": len(keys), "n_ok": len(ok), "n_fail": len(fails),
            "fails": by_reason, "exec_s": round(t_exec / max(n_exec, 1), 2),
            "render_s": round(t_render / max(n_render, 1), 2),
            "elapsed": round(time.time() - t_start, 1), "ts": time.strftime("%Y-%m-%d %H:%M:%S")}


# ----------------------------------------------------------------------------- dir mode
def do_part(step_path):
    cfg = _CFG
    key = os.path.splitext(os.path.basename(step_path))[0]
    png_dir = os.path.join(cfg["out"], "png")
    if glob.glob(os.path.join(png_dir, f"{key}_v*.png")):
        return {"key": key, "skipped": True}
    t0 = time.time()
    wd = os.path.join(cfg["tmp"], key)
    shutil.rmtree(wd, ignore_errors=True)
    os.makedirs(wd)
    seed = zlib.crc32(key.encode()) % (2 ** 31)
    if cfg["variants"]:  # forced-variant renders keyed by the real uuid (eval cache from GT STEPs)
        if key not in cfg["variants"]:
            return {"key": key, "ok": False, "reason": "no_variant_spec", "msg": ""}
        ruuid, variant = key, int(cfg["variants"][key])
    else:  # render_ext.py conventions
        ruuid, variant = hashlib.md5(key.encode()).hexdigest(), 0
    png_path = os.path.join(wd, key + ".png")
    meta_path = os.path.join(wd, key + ".json")
    reason, msg, meta = render_step(cfg, step_path, ruuid, seed, variant, png_path, meta_path, wd)
    rec = {"key": key, "elapsed": round(time.time() - t0, 1), "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
    if reason is None:
        meta["render_uuid"] = ruuid
        vi = meta["variant"]
        os.makedirs(png_dir, exist_ok=True)
        shutil.move(png_path, os.path.join(png_dir, f"{key}_v{vi}.png"))
        rec.update(ok=True, member=f"{key}_v{vi}", meta=meta)
    else:
        rec.update(ok=False, reason=reason, msg=msg)
    shutil.rmtree(wd, ignore_errors=True)
    return rec


# ----------------------------------------------------------------------------- retry mode
RETRY_REASONS = ("render_legacy", "render_fail", "render_timeout")


def do_retry(shard_path):
    """Re-attempt the recorded render failures of a COMPLETED shard (after an adapter fix) and
    append the recovered members to its tar / sidecar; the failures file keeps the losers and
    lists the winners under "recovered"."""
    cfg = _CFG
    name = os.path.basename(shard_path)[:-4]
    out_tar = os.path.join(cfg["out"], name + ".tar")
    out_side = os.path.join(cfg["out"], name + ".renderers.json")
    fail_path = os.path.join(cfg["out"], "failures", name + ".json")
    if not (os.path.exists(out_tar) and os.path.exists(out_side) and os.path.exists(fail_path)):
        return {"shard": name, "skipped": True}
    fails = json.load(open(fail_path))
    todo = sorted(k for k, v in fails.items() if v[0] in cfg["retry_reasons"])
    if not todo:
        return {"shard": name, "skipped": True, "n_todo": 0}
    t_start = time.time()
    wd = os.path.join(cfg["tmp"], name + "_retry")
    shutil.rmtree(wd, ignore_errors=True)
    os.makedirs(wd)
    pys = {}
    with tarfile.open(shard_path) as tf:
        for m in tf.getmembers():
            base, _, ext = m.name.partition(".")
            if ext == "py" and base in todo:
                pys[base] = tf.extractfile(m).read()
    recovered, still = [], {}
    for key in todo:
        uuid, _, vs = key.rpartition("_v")
        py_path, step_path = os.path.join(wd, key + ".py"), os.path.join(wd, key + ".step")
        png_path, meta_path = os.path.join(wd, key + ".png"), os.path.join(wd, key + ".json")
        with open(py_path, "wb") as f:
            f.write(pys[key])
        r = exec_to_step(cfg, py_path, step_path, wd)
        if r is not None:
            still[key] = list(r)
            continue
        reason, msg, meta = render_step(cfg, step_path, uuid, zlib.crc32(uuid.encode()) % (2 ** 31),
                                        int(vs), png_path, meta_path, wd)
        if reason is not None:
            still[key] = [reason, msg]
            continue
        recovered.append((key, open(png_path, "rb").read(), pys[key], meta))
    if recovered:
        with tarfile.open(out_tar, "a") as tf:  # uncompressed tar: append in place
            for key, png, py, _ in recovered:
                for ext, data in (("png", png), ("py", py)):
                    info = tarfile.TarInfo(f"{key}.{ext}")
                    info.size = len(data)
                    info.mtime = int(time.time())
                    tf.addfile(info, io.BytesIO(data))
        side = json.load(open(out_side))
        for key, _, _, meta in recovered:
            side[key] = meta
        with open(out_side + ".tmp", "w") as f:
            json.dump(side, f, indent=1, sort_keys=True)
        os.replace(out_side + ".tmp", out_side)
    for key in todo:
        if key in still:
            fails[key] = still[key]
        else:
            fails.pop(key)
    fails.setdefault("recovered", [])
    fails["recovered"] = sorted(set(fails["recovered"]) | {k for k, *_ in recovered})
    with open(fail_path + ".tmp", "w") as f:
        json.dump(fails, f, indent=1, sort_keys=True)
    os.replace(fail_path + ".tmp", fail_path)
    shutil.rmtree(wd, ignore_errors=True)
    by_reason: dict[str, int] = {}
    for reason, _ in still.values():
        by_reason[reason] = by_reason.get(reason, 0) + 1
    return {"shard": name, "retry": True, "n_todo": len(todo), "n_recovered": len(recovered),
            "still": by_reason, "elapsed": round(time.time() - t_start, 1), "ts": time.strftime("%Y-%m-%d %H:%M:%S")}


def _init(cfg):
    global _CFG
    _CFG = cfg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["tars", "dir", "retry"])
    ap.add_argument("--tars", default="/srv/scratch/bimrose2/tars_v14")
    ap.add_argument("--src", help="dir mode: directory of *.step")
    ap.add_argument("--out", required=True)
    ap.add_argument("--shards", default="", help="tars mode: 'a-b' index range or comma list of shard numbers")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=288)
    ap.add_argument("--log", required=True, help="jsonl progress log (appended)")
    ap.add_argument("--exec-py", default=DEFAULTS["exec_py"])
    ap.add_argument("--render-py", default=DEFAULTS["render_py"])
    ap.add_argument("--script-dir", default=DEFAULTS["script_dir"])
    ap.add_argument("--tmp", default=DEFAULTS["tmp"])
    ap.add_argument("--exec-timeout", type=int, default=120)
    ap.add_argument("--render-timeout", type=int, default=400)
    ap.add_argument("--skip-keys", default="", help="keys never attempted (known exec-bad), recorded as skipped_known_bad")
    ap.add_argument("--keep-keys", default="", help="keys always attempted even if in --skip-keys (certified eval)")
    ap.add_argument("--allow-legacy", action="store_true", help="keep sheets drawn by the legacy fallback renderer")
    ap.add_argument("--variants", default="", help="dir mode: JSON {key: N} forcing variant N and using key as the renderer uuid")
    ap.add_argument("--retry-reasons", default=",".join(RETRY_REASONS), help="retry mode: failure reasons to re-attempt")
    a = ap.parse_args()

    def _keys(p):
        return frozenset(ln.strip() for ln in open(p) if ln.strip()) if p else frozenset()

    cfg = dict(out=os.path.abspath(a.out), exec_py=a.exec_py, render_py=a.render_py,
               script_dir=a.script_dir, tmp=a.tmp, exec_timeout=a.exec_timeout,
               render_timeout=a.render_timeout, skip_keys=_keys(a.skip_keys),
               keep_keys=_keys(a.keep_keys), allow_legacy=a.allow_legacy,
               variants=json.load(open(a.variants)) if a.variants else {},
               retry_reasons=tuple(a.retry_reasons.split(",")))
    os.makedirs(cfg["out"], exist_ok=True)
    os.makedirs(cfg["tmp"], exist_ok=True)

    if a.mode in ("tars", "retry"):
        items = sorted(glob.glob(os.path.join(os.path.abspath(a.tars), "shard_*.tar")))
        if a.shards:
            if "-" in a.shards:
                lo, hi = (int(x) for x in a.shards.split("-"))
                items = items[lo:hi + 1]
            else:
                want = {int(x) for x in a.shards.split(",")}
                items = [p for p in items if int(os.path.basename(p)[6:12]) in want]
        fn = do_retry if a.mode == "retry" else do_shard
        unit = "shards"
    else:
        items = sorted(glob.glob(os.path.join(os.path.abspath(a.src), "*.step")))  # subprocess cwd is the temp dir
        fn = do_part
        unit = "parts"
    if a.limit:
        items = items[:a.limit]
    print(f"[rerender] {a.mode}: {len(items)} {unit}, workers={a.workers}, skip={len(cfg['skip_keys'])} "
          f"keep={len(cfg['keep_keys'])} -> {cfg['out']}", flush=True)
    t0 = time.time()
    done = ok = fail = skipped = 0
    with mp.Pool(a.workers, initializer=_init, initargs=(cfg,)) as pool, open(a.log, "a") as log:
        for rec in pool.imap_unordered(fn, items):
            done += 1
            log.write(json.dumps(rec) + "\n")
            log.flush()
            if rec.get("skipped"):
                skipped += 1
            elif a.mode == "retry":
                ok += rec.get("n_recovered", 0)
                fail += rec.get("n_todo", 0) - rec.get("n_recovered", 0)
            elif a.mode == "tars":
                ok += rec.get("n_ok", 0)
                fail += rec.get("n_fail", 0)
            else:
                ok += int(bool(rec.get("ok")))
                fail += int(not rec.get("ok"))
            if done % (1 if a.mode == "tars" else 25) == 0 or done == len(items):
                el = time.time() - t0
                rate = (ok + fail) / max(el, 1e-6)
                per = (el / max(done - skipped, 1)) * (len(items) - done) / max(a.workers, 1)
                print(f"[rerender] {done}/{len(items)} {unit} ({skipped} skipped) parts ok={ok} fail={fail} "
                      f"({100 * fail / max(ok + fail, 1):.1f}%) {rate:.2f} parts/s "
                      f"elapsed {el / 3600:.2f} h  ETA ~{per / 3600:.2f} h", flush=True)
    if a.mode == "dir":  # merge the sidecar + failure list like render_ext.py
        side_path = os.path.join(cfg["out"], "renderers.json")
        side = json.load(open(side_path)) if os.path.exists(side_path) else {}
        fails = {}
        for ln in open(a.log):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if r.get("ok"):
                side[r["member"]] = r["meta"]
            elif "reason" in r:
                fails[r["key"]] = f"{r['reason']}: {r.get('msg', '')}"
        json.dump(side, open(side_path, "w"), indent=1, sort_keys=True)
        json.dump(fails, open(os.path.join(cfg["out"], "failures.json"), "w"), indent=1, sort_keys=True)
        print(f"[rerender] sidecar entries {len(side)}, failures {len(fails)}", flush=True)
    print(f"[rerender] DONE ok={ok} fail={fail} in {(time.time() - t0) / 3600:.2f} h", flush=True)


if __name__ == "__main__":
    main()
