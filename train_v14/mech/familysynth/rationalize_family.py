"""Style-matched rationalized think traces for family ground-truth programs (H6c, 2026-09-28).

H6b: family GT programs trained with EMPTY think lift the real bench a lot in no-think mode (vote 0.275 -> 0.457)
but nothing in think mode, which is how we serve (same format trap as e54). e56 gave GT rows base-model plans and
lost general skill -- those plans were ~2,000 chars and off e55's own style. Here DeepSeek-V4.1-Flash (vision, hub,
uncapped, x-hub-user attributed) sees the sheet AND the correct program and writes the plan in e55's own terse
numbered process-plan style (few-shot from e55's accepted RFT traces, 350-1000 chars), citing printed values.
Plans that mention code/programs/variables or fall outside the length band are dropped.
    python rationalize_family.py --tier <tier dir with accepted-000.jsonl + png/> --out <tier_rat dir> [--workers 48]"""
import argparse, base64, json, os, re, shutil, sys, threading
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from family_synth import call, _DS
EX = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "style_examples.json")))

PROMPT = """The image is an engineering drawing of a part. Below it you are given the part's correct build123d model, for YOUR reference only.
Write the short numbered manufacturing/modelling plan that a skilled machinist would jot down while reading THIS DRAWING before modelling it.
Requirements:
- It must read as derived purely from the drawing: cite the dimensions and callouts as PRINTED on the sheet (the sheet is authoritative for values;
  derive any unprinted value arithmetically from printed ones, e.g. "half of the 80 length"). Consistent with the correct model's shape and features.
- Cover the overall stock/envelope, the main body construction, then every feature (walls, pockets, bosses, ribs, holes with counts/patterns, slots, fillets, chamfers) in build order.
- Never mention code, programs, scripts, variables, parameters, CAD software, build123d, or that a model was provided.
- Style: plain numbered lines exactly like these examples, terse, 4-10 lines, 350-1000 characters total. Output ONLY the plan. Do not deliberate at length.

Example plans (other parts):
""" + "\n\n".join(f"<example>\n{e}\n</example>" for e in EX[:4])

BAD = re.compile(r"\b(code|program|script|variable|parameter|build123d|python|cad software|reference model|provided model|the model given)\b", re.I)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tier"); ap.add_argument("--out"); ap.add_argument("--workers", type=int, default=48)
    ap.add_argument("--min-chars", type=int, default=250); ap.add_argument("--max-chars", type=int, default=1400)
    a = ap.parse_args(); os.makedirs(os.path.join(a.out, "png"), exist_ok=True)
    rows = [json.loads(l) for l in open(os.path.join(a.tier, "accepted-000.jsonl"))]
    raw = os.path.join(a.out, "raw.jsonl"); done = {j["key"] for j in map(json.loads, open(raw)) if j["plan"]} if os.path.exists(raw) else set()   # empty plans are retried
    lock = threading.Lock(); st = {"n": 0}
    def one(r):
        if r["key"] in done: return
        img = base64.b64encode(open(os.path.join(a.tier, "png", r["key"] + ".png"), "rb").read()).decode()
        code = re.sub(r"#.*", "", r["code"])   # comments would leak intent words
        try:
            txt, u = call(_DS, [{"role": "user", "content": [{"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": img}},
                  {"type": "text", "text": PROMPT + f"\n\nCorrect model (reference only):\n```python\n{code}\n```"}]}], max_tokens=30000, effort="low")   # 6000: 63% of calls thought to the cap with no plan
        except Exception as e:
            txt, u = "", {"err": str(e)}
        plan = txt.strip()
        with lock:
            with open(raw, "a") as f: f.write(json.dumps({"key": r["key"], "plan": plan, "usage": u}) + "\n")
            st["n"] += 1
            if st["n"] % 50 == 0: print(f"[rat] {st['n']}/{len(rows)}", flush=True)
    with ThreadPoolExecutor(a.workers) as ex: list(ex.map(one, rows))
    plans = {}
    for l in open(raw):
        j = json.loads(l); p = j["plan"]
        if not p: continue
        if a.min_chars <= len(p) <= a.max_chars and re.match(r"^1\.", p) and not BAD.search(p): plans[j["key"]] = p
    with open(os.path.join(a.out, "accepted-000.jsonl"), "w") as f:
        for r in rows:
            if r["key"] in plans:
                f.write(json.dumps(dict(r, think=plans[r["key"]])) + "\n"); shutil.copy(os.path.join(a.tier, "png", r["key"] + ".png"), os.path.join(a.out, "png"))
    print(f"RAT DONE {len(plans)}/{len(rows)} plans kept", flush=True)

if __name__ == "__main__":
    main()
