"""Translate Zero-to-CAD (ADSKAILab/Zero-To-CAD-100k, Apache-2.0) CadQuery programs into build123d (2026-09-28).

H6b showed family ground-truth programs generalise to the real bench with a learning curve still rising at 1,655
parts; Zero-to-CAD offers ~1M agent-synthesised programs over 65 categories, but in CadQuery. DeepSeek-V4.1-Flash
(hub, uncapped, x-hub-user attributed) rewrites each program in our build123d style; the result is executed and
accepted only if it is one valid solid whose centred volume IoU with the dataset's own STL is >= --min-iou and whose
bbox extents match within 2%. Repair loop feeds back the traceback / the geometric mismatch.
    python zerocad_translate.py --parquet a.parquet b.parquet --out <dir> [--limit 300] [--workers 48]
Outputs like family_synth synth: code/<id>.py, step_mm/<id>.step, gt_meshes_v15/<id>.stl, rows.jsonl."""
import argparse, json, os, random, shutil, subprocess, sys, tempfile, threading, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from family_synth import call, code_of, run, check, _DS
IOU_ONCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "geom", "iou_once.py")

SYSTEM = """You are an expert CAD engineer fluent in both CadQuery and build123d (Python).
Translate the given CadQuery program into an equivalent build123d program that produces EXACTLY the same solid:
same dimensions, same position and orientation in space, same features.
Rules:
- Start with `from build123d import *`, then define every dimension as a plain named variable (mm) before any geometry
  (flatten any Measures/SimpleNamespace structs into simple variables with descriptive names).
- Use idiomatic build123d: Box/Cylinder/Sphere/Cone/Torus, BuildPart/BuildSketch/BuildLine with extrude/revolve/loft/sweep,
  Locations/GridLocations/PolarLocations, Plane.XY/XZ/YZ(.offset), fillet/chamfer/offset(openings=...), boolean + and -.
- Watch the conventions: CadQuery box() is centred like Box(); CadQuery workplane .hole() cuts through; .shell(-t) on a
  selected face = offset(..., amount=-t, openings=face); edge/face selectors like ">Z" map to .sort_by(Axis.Z)[-1] /
  .filter_by(...) — pick the SAME edges; Workplane("XZ") normal is -Y in CadQuery, build123d Plane.XZ normal is -Y too.
- End with `part = <final solid>` and `export_step(part, OUTPUT_PATH)`.
- No comments referring to CadQuery. Answer with a single ```python code block."""

def iou(stl, gt, py):
    try:
        p = subprocess.run([py, IOU_ONCE, stl, gt], capture_output=True, text=True, timeout=180)
        return float(json.loads(p.stdout)["iou_centered"])
    except Exception:
        return 0.0

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--parquet", nargs="+"); ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0); ap.add_argument("--workers", type=int, default=48); ap.add_argument("--turns", type=int, default=4)
    ap.add_argument("--min-iou", type=float, default=0.95); ap.add_argument("--min-faces", type=int, default=7); ap.add_argument("--max-chars", type=int, default=6000)
    ap.add_argument("--py", default=sys.executable); ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    import pyarrow.parquet as pq
    for sub in ("step_mm", "gt_meshes_v15", "code", "src_stl", "src_cq"): os.makedirs(os.path.join(a.out, sub), exist_ok=True)
    rows = []
    for f in a.parquet:
        for r in pq.read_table(f, columns=["uuid", "cadquery_file", "num_faces", "cadquery_ops_count", "stl_file"]).to_pylist():
            cq = r["cadquery_file"].decode() if isinstance(r["cadquery_file"], bytes) else r["cadquery_file"]
            if len(cq) <= a.max_chars: rows.append(dict(r, cadquery_file=cq))
    random.seed(a.seed); random.shuffle(rows)
    if a.limit: rows = rows[: a.limit]
    out = os.path.join(a.out, "rows.jsonl"); done = {json.loads(l)["id"] for l in open(out)} if os.path.exists(out) else set()
    wd = tempfile.mkdtemp(prefix="zcad_", dir="/dev/shm"); lock = threading.Lock(); t0 = time.time(); stats = {"ok": 0, "n": 0}
    print(f"[zcad] {len(rows)} programs, {len(done)} done", flush=True)
    def one(r):
        rid = "Q_" + r["uuid"][:16]
        if rid in done: return
        gt = os.path.join(a.out, "src_stl", rid + ".stl"); open(gt, "wb").write(r["stl_file"])
        open(os.path.join(a.out, "src_cq", rid + ".py"), "w").write(r["cadquery_file"])
        msgs = [{"role": "user", "content": f"CadQuery program:\n```python\n{r['cadquery_file']}\n```\nWrite the equivalent build123d program. Translate it directly, statement by statement; do not deliberate at length."}]
        rec = {"id": rid, "uuid": r["uuid"], "src_faces": r["num_faces"], "src_ops": r["cadquery_ops_count"], "model": _DS, "ok": False, "turns": 0, "usage": []}
        for turn in range(a.turns):
            rec["turns"] = turn + 1
            try: txt, u = call(_DS, msgs, system=SYSTEM, effort="low", max_tokens=30000)   # pilot: 45% ran out of 15k tokens thinking
            except Exception as e: rec["err"] = str(e); break
            rec["usage"].append(u); code = code_of(txt)
            if not code:
                msgs += [{"role": "assistant", "content": txt or "(empty)"}, {"role": "user", "content": "You ran out of space while thinking. Translate directly now, statement by statement, and answer with a single ```python code block."}]; continue
            res, err = run(code, wd, rid, a.py)
            if res and not err: err = check(res[2], a.min_faces)
            if res and not err:
                v = iou(res[0], gt, a.py); rec["iou"] = v
                if v < a.min_iou:
                    err = (f"the build123d solid does not match the CadQuery solid (volume IoU {v:.3f}; its bbox extents are "
                           f"{[round(x, 2) for x in res[2]['bbox']]}). Some feature, position, orientation or edge selection differs; find and fix it.")
            if not err:
                stl, stp, v = res
                shutil.move(stp, os.path.join(a.out, "step_mm", rid + ".step")); shutil.move(stl, os.path.join(a.out, "gt_meshes_v15", rid + ".stl"))
                open(os.path.join(a.out, "code", rid + ".py"), "w").write(code)
                rec.update(ok=True, code=code, **{k: v[k] for k in ("faces", "edges", "volume", "bbox")}); break
            rec["last_err"] = err[:600]
            msgs += [{"role": "assistant", "content": f"```python\n{code}\n```"}, {"role": "user", "content": err + "\nFix the program and answer with the complete corrected ```python code block."}]
        with lock:
            stats["n"] += 1; stats["ok"] += rec["ok"]
            with open(out, "a") as f: f.write(json.dumps(rec) + "\n")
            if stats["n"] % 25 == 0: print(f"[zcad] {stats['n']}/{len(rows)} ok {stats['ok']} {time.time()-t0:.0f}s", flush=True)
    def safe(r):
        try: one(r)
        except Exception:
            import traceback; print("[zcad] worker error", traceback.format_exc()[-600:], flush=True)
    with ThreadPoolExecutor(a.workers) as ex: list(ex.map(safe, rows))
    print("ZCAD DONE", stats, flush=True)

if __name__ == "__main__":
    main()
