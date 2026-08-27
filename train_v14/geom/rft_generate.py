"""Rejection-sampling data generation (STaR/RFT).

One worker = one GPU. Streams its assigned tars_v14 shards (stride
partitioning), generates a build123d program per drawing at mild
temperature, executes it AND the GT program (GT STL cached for reuse),
scores exact volumetric IoU, and appends accepted samples
(iou >= --min-iou) to a per-worker jsonl:

    {"key", "iou", "think", "code"}

Filters mirror training: exec-bad GT keys, legacy-renderer keys, and both
eval residues (7 = legacy holdout, 0 = frozen manifest eval) are skipped.
Resume-safe: keys already in the output jsonl (accepted or rejected log)
are skipped.

    python rft_generate.py --ckpt runs/e16-full-execfilter/final \
        --run e16-full-execfilter --worker 3 --stride 16 \
        --out rft_v1 --max-accepted 4000
"""
from __future__ import annotations

import argparse
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
from concurrent.futures import ThreadPoolExecutor

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

from PIL import Image  # noqa: E402

from data_v14 import (  # noqa: E402
    all_shards, bad_keys, is_manifest_eval_uuid, is_val_uuid, legacy_keys,
    uuid_of_key,
)
from geom_eval_worker import (  # noqa: E402
    HARNESS, PYTHON, build_gen_messages, load_model, run_config,
)
from iou import iou_pair  # noqa: E402

_CODE_START = "```python"


def extract_think_code(text: str) -> tuple[str, str | None]:
    think = ""
    tail = text
    if "</think>" in text:
        think, tail = text.split("</think>", 1)
        think = think.replace("<think>", "").strip()
    import re
    blocks = re.findall(r"```python\s*\n(.*?)```", tail, re.DOTALL)
    return think, (blocks[-1].strip() if blocks else None)


