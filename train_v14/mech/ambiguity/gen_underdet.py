"""Best-of-K generation on a fixed key list with an ambiguity-aware system
prompt (the champion's 'detailed' prompt plus a stated convention for
undimensioned features).  Same sampling as the served policy (draw 0 greedy,
draws 1..K-1 at T), every candidate executed and IoU-scored, output in the
results/bo8_*.json format so consistency_rerank.py can be run on it unchanged.
Logic mirrors train_v14/geom/bestofn_verifier_eval.py (not edited).

    python gen_underdet.py --ckpt runs/e24-rft/final --run e24-rft \
        --keys keys_underdet.txt --variant convention --out out/bo8_underdet_convention.json
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
sys.path.insert(0, os.path.join(DV, "train_v14")); sys.path.insert(0, os.path.join(DV, "train_v14", "geom"))

from collate_v14 import SYSTEM_PROMPTS, USER_PROMPT  # noqa: E402
from data_v14 import EVAL_CACHE, EVAL_CACHE_V15, _decode_png  # noqa: E402
from geom_eval_worker import extract_code, load_model, run_config  # noqa: E402
from iou import iou_pair  # noqa: E402
from rft_generate import exec_to_stl  # noqa: E402

# The convention observed in the generator's output (train_v14/mech/ambiguity/RESULTS.md):
# the dropped dimension is almost always the overall length; the sheet is to
# scale; hole patterns are centred so first+last edge offsets give the length.
CONVENTION = (
    "\n\nNote on omitted dimensions: sheets from this drafting system are drawn "
    "to one common scale and occasionally omit a dimension, most often the "
    "overall length of the part. When a dimension is not called out, never "
    "invent an arbitrary value. Derive it: hole patterns, slots and pockets are "
    "centred on the outline, so an overall length equals the first hole's "
    "offset from one edge plus the last hole's offset from the same edge "
    "(e.g. offsets 8 and 92 give a length of 100), and a feature dimensioned "
    "from one edge sits at the mirrored offset from the opposite edge. If no "
    "such relation exists, measure the undimensioned extent in proportion to a "
    "dimensioned extent in the same view and round to a plausible stock size "
    "(overall sizes are usually multiples of 5 mm)."
)

VARIANTS = {
    "baseline": lambda base: base,
    "convention": lambda base: base + CONVENTION,
}


def build_msgs(image, system_text: str) -> list[dict]:
    return [
        {"role": "system", "content": [{"type": "text", "text": system_text}]},
        {"role": "user", "content": [
            {"type": "image", "image": image},
            {"type": "text", "text": USER_PROMPT}]},
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--kind", default="hf")
    ap.add_argument("--run", required=True)
    ap.add_argument("--keys", required=True)
    ap.add_argument("--variant", default="convention", choices=sorted(VARIANTS))
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--max-new-tokens", type=int, default=2400)
    ap.add_argument("--out", required=True)
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
    keys = [l.strip() for l in open(args.keys) if l.strip()]
    keys = [k for k in keys if k in cache["samples"] and os.path.exists(os.path.join(gt_dir, f"{k}.stl"))]
    samples = [{"uuid": k, "image": _decode_png(cache["samples"][k]["png"])} for k in keys]
    system_text = VARIANTS[args.variant](SYSTEM_PROMPTS[cfg.get("system_prompt", "detailed")])
    print(f"[gen:{args.variant}] {len(samples)} samples, K={args.k}, T={args.temperature}", flush=True)
    print("[gen] system prompt:\n" + system_text, flush=True)

    import torch
    from qwen_vl_utils import process_vision_info

    model, processor = load_model(args.ckpt, args.kind, cfg)

    def gen_batch(msgs_list, sample_mode):
        tmpl = dict(enable_thinking=True, reasoning_effort=cfg.get("reasoning_effort", "medium")) \
            if cfg.get("trace_style", "think") == "think" else {}
        texts = [processor.apply_chat_template(m, add_generation_prompt=True, tokenize=False, **tmpl)
                 for m in msgs_list]
        images, videos = process_vision_info(msgs_list)
        enc = processor(text=texts, images=images, videos=videos, return_tensors="pt", padding=True)
        enc = {k2: (v.to(model.device) if hasattr(v, "to") else v) for k2, v in enc.items()}
        kw = dict(max_new_tokens=args.max_new_tokens,
                  pad_token_id=processor.tokenizer.pad_token_id or processor.tokenizer.eos_token_id)
        if sample_mode:
            kw.update(do_sample=True, temperature=args.temperature, top_p=0.95)
        else:
            kw["do_sample"] = False
        with torch.no_grad():
            out = model.generate(**enc, **kw)
        return processor.tokenizer.batch_decode(out[:, enc["input_ids"].shape[1]:],
                                                skip_special_tokens=True)

    cands = [[] for _ in samples]
    partial = args.out + ".partial.json"
    keys_list = [s["uuid"] for s in samples]
    start_draw = 0
    if os.path.exists(partial):
        pd = json.load(open(partial))
        if pd.get("keys") == keys_list and pd.get("k") == args.k and pd["cands"] and pd["cands"][0]:
            cands, start_draw = pd["cands"], len(pd["cands"][0])
            print(f"[gen] resuming from {partial}: {start_draw} draws done", flush=True)
    for draw in range(start_draw, args.k):
        outs = []
        for b in range(0, len(samples), args.batch):
            chunk = samples[b:b + args.batch]
            msgs = [build_msgs(s["image"], system_text) for s in chunk]
            outs.extend(gen_batch(msgs, draw > 0))
            if sum("!!!!!!!!" in t for t in outs) > max(4, len(outs) // 3):
                raise RuntimeError("degenerate generations — bad GPU?")
        for i, text in enumerate(outs):
            cands[i].append({"draw": draw, "code": extract_code(text), "exec": False, "iou": 0.0,
                             "raw_len": len(text)})
        print(f"[gen] draw {draw} done", flush=True)
        with open(partial, "w") as f:
            json.dump({"keys": keys_list, "k": args.k, "cands": cands}, f)

    del model
    torch.cuda.empty_cache()
    with tempfile.TemporaryDirectory(prefix="amb_") as td:
        def run_one(i, j):
            c = cands[i][j]
            if not c["code"]:
                return
            stl = os.path.join(td, f"{samples[i]['uuid']}_{j}.stl")
            if exec_to_stl(c["code"], stl, td, f"{samples[i]['uuid']}_{j}"):
                c["exec"] = True
                c["iou"] = iou_pair(stl, os.path.join(gt_dir, f"{samples[i]['uuid']}.stl"))["iou_centered"]
        with ThreadPoolExecutor(max_workers=16) as ex:
            list(ex.map(lambda p: run_one(*p), [(i, j) for i in range(len(samples)) for j in range(args.k)]))
    n_exec = sum(c["exec"] for cs in cands for c in cs)
    print(f"[gen] executed {n_exec}/{len(samples) * args.k} candidates", flush=True)

    def pick(cs, key):
        ex = [c for c in cs if c["exec"]]
        if not ex:
            return None
        return max(ex, key=key) if key else ex[0]
    metrics = {}
    for name, fn in {"first_exec": lambda cs: pick(cs, None), "oracle": lambda cs: pick(cs, lambda c: c["iou"]),
                     "greedy_only": lambda cs: (cs[0] if cs[0]["exec"] else None)}.items():
        ious = [(fn(cs)["iou"] if fn(cs) else 0.0) for cs in cands]
        n = len(ious); s = sorted(ious)
        metrics[name] = {"exec_ok_frac": sum(i > 0 for i in ious) / n, "iou_mean": sum(ious) / n,
                         "iou_median": s[n // 2], "frac_iou50": sum(i >= 0.5 for i in ious) / n,
                         "frac_iou85": sum(i >= 0.85 for i in ious) / n}
    metrics.update({"n": len(samples), "k": args.k, "temperature": args.temperature, "variant": args.variant})
    print(json.dumps(metrics, indent=1), flush=True)
    with open(args.out, "w") as f:
        json.dump({"metrics": metrics, "ckpt": args.ckpt, "verifier": "", "variant": args.variant,
                   "system_prompt": system_text,
                   "candidates": [{"key": s["uuid"], "cands": cs} for s, cs in zip(samples, cands)]}, f)


if __name__ == "__main__":
    main()
