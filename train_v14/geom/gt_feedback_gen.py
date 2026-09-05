"""Privileged-feedback generation on unsolved real parts.

For each key: start from the best prior candidate (seed) or a fresh draw, then run
--rounds feedback rounds in which the model sees its own script plus measurements
of the produced solid against the reference mesh (volume, extents, IoU, solid
count, coarse where-is-the-material-wrong summary) and regenerates K samples at
temperature T. Everything is executed and IoU-scored; rows at >= --accept go to
accepted-000.jsonl in the standard RFT tier format (key, iou, ok, think, code,
sample). The reference is only used to write the feedback; the training pair is
drawing -> final script, so nothing privileged enters the model input at train time.

    python gt_feedback_gen.py --ckpt runs/<run>/final --run <run> --keys unsolved_keys.json \
        --corpus corpus1 --seeds seeds.json --out <tier_dir> --rounds 3 --k 4 --shard i --nshards 8
Env: DRAWING_VLM_TRACES_JSON / DRAWING_VLM_EVAL_CACHE point at the corpus cache.
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import sys
import tempfile
import warnings
from concurrent.futures import ThreadPoolExecutor

import numpy as np

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from collate_v14 import wrap_python  # noqa: E402
from data_v14 import EVAL_CACHE, _decode_png  # noqa: E402
from geom_eval_worker import build_gen_messages, build_repair_messages, extract_code, load_model, run_config  # noqa: E402
from iou import center_mesh, iou_pair, load_mesh  # noqa: E402
from rft_generate import exec_to_stl  # noqa: E402

OCT = [(sx, sy, sz) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]


def octant_name(o):
    return ",".join(f"{a}{'+' if s > 0 else '-'}" for a, s in zip("xyz", o))


def measure(pred_stl, gt_stl, iou, rng):
    """Feedback text + metrics comparing the produced solid with the reference (both bbox-centered)."""
    m, g = load_mesh(pred_stl), load_mesh(gt_stl)
    if m is None or g is None:
        return None, {}
    m, g = center_mesh(m), center_mesh(g)
    em, eg = m.bounds[1] - m.bounds[0], g.bounds[1] - g.bounds[0]
    vr = float(m.volume / max(g.volume, 1e-9))
    try:
        nm, ng = len(m.split(only_watertight=False)), len(g.split(only_watertight=False))
    except Exception:  # noqa: BLE001
        nm, ng = 1, 1
    lines = [f"- volume: yours {m.volume:.0f} mm^3, reference {g.volume:.0f} mm^3 (ratio {vr:.2f})",
             f"- bounding box X x Y x Z: yours {em[0]:.1f} x {em[1]:.1f} x {em[2]:.1f}, reference {eg[0]:.1f} x {eg[1]:.1f} x {eg[2]:.1f}",
             f"- volumetric IoU with the reference: {iou:.2f}",
             f"- separate solids: yours {nm}, reference {ng}"]
    # coarse localisation: occupancy per octant of the union bbox from uniform samples
    try:
        lo = np.minimum(m.bounds[0], g.bounds[0]); hi = np.maximum(m.bounds[1], g.bounds[1])
        pts = lo + rng.random((12000, 3)) * (hi - lo)
        im, ig = m.contains(pts), g.contains(pts)
        oct_idx = ((pts > 0).astype(int) * 2 - 1)
        diffs = []
        for o in OCT:
            sel = np.all(oct_idx == np.array(o), axis=1)
            if sel.sum() < 50:
                continue
            fm, fg = im[sel].mean(), ig[sel].mean()
            diffs.append((fm - fg, o, fm, fg))
        extra = [d for d in sorted(diffs, reverse=True) if d[0] > 0.08][:2]
        miss = [d for d in sorted(diffs) if d[0] < -0.08][:2]
        if extra:
            lines.append("- too much material in region(s): " + "; ".join(f"{octant_name(o)} ({fm:.0%} filled vs {fg:.0%} in the reference)" for _, o, fm, fg in extra))
        if miss:
            lines.append("- missing material in region(s): " + "; ".join(f"{octant_name(o)} ({fm:.0%} filled vs {fg:.0%} in the reference)" for _, o, fm, fg in miss))
    except Exception:  # noqa: BLE001
        pass
    text = ("### Execution: OK, but the solid does not match the part in the drawing.\n"
            "Measured against the reference part (both centered on their bounding boxes; axes as in your script):\n"
            + "\n".join(lines) +
            "\n\nRe-read the drawing and find which features are wrong (missing or extra holes, pockets, "
            "bosses or fillets, wrong depths or profiles, wrong placement, extra bodies). Then output the complete "
            "corrected script as a single ```python code block ending with `export_step(part, \"output.step\")`.")
    return text, {"vol_ratio": vr, "extent_pred": em.round(1).tolist(), "extent_gt": eg.round(1).tolist(), "solids": [nm, ng]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True); ap.add_argument("--run", required=True)
    ap.add_argument("--keys", required=True); ap.add_argument("--corpus", default="", help="sub-list name inside --keys (corpus1/corpus2)")
    ap.add_argument("--seeds", default=""); ap.add_argument("--out", required=True)
    ap.add_argument("--rounds", type=int, default=3); ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--temperature", type=float, default=0.7); ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--max-new-tokens", type=int, default=2400); ap.add_argument("--accept", type=float, default=0.8)
    ap.add_argument("--shard", type=int, default=0); ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    cfg = run_config(args.run)
    gt_dir = os.path.join(os.path.dirname(EVAL_CACHE), "gt_meshes_v15")
    cache = pickle.load(open(EVAL_CACHE, "rb"))
    kj = json.load(open(args.keys))
    keys = kj[args.corpus] if args.corpus else (kj["unsolved"] if isinstance(kj, dict) else kj)
    keys = [k for k in keys if k in cache["samples"] and os.path.exists(os.path.join(gt_dir, f"{k}.stl"))]
    keys = keys[args.shard::args.nshards]
    if args.limit:
        keys = keys[:args.limit]
    seeds = json.load(open(args.seeds)) if args.seeds else {}
    os.makedirs(args.out, exist_ok=True)
    tag = f"{args.shard:03d}"
    done_file = os.path.join(args.out, f"done-{tag}.txt")
    done = set(open(done_file).read().split()) if os.path.exists(done_file) else set()
    keys = [k for k in keys if k not in done]
    print(f"[gtfb] shard {args.shard}/{args.nshards}: {len(keys)} keys to do, {len(done)} done; seeds for {sum(k in seeds for k in keys)}", flush=True)

    import torch
    from qwen_vl_utils import process_vision_info
    model, processor = load_model(args.ckpt, "hf", cfg)
    rng = np.random.default_rng(args.shard)

    def gen(msgs_list, sample_mode):
        tmpl = dict(enable_thinking=True, reasoning_effort=cfg.get("reasoning_effort", "medium")) \
            if cfg.get("trace_style", "think") == "think" else {}
        texts = [processor.apply_chat_template(m, add_generation_prompt=True, tokenize=False, **tmpl) for m in msgs_list]
        images, videos = process_vision_info(msgs_list)
        enc = processor(text=texts, images=images, videos=videos, return_tensors="pt", padding=True)
        enc = {k2: (v.to(model.device) if hasattr(v, "to") else v) for k2, v in enc.items()}
        kw = dict(max_new_tokens=args.max_new_tokens, pad_token_id=processor.tokenizer.pad_token_id or processor.tokenizer.eos_token_id)
        kw.update(dict(do_sample=True, temperature=args.temperature, top_p=0.95) if sample_mode else dict(do_sample=False))
        with torch.no_grad():
            out = model.generate(**enc, **kw)
        return processor.tokenizer.batch_decode(out[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)

    def split(text):
        think = text.split("</think>", 1)[0].replace("<think>", "").strip() if "</think>" in text else ""
        return think, extract_code(text)

    state = {}  # key -> dict(best_code, best_iou, best_think, stl, feedback, seed_iou)
    images = {k: _decode_png(cache["samples"][k]["png"]) for k in keys}
    sc = open(os.path.join(args.out, f"scored-{tag}.jsonl"), "a"); acc = open(os.path.join(args.out, f"accepted-{tag}.jsonl"), "a")
    td = tempfile.mkdtemp(prefix="gtfb_")
    stats = {"cands": 0, "exec": 0, "acc_rows": 0, "acc_keys": set()}

    def score_batch(items):
        """items: list of (key, round, sample, think, code). Executes, scores, records, updates best."""
        def one(it):
            key, rnd, s, think, code = it
            rec = {"key": key, "round": rnd, "sample": s, "think": think, "code": code, "exec": False, "iou": 0.0, "ok": False, "seed_iou": state[key]["seed_iou"]}
            if code:
                stl = os.path.join(td, f"{key}_{rnd}_{s}.stl")
                if exec_to_stl(code, stl, td, f"{key}_{rnd}_{s}"):
                    rec["exec"] = True; rec["stl"] = stl
                    rec["iou"] = float(iou_pair(stl, os.path.join(gt_dir, f"{key}.stl"))["iou_centered"])
                    rec["ok"] = rec["iou"] >= args.accept
            return rec
        with ThreadPoolExecutor(8) as ex:
            recs = list(ex.map(one, items))
        for rec in recs:
            stl = rec.pop("stl", None)
            sc.write(json.dumps(rec) + "\n"); stats["cands"] += 1; stats["exec"] += rec["exec"]
            if rec["ok"]:
                acc.write(json.dumps({k2: rec[k2] for k2 in ("key", "iou", "ok", "think", "code", "sample")} | {"round": rec["round"]}) + "\n")
                stats["acc_rows"] += 1; stats["acc_keys"].add(rec["key"])
            st = state[rec["key"]]
            if rec["exec"] and rec["iou"] > st["best_iou"]:
                st.update(best_iou=rec["iou"], best_code=rec["code"], best_think=rec["think"], stl=stl)
        sc.flush(); acc.flush()

    # ---- round 0: seeds or fresh draws ----
    fresh = []
    for k in keys:
        s = seeds.get(k)
        state[k] = {"best_iou": -1.0, "best_code": None, "best_think": "", "stl": None, "seed_iou": None}
        if s and s.get("code"):
            state[k]["seed_iou"] = s.get("iou")
            stl = os.path.join(td, f"{k}_seed.stl")
            if exec_to_stl(s["code"], stl, td, f"{k}_seed"):
                iou = float(iou_pair(stl, os.path.join(gt_dir, f"{k}.stl"))["iou_centered"])
                state[k].update(best_iou=iou, best_code=s["code"], best_think=s.get("think", ""), stl=stl)
                continue
        fresh.append(k)
    print(f"[gtfb] seeds executed for {len(keys) - len(fresh)} keys; fresh draws for {len(fresh)}", flush=True)
    for b in range(0, len(fresh), max(1, args.batch // args.k)):
        chunk = fresh[b:b + max(1, args.batch // args.k)]
        msgs = [build_gen_messages(images[k], cfg) for k in chunk for _ in range(args.k)]
        outs = gen(msgs, True)
        items = []
        for i, k in enumerate(chunk):
            for s in range(args.k):
                th, code = split(outs[i * args.k + s]); items.append((k, 0, s, th, code))
        score_batch(items)

    # ---- feedback rounds ----
    for rnd in range(1, args.rounds + 1):
        active = [k for k in keys if state[k]["best_code"] and state[k]["best_iou"] < args.accept and state[k]["stl"]]
        fb = {}
        for k in active:
            text, _ = measure(state[k]["stl"], os.path.join(gt_dir, f"{k}.stl"), state[k]["best_iou"], rng)
            if text:
                fb[k] = text
        active = [k for k in active if k in fb]
        print(f"[gtfb] round {rnd}: {len(active)} keys active; accepted so far {len(stats['acc_keys'])}", flush=True)
        per = max(1, args.batch // args.k)
        for b in range(0, len(active), per):
            chunk = active[b:b + per]
            msgs = [build_repair_messages(images[k], cfg, wrap_python(state[k]["best_code"]), fb[k]) for k in chunk for _ in range(args.k)]
            outs = gen(msgs, True)
            items = []
            for i, k in enumerate(chunk):
                for s in range(args.k):
                    th, code = split(outs[i * args.k + s]); items.append((k, rnd, s, th, code))
            score_batch(items)
            print(f"[gtfb] round {rnd}: {min(b + per, len(active))}/{len(active)}; cands {stats['cands']} exec {stats['exec']} accepted {stats['acc_rows']} rows / {len(stats['acc_keys'])} keys", flush=True)
    with open(done_file, "a") as f:
        f.write("\n".join(keys) + "\n")
    json.dump({"best": {k: {"iou": v["best_iou"], "seed_iou": v["seed_iou"]} for k, v in state.items()},
               "cands": stats["cands"], "exec": stats["exec"], "acc_rows": stats["acc_rows"], "acc_keys": sorted(stats["acc_keys"])},
              open(os.path.join(args.out, f"summary-{tag}.json"), "w"), indent=1)
    print(f"[gtfb] DONE shard {args.shard}: {stats['cands']} cands, exec {stats['exec']}, accepted {stats['acc_rows']} rows on {len(stats['acc_keys'])}/{len(keys)} keys", flush=True)


if __name__ == "__main__":
    main()
