"""Execute every GT .py in one tar shard; record which produce a STEP file.

    python audit_shard.py <shard.tar> <out.jsonl>

Imports build123d once per worker; each script runs under a 60s SIGALRM in a
temp cwd. Appends {"key", "ok", "err"} per sample and flushes as it goes, so
a crashed worker can be resumed (existing keys are skipped).
"""
from __future__ import annotations

import io
import json
import os
import signal
import sys
import tarfile
import tempfile


def _alarm(_sig, _frm):
    raise TimeoutError("timeout")


def main():
    shard, out_path = sys.argv[1], sys.argv[2]
    done = set()
    if os.path.exists(out_path):
        with open(out_path) as f:
            for line in f:
                try:
                    done.add(json.loads(line)["key"])
                except Exception:
                    pass

    # Crash recovery: some GT scripts SEGFAULT the OCC kernel, killing this
    # process. The inflight marker names the sample being executed; if we
    # start up and it isn't in `done`, the previous attempt died on it —
    # record it as a crash and skip it forever.
    inflight = out_path + ".inflight"
    if os.path.exists(inflight):
        with open(inflight) as f:
            poison = f.read().strip()
        if poison and poison not in done:
            with open(out_path, "a") as f:
                f.write(json.dumps({"key": poison, "ok": False,
                                    "err": "segfault"}) + "\n")
            done.add(poison)
        os.unlink(inflight)

    signal.signal(signal.SIGALRM, _alarm)
    import contextlib

    # Warm the heavy import once so no sample's 60s alarm pays for it.
    try:
        import build123d  # noqa: F401
    except Exception:
        pass

    out = open(out_path, "a")
    with tarfile.open(shard, "r") as tf:
        names = [n for n in tf.getnames() if n.endswith(".py")]
        for name in names:
            key = name[: -len(".py")]
            if key in done:
                continue
            try:
                code = tf.extractfile(name).read().decode("utf-8", errors="replace")
            except Exception:
                out.write(json.dumps({"key": key, "ok": False, "err": "unreadable"}) + "\n")
                continue
            ok, err = False, ""
            with open(inflight, "w") as f:
                f.write(key)
            with tempfile.TemporaryDirectory(prefix="gtaudit_") as td:
                cwd = os.getcwd()
                os.chdir(td)
                g = {"__name__": "__main__", "OUTPUT_PATH": "output.step"}
                buf = io.StringIO()
                try:
                    signal.alarm(60)
                    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                        exec(compile(code, name, "exec"), g)  # noqa: S102
                    step = os.path.join(td, "output.step")
                    ok = os.path.exists(step) and os.path.getsize(step) > 0
                    if not ok:
                        err = "no_step"
                except TimeoutError:
                    err = "timeout"
                except SystemExit:
                    step = os.path.join(td, "output.step")
                    ok = os.path.exists(step) and os.path.getsize(step) > 0
                except Exception as e:
                    err = f"{type(e).__name__}: {str(e)[:80]}"
                finally:
                    signal.alarm(0)
                    os.chdir(cwd)
            out.write(json.dumps({"key": key, "ok": ok, "err": err}) + "\n")
            out.flush()
    out.close()
    if os.path.exists(inflight):
        os.unlink(inflight)


if __name__ == "__main__":
    main()