def exec_to_stl(code: str, stl_path: str, workdir: str, key: str) -> bool:
    cp = os.path.join(workdir, key + ".py")
    with open(cp, "w") as f:
        f.write(code)
    try:
        p = subprocess.run([PYTHON, HARNESS, cp, stl_path],
                           capture_output=True, text=True, timeout=120)
        return p.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--kind", default="hf")
    ap.add_argument("--run", required=True)
    ap.add_argument("--worker", type=int, required=True)
    ap.add_argument("--stride", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--max-new-tokens", type=int, default=2400)
    ap.add_argument("--min-iou", type=float, default=0.8)
    ap.add_argument("--temperature", type=float, default=0.6)
    ap.add_argument("--max-accepted", type=int, default=4000)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    gt_cache = os.path.join(args.out, "gt_stl_cache")
    os.makedirs(gt_cache, exist_ok=True)
    acc_path = os.path.join(args.out, f"accepted-{args.worker:03d}.jsonl")
    seen_path = os.path.join(args.out, f"seen-{args.worker:03d}.jsonl")

    seen: set[str] = set()
    n_accepted = 0
    for p in (acc_path, seen_path):
        if os.path.exists(p):
            with open(p) as f:
                for line in f:
                    try:
                        r = json.loads(line)
                        seen.add(r["key"])
                        if p == acc_path:
                            n_accepted += 1
                    except Exception:
                        pass
    print(f"[rft w{args.worker}] resume: {len(seen)} seen, {n_accepted} accepted",
          flush=True)

    bad = bad_keys()
    legacy = legacy_keys()
    cfg = run_config(args.run)
    model, processor = load_model(args.ckpt, args.kind, cfg)

    shards = all_shards()[args.worker::args.stride]
    acc_f = open(acc_path, "a")
    seen_f = open(seen_path, "a")
    pool = ThreadPoolExecutor(max_workers=4)

    def score_one(key: str, think: str, code: str | None, gt_code: str,
                  td: str) -> dict:
        rec = {"key": key, "iou": 0.0, "ok": False}
        try:
            if code is None:
                return rec
            pred_stl = os.path.join(td, key + ".pred.stl")
            if not exec_to_stl(code, pred_stl, td, key + ".pred"):
                return rec
            gt_stl = os.path.join(gt_cache, key + ".stl")
            if not (os.path.exists(gt_stl) and os.path.getsize(gt_stl) > 0):
                tmp = os.path.join(td, key + ".gt.stl")
                if not exec_to_stl(gt_code, tmp, td, key + ".gt"):
                    return rec
                import shutil
                # /tmp -> Lustre crosses filesystems; shutil.move handles it.
                shutil.move(tmp, gt_stl + f".w{args.worker}")
                os.replace(gt_stl + f".w{args.worker}", gt_stl)
            iou = iou_pair(pred_stl, gt_stl)["iou_centered"]
            rec.update({"iou": iou, "ok": iou >= args.min_iou,
                        "think": think, "code": code})
        except Exception as e:
            print(f"[rft w{args.worker}] score error {key}: "
                  f"{type(e).__name__}: {e}", flush=True)
        return rec

    with tempfile.TemporaryDirectory(prefix=f"rft{args.worker}_") as td:
        batch_samples, batch_meta = [], []

        def flush():
            nonlocal n_accepted, batch_samples, batch_meta
            if not batch_samples:
                return
            from qwen_vl_utils import process_vision_info
            tmpl = dict(enable_thinking=True,
                        reasoning_effort=cfg.get("reasoning_effort", "medium"))
            msgs = [build_gen_messages(im, cfg) for im in batch_samples]
            texts = [processor.apply_chat_template(
                m, add_generation_prompt=True, tokenize=False, **tmpl)
                for m in msgs]
            images, videos = process_vision_info(msgs)
            enc = processor(text=texts, images=images, videos=videos,
                            return_tensors="pt", padding=True)
            enc = {k: (v.to(model.device) if hasattr(v, "to") else v)
                   for k, v in enc.items()}
            with torch.no_grad():
                out = model.generate(
                    **enc, max_new_tokens=args.max_new_tokens, do_sample=True,
                    temperature=args.temperature, top_p=0.95,
                    pad_token_id=processor.tokenizer.pad_token_id
                    or processor.tokenizer.eos_token_id)
            gen = out[:, enc["input_ids"].shape[1]:]
            decoded = processor.tokenizer.batch_decode(
                gen, skip_special_tokens=True)
            futs = []
            for (key, gt_code), text in zip(batch_meta, decoded):
                think, code = extract_think_code(text)
                futs.append(pool.submit(score_one, key, think, code, gt_code, td))
            for fut in futs:
                rec = fut.result()
                seen_f.write(json.dumps(
                    {"key": rec["key"], "iou": rec["iou"]}) + "\n")
                if rec["ok"]:
                    acc_f.write(json.dumps(rec) + "\n")
                    n_accepted += 1
            acc_f.flush()
            seen_f.flush()
            batch_samples, batch_meta = [], []

        for sp in shards:
            if n_accepted >= args.max_accepted:
                break
            try:
                tf = tarfile.open(sp)
            except Exception:
                continue
            members = {}
            for m in tf.getmembers():
                base, _, ext = m.name.partition(".")
                members.setdefault(base, {})[ext] = m
            for key in sorted(members):
                if n_accepted >= args.max_accepted:
                    break
                g = members[key]
                if "png" not in g or "py" not in g or key in seen:
                    continue
                if key in bad or key in legacy:
                    continue
                uuid = uuid_of_key(key)
                if is_val_uuid(uuid) or is_manifest_eval_uuid(uuid):
                    continue
                try:
                    png = tf.extractfile(g["png"]).read()
                    gt_code = tf.extractfile(g["py"]).read().decode(
                        "utf-8", errors="replace")
                except Exception:
                    continue
                img = Image.open(io.BytesIO(png))
                if img.mode == "RGBA":
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    bg.paste(img, mask=img.split()[3])
                    img = bg
                else:
                    img = img.convert("RGB")
                seen.add(key)
                batch_samples.append(img)
                batch_meta.append((key, gt_code))
                if len(batch_samples) >= args.batch:
                    flush()
                    if len(seen) % 200 < args.batch:
                        print(f"[rft w{args.worker}] seen={len(seen)} "
                              f"accepted={n_accepted}", flush=True)
            tf.close()
        flush()
    print(f"[rft w{args.worker}] DONE seen={len(seen)} accepted={n_accepted}",
          flush=True)


if __name__ == "__main__":
    main()
