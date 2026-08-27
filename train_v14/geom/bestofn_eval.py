"""Best-of-N execution-gated evaluation (deployment-realistic).

For each eval sample: draw N candidates at temperature T. Execute in draw
order and keep the FIRST that produces a STEP (no GT signal used for
selection — same policy a production server could run). If none execute,
one repair round on the last candidate. Reports the same metric family as
geom_eval_worker plus per-k coverage (how many samples succeeded by draw k).

    python bestofn_eval.py --ckpt <hf_dir> --run <run_name> --n 96 --k 4
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

from data_v14 import EVAL_CACHE, EVAL_CACHE_V15, _decode_png  # noqa: E402
from geom_eval_worker import (  # noqa: E402
    build_gen_messages, build_repair_messages, extract_code, feedback_text,
    generate_all, load_model, run_config,
)
from iou import iou_pair  # noqa: E402
from rft_generate import exec_to_stl  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--kind", default="hf")
    ap.add_argument("--run", required=True)
    ap.add_argument("--n", type=int, default=96)
    ap.add_argument("--k", type=int, default=4)
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
    keys = [k for k in cache["pools"][pool]
            if os.path.exists(os.path.join(gt_dir, f"{k}.stl"))][: args.n]
    samples = [{"uuid": k, "image": _decode_png(cache["samples"][k]["png"])}
               for k in keys]
    print(f"[bo{args.k}] {len(samples)} samples, T={args.temperature}", flush=True)

    model, processor = load_model(args.ckpt, args.kind, cfg)

    import torch
    from qwen_vl_utils import process_vision_info

    def gen_batch(msgs_list, sample_mode):
        tmpl = dict(enable_thinking=True,
                    reasoning_effort=cfg.get("reasoning_effort", "medium")) \
            if cfg.get("trace_style", "think") == "think" else {}
        texts = [processor.apply_chat_template(
            m, add_generation_prompt=True, tokenize=False, **tmpl)
            for m in msgs_list]
        images, videos = process_vision_info(msgs_list)
        enc = processor(text=texts, images=images, videos=videos,
                        return_tensors="pt", padding=True)
        enc = {k2: (v.to(model.device) if hasattr(v, "to") else v)
               for k2, v in enc.items()}
        kw = dict(max_new_tokens=args.max_new_tokens,
                  pad_token_id=processor.tokenizer.pad_token_id
                  or processor.tokenizer.eos_token_id)
        if sample_mode:
            kw.update(do_sample=True, temperature=args.temperature, top_p=0.95)
        else:
            kw["do_sample"] = False
        with torch.no_grad():
            out = model.generate(**enc, **kw)
        gen = out[:, enc["input_ids"].shape[1]:]
        return processor.tokenizer.batch_decode(gen, skip_special_tokens=True)

    recs = [{"key": s["uuid"], "exec_ok": False, "by_k": None, "iou": 0.0,
             "last_reply": "", "last_rec": {}} for s in samples]

    with tempfile.TemporaryDirectory(prefix="bon_") as td:
        pool_ex = ThreadPoolExecutor(max_workers=8)
        for draw in range(args.k):
            todo = [i for i, r in enumerate(recs) if not r["exec_ok"]]
            if not todo:
                break
            print(f"[bo{args.k}] draw {draw}: {len(todo)} unsolved", flush=True)
            outs = []
            # draw 0 greedy (matches single-shot), later draws sampled
            for b in range(0, len(todo), args.batch):
                chunk = todo[b:b + args.batch]
                msgs = [build_gen_messages(samples[i]["image"], cfg)
                        for i in chunk]
                outs.extend(gen_batch(msgs, sample_mode=(draw > 0)))
                n_deg = sum("!!!!!!!!" in t for t in outs)
                if n_deg > max(4, len(outs) // 3):
                    raise RuntimeError("degenerate generations — bad GPU?")
            def try_one(i, text):
                code = extract_code(text)
                r = recs[i]
                r["last_reply"] = (code and f"```python\n{code}\n```") or text[-1200:]
                if code is None:
                    r["last_rec"] = {"code": None}
                    return
                stl = os.path.join(td, f"{r['key']}.stl")
                ok = exec_to_stl(code, stl, td, f"{r['key']}_d{draw}")
                r["last_rec"] = {"code": code, "exec_rc": 0 if ok else 2,
                                 "stderr_tail": ""}
                if ok:
                    r["exec_ok"] = True
                    r["by_k"] = draw
            list(pool_ex.map(lambda p: try_one(*p), zip(todo, outs)))

        # one repair round for the still-unsolved
        todo = [i for i, r in enumerate(recs) if not r["exec_ok"]]
        if todo:
            print(f"[bo{args.k}] repair round: {len(todo)}", flush=True)
            msgs = [build_repair_messages(
                samples[i]["image"], cfg, recs[i]["last_reply"],
                feedback_text(recs[i]["last_rec"])) for i in todo]
            outs = []
            for b in range(0, len(msgs), args.batch):
                outs.extend(gen_batch(msgs[b:b + args.batch], sample_mode=False))
            def try_rep(i, text):
                code = extract_code(text)
                if code is None:
                    return
                stl = os.path.join(td, f"{recs[i]['key']}.stl")
                if exec_to_stl(code, stl, td, f"{recs[i]['key']}_rep"):
                    recs[i]["exec_ok"] = True
                    recs[i]["by_k"] = "repair"
            list(pool_ex.map(lambda p: try_rep(*p), zip(todo, outs)))

        def score(r):
            if r["exec_ok"]:
                r["iou"] = iou_pair(os.path.join(td, f"{r['key']}.stl"),
                                    os.path.join(gt_dir, f"{r['key']}.stl")
                                    )["iou_centered"]
            r.pop("last_reply", None)
            r.pop("last_rec", None)
            return r
        list(pool_ex.map(score, recs))

    n = len(recs)
    ex = [r for r in recs if r["exec_ok"]]
    ious = sorted(r["iou"] for r in recs)
    from collections import Counter
    cov = Counter(r["by_k"] for r in recs)
    m = {
        "n": n, "k": args.k, "temperature": args.temperature,
        "exec_ok_frac": len(ex) / n,
        "iou_mean": sum(ious) / n,
        "iou_median": ious[n // 2],
        "frac_iou50": sum(r["iou"] >= 0.5 for r in recs) / n,
        "frac_iou85": sum(r["iou"] >= 0.85 for r in recs) / n,
        "coverage_by_draw": {str(k2): v for k2, v in sorted(
            cov.items(), key=lambda x: str(x[0]))},
    }
    print(json.dumps(m, indent=1), flush=True)
    with open(args.out, "w") as f:
        json.dump({"metrics": m, "records": recs, "ckpt": args.ckpt}, f, indent=1)


if __name__ == "__main__":
    main()
