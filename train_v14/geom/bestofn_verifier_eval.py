"""Best-of-N with selection policies compared on the SAME candidates:
  first_exec — first candidate (draw order) that executes  (current serving)
  verifier   — executing candidate with the highest verifier-predicted IoU
  oracle     — executing candidate with the highest TRUE IoU (upper bound)
Draw 0 is greedy, draws 1..K-1 sampled at T. Every candidate is executed and
IoU-scored; the verifier scores every executing candidate. Also reports the
verifier's Spearman correlation with true IoU and its oracle-hit rate.

    python bestofn_verifier_eval.py --ckpt <policy_hf> --run <run> \
        --verifier <adapter_or_hf_dir> --verifier-run v1-verifier-lora \
        --n 96 --k 8 --out results/bo8_verifier.json
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import re
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

from collate_v14 import VERIFIER_SYSTEM, VERIFIER_USER, wrap_python  # noqa: E402
from data_v14 import EVAL_CACHE, EVAL_CACHE_V15, _decode_png  # noqa: E402
from geom_eval_worker import (  # noqa: E402
    build_gen_messages, classify_ckpt, extract_code, load_model, run_config,
)
from iou import iou_pair  # noqa: E402
from rft_generate import exec_to_stl  # noqa: E402


def spearman(a, b):
    import numpy as np
    if len(a) < 3:
        return float("nan")
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--kind", default="hf")
    ap.add_argument("--run", required=True)
    ap.add_argument("--verifier", default="", help="empty: skip verifier scoring (oracle/first-exec K-curve only)")
    ap.add_argument("--verifier-run", default="v1-verifier-lora")
    ap.add_argument("--verifier-mode", default="regression",
                    choices=["regression", "binary"],
                    help="binary: rank by log-odds of the yes token (v2)")
    ap.add_argument("--n", type=int, default=96)
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--max-new-tokens", type=int, default=2400)
    ap.add_argument("--out", required=True)
    ap.add_argument("--shard", type=int, default=0, help="this worker's index (keys[shard::nshards])")
    ap.add_argument("--nshards", type=int, default=1, help="run N single-GPU workers and merge with merge_bo_shards.py")
    args = ap.parse_args()

    cfg = run_config(args.run)
    if int(cfg.get("data_version", 1)) == 2:
        cache_path, pool = EVAL_CACHE_V15, "certified"
        gt_dir = os.path.join(os.path.dirname(EVAL_CACHE), "gt_meshes_v15")
    else:
        cache_path, pool = EVAL_CACHE, "all"
        gt_dir = os.path.join(os.path.dirname(EVAL_CACHE), "gt_meshes_v14")
    with open(cache_path, "rb") as f:
        cache = pickle.load(f)
    keys = [k for k in cache["pools"][pool]
            if os.path.exists(os.path.join(gt_dir, f"{k}.stl"))][: args.n]
    keys = keys[args.shard::args.nshards]
    samples = [{"uuid": k, "image": _decode_png(cache["samples"][k]["png"])} for k in keys]
    print(f"[bo{args.k}+verifier] {len(samples)} samples, T={args.temperature}", flush=True)

    import torch
    from qwen_vl_utils import process_vision_info

    model, processor = load_model(args.ckpt, args.kind, cfg)

    def gen_batch(msgs_list, sample_mode, tmpl_cfg, mdl, proc, max_new):
        tmpl = dict(enable_thinking=True,
                    reasoning_effort=tmpl_cfg.get("reasoning_effort", "medium")) \
            if tmpl_cfg.get("trace_style", "think") == "think" else {}
        texts = [proc.apply_chat_template(m, add_generation_prompt=True, tokenize=False, **tmpl)
                 for m in msgs_list]
        images, videos = process_vision_info(msgs_list)
        enc = proc(text=texts, images=images, videos=videos, return_tensors="pt", padding=True)
        enc = {k2: (v.to(mdl.device) if hasattr(v, "to") else v) for k2, v in enc.items()}
        kw = dict(max_new_tokens=max_new,
                  pad_token_id=proc.tokenizer.pad_token_id or proc.tokenizer.eos_token_id)
        if sample_mode:
            kw.update(do_sample=True, temperature=args.temperature, top_p=0.95)
        else:
            kw["do_sample"] = False
        with torch.no_grad():
            out = mdl.generate(**enc, **kw)
        return proc.tokenizer.batch_decode(out[:, enc["input_ids"].shape[1]:],
                                           skip_special_tokens=True)

    # ---- 1. draw K candidates for every sample ----
    cands = [[] for _ in samples]   # per sample: list of dicts
    # Per-draw checkpoint so a long run (1k parts x K draws) survives a crash.
    partial = args.out + ".partial.json"
    keys_list = [s["uuid"] for s in samples]
    start_draw = 0
    if os.path.exists(partial):
        pd = json.load(open(partial))
        if pd.get("keys") == keys_list and pd.get("k", 0) <= args.k and pd["cands"] and pd["cands"][0]:
            cands, start_draw = pd["cands"], len(pd["cands"][0])
            print(f"[bo{args.k}] resuming from {partial}: {start_draw} draws done", flush=True)
    for draw in range(start_draw, args.k):
        outs = []
        for b in range(0, len(samples), args.batch):
            chunk = samples[b:b + args.batch]
            msgs = [build_gen_messages(s["image"], cfg) for s in chunk]
            outs.extend(gen_batch(msgs, draw > 0, cfg, model, processor, args.max_new_tokens))
            if sum("!!!!!!!!" in t for t in outs) > max(4, len(outs) // 3):
                raise RuntimeError("degenerate generations — bad GPU?")
        for i, text in enumerate(outs):
            think = text.split("</think>", 1)[0].replace("<think>", "").strip() if "</think>" in text else ""
            cands[i].append({"draw": draw, "code": extract_code(text), "exec": False, "iou": 0.0,
                             "think": think})   # kept so accepted candidates can become an RFT tier
        print(f"[bo{args.k}] draw {draw} done", flush=True)
        with open(partial, "w") as f:
            json.dump({"keys": keys_list, "k": args.k, "cands": cands}, f)

    # ---- 2. execute + score every candidate ----
    with tempfile.TemporaryDirectory(prefix="bov_") as td:
        def run_one(i, j):
            c = cands[i][j]
            if not c["code"]:
                return
            stl = os.path.join(td, f"{samples[i]['uuid']}_{j}.stl")
            if exec_to_stl(c["code"], stl, td, f"{samples[i]['uuid']}_{j}"):
                c["exec"] = True
                c["iou"] = iou_pair(stl, os.path.join(gt_dir, f"{samples[i]['uuid']}.stl"))["iou_centered"]
        with ThreadPoolExecutor(max_workers=8) as ex:
            list(ex.map(lambda p: run_one(*p), [(i, j) for i in range(len(samples)) for j in range(args.k)]))
    n_exec = sum(c["exec"] for cs in cands for c in cs)
    print(f"[bo{args.k}] executed {n_exec}/{len(samples) * args.k} candidates", flush=True)

    # ---- 3. verifier scores every executing candidate ----
    del model
    torch.cuda.empty_cache()
    if not args.verifier:
        for cs in cands:
            for c in cs:
                c["pred"] = c["iou"] * 0.0   # verifier policy degenerates to first-exec
        _skip = True
    else:
        _skip = False
    vcfg = run_config(args.verifier_run) or cfg
    if _skip:
        todo = []
    else:
        verifier, vproc = load_model(args.verifier, classify_ckpt(args.verifier), vcfg)
    todo = [] if _skip else [(i, j) for i in range(len(samples)) for j in range(args.k) if cands[i][j]["exec"]]
    for b in range(0, len(todo), args.batch):
        chunk = todo[b:b + args.batch]
        msgs = [[{"role": "system", "content": [{"type": "text", "text": VERIFIER_SYSTEM}]},
                 {"role": "user", "content": [
                     {"type": "image", "image": samples[i]["image"]},
                     {"type": "text", "text": VERIFIER_USER.format(code=wrap_python(cands[i][j]["code"]))}]}]
                for i, j in chunk]
        if args.verifier_mode == "binary":
            # one forward step; score = logit(yes) - logit(no) on the first token
            tok = vproc.tokenizer
            yes_ids = {tok.encode(v, add_special_tokens=False)[0] for v in ("yes", " yes", "Yes")}
            no_ids = {tok.encode(v, add_special_tokens=False)[0] for v in ("no", " no", "No")}
            tmpl = dict(enable_thinking=True,
                        reasoning_effort=vcfg.get("reasoning_effort", "medium"))                 if vcfg.get("trace_style", "think") == "think" else {}
            texts = [vproc.apply_chat_template(m2, add_generation_prompt=True,
                                               tokenize=False, **tmpl) for m2 in msgs]
            images, videos = process_vision_info(msgs)
            enc = vproc(text=texts, images=images, videos=videos,
                        return_tensors="pt", padding=True)
            enc = {k2: (v.to(verifier.device) if hasattr(v, "to") else v)
                   for k2, v in enc.items()}
            with torch.no_grad():
                out = verifier.generate(
                    **enc, max_new_tokens=1, do_sample=False,
                    output_scores=True, return_dict_in_generate=True,
                    pad_token_id=tok.pad_token_id or tok.eos_token_id)
            logits = out.scores[0].float()
            for row, (i, j) in enumerate(chunk):
                ly = max(logits[row, t].item() for t in yes_ids)
                ln = max(logits[row, t].item() for t in no_ids)
                cands[i][j]["pred"] = ly - ln
        else:
            outs = gen_batch(msgs, False, vcfg, verifier, vproc, 8)
            for (i, j), text in zip(chunk, outs):
                m = re.search(r"\d*\.?\d+", text)
                cands[i][j]["pred"] = float(m.group(0)) if m else 0.0

    # ---- 4. selection policies ----
    def pick(cs, key):
        ex = [c for c in cs if c["exec"]]
        if not ex:
            return None
        return max(ex, key=key) if key else ex[0]
    pol = {"first_exec": lambda cs: pick(cs, None),
           "verifier": lambda cs: pick(cs, lambda c: c.get("pred", -1e9)),
           "oracle": lambda cs: pick(cs, lambda c: c["iou"]),
           "greedy_only": lambda cs: (cs[0] if cs[0]["exec"] else None)}
    metrics = {}
    for name, fn in pol.items():
        ious = []
        for cs in cands:
            c = fn(cs)
            ious.append(c["iou"] if c else 0.0)
        n = len(ious); ious_s = sorted(ious)
        metrics[name] = {"exec_ok_frac": sum(i > 0 for i in ious) / n, "iou_mean": sum(ious) / n,
                         "iou_median": ious_s[n // 2], "frac_iou50": sum(i >= 0.5 for i in ious) / n,
                         "frac_iou85": sum(i >= 0.85 for i in ious) / n}
    preds = [c["pred"] for cs in cands for c in cs if c["exec"]]
    trues = [c["iou"] for cs in cands for c in cs if c["exec"]]
    hits = sum(1 for cs in cands if pol["verifier"](cs) and pol["oracle"](cs)
               and pol["verifier"](cs)["iou"] >= pol["oracle"](cs)["iou"] - 1e-6)
    metrics["verifier_spearman"] = spearman(preds, trues)
    metrics["verifier_oracle_hit_frac"] = hits / len(cands)
    # oracle mean as a function of k (how the ceiling grows with draws)
    ocurve = {}
    for kk in range(1, args.k + 1):
        vals = []
        for cs in cands:
            ex = [c["iou"] for c in cs[:kk] if c["exec"]]
            vals.append(max(ex) if ex else 0.0)
        ocurve[str(kk)] = sum(vals) / len(vals)
    metrics["oracle_by_k"] = ocurve
    metrics.update({"n": len(samples), "k": args.k, "temperature": args.temperature})
    print(json.dumps(metrics, indent=1), flush=True)
    with open(args.out, "w") as f:
        json.dump({"metrics": metrics, "ckpt": args.ckpt, "verifier": args.verifier,
                   "candidates": [{"key": s["uuid"], "cands": cs} for s, cs in zip(samples, cands)]}, f)


if __name__ == "__main__":
    main()
