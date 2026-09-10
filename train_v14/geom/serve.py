"""End-to-end serving: engineering-drawing PNG(s) -> build123d script + STEP
with the agreement-gated verifier policy (RECIPE.md "Serving policy").

Per drawing, on ONE GPU with the generator (e55 final) and the verifier LoRA
(v3b-verifier-real-reg) loaded once (the adapter is toggled off for
generation, on for scoring):
  1. draw K candidates with the run's prompts/config (draw 0 greedy, draws
     1..K-1 sampled at T with top_p 0.95 -- the same recipe as
     bestofn_verifier_eval.py);
  2. execute every candidate in a temp dir (exec_harness.py -> STL + STEP);
  3. pairwise centered IoU among the executing candidates, medoid = the one
     with the highest mean agreement;
  4. gate: if the medoid's mean agreement >= --gate (0.85) serve the medoid
     ("vote"); otherwise score every executing candidate with the verifier's
     expected IoU (verifier_select_offline.reg_ev_scores) and serve the argmax
     ("verifier"). No executing candidate -> "none" (record only).
  5. write <out>/<stem>/chosen.py, chosen.step and record.json (every
     candidate's code / exec status / agreement / verifier score, the pairwise
     matrix, the policy branch and timings); <out>/serve_summary.json lists
     every drawing's outcome.

    CUDA_VISIBLE_DEVICES=0 python serve.py drawing.png [more.png | a_dir/] \
        --out served/ [--ckpt /dev/shm/.../base] [--k 8] [--gate 0.85]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import combinations

# candidate-vs-candidate agreement: coarse Monte-Carlo fallback (as consistency_rerank.py)
os.environ.setdefault("IOU_MC_POINTS", "20000")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

from PIL import Image  # noqa: E402

from geom_eval_worker import (  # noqa: E402
    HARNESS, PYTHON, RUNS_DIR, build_gen_messages, extract_code, load_model, normalize_adapter,
    run_config,
)
from iou import iou_pair  # noqa: E402
from verifier_select_offline import reg_ev_scores  # noqa: E402

# e55 = the round-5 recipe retrained on draftwright-0.4.23 sheets, the engine every render
# uses since 2026-09-10 (RECIPE "Training sheets re-rendered with draftwright 0.4.23").
DEFAULT_RUN = "e55-rft-real-u5-gt-dw423"
# The verifier LoRA was trained on e51's weights but is stacked on the generator here. Measured
# 2026-09-10 on the 144-part permissive bench: scored on e55's own weights it gives verifier
# 0.543 / gate 0.540 against 0.542 / 0.539 on its e51 base -- within noise, so one model is
# still loaded (results/ext/bo8_ext_dw423p_e55vb55_gated_summary.txt).
DEFAULT_VERIFIER_RUN = "v3b-verifier-real-reg"


def list_inputs(paths):
    out = []
    for p in paths:
        if os.path.isdir(p):
            out += sorted(glob.glob(os.path.join(p, "*.png")))
        else:
            out.append(p)
    return out


def load_image(path):
    img = Image.open(path)
    if img.mode == "RGBA":     # our sheets: black lines on transparent -> composite over white
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        return bg
    return img.convert("RGB")


def generate(model, proc, cfg, msgs_list, sample, temperature, top_p, max_new):
    import torch
    from qwen_vl_utils import process_vision_info
    tmpl = dict(enable_thinking=True, reasoning_effort=cfg.get("reasoning_effort", "medium")) \
        if cfg.get("trace_style", "think") == "think" else {}
    texts = [proc.apply_chat_template(m, add_generation_prompt=True, tokenize=False, **tmpl) for m in msgs_list]
    images, videos = process_vision_info(msgs_list)
    enc = proc(text=texts, images=images, videos=videos, return_tensors="pt", padding=True)
    enc = {k: (v.to(model.device) if hasattr(v, "to") else v) for k, v in enc.items()}
    kw = dict(max_new_tokens=max_new, pad_token_id=proc.tokenizer.pad_token_id or proc.tokenizer.eos_token_id)
    kw.update(dict(do_sample=True, temperature=temperature, top_p=top_p) if sample else dict(do_sample=False))
    with torch.no_grad():
        out = model.generate(**enc, **kw)
    return proc.tokenizer.batch_decode(out[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)


def execute(code, workdir, tag):
    """Run one candidate through the harness; returns (exec_ok, rc, stderr_tail, stl, step)."""
    cp, stl, step = (os.path.join(workdir, f"{tag}.{e}") for e in ("py", "stl", "step"))
    with open(cp, "w") as f:
        f.write(code)
    try:
        p = subprocess.run([PYTHON, HARNESS, cp, stl, step], capture_output=True, text=True, timeout=120)
        ok = p.returncode == 0 and os.path.exists(stl) and os.path.exists(step)
        return ok, p.returncode, ("" if ok else p.stderr[-1200:]), (stl if ok else None), (step if ok else None)
    except subprocess.TimeoutExpired:
        return False, -9, "timeout after 120s", None, None


def pairwise(cands, threads):
    """Fill pair_iou (K x K, None off the executing set) and each candidate's mean agreement."""
    ex = [j for j, c in enumerate(cands) if c["exec"]]
    k = len(cands)
    mat = [[None] * k for _ in range(k)]
    pairs = list(combinations(ex, 2))

    def one(ab):
        a, b = ab
        try:
            return iou_pair(cands[a]["stl"], cands[b]["stl"])["iou_centered"]
        except Exception:
            return 0.0
    with ThreadPoolExecutor(max_workers=threads) as pool:
        vals = list(pool.map(one, pairs))
    for (a, b), v in zip(pairs, vals):
        mat[a][b] = mat[b][a] = round(float(v), 4)
    for j in ex:
        others = [mat[j][i] or 0.0 for i in ex if i != j]
        cands[j]["agree"] = float(sum(others) / len(others)) if others else 0.0
    return mat, ex


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+", help="PNG files and/or directories of PNGs")
    ap.add_argument("--out", required=True)
    ap.add_argument("--run", default=DEFAULT_RUN, help="generator run (prompts / image config)")
    ap.add_argument("--ckpt", default="", help="generator weights (default runs/<run>/final; e.g. a /dev/shm copy)")
    ap.add_argument("--verifier", default="", help="verifier LoRA dir (default runs/<verifier-run>/final)")
    ap.add_argument("--verifier-run", default=DEFAULT_VERIFIER_RUN)
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--top-p", type=float, default=0.95)
    ap.add_argument("--gate", type=float, default=0.85, help="serve the medoid when its mean agreement >= gate")
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--max-new-tokens", type=int, default=2400)
    ap.add_argument("--threads", type=int, default=8, help="candidate execution / IoU threads")
    ap.add_argument("--keep-candidates", action="store_true", help="also keep every candidate's STEP")
    ap.add_argument("--keep-think", action="store_true", help="store the reasoning text in record.json")
    args = ap.parse_args()

    inputs = list_inputs(args.inputs)
    assert inputs, "no PNG inputs"
    cfg = run_config(args.run)
    assert cfg, f"no config for {args.run}"
    vcfg = run_config(args.verifier_run)
    assert vcfg, f"no config for {args.verifier_run}"
    ckpt = args.ckpt or os.path.join(RUNS_DIR, args.run, "final")
    verifier = args.verifier or os.path.join(RUNS_DIR, args.verifier_run, "final")
    os.makedirs(args.out, exist_ok=True)
    print(f"[serve] {len(inputs)} drawing(s); generator {ckpt}; verifier {verifier}; "
          f"K={args.k} T={args.temperature} gate={args.gate}", flush=True)

    # --- models: generator weights once, verifier LoRA on top (toggled per phase)
    t0 = time.time()
    import torch
    from peft import PeftModel
    cfg = dict(cfg, model_id=ckpt)      # processor + base class come from the generator weights
    model, proc = load_model(ckpt, "hf", cfg)
    normalize_adapter(verifier)
    model = PeftModel.from_pretrained(model, verifier)
    model.eval()
    t_load = time.time() - t0
    print(f"[serve] models loaded in {t_load:.0f}s", flush=True)

    # --- 1. generation: greedy draw 0 for every drawing, then sampled draws (batched)
    t0 = time.time()
    images = [load_image(p) for p in inputs]
    cands = [[None] * args.k for _ in inputs]
    jobs = [(i, 0) for i in range(len(inputs))] + [(i, d) for d in range(1, args.k) for i in range(len(inputs))]
    with model.disable_adapter():
        for sample in (False, True):
            todo = [(i, d) for i, d in jobs if (d > 0) == sample]
            for b in range(0, len(todo), args.batch):
                chunk = todo[b:b + args.batch]
                outs = generate(model, proc, cfg, [build_gen_messages(images[i], cfg) for i, _ in chunk],
                                sample, args.temperature, args.top_p, args.max_new_tokens)
                if sum("!!!!!!!!" in t for t in outs) > max(1, len(outs) // 3):
                    print("[serve] WARNING: degenerate generations ('!!!' floods) - bad GPU?", flush=True)
                for (i, d), text in zip(chunk, outs):
                    think = text.split("</think>", 1)[0].replace("<think>", "").strip() if "</think>" in text else ""
                    cands[i][d] = {"draw": d, "sampled": d > 0, "code": extract_code(text), "exec": False,
                                   "rc": None, "stderr_tail": "", "agree": None, "verifier": None,
                                   **({"think": think} if args.keep_think else {})}
                print(f"[serve] {'sampled' if sample else 'greedy'} draws {b + len(chunk)}/{len(todo)}", flush=True)
    t_gen = time.time() - t0

    summary = []
    with tempfile.TemporaryDirectory(prefix="serve_") as td:
        # --- 2. execute every candidate (all drawings at once)
        t0 = time.time()
        def run_one(ij):
            i, j = ij
            c = cands[i][j]
            if not c["code"]:
                c["rc"] = "no code"
                return
            c["exec"], c["rc"], c["stderr_tail"], c["stl"], c["step"] = execute(c["code"], td, f"{i}_{j}")
        with ThreadPoolExecutor(max_workers=args.threads) as pool:
            list(pool.map(run_one, [(i, j) for i in range(len(inputs)) for j in range(args.k)]))
        t_exec = time.time() - t0

        # --- 3./4. per drawing: agreement, gate, verifier when needed
        for i, path in enumerate(inputs):
            stem = os.path.splitext(os.path.basename(path))[0]
            odir = os.path.join(args.out, stem)
            os.makedirs(odir, exist_ok=True)
            cs = cands[i]
            t0 = time.time()
            mat, ex = pairwise(cs, args.threads)
            t_iou = time.time() - t0
            rec = {"input": os.path.abspath(path), "run": args.run, "ckpt": ckpt, "verifier": verifier,
                   "k": args.k, "temperature": args.temperature, "top_p": args.top_p, "gate": args.gate,
                   "n_exec": len(ex), "pair_iou": mat, "medoid": None, "agree_medoid": 0.0,
                   "verifier_argmax": None, "policy": "none", "chosen": None,
                   "timing": {"load_s": t_load, "gen_s_all": t_gen, "exec_s_all": t_exec, "pair_iou_s": t_iou,
                              "verifier_s": 0.0}}
            chosen = None
            if ex:
                jm = max(ex, key=lambda j: cs[j]["agree"])        # first on ties (draw order)
                rec["medoid"], rec["agree_medoid"] = jm, cs[jm]["agree"]
                if len(ex) > 1 and cs[jm]["agree"] >= args.gate:
                    rec["policy"], chosen = "vote", jm
                else:
                    t0 = time.time()
                    evs = reg_ev_scores(model, proc, [images[i]] * len(ex), [cs[j]["code"] for j in ex], vcfg,
                                        batch=args.batch, log=None)
                    for j, ev in zip(ex, evs):
                        cs[j]["verifier"] = ev
                    jv = max(ex, key=lambda j: cs[j]["verifier"])
                    rec["verifier_argmax"], rec["policy"], chosen = jv, "verifier", jv
                    rec["timing"]["verifier_s"] = time.time() - t0
            rec["chosen"] = chosen
            if chosen is not None:
                with open(os.path.join(odir, "chosen.py"), "w") as f:
                    f.write(cs[chosen]["code"])
                shutil.copyfile(cs[chosen]["step"], os.path.join(odir, "chosen.step"))
            if args.keep_candidates:
                for j in ex:
                    shutil.copyfile(cs[j]["step"], os.path.join(odir, f"cand_{j}.step"))
            rec["candidates"] = [{k: v for k, v in c.items() if k not in ("stl", "step")} for c in cs]
            with open(os.path.join(odir, "record.json"), "w") as f:
                json.dump(rec, f, indent=1)
            line = {"stem": stem, "policy": rec["policy"], "chosen": chosen, "n_exec": len(ex),
                    "agree_medoid": rec["agree_medoid"], "medoid": rec["medoid"],
                    "verifier_argmax": rec["verifier_argmax"],
                    "verifier_scores": {j: cs[j]["verifier"] for j in ex if cs[j]["verifier"] is not None}}
            summary.append(line)
            print(f"[serve] {stem}: {len(ex)}/{args.k} executed, medoid {rec['medoid']} agreement "
                  f"{rec['agree_medoid']:.3f} -> policy {rec['policy']}, chosen draw {chosen}"
                  + (f" (verifier argmax {rec['verifier_argmax']}, scores "
                     + ", ".join(f"{j}:{cs[j]['verifier']:.2f}" for j in ex) + ")"
                     if rec["policy"] == "verifier" else ""), flush=True)
    with open(os.path.join(args.out, "serve_summary.json"), "w") as f:
        json.dump({"inputs": inputs, "ckpt": ckpt, "verifier": verifier, "k": args.k, "gate": args.gate,
                   "results": summary}, f, indent=1)
    n_pol = {p: sum(r["policy"] == p for r in summary) for p in ("vote", "verifier", "none")}
    print(f"[serve] done: {n_pol}; outputs under {args.out}", flush=True)


if __name__ == "__main__":
    main()
