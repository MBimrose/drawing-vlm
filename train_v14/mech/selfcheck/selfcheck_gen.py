"""Visual self-check, one round, on the 96-pool served candidates (GPU).

Prompt = the champion's own serving conversation continued:
  system (detailed) / user [original drawing + USER_PROMPT] /
  assistant [served script] /
  user [drawing RENDERED FROM THE SERVED PART + compare-and-correct instruction]
Greedy decode with thinking (same template as serving). The revision is
executed (STL) and scored: exact IoU vs GT, IoU vs the served part, and mean
agreement with the other stored executing candidates (same reference set as
the served candidate's agreement). Acceptance policies are evaluated offline
by analyze.py from this record.

    python selfcheck_gen.py --prestage out/prestage --out out/selfcheck_96.json
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
DV = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(DV, "train_v14"))
sys.path.insert(0, os.path.join(DV, "train_v14", "geom"))

from collate_v14 import SYSTEM_PROMPTS, USER_PROMPT  # noqa: E402
from data_v14 import EVAL_CACHE_V15, _decode_png  # noqa: E402
from geom_eval_worker import extract_code, load_model, run_config  # noqa: E402
from iou import iou_pair  # noqa: E402
from rft_generate import exec_to_stl  # noqa: E402
from PIL import Image  # noqa: E402

BO8 = os.path.join(DV, "results", "bo8_full_e24.json")
POOL96 = os.path.join(DV, "results", "bo8_verifier2_e24.json")
GT_DIR = os.path.join(DV, "step_to_drw", "wds_dataset", "gt_meshes_v15")

CHECK_PROMPT = (
    "The drawing above was rendered automatically from the part that your script "
    "produces (same conventions as the original: top / front / right views and an "
    "isometric view; every dimension shown is MEASURED from your model — overall "
    "size, hole diameters, hole positions).\n\n"
    "Compare it carefully against the ORIGINAL drawing (the first image): overall "
    "width / depth / height, hole count / diameters / spacing, pockets, slots, "
    "steps, wall thicknesses, bosses, fillets and chamfers, and which side each "
    "feature is on. List every mismatch you find, then fix the script so the part "
    "matches the ORIGINAL drawing. If everything already matches, return the script "
    "unchanged.\n\n"
    "Output the complete corrected script as a single ```python code block ending "
    "with `export_step(part, \"output.step\")`."
)


def build_messages(orig_img, render_img, prev_code: str, cfg: dict) -> list[dict]:
    return [
        {"role": "system", "content": [
            {"type": "text", "text": SYSTEM_PROMPTS[cfg.get("system_prompt", "detailed")]}]},
        {"role": "user", "content": [
            {"type": "image", "image": orig_img},
            {"type": "text", "text": USER_PROMPT}]},
        {"role": "assistant", "reasoning_content": "",
         "content": [{"type": "text", "text": f"```python\n{prev_code}\n```"}]},
        {"role": "user", "content": [
            {"type": "image", "image": render_img},
            {"type": "text", "text": CHECK_PROMPT}]},
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prestage", default=os.path.join(HERE, "out", "prestage"))
    ap.add_argument("--out", default=os.path.join(HERE, "out", "selfcheck_96.json"))
    ap.add_argument("--ckpt", default=os.path.join(DV, "runs", "e24-rft", "final"))
    ap.add_argument("--run", default="e24-rft")
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--max-new-tokens", type=int, default=2400)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    cfg = run_config(a.run)
    keys = [p["key"] for p in json.load(open(POOL96))["candidates"]]
    if a.limit:
        keys = keys[: a.limit]
    bo8 = {p["key"]: p for p in json.load(open(BO8))["candidates"]}
    with open(EVAL_CACHE_V15, "rb") as f:
        cache = pickle.load(f)

    # resume
    recs: dict[str, dict] = {}
    if os.path.exists(a.out):
        recs = {r["key"]: r for r in json.load(open(a.out))["records"]}
        print(f"[sc] resuming: {len(recs)} done", flush=True)

    items = []
    for k in keys:
        meta = json.load(open(os.path.join(a.prestage, k, "meta.json")))
        if k in recs:
            continue
        rec = {"key": k, "served": meta["served"], "served_iou": meta["served_iou"],
               "served_agree": meta["served_agree"], "stored_iou": meta["stored_iou"],
               "render_ok": bool(meta["render"]), "rev_code": None, "rev_text_len": 0,
               "rev_exec": False, "rev_iou": 0.0, "rev_vs_served": None, "rev_agree": None,
               "changed": None, "gen_s": None}
        if meta["served"] is None or not meta["render"]:
            recs[k] = rec   # nothing to check (no executing candidate / render failed)
            continue
        items.append((k, meta, rec))
    print(f"[sc] {len(items)} parts to self-check", flush=True)

    def save():
        os.makedirs(os.path.dirname(a.out), exist_ok=True)
        json.dump({"ckpt": a.ckpt, "records": [recs[k] for k in keys if k in recs]},
                  open(a.out, "w"), indent=1)

    if not items:
        save(); return

    import torch
    from qwen_vl_utils import process_vision_info
    model, processor = load_model(a.ckpt, "hf", cfg)
    tmpl = dict(enable_thinking=True, reasoning_effort=cfg.get("reasoning_effort", "medium"))

    def gen(msgs_list):
        texts = [processor.apply_chat_template(m, add_generation_prompt=True, tokenize=False, **tmpl)
                 for m in msgs_list]
        images, videos = process_vision_info(msgs_list)
        enc = processor(text=texts, images=images, videos=videos, return_tensors="pt", padding=True)
        enc = {k2: (v.to(model.device) if hasattr(v, "to") else v) for k2, v in enc.items()}
        with torch.no_grad():
            out = model.generate(**enc, max_new_tokens=a.max_new_tokens, do_sample=False,
                                 pad_token_id=processor.tokenizer.pad_token_id
                                 or processor.tokenizer.eos_token_id)
        return processor.tokenizer.batch_decode(out[:, enc["input_ids"].shape[1]:],
                                                skip_special_tokens=True)

    def score(k, meta, rec, td):
        code = rec["rev_code"]
        if not code:
            return
        stl = os.path.join(td, f"{k}.stl")
        if not exec_to_stl(code, stl, td, k):
            return
        rec["rev_exec"] = True
        rec["rev_iou"] = iou_pair(stl, os.path.join(GT_DIR, f"{k}.stl"))["iou_centered"]
        served_stl = meta["cand_stl"][meta["served"]]
        rec["rev_vs_served"] = iou_pair(stl, served_stl)["iou_centered"] if served_stl else None
        others = [s for j, s in enumerate(meta["cand_stl"]) if s and j != meta["served"]]
        if others:
            rec["rev_agree"] = sum(iou_pair(stl, s)["iou_centered"] for s in others) / len(others)

    pool = ThreadPoolExecutor(max_workers=8)
    td = tempfile.mkdtemp(prefix="selfcheck_")
    for b in range(0, len(items), a.batch):
        chunk = items[b:b + a.batch]
        msgs = []
        for k, meta, rec in chunk:
            orig = _decode_png(cache["samples"][k]["png"])
            rend = Image.open(meta["render"]).convert("RGB")
            prev = bo8[k]["cands"][meta["served"]]["code"]
            msgs.append(build_messages(orig, rend, prev, cfg))
        t0 = time.time()
        outs = gen(msgs)
        dt = (time.time() - t0) / len(chunk)
        def _corrupt(t):
            if "!!!!!!!!" in t:
                return True
            c = extract_code(t)
            if not c:
                return True
            try:
                compile(c, "<rev>", "exec")
            except SyntaxError:
                return True
            return False
        n_bad = sum(_corrupt(t) for t in outs)
        if n_bad:
            print(f"[sc] WARNING degenerate generations in batch: {n_bad}/{len(outs)} (bad GPU?)", flush=True)
            if n_bad >= 2:
                raise RuntimeError("degenerate generations — bad GPU?")
        futs = []
        for (k, meta, rec), text in zip(chunk, outs):
            rec["rev_text_len"] = len(text)
            rec["rev_code"] = extract_code(text)
            rec["gen_s"] = round(dt, 1)
            prev = bo8[k]["cands"][meta["served"]]["code"]
            rec["changed"] = (rec["rev_code"] or "").strip() != prev.strip()
            rec["think_tail"] = (text.split("</think>")[0] if "</think>" in text else text)[-1500:]
            recs[k] = rec
            futs.append(pool.submit(score, k, meta, rec, td))
        for f in futs:
            f.result()
        for k, meta, rec in chunk:
            print(f"[sc] {k[:8]} served={rec['served_iou']:.3f} rev={rec['rev_iou']:.3f} "
                  f"exec={rec['rev_exec']} changed={rec['changed']} agree {rec['served_agree']:.3f}->"
                  f"{(rec['rev_agree'] or 0):.3f} ({rec['gen_s']}s)", flush=True)
        save()
        print(f"[sc] {min(b + a.batch, len(items))}/{len(items)}", flush=True)
    save()
    print("[sc] done", flush=True)


if __name__ == "__main__":
    main()
