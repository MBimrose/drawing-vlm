"""Zero-to-CAD-style synthesis of missing real part families (2026-09-23), in build123d.

Stage 1 (describe): a vision model (Kimi-K3 on the lab hub) reads the drawing of a real training-side part
that e55 fails, names its family and writes 3 dimension-free one-to-three-sentence descriptions: the part
itself and two distinct plausible siblings of the same family (not copies).
Stage 2 (synthesize): per description, a code model (round-robin GLM-5.3 / DeepSeek-V4.1-Flash / Kimi-K3)
writes a build123d program in a repair loop: execute (exec_harness.py) + validate (validate_step.py) and feed
the traceback or the failed check back, up to --turns turns. Accepted parts: one valid solid, >= --min-faces
faces, positive volume, max extent 10-400 mm. Writes step_mm/<id>.step, gt_meshes_v15/<id>.stl, rows.jsonl.
Never uses gpt-oss (user preference).
    python family_synth.py describe --seeds seeds.json --out <dir>
    python family_synth.py synth --out <dir> [--workers 24]
"""
import argparse, base64, json, os, random, re, shutil, subprocess, sys, tempfile, threading, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

HUB_USER = os.environ.get("HUB_USER", "bimrose2")   # user: attribute every hub request to bimrose2
HUB = os.environ.get("CLAUDE_HUB_ROUTER", "http://wpk-serv-07.mechse.illinois.edu:3456") + "/v1/messages"
HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.join(HERE, "..", "..", "geom", "exec_harness.py")
VALIDATE = os.path.join(HERE, "validate_step.py")
# coder mix, weighted toward the uncapped model: 6 DeepSeek : 2 GLM : 1 Kimi
_DS, _GLM, _KIMI = "claude-deepseek-ai/DeepSeek-V4.1-Flash[1m]", "claude-glm-5.3[1m]", "claude-moonshotai/Kimi-K3[1m]"
CODERS = [_DS, _GLM, _DS, _DS, _KIMI, _DS, _GLM, _DS, _DS]
VISION = "claude-moonshotai/Kimi-K3[1m]"
# per-model concurrency caps on the shared hub (user, 2026-09-23, "don't saturate the box"): Kimi <= 2, GLM <= 4, DeepSeek uncapped
LIMITS = {"claude-moonshotai/Kimi-K3[1m]": threading.BoundedSemaphore(2), "claude-glm-5.3[1m]": threading.BoundedSemaphore(4)}

def call(model, messages, system=None, max_tokens=16000, timeout=900, tries=4, think=6000):
    # explicit thinking budget: without it GLM-5.3 thinks up to max_tokens (30k tokens, 4+ min per turn)
    body = {"model": model, "max_tokens": max_tokens, "messages": messages, "thinking": {"type": "enabled", "budget_tokens": think}}
    if system: body["system"] = system
    for t in range(tries):
        try:
            rq = urllib.request.Request(HUB, data=json.dumps(body).encode(), headers={
                "content-type": "application/json", "x-api-key": "not-needed", "anthropic-version": "2023-06-01",
                "x-hub-user": HUB_USER})   # router usage attribution (hub_user in its usage log)
            sem = LIMITS.get(model)
            if sem:
                with sem: d = json.load(urllib.request.urlopen(rq, timeout=timeout))
            else:
                d = json.load(urllib.request.urlopen(rq, timeout=timeout))
            return "".join(b.get("text", "") for b in d.get("content", []) if b.get("type") == "text"), d.get("usage", {})
        except Exception as e:
            err = e; time.sleep(5 * (t + 1))
    raise RuntimeError(f"hub call failed: {err}")

DESCRIBE = """You are an expert mechanical parts librarian. The image is an engineering drawing of one real part.
1. Name the part's family in a few words (e.g. "desk frame of thin panels", "ribbed plastic enclosure half", "bent sheet-metal bracket").
2. Write three concise engineering part descriptions (1-3 sentences each) for a CAD modeller:
   - the first describes THIS part's form: its main bodies, how they are joined, walls/panels/shells, holes, slots, ribs, bosses, fillets, patterns;
   - the second and third describe two DIFFERENT plausible parts of the SAME family (vary layout, counts, feature mix), not copies.
DO NOT include any dimensions or numbers of millimetres. Counts of features are fine.
Answer with JSON only: {"family": "...", "descriptions": ["...", "...", "..."]}"""

