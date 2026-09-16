"""Execute and score generations dumped by dsv41_lora_train.py's eval (key, text, code per line).

The DeepSeek spike generates on GPU boxes that cannot run the CAD stack (serv-04: glibc 2.28),
so the eval is split: this half runs where build123d/trimesh work (the cluster, main .venv),
same exec harness + centered IoU as every bo8_ext "first-exec" column.

    python dsv41_eval_score.py --gens runs/x/eval_gen.rank0.jsonl [...] \
        --bench train_v14/mech/benchmarks/data/ext_bench --out runs/x/eval.json [--workers 8]
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.join(HERE, "exec_harness.py")
IOU_ONCE = os.path.join(HERE, "iou_once.py")


def score_one(rec, gt_dir, timeout):
    key, code = rec["key"], rec.get("code") or ""
    out = {"key": key, "exec": False, "iou": 0.0, "chars": len(rec.get("text", "")), "has_code": bool(code)}
    if not code:
        return out
    with tempfile.TemporaryDirectory(prefix="dsv41eval_") as td:
        cp, stl = os.path.join(td, "c.py"), os.path.join(td, "c.stl")
        open(cp, "w").write(code)
        try:
            p = subprocess.run([sys.executable, HARNESS, cp, stl], capture_output=True, text=True, timeout=timeout)
            if p.returncode == 0 and os.path.exists(stl):
                out["exec"] = True
                q = subprocess.run([sys.executable, IOU_ONCE, stl, os.path.join(gt_dir, key + ".stl")],
                                   capture_output=True, text=True, timeout=timeout)
                if q.returncode == 0 and q.stdout.strip():
                    out["iou"] = float(json.loads(q.stdout.strip().splitlines()[-1])["iou_centered"])
            else:
                out["error"] = (p.stderr or "")[-200:]
        except subprocess.TimeoutExpired:
            out["error"] = "timeout"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gens", nargs="+", required=True)
    ap.add_argument("--bench", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--timeout", type=int, default=120)
    a = ap.parse_args()
    recs, seen = [], set()
    for g in a.gens:
        for line in open(g):
            r = json.loads(line)
            if r["key"] in seen:
                continue
            seen.add(r["key"]); recs.append(r)
    gt_dir = os.path.join(a.bench, "gt_meshes_v15")
    with ThreadPoolExecutor(a.workers) as ex:
        scored = list(ex.map(lambda r: score_one(r, gt_dir, a.timeout), recs))
    ious = [r["iou"] for r in scored]
    n = max(1, len(ious))
    summ = {"n": len(scored), "first_exec_mean": sum(ious) / n, "median": sorted(ious)[len(ious) // 2] if ious else 0.0,
            "ge85": sum(x >= 0.85 for x in ious) / n, "ge50": sum(x >= 0.5 for x in ious) / n,
            "executed": sum(r["exec"] for r in scored), "with_code": sum(r["has_code"] for r in scored),
            "mean_chars": sum(r["chars"] for r in scored) / n}
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump({"summary": summ, "records": scored}, open(a.out, "w"), indent=1)
    print("[eval] " + json.dumps(summ))


if __name__ == "__main__":
    main()
