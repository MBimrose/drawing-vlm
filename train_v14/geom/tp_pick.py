"""Vote pick (medoid of pairwise centred IoU among executing draws) from gen_openai_bo partial shards -> picks json."""
import glob, json, os, subprocess, sys, tempfile, itertools
HERE = os.path.dirname(os.path.abspath(__file__)); PY = sys.executable
parts, out = sys.argv[1], sys.argv[2]
cands = {}
for f in glob.glob(parts):
    d = json.load(open(f))
    for k, cs in zip(d["keys"], d["cands"]): cands.setdefault(k, []).extend(cs)
res = {}
for k, cs in cands.items():
    td = tempfile.mkdtemp(prefix="tpp_", dir="/dev/shm"); stls = []
    for i, c in enumerate(cs):
        code = c.get("code") or ""
        if not code: continue
        cp, stl, stp = f"{td}/{i}.py", f"{td}/{i}.stl", f"{td}/{i}.step"; open(cp, "w").write(code)
        try:
            if subprocess.run([PY, os.path.join(HERE, "exec_harness.py"), cp, stl, stp], capture_output=True, timeout=120).returncode == 0 and os.path.exists(stl): stls.append((i, stl))
        except subprocess.TimeoutExpired: pass
    if not stls: print(k, "no executing draw"); continue
    sc = {i: 0.0 for i, _ in stls}
    for (i, a), (j, b) in itertools.combinations(stls, 2):
        try: v = float(json.loads(subprocess.run([PY, os.path.join(HERE, "iou_once.py"), a, b], capture_output=True, text=True, timeout=300).stdout)["iou_centered"])
        except Exception: v = 0.0
        sc[i] += v; sc[j] += v
    best = max(sc, key=sc.get); res[k] = {"code": cs[best]["code"], "iou": 0.0, "draw": best, "n_exec": len(stls), "n": len(cs)}
    print(k, "executing", len(stls), "of", len(cs), "pick", best)
json.dump(res, open(out, "w"))
