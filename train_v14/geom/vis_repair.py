"""Closed-loop visual repair (first-principles test, 2026-09-29).

H3 showed wrong candidates visibly contradict the input sheet, yet the pipeline is open-loop: the model never sees
what its program draws. Here a vision LLM (DeepSeek-V4.1-Flash on the lab hub, x-hub-user attributed, DS_CAP-limited)
gets, per round: the target sheet, the program, and -- arm "vis" -- the sheet that program produces (same draftwright
renderer, same layout seed), and returns a corrected program. Arm "blind" is identical without the candidate sheet
(isolates the value of seeing the render). Arm "scratch" starts from nothing (round 0 = DeepSeek alone from the sheet).
Every round's program is scored by centred IoU vs GT (evaluation only; never shown).
    python vis_repair.py --bench <bench dir> --picks e55_vote_picks.json --arm vis --rounds 3 --out <jsonl>"""
import argparse, base64, json, os, pickle, sys, tempfile, threading, subprocess
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "mech", "familysynth")); sys.path.insert(0, HERE)
from family_synth import call, code_of, _DS
from render_compare import render_candidate
from rc_metric2 import sheet_score_v3
IOU_ONCE = os.path.join(HERE, "iou_once.py")

SYS = """You are an expert CAD engineer. You write build123d (Python) programs that reproduce parts from engineering drawings exactly.
Program conventions: `from build123d import *`, named dimension variables, final solid in `part`, end with `export_step(part, "output.step")`."""
VIS = """Image 1 is the TARGET engineering drawing. Image 2 is the drawing produced by the same drafting tool from the CURRENT program below.
Compare them view by view: overall envelope and proportions, each view's outline, walls/shells and their thickness, pockets, bosses, ribs, holes (count, size, position), slots, fillets/chamfers, and the printed dimension values.
List the discrepancies in a few short bullets, then output the complete corrected program in a single ```python block that makes image 2 match image 1. If they already match, output the program unchanged. Do not deliberate at length."""
BLIND = """The image is the TARGET engineering drawing. Below is the CURRENT program, which is meant to reproduce it but may be wrong.
Check it against the drawing view by view: overall envelope and proportions, each view's outline, walls/shells and their thickness, pockets, bosses, ribs, holes (count, size, position), slots, fillets/chamfers, and the printed dimension values.
List the discrepancies in a few short bullets, then output the complete corrected program in a single ```python block. If it is already right, output the program unchanged. Do not deliberate at length."""
SCRATCH = """The image is an engineering drawing of one part. Read every view and printed dimension, then write the build123d program that reproduces the part exactly, in a single ```python block. Do not deliberate at length."""

