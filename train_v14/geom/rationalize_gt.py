"""Rationalize ground-truth code rows: generate a reasoning plan in the model's own style from
(drawing, correct script), so the rows can be trained in the normal think + code format.

    python rationalize_gt.py --tier <dir with accepted-*.jsonl and png/> --ckpt <hf dir> --run <run>
        --out <tier_out> [--also-keys-suffix _dw423 --alt-png <dir>]   (one plan per part; rows for
        keys sharing the same base part reuse the plan)
Rows without a usable plan (too short, contains a code fence) are dropped and counted.
"""
from __future__ import annotations
import argparse, glob, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from collate_v14 import SYSTEM_PROMPTS, USER_PROMPT, wrap_python  # noqa: E402
from geom_eval_worker import load_model, run_config  # noqa: E402
from PIL import Image  # noqa: E402

RAT_USER = (USER_PROMPT + "\n\nThe correct build123d script for this drawing is known and shown below. "
            "Write the numbered plan you would reason through before writing exactly this script: read every "
            "dimension and callout off the drawing, derive each feature's size and position from them (show the "
            "arithmetic where a value is derived), and state the operations in build order. Do not restate or "
            "include any code; output only the numbered plan.\n\n{code}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", required=True); ap.add_argument("--ckpt", required=True); ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--max-new-tokens", type=int, default=900); ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    cfg = run_config(a.run)
    rows = [json.loads(l) for f in sorted(glob.glob(os.path.join(a.tier, "accepted-*.jsonl"))) for l in open(f)]
    if a.limit: rows = rows[:a.limit]
    # one plan per base part (strip renderer suffixes), rendered from the first key's PNG
    base = {}
    for r in rows:
        b = re.sub(r"_dw\d+$", "", r["key"]); base.setdefault(b, []).append(r)
    print(f"[rat] {len(rows)} rows, {len(base)} parts", flush=True)
    import torch
    from qwen_vl_utils import process_vision_info
    model, processor = load_model(a.ckpt, "hf", cfg)
    sysmsg = SYSTEM_PROMPTS[cfg.get("system_prompt", "detailed")]
    plans = {}; parts = sorted(base)
    for i in range(0, len(parts), a.batch):
        chunk = parts[i:i + a.batch]; msgs = []
        for b in chunk:
            r = base[b][0]; png = os.path.join(a.tier, "png", r["key"] + ".png")
            img = Image.open(png).convert("RGB")
            msgs.append([{"role": "system", "content": [{"type": "text", "text": sysmsg}]},
                         {"role": "user", "content": [{"type": "image", "image": img},
                                                      {"type": "text", "text": RAT_USER.format(code=wrap_python(r["code"]))}]}])
        texts = [processor.apply_chat_template(m, add_generation_prompt=True, tokenize=False, enable_thinking=False) for m in msgs]
        images, videos = process_vision_info(msgs)
        enc = processor(text=texts, images=images, videos=videos, return_tensors="pt", padding=True)
        enc = {k: (v.to(model.device) if hasattr(v, "to") else v) for k, v in enc.items()}
        with torch.no_grad():
            out = model.generate(**enc, max_new_tokens=a.max_new_tokens, do_sample=False,
                                 pad_token_id=processor.tokenizer.pad_token_id or processor.tokenizer.eos_token_id)
        dec = processor.tokenizer.batch_decode(out[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)
        for b, t in zip(chunk, dec):
            t = t.split("</think>", 1)[-1].strip()
            plans[b] = t
        print(f"[rat] {min(i + a.batch, len(parts))}/{len(parts)}", flush=True)
    os.makedirs(os.path.join(a.out, "png"), exist_ok=True)
    kept = dropped = 0
    with open(os.path.join(a.out, "accepted-000.jsonl"), "w") as f:
        for b, rs in base.items():
            p = plans.get(b, "")
            if len(p) < 200 or "```" in p or not re.search(r"^\s*1[.)]", p, re.M):
                dropped += len(rs); continue
            for r in rs:
                r2 = dict(r); r2["think"] = p; f.write(json.dumps(r2) + "\n"); kept += 1
                src = os.path.join(a.tier, "png", r["key"] + ".png"); dst = os.path.join(a.out, "png", r["key"] + ".png")
                if not os.path.exists(dst): os.link(src, dst) if os.stat(src).st_dev == os.stat(os.path.dirname(dst)).st_dev else __import__("shutil").copy(src, dst)
    json.dump(plans, open(os.path.join(a.out, "plans.json"), "w"), indent=1)
    print(f"[rat] DONE kept {kept} rows, dropped {dropped}; plans for {len(plans)} parts", flush=True)


if __name__ == "__main__":
    main()
