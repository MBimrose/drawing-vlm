"""STaR rationalization of the guide bank in DeepSeek's OWN voice, T0 regime (2026-10-07, dsgrpo3).
For each bank part (best-known GT-verified program, Qwen search), the served DeepSeek policy gets the T0 request
(/v1/messages, vis_repair SYS, [sheet, SCRATCH], effort "low" = Reasoning Effort 25, T 1.0) with the verified program
appended as a hint (build_guide_bank.HINT). Kept: its reasoning (thinking block) + its reply text with the longest code
block REPLACED by the verified program -> trained later under the NORMAL prompt (no hint) as a guided group member.
Dropped: leaks of the hint in the reasoning or the reply notes, empty/truncated reasoning, > --max-tokens output.
The bank's own `think` (Qwen's voice) is never used.
    python dsv41_t0_rationalize.py --banks c4:<json>:<bench>,c2:...,c1:... --n 1000 --base-url http://127.0.0.1:8500 --out bank_ds.json"""
import argparse, json, os, pickle, random, re, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from dsv41_t0_rollout import SCRATCH, img_block, call, code_of
from build_guide_bank import HINT, LEAK
LEAK2 = re.compile(r"\b(hint|reference implementation|the code (above|below|given)|program (shown|given|provided))\b"
                   r"|\b(provided|given|verified|supplied|reference|existing|target)\b[^.\n]{0,40}\b(program|code|solution|script)\b"
                   r"|\b(user|they|you)\s+(provided|gave|give|gives|supplied|shared|asked)\b|\bthe (solution|answer) (is|was)\b", re.I)
# 2026-10-07: the plain STaR hint (the model reasons with the program in view) failed in the T0 regime: 87/100 traces
# said "the user provided a verified program, just output it". WRITE mode instead asks DeepSeek to WRITE the solver's
# reasoning trace (as its answer text) for the drawing that leads to this program, in first person, never mentioning it.
WRITE = ("\n\nBelow is a correct build123d program for this drawing. Write the reasoning you would go through while solving "
         "this drawing yourself, BEFORE you knew the answer: read each view and the printed dimensions, identify the base "
         "feature, every added/removed feature (holes, pockets, slots, bosses, fillets, chamfers, patterns) with its size and "
         "position, then the construction order -- arriving exactly at this program's construction and values. Write it in "
         "the first person as working notes (\"The front view shows ... so ...\"). Never mention or allude to a given, "
         "provided or reference program, solution or hint. Output ONLY the reasoning notes, no code.\n```python\n{code}\n```")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--banks", required=True, help="tag:bank.json:bench,... (bench = dir with eval_cache_v15.pkl + gt_meshes_v15)")
    ap.add_argument("--n", type=int, default=1000); ap.add_argument("--base-url", required=True); ap.add_argument("--model", default="pol")
    ap.add_argument("--out", required=True); ap.add_argument("--workers", type=int, default=48)
    ap.add_argument("--max-tokens", type=int, default=30000); ap.add_argument("--min-iou", type=float, default=0.5)
    ap.add_argument("--mode", choices=["hint", "write"], default="write")
    a = ap.parse_args()
    items = []
    for spec in a.banks.split(","):
        tag, bf, bench = spec.split(":")
        bank = json.load(open(bf))
        S = pickle.load(open(os.path.join(bench, "eval_cache_v15.pkl"), "rb"))["samples"]
        n0 = len(items)
        for k, v in bank.items():
            if k in S and v.get("code") and v["iou"] >= a.min_iou and os.path.exists(os.path.join(bench, "gt_meshes_v15", k + ".stl")):
                items.append((bench, k, v["code"].strip(), float(v["iou"]), S[k]["png"]))
        print(f"[rat] {tag}: {len(items) - n0}/{len(bank)} usable", flush=True)
        del S
    random.Random(0).shuffle(items); items = items[: a.n]
    out = json.load(open(a.out)) if os.path.exists(a.out) else {}
    todo = [it for it in items if it[1] not in out]
    print(f"[rat] {len(items)} selected, {len(out)} done, {len(todo)} to rationalize", flush=True)
    lock = threading.Lock(); t0 = time.time(); n = [0]; stats = {"ok": 0, "leak": 0, "trunc": 0, "err": 0, "empty": 0}

    def one(it):
        bench, k, code, iou, png = it
        hint = WRITE if a.mode == "write" else HINT
        msgs = [{"role": "user", "content": [img_block(png), {"type": "text", "text": SCRATCH + hint.format(code=code)}]}]
        try:
            think, txt, stop, usage = call(a.base_url, a.model, msgs, a.max_tokens, None)
        except Exception as ex:
            r = {"status": "err", "err": str(ex)[:200]}
        else:
            if a.mode == "write":   # the trace is the ANSWER text (code blocks stripped); the reply trained = the bank program
                think = re.sub(r"```.*?```", "", txt or "", flags=re.S).strip(); txt = f"```python\n{code}\n```"
            if stop == "max_tokens":
                r = {"status": "trunc"}
            elif len(think.strip()) < (500 if a.mode == "write" else 200):
                r = {"status": "empty"}
            else:
                notes = (txt or "").split("```")[0]
                if LEAK.search(think) or LEAK2.search(think) or LEAK.search(notes) or LEAK2.search(notes):
                    r = {"status": "leak"}
                else:
                    own = code_of(txt)
                    reply = txt.replace(own, code + "\n", 1) if own else f"```python\n{code}\n```"
                    r = {"status": "ok", "think": think, "reply": reply, "own_code_same": (own or "").strip() == code,
                         "output_tokens": usage.get("output_tokens")}
        r.update(bench=bench, code=code, iou=iou)
        with lock:
            out[k] = r; stats[r["status"]] += 1; n[0] += 1
            if n[0] % 25 == 0:
                json.dump(out, open(a.out + ".tmp", "w")); os.replace(a.out + ".tmp", a.out)
                print(f"[rat] {n[0]}/{len(todo)} {stats} {(time.time() - t0) / 60:.1f} min", flush=True)

    with ThreadPoolExecutor(a.workers) as ex:
        list(ex.map(one, todo))
    json.dump(out, open(a.out + ".tmp", "w")); os.replace(a.out + ".tmp", a.out)
    ok = [v for v in out.values() if v["status"] == "ok"]
    print(f"[rat] done: {len(ok)}/{len(out)} kept {stats}; own code identical to the bank program in "
          f"{sum(v['own_code_same'] for v in ok)}; {(time.time() - t0) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