SYSTEM = """You are an expert CAD engineer who writes build123d (Python) programs for real manufactured parts.
Rules:
- Start with `from build123d import *`, then define every dimension as a named variable (mm) before any geometry.
- Choose realistic proportions; the largest dimension between 20 and 300 mm; walls, panels and sheet thicknesses realistic (often 1-6 mm).
- Model the COMPLETE described part with rich, faithful detail: every panel, wall, rib, boss, hole, slot, fillet and pattern described. The result must be ONE connected solid (fuse touching bodies).
- Prefer clear construction (Box/Cylinder/extrude/revolve/loft/sweep, Locations/GridLocations/PolarLocations, fillet/chamfer, boolean + and -). Hollow bodies: build them explicitly (outer minus inner) or use offset with `openings=`; note `offset(solid, amount=-t)` WITHOUT openings shrinks the solid instead of hollowing it.
- End with `part = <final solid>` and `export_step(part, OUTPUT_PATH)`.
- If execution fails, read the error and FIX it; never simplify the part to avoid an error.
Answer with a single ```python code block.

Style example:
```python
from build123d import *

outer_diameter = 80.0
inner_diameter = 40.0
sheet_thickness = 5.0
rib_width = 8.0
rib_height = 3.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
        Circle(inner_diameter / 2, mode=Mode.SUBTRACT)
    extrude(amount=sheet_thickness)
    with BuildSketch(Plane.XY.offset(sheet_thickness)) as s2:
        Circle(outer_diameter / 2)
        Circle(outer_diameter / 2 - rib_width, mode=Mode.SUBTRACT)
    extrude(amount=rib_height)

part = chamfer(p.part.edges(), chamfer_size)
export_step(part, OUTPUT_PATH)
```"""

def code_of(txt):
    m = re.findall(r"```(?:python)?\s*\n(.*?)```", txt, re.S)
    return max(m, key=len) if m else None

def run(code, workdir, key, py, timeout=120):
    cp = os.path.join(workdir, key + ".py"); stl = os.path.join(workdir, key + ".stl"); stp = os.path.join(workdir, key + ".step")
    open(cp, "w").write(code)
    try:
        p = subprocess.run([py, HARNESS, cp, stl, stp], capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, f"execution timed out after {timeout} s (simplify nothing; make the construction cheaper)"
    if p.returncode != 0:
        tb = (p.stderr or p.stdout or "").strip().splitlines()
        return None, "execution failed:\n" + "\n".join(tb[-25:])
    try:
        v = json.loads(subprocess.run([py, VALIDATE, stp], capture_output=True, text=True, timeout=120).stdout.strip().splitlines()[-1])
    except Exception as e:
        return None, f"could not validate STEP: {e}"
    return (stl, stp, v), None

def check(v, min_faces):
    if "error" in v: return "STEP could not be read: " + v["error"]
    if v["solids"] != 1: return f"the result has {v['solids']} separate solids; it must be ONE connected solid (fuse touching bodies, make sure parts overlap)"
    if not v["valid"]: return "the solid is not topologically valid (self-intersection or bad boolean); rebuild the failing feature"
    if v["volume"] <= 0: return "the solid has no volume"
    if v["faces"] < min_faces: return f"only {v['faces']} faces: the part is far simpler than described; model all described features"
    mx = max(v["bbox"])
    if not 10 <= mx <= 400: return f"largest extent {mx:.1f} mm is outside 10-400 mm; use realistic dimensions"
    return None

def describe(a):
    seeds = json.load(open(a.seeds)); out = os.path.join(a.out, "descriptions.jsonl")
    done = {json.loads(l)["seed"] for l in open(out)} if os.path.exists(out) else set()
    lock = threading.Lock()
    def one(s):
        if s["key"] in done: return
        img = base64.b64encode(open(s["png"], "rb").read()).decode()
        txt, _ = call(VISION, [{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": img}},
            {"type": "text", "text": DESCRIBE}]}], max_tokens=4000)
        m = re.search(r"\{.*\}", txt, re.S)
        try: j = json.loads(m.group(0))
        except Exception: print("describe parse fail", s["key"], txt[:200], flush=True); return
        if re.search(r"\d+(\.\d+)?\s*(mm|cm|in)\b", " ".join(j.get("descriptions", []))): print("dimension leak", s["key"], flush=True)
        with lock:
            with open(out, "a") as f: f.write(json.dumps({"seed": s["key"], "seed_family": s["family"], **j}) + "\n")
    with ThreadPoolExecutor(a.workers) as ex: list(ex.map(one, seeds))
    print("DESCRIBE DONE", sum(1 for _ in open(out)), flush=True)