def img(b): return {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": base64.b64encode(b).decode()}}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--bench"); ap.add_argument("--picks"); ap.add_argument("--arm", choices=["vis", "blind", "scratch"])
    ap.add_argument("--rounds", type=int, default=3); ap.add_argument("--out"); ap.add_argument("--workers", type=int, default=16); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--adopt", choices=["exec", "v3"], default="exec"); ap.add_argument("--margin", type=float, default=0.02)
    ap.add_argument("--py", default=sys.executable); ap.add_argument("--rpy"); ap.add_argument("--script-dir")
    a = ap.parse_args()
    cache = pickle.load(open(os.path.join(a.bench, "eval_cache_v15.pkl"), "rb"))["samples"]
    picks = json.load(open(a.picks)); keys = sorted(picks)[: a.limit or None]
    done = {json.loads(l)["key"] for l in open(a.out)} if os.path.exists(a.out) else set(); lock = threading.Lock()
    def score(code, k):
        """-> (iou, exec ok, error text)"""
        with tempfile.TemporaryDirectory(prefix="vr_", dir="/dev/shm") as td:
            cp, stl, stp = [os.path.join(td, "c" + e) for e in (".py", ".stl", ".step")]; open(cp, "w").write(code)
            try:
                q = subprocess.run([a.py, os.path.join(HERE, "exec_harness.py"), cp, stl, stp], capture_output=True, text=True, timeout=120)
                if q.returncode or not os.path.exists(stl): return 0.0, False, "\n".join((q.stderr or q.stdout or "no output").strip().splitlines()[-15:])
                p = subprocess.run([a.py, IOU_ONCE, stl, os.path.join(a.bench, "gt_meshes_v15", k + ".stl")], capture_output=True, text=True, timeout=300)
                return float(json.loads(p.stdout)["iou_centered"]), True, ""
            except subprocess.TimeoutExpired: return 0.0, False, "execution timed out"
            except Exception as ex: return 0.0, True, str(ex)[:200]
    def rv3(code, k):
        png, info = render_candidate(code, k, a.py, a.rpy, a.script_dir, 120, 300)
        if png is None: return None, 0.0, info
        try: return png, float(sheet_score_v3(cache[k]["png"], png)["v3"]), info
        except Exception as ex: return png, 0.0, {"error": str(ex)[:100]}
    def one(k):
        if k in done: return
        target = cache[k]["png"]; code = None if a.arm == "scratch" else picks[k]["code"]; hist = []
        cur_png = cur_v3 = None
        if code:
            s, e, _ = score(code, k); hist.append({"round": 0, "iou": s, "exec": e, "code": code})
            if a.adopt == "v3": cur_png, cur_v3, _ = rv3(code, k); hist[-1]["v3"] = cur_v3
        for r in range(1, a.rounds + 1) if code else range(0, a.rounds + 1):
            if code is None:
                content = [img(target), {"type": "text", "text": SCRATCH}]
            elif a.arm == "vis":
                png, info = (cur_png, {"stage": "render", "error": "cached render failed"}) if a.adopt == "v3" else render_candidate(code, k, a.py, a.rpy, a.script_dir, 120, 300)
                if png is None:
                    content = [img(target), {"type": "text", "text": BLIND + f"\n\nNote: the current program could not be drawn ({info.get('stage')}: {info.get('error','')[-200:]}); fix that too.\n\nCURRENT program:\n```python\n{code}\n```"}]
                else:
                    content = [img(target), img(png), {"type": "text", "text": VIS + f"\n\nCURRENT program:\n```python\n{code}\n```"}]
            else:
                content = [img(target), {"type": "text", "text": BLIND + f"\n\nCURRENT program:\n```python\n{code}\n```"}]
            msgs = [{"role": "user", "content": content}]
            for fix in range(3):   # up to 2 in-round fixes of a non-executing edit, with the traceback
                try: txt, u = call(_DS, msgs, system=SYS, max_tokens=30000, effort="low")
                except Exception as ex: txt = None; hist.append({"round": r, "err": str(ex)[:200]}); break
                new = code_of(txt)
                if not new:
                    msgs += [{"role": "assistant", "content": txt or "(empty)"}, {"role": "user", "content": "Answer now with the complete program in a single ```python block; do not deliberate."}]; continue
                s_, e, err = score(new, k)
                if e: break
                msgs += [{"role": "assistant", "content": f"```python\n{new}\n```"}, {"role": "user", "content": f"This program fails to execute:\n{err}\nFix it and answer with the complete program in a single ```python block."}]
            if txt is None: break
            if not new: hist.append({"round": r, "nocode": True}); continue
            hist.append({"round": r, "iou": s_, "exec": e, "fixes": fix, "code": new, "notes": (txt or "").split("```")[0][-1500:]})
            if e and a.adopt == "exec": code = new          # a non-executing edit is not adopted
            elif e:                                          # adopt only if the render matches the target better (label-free)
                npng, nv3, _ = rv3(new, k); hist[-1]["v3"] = nv3
                if npng is not None and nv3 > (cur_v3 or 0.0) + a.margin:
                    code, cur_png, cur_v3 = new, npng, nv3; hist[-1]["adopted"] = True
        with lock:
            with open(a.out, "a") as f: f.write(json.dumps({"key": k, "arm": a.arm, "hist": hist}) + "\n")
    def safe(k):
        try: one(k)
        except Exception:
            import traceback; print("[vr] error", k, traceback.format_exc()[-500:], flush=True)
    with ThreadPoolExecutor(a.workers) as ex: list(ex.map(safe, keys))
    print("VR DONE", a.arm, flush=True)

if __name__ == "__main__":
    main()
