"""Run exec_worker.py tasks with N persistent workers and a per-task timeout.

    python run_exec.py tasks.jsonl results.jsonl [--workers 16] [--timeout 60]

tasks.jsonl rows: {"id", "code"} or {"id", "step"} (+ any extra keys, copied to the result).
Resumable: ids already present in results.jsonl are skipped.
"""
from __future__ import annotations

import argparse
import json
import os
import queue
import select
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WORKER = os.path.join(HERE, "exec_worker.py")


class Worker:
    def __init__(self, py):
        self.py = py
        self.p = None
        self.n = 0

    def start(self):
        self.p = subprocess.Popen([self.py, WORKER], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL, text=True, bufsize=1)
        line = self._read(900)
        if line is None or "ready" not in line:
            raise RuntimeError("worker failed to start")
        self.n = 0

    def _read(self, timeout):
        end = time.time() + timeout
        while True:
            rem = end - time.time()
            if rem <= 0:
                return None
            r, _, _ = select.select([self.p.stdout], [], [], rem)
            if r:
                line = self.p.stdout.readline()
                return line if line else None

    def kill(self):
        try:
            self.p.kill()
            self.p.wait(5)
        except Exception:
            pass
        self.p = None

    def run(self, task, timeout):
        if self.p is None or self.p.poll() is not None or self.n >= 250:
            if self.p is not None:
                self.kill()
            self.start()
        self.n += 1
        payload = {k: task[k] for k in ("id", "code", "step") if k in task}
        try:
            self.p.stdin.write(json.dumps(payload) + "\n")
            self.p.stdin.flush()
        except BrokenPipeError:
            self.kill()
            return {"id": task["id"], "ok": False, "stage": "crash"}
        line = self._read(timeout)
        if line is None:
            crashed = self.p.poll() is not None
            self.kill()
            return {"id": task["id"], "ok": False, "stage": "crash" if crashed else "timeout"}
        return json.loads(line)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tasks")
    ap.add_argument("out")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--timeout", type=float, default=60)
    ap.add_argument("--python", default=sys.executable)
    a = ap.parse_args()
    done = set()
    if os.path.exists(a.out):
        for l in open(a.out):
            try:
                done.add(json.loads(l)["id"])
            except Exception:
                pass
    tasks = [json.loads(l) for l in open(a.tasks)]
    tasks = [t for t in tasks if t["id"] not in done]
    print(f"[run_exec] {len(tasks)} tasks ({len(done)} done) workers={a.workers}", flush=True)
    q: queue.Queue = queue.Queue()
    for t in tasks:
        q.put(t)
    lock = threading.Lock()
    fo = open(a.out, "a")
    cnt = [0]
    t0 = time.time()

    def loop():
        w = Worker(a.python)
        while True:
            try:
                t = q.get_nowait()
            except queue.Empty:
                break
            r = w.run(t, a.timeout)
            for k, v in t.items():
                if k not in ("code", "step") and k not in r:
                    r[k] = v
            with lock:
                fo.write(json.dumps(r) + "\n")
                fo.flush()
                cnt[0] += 1
                if cnt[0] % 200 == 0:
                    print(f"[run_exec] {cnt[0]}/{len(tasks)} {time.time() - t0:.0f}s", flush=True)
        if w.p is not None:
            w.kill()

    th = [threading.Thread(target=loop) for _ in range(a.workers)]
    for x in th:
        x.start()
    for x in th:
        x.join()
    print(f"[run_exec] done {cnt[0]} in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