def synth(a):
    rows = [json.loads(l) for l in open(os.path.join(a.out, "descriptions.jsonl"))]
    jobs = []
    for i, r in enumerate(rows):
        for j, d in enumerate(r.get("descriptions", [])[:3]):
            jobs.append({"id": f"Z_{i:05d}_{j}", "seed": r["seed"], "family": r["family"], "desc": d})
    random.seed(0)
    for n, jb in enumerate(jobs): jb["model"] = CODERS[n % len(CODERS)]
    if a.limit: jobs = jobs[: a.limit]
    for sub in ("step_mm", "gt_meshes_v15", "code"): os.makedirs(os.path.join(a.out, sub), exist_ok=True)
    out = os.path.join(a.out, "rows.jsonl"); done = {json.loads(l)["id"] for l in open(out)} if os.path.exists(out) else set()
    wd = tempfile.mkdtemp(prefix="famsyn_", dir="/dev/shm"); lock = threading.Lock(); t0 = time.time(); stats = {"ok": 0, "n": 0}
    def one(jb):
        if jb["id"] in done: return
        msgs = [{"role": "user", "content": f"Part description: {jb['desc']}\nPart family: {jb['family']}\nWrite the build123d program."}]
        rec = dict(jb, ok=False, turns=0, usage=[])
        for turn in range(a.turns):
            rec["turns"] = turn + 1
            try: txt, u = call(jb["model"], msgs, system=SYSTEM)
            except Exception as e: rec["err"] = str(e); break
            rec["usage"].append(u); code = code_of(txt)
            if not code:
                msgs += [{"role": "assistant", "content": txt or "(empty)"}, {"role": "user", "content": "Answer with a single ```python code block."}]; continue
            res, err = run(code, wd, jb["id"], a.py)
            if res and not err: err = check(res[2], a.min_faces)
            if not err:
                stl, stp, v = res
                shutil.move(stp, os.path.join(a.out, "step_mm", jb["id"] + ".step")); shutil.move(stl, os.path.join(a.out, "gt_meshes_v15", jb["id"] + ".stl"))  # /dev/shm -> disk: os.replace cannot cross filesystems
                open(os.path.join(a.out, "code", jb["id"] + ".py"), "w").write(code)
                rec.update(ok=True, code=code, **{k: v[k] for k in ("faces", "edges", "volume", "bbox")}); break
            rec["last_err"] = err[:600]
            msgs += [{"role": "assistant", "content": f"```python\n{code}\n```"}, {"role": "user", "content": err + "\nFix the program and answer with the complete corrected ```python code block."}]
        with lock:
            stats["n"] += 1; stats["ok"] += rec["ok"]
            with open(out, "a") as f: f.write(json.dumps(rec) + "\n")
            if stats["n"] % 20 == 0: print(f"[synth] {stats['n']}/{len(jobs)} ok {stats['ok']} {time.time()-t0:.0f}s", flush=True)
    def safe(jb):
        try: one(jb)
        except Exception as e:
            import traceback; print("[synth] worker error", jb["id"], traceback.format_exc()[-600:], flush=True)
    with ThreadPoolExecutor(a.workers) as ex: list(ex.map(safe, jobs))
    print("SYNTH DONE", stats, flush=True)

ap = argparse.ArgumentParser(); ap.add_argument("stage"); ap.add_argument("--seeds"); ap.add_argument("--out", required=True)
ap.add_argument("--workers", type=int, default=16); ap.add_argument("--turns", type=int, default=6); ap.add_argument("--min-faces", type=int, default=10)
ap.add_argument("--limit", type=int, default=0); ap.add_argument("--py", default=sys.executable)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
{"describe": describe, "synth": synth}[a.stage](a)
