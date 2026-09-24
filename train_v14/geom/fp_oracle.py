"""H4 stage oracles on the real bench (diagnosis only; GT views are never used for training).
  describe : Kimi-K3 reads the GT 3D views (gtviews.py) and writes a dimension-free structural description.
  prompts  : writes {key: user prompt} for e55 = standard prompt + that description  (oracle a: e55 sees sheet + description).
  code     : DeepSeek-V4.1-Flash writes build123d from description + the sheet's printed dimension labels, no image
             (oracle b: can a strong coder express the structure given perfect understanding?), family_synth repair loop.
All hub calls carry x-hub-user bimrose2 and the family_synth caps (Kimi 2, GLM 4).
    python fp_oracle.py describe --views <dir> --out <dir>;  python fp_oracle.py prompts --out <dir>
    python fp_oracle.py code --out <dir> --renderers <renderers.json> [--workers 16]"""
import argparse, base64, json, os, re, sys, tempfile, threading, time
from concurrent.futures import ThreadPoolExecutor
FS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mech", "familysynth")
sys.argv_saved = sys.argv; sys.argv = [sys.argv[0], "noop", "--out", "/tmp"]
src = open(os.path.join(FS, "family_synth.py")).read().split("ap = argparse.ArgumentParser()")[0]
fs = {"__file__": os.path.join(FS, "family_synth.py")}; exec(src, fs); sys.argv = sys.argv_saved
USER_PROMPT = "Reproduce the geometry as accurately as possible from the drawing."
DESC = """The image shows four views (front, top, right, isometric) of ONE real mechanical part's true 3D geometry.
Write a precise structural description that would let a CAD modeller rebuild it from an engineering drawing:
the main body and how it is built (plate, shell, frame, revolved body, ...), which regions are hollow or open, wall/panel
arrangement, every feature (holes, slots, pockets, ribs, bosses, fillets, chamfers, patterns with counts) and where it sits
relative to the others. Use relative words (e.g. "wall thin relative to the height"), NOT numbers of millimetres.
Answer with the description only, 4-10 sentences."""
CODE_SYS = fs["SYSTEM"].replace("for real manufactured parts.", "for real manufactured parts. You are given a structural description and the dimension values printed on the part's engineering drawing (which dimension each value belongs to is not given; infer it). Use the printed values exactly.")
def describe(a):
    out = os.path.join(a.out, "gt_desc.jsonl"); done = {json.loads(l)["key"] for l in open(out)} if os.path.exists(out) else set()
    lock = threading.Lock()
    def one(png):
        k = os.path.basename(png)[:-4]
        if k in done: return
        img = base64.b64encode(open(png, "rb").read()).decode()
        txt, _ = fs["call"](fs["VISION"], [{"role": "user", "content": [{"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": img}}, {"type": "text", "text": DESC}]}], max_tokens=6000)
        with lock:
            with open(out, "a") as f: f.write(json.dumps({"key": k, "desc": txt.strip()}) + "\n")
    pngs = sorted(os.path.join(a.views, f) for f in os.listdir(a.views) if f.endswith(".png"))
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, pngs))   # Kimi cap 2
    print("DESCRIBE DONE", sum(1 for _ in open(out)))
def prompts(a):
    D = [json.loads(l) for l in open(os.path.join(a.out, "gt_desc.jsonl"))]
    json.dump({d["key"]: USER_PROMPT + "\n\nStructural description of the part (from its true 3D geometry): " + d["desc"] for d in D},
              open(os.path.join(a.out, "user_prompts_oracle_a.json"), "w"), indent=1)
    print("prompts", len(D))
def code(a):
    rend = json.load(open(a.renderers)); side = {k.rsplit("_v", 1)[0]: v for k, v in rend.items() if v}
    D = [json.loads(l) for l in open(os.path.join(a.out, "gt_desc.jsonl"))]
    os.makedirs(os.path.join(a.out, "b_stl"), exist_ok=True)
    out = os.path.join(a.out, "oracle_b.jsonl"); done = {json.loads(l)["key"] for l in open(out)} if os.path.exists(out) else set()
    wd = tempfile.mkdtemp(prefix="fporacle_", dir="/dev/shm"); lock = threading.Lock()
    def one(d):
        k = d["key"]
        if k in done or k not in side: return
        labels = [str(x.get("label")) for x in (side[k].get("annotations") or {}).values()]
        msgs = [{"role": "user", "content": f"Structural description: {d['desc']}\nDimensions printed on the drawing (mm): {', '.join(labels)}\nWrite the build123d program."}]
        rec = {"key": k, "ok": False, "turns": 0}
        for t in range(6):
            rec["turns"] = t + 1
            try: txt, _ = fs["call"]("claude-deepseek-ai/DeepSeek-V4.1-Flash[1m]", msgs, system=CODE_SYS, effort=rec.get("effort"))
            except Exception as e: rec["err"] = str(e); break
            c = fs["code_of"](txt)
            if not c:
                rec["effort"] = "low"; msgs += [{"role": "assistant", "content": txt or "(empty)"}, {"role": "user", "content": "Answer with a single ```python code block."}]; continue
            res, err = fs["run"](c, wd, k, a.py)
            if res and not err and res[2].get("solids", 0) < 1: err = "no solid produced"
            if not err:
                import shutil; shutil.move(res[0], os.path.join(a.out, "b_stl", k + ".stl")); rec.update(ok=True, code=c); break
            msgs += [{"role": "assistant", "content": f"```python\n{c}\n```"}, {"role": "user", "content": err + "\nFix the program; answer with the complete corrected ```python code block."}]
        with lock:
            with open(out, "a") as f: f.write(json.dumps(rec) + "\n")
    with ThreadPoolExecutor(a.workers) as ex: list(ex.map(one, D))
    print("CODE DONE", sum(1 for _ in open(out)))
ap = argparse.ArgumentParser(); ap.add_argument("stage"); ap.add_argument("--views"); ap.add_argument("--out", required=True)
ap.add_argument("--renderers"); ap.add_argument("--workers", type=int, default=16); ap.add_argument("--py", default=sys.executable)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
{"describe": describe, "prompts": prompts, "code": code}[a.stage](a)
