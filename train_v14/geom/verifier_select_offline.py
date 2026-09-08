"""Offline selection study for a learned verifier on STORED best-of-N
candidates (no generation, no re-execution): score every executing candidate
with a binary verifier adapter (LoRA on its base, log-odds of "yes" vs "no"),
then compare selection policies on the same candidates at K = first K draws:

  first_exec      first executing candidate (draw order)
  vote            consistency medoid on the stored pairwise-IoU matrix
  verifier        argmax verifier score
  ver_top{k}_vote verifier top-k, then medoid inside the top-k        (k = 4, 8)
  vote_top{k}_ver agreement top-k, then argmax verifier               (k = 4, 8)
  hybrid          argmax of mean rank (verifier rank + agreement rank)
  ver_gate{t}     verifier argmax if its p(yes) >= t, else the vote (t = 0.5, 0.8)
  agree_gate{t}   the vote if the medoid's mean agreement >= t (confident,
                  in-distribution-like), else verifier argmax (t = 0.7, 0.85)
  oracle          argmax true IoU (ceiling)

plus the verifier's Spearman with true IoU (pooled and per part) and its
AUROC for iou >= 0.8 / 0.85.

Prompt: the SAME text the binary verifier was trained on (VERIFIER_BIN_USER,
assistant prefix "<think>\n\n</think>\n\n") and the logits at the position of
the yes/no token — bestofn_verifier_eval.py's binary mode scored v2 with the
regression prompt and at the "<think>\n" position (--prompt-mode legacy
reproduces that for comparison). --prompt-mode reg scores a REGRESSION
verifier (v1/v3b target "0.73"): greedy-decode the number after the same
assistant prefix; pred = p_yes = the predicted IoU. --prompt-mode reg_ev
scores the same regression verifier by the EXPECTED value of its number
(one forward pass on prefix + "0.": p(first token = "1") and the first-decimal
digit distribution) — continuous, no ties from the 2-decimal greedy decode.

    python verifier_select_offline.py --verifier runs/v3-verifier-real/best_adapter \
        --verifier-run v3-verifier-real \
        --cands results/ext/bo32_ext_e51-rft-real-u3-strict90.json \
        --consistency results/ext/bo32_ext_e51-rft-real-u3-strict90_consistency.json \
        --cache train_v14/mech/benchmarks/data/ext_bench/eval_cache_v14.pkl \
        --split train_v14/mech/benchmarks/data/ext_bench/split.json \
        --k 8 32 --out results/ext/vsel_v3_e51_bo32.json
Preds are cached in <out>.preds.json; with --no-model the policies are
recomputed from that cache (instant).
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

from collate_v14 import VERIFIER_BIN_USER, VERIFIER_SYSTEM, VERIFIER_USER, wrap_python  # noqa: E402
from data_v14 import _decode_png  # noqa: E402


# ----------------------------------------------------------------- statistics
def spearman(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3 or a.std() == 0 or b.std() == 0:
        return float("nan")
    from scipy.stats import rankdata
    return float(np.corrcoef(rankdata(a), rankdata(b))[0, 1])


def auroc(scores, labels):
    from scipy.stats import rankdata
    s, y = np.asarray(scores, float), np.asarray(labels, bool)
    n1, n0 = y.sum(), (~y).sum()
    if n1 == 0 or n0 == 0:
        return float("nan")
    r = rankdata(s)
    return float((r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


# ------------------------------------------------------------------- scoring
def build_prompt(proc, image, code, mode, vcfg):
    tmpl = dict(enable_thinking=True, reasoning_effort=vcfg.get("reasoning_effort", "medium")) \
        if vcfg.get("trace_style", "think") == "think" else {}
    if mode == "legacy":
        msgs = [{"role": "system", "content": [{"type": "text", "text": VERIFIER_SYSTEM}]},
                {"role": "user", "content": [{"type": "image", "image": image},
                                             {"type": "text", "text": VERIFIER_USER.format(code=wrap_python(code))}]}]
        return msgs, proc.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False, **tmpl)
    user = VERIFIER_USER if mode in ("reg", "reg_ev") else VERIFIER_BIN_USER
    ans = "0.00" if mode in ("reg", "reg_ev") else "yes"
    msgs = [{"role": "system", "content": [{"type": "text", "text": VERIFIER_SYSTEM}]},
            {"role": "user", "content": [{"type": "image", "image": image},
                                         {"type": "text", "text": user.format(code=wrap_python(code))}]},
            {"role": "assistant", "content": [{"type": "text", "text": ans}]}]
    full = proc.apply_chat_template(msgs, add_generation_prompt=False, tokenize=False, **tmpl)
    cut = full.rfind(ans + "<|im_end|>")
    assert cut > 0, full[-200:]
    text = full[:cut]
    assert text.endswith("<think>\n\n</think>\n\n"), repr(text[-60:])
    if mode == "reg_ev":
        text += "0."
    return msgs[:-1], text


def reg_ev_scores(model, proc, images, codes, vcfg, batch=8, log=print):
    """Expected-value score of a REGRESSION verifier for aligned (image, code)
    pairs: one forward pass on the training prompt + assistant prefix + "0.",
    p(first token = "1") + p("0") * E[first decimal digit + 0.05]. Shared by
    the offline study (reg_ev mode) and serve.py; `model` may be a PeftModel
    with the verifier adapter active. Returns a list of floats."""
    import torch
    from qwen_vl_utils import process_vision_info
    tok = proc.tokenizer
    d_ids = [tok.encode(str(d), add_special_tokens=False)[0] for d in range(10)]
    out_scores = []
    for b in range(0, len(codes), batch):
        msgs, texts = [], []
        for image, code in zip(images[b:b + batch], codes[b:b + batch]):
            m, t = build_prompt(proc, image, code, "reg_ev", vcfg)
            msgs.append(m); texts.append(t)
        imgs, vids = process_vision_info(msgs)
        enc = proc(text=texts, images=imgs, videos=vids, return_tensors="pt", padding=True)
        enc = {k: (v.to(model.device) if hasattr(v, "to") else v) for k, v in enc.items()}
        with torch.no_grad():
            try:
                out = model(**enc, use_cache=False, logits_to_keep=3)
            except TypeError:
                out = model(**enc, use_cache=False)
        lg = out.logits.float()
        for row in range(len(texts)):
            first = torch.softmax(lg[row, -3, [d_ids[0], d_ids[1]]], 0)   # after "\n\n": "0" vs "1"
            dec = torch.softmax(lg[row, -1, d_ids], 0)                     # after "0.": first decimal
            ev = first[1].item() + first[0].item() * sum(dec[d].item() * (d / 10 + 0.05) for d in range(10))
            out_scores.append(ev)
        if log and (b // batch) % 20 == 0:
            log(f"[vsel] {b + len(texts)}/{len(codes)} ev e.g. {out_scores[-1]:.3f}")
    return out_scores


def score_all(args, parts, images):
    import torch
    from qwen_vl_utils import process_vision_info
    from geom_eval_worker import classify_ckpt, load_model, run_config

    vcfg = run_config(args.verifier_run)
    assert vcfg, f"no config for {args.verifier_run}"
    if args.base:
        vcfg["model_id"] = args.base
    model, proc = load_model(args.verifier, classify_ckpt(args.verifier), vcfg)
    model.eval()
    tok = proc.tokenizer
    yes_id, no_id = tok.encode("yes", add_special_tokens=False)[0], tok.encode("no", add_special_tokens=False)[0]
    yes_ids = {tok.encode(v, add_special_tokens=False)[0] for v in ("yes", " yes", "Yes")}
    no_ids = {tok.encode(v, add_special_tokens=False)[0] for v in ("no", " no", "No")}
    todo = [(pi, j) for pi, p in enumerate(parts) for j, c in enumerate(p["cands"])
            if c.get("exec") and c.get("code")]
    print(f"[vsel] scoring {len(todo)} executing candidates, mode={args.prompt_mode}, batch={args.batch}", flush=True)
    if args.prompt_mode == "reg_ev":
        evs = reg_ev_scores(model, proc, [images[parts[pi]["key"]] for pi, _ in todo],
                            [parts[pi]["cands"][j]["code"] for pi, j in todo], vcfg, batch=args.batch,
                            log=lambda m: print(m, flush=True))
        for (pi, j), ev in zip(todo, evs):
            c = parts[pi]["cands"][j]
            c["pred"], c["pred_maxvar"], c["p_yes"] = ev, ev, ev
        todo = []
    kw_keep = {"logits_to_keep": 1}
    for b in range(0, len(todo), args.batch):
        chunk = todo[b:b + args.batch]
        msgs, texts = [], []
        for pi, j in chunk:
            m, t = build_prompt(proc, images[parts[pi]["key"]], parts[pi]["cands"][j]["code"],
                                args.prompt_mode, vcfg)
            msgs.append(m); texts.append(t)
        imgs, vids = process_vision_info(msgs)
        enc = proc(text=texts, images=imgs, videos=vids, return_tensors="pt", padding=True)
        enc = {k: (v.to(model.device) if hasattr(v, "to") else v) for k, v in enc.items()}
        if args.prompt_mode == "reg":
            import re
            with torch.no_grad():
                gen = model.generate(**enc, max_new_tokens=6, do_sample=False,
                                     pad_token_id=tok.pad_token_id or tok.eos_token_id)
            texts_out = tok.batch_decode(gen[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)
            for (pi, j), t in zip(chunk, texts_out):
                m = re.search(r"\d*\.?\d+", t)
                v = float(m.group(0)) if m else 0.0
                c = parts[pi]["cands"][j]
                c["pred"], c["pred_maxvar"], c["p_yes"] = v, v, v
            if (b // args.batch) % 20 == 0:
                print(f"[vsel] {b + len(chunk)}/{len(todo)} e.g. {texts_out[0]!r}", flush=True)
            continue
        with torch.no_grad():
            try:
                out = model(**enc, use_cache=False, **kw_keep)
            except TypeError:
                kw_keep = {}
                out = model(**enc, use_cache=False)
        logits = out.logits[:, -1, :].float()
        for row, (pi, j) in enumerate(chunk):
            c = parts[pi]["cands"][j]
            ly, ln = logits[row, yes_id].item(), logits[row, no_id].item()
            c["pred"] = ly - ln
            c["pred_maxvar"] = max(logits[row, t].item() for t in yes_ids) - max(logits[row, t].item() for t in no_ids)
            c["p_yes"] = float(torch.softmax(torch.tensor([ly, ln]), 0)[0])
        if (b // args.batch) % 20 == 0:
            print(f"[vsel] {b + len(chunk)}/{len(todo)}", flush=True)
    del model
    torch.cuda.empty_cache()


# ------------------------------------------------------------------ policies
def medoid(idx, mat, tiebreak):
    """idx: candidate positions; mat[i][j] pairwise IoU (None -> 0)."""
    if len(idx) == 1:
        return idx[0]
    best, best_key = None, None
    for j in idx:
        agree = np.mean([(mat[j][i] or 0.0) for i in idx if i != j])
        key = (agree, tiebreak.get(j, 0.0))
        if best_key is None or key > best_key:
            best, best_key = j, key
    return best


GATES = (0.5, 0.8)
AGATES = (0.7, 0.85)


def select(part, mat, K, topks):
    cs = part["cands"][:K]
    ex = [j for j, c in enumerate(cs) if c.get("exec") and "pred" in c]
    ious = [c["iou"] for c in cs]
    out = {}
    if not ex:
        return {name: 0.0 for name in ["first_exec", "vote", "verifier", "oracle", "hybrid"]
                + [f"ver_top{k}_vote" for k in topks] + [f"vote_top{k}_ver" for k in topks]
                + [f"ver_gate{t}" for t in GATES] + [f"agree_gate{t}" for t in AGATES]}
    pred = {j: cs[j]["pred"] for j in ex}
    agree = {j: (np.mean([(mat[j][i] or 0.0) for i in ex if i != j]) if len(ex) > 1 else 0.0) for j in ex}
    out["first_exec"] = ious[ex[0]]
    out["vote"] = ious[medoid(ex, mat, tiebreak={})]
    out["verifier"] = ious[max(ex, key=lambda j: pred[j])]
    out["oracle"] = max(ious[j] for j in ex)
    for k in topks:
        top = sorted(ex, key=lambda j: -pred[j])[:k]
        out[f"ver_top{k}_vote"] = ious[medoid(top, mat, tiebreak=pred)]
        topa = sorted(ex, key=lambda j: -agree[j])[:k]
        out[f"vote_top{k}_ver"] = ious[max(topa, key=lambda j: pred[j])]
    from scipy.stats import rankdata
    rp = rankdata([pred[j] for j in ex]); ra = rankdata([agree[j] for j in ex])
    out["hybrid"] = ious[ex[int(np.argmax(rp + ra))]]
    jv = max(ex, key=lambda j: pred[j])
    for t in GATES:
        out[f"ver_gate{t}"] = ious[jv] if cs[jv].get("p_yes", 0.0) >= t else out["vote"]
    amax = max(agree.values())
    for t in AGATES:
        out[f"agree_gate{t}"] = out["vote"] if amax >= t else ious[jv]
    return out


def summarise(rows, names):
    n = len(rows)
    return {nm: {"mean": float(np.mean([r[nm] for r in rows])),
                 "ge85": float(np.mean([r[nm] >= 0.85 for r in rows])),
                 "ge50": float(np.mean([r[nm] >= 0.5 for r in rows]))} for nm in names}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verifier", default="")
    ap.add_argument("--verifier-run", default="v3-verifier-real")
    ap.add_argument("--base", default="", help="override the base model dir (e.g. weights staged in /dev/shm)")
    ap.add_argument("--cands", required=True)
    ap.add_argument("--consistency", default="", help="consistency_rerank output with parts[].pair_iou")
    ap.add_argument("--cache", required=True, help="eval cache pkl with samples[key].png")
    ap.add_argument("--split", default="", help="ext_bench split.json (family / underdetermined slices)")
    ap.add_argument("--k", type=int, nargs="+", default=[8, 32])
    ap.add_argument("--topk", type=int, nargs="+", default=[4, 8])
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--prompt-mode", default="bin", choices=["bin", "legacy", "reg", "reg_ev"])
    ap.add_argument("--no-model", action="store_true", help="reuse <out>.preds.json")
    ap.add_argument("--n", type=int, default=0, help="first n parts only (0 = all)")
    ap.add_argument("--subset", type=int, default=0, help="random subset of this many parts (seeded)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    data = json.load(open(args.cands))
    parts = data["candidates"][: args.n or None]
    if args.subset and args.subset < len(parts):
        import random
        parts = random.Random(args.seed).sample(parts, args.subset)
        parts.sort(key=lambda p: p["key"])
        print(f"[vsel] random subset of {len(parts)} parts (seed {args.seed})", flush=True)
    for p in parts:
        p["cands"].sort(key=lambda c: c.get("draw", 0))
    keys = [p["key"] for p in parts]
    preds_path = args.out + ".preds.json"
    if args.no_model:
        pr = json.load(open(preds_path))
        for p in parts:
            for c, v in zip(p["cands"], pr[p["key"]]):
                c.pop("pred", None)
                if v is not None:
                    c["pred"], c["pred_maxvar"], c["p_yes"] = v
    else:
        with open(args.cache, "rb") as f:
            cache = pickle.load(f)
        images = {k: _decode_png(cache["samples"][k]["png"]) for k in keys}
        for p in parts:
            for c in p["cands"]:
                c.pop("pred", None)     # stored preds are from the generation-time verifier stub
        score_all(args, parts, images)
        json.dump({p["key"]: [([c["pred"], c["pred_maxvar"], c["p_yes"]] if "pred" in c else None)
                              for c in p["cands"]] for p in parts}, open(preds_path, "w"))

    # agreement matrices
    mats = {}
    if args.consistency:
        cons = json.load(open(args.consistency))
        for cp in cons["parts"]:
            mats[cp["key"]] = cp["pair_iou"]
    for p in parts:
        k = len(p["cands"])
        if p["key"] not in mats or mats[p["key"]] is None:
            mats[p["key"]] = [[None] * k for _ in range(k)]
    split = json.load(open(args.split)) if args.split else {}

    names = ["first_exec", "vote", "verifier"] + [f"ver_top{k}_vote" for k in args.topk] + \
            [f"vote_top{k}_ver" for k in args.topk] + ["hybrid"] + \
            [f"ver_gate{t}" for t in GATES] + [f"agree_gate{t}" for t in AGATES] + ["oracle"]
    result = {"cands": args.cands, "verifier": args.verifier, "prompt_mode": args.prompt_mode,
              "n_parts": len(parts), "subset": args.subset, "seed": args.seed, "keys": keys, "by_k": {}}
    lines = []
    for K in args.k:
        rows = [dict(key=p["key"], **select(p, mats[p["key"]], K, args.topk)) for p in parts]
        slices = {"all": rows}
        if split:
            slices["determinate"] = [r for r in rows if split.get(r["key"], {}).get("underdetermined") is False]
            slices["underdetermined"] = [r for r in rows if split.get(r["key"], {}).get("underdetermined") is True]
            slices["F"] = [r for r in rows if split.get(r["key"], {}).get("family") == "F"]
            slices["A"] = [r for r in rows if split.get(r["key"], {}).get("family") == "A"]
        # verifier quality on the executing candidates of the first K draws
        pooled_p, pooled_i, per_part = [], [], []
        for p in parts:
            cs = [c for c in p["cands"][:K] if "pred" in c]
            pooled_p += [c["pred"] for c in cs]; pooled_i += [c["iou"] for c in cs]
            if len(cs) >= 3:
                s = spearman([c["pred"] for c in cs], [c["iou"] for c in cs])
                if not np.isnan(s):
                    per_part.append(s)
        q = {"n_scored": len(pooled_p),
             "spearman_pooled": spearman(pooled_p, pooled_i),
             "spearman_per_part_mean": float(np.mean(per_part)) if per_part else float("nan"),
             "auroc_0.8": auroc(pooled_p, [i >= 0.8 for i in pooled_i]),
             "auroc_0.85": auroc(pooled_p, [i >= 0.85 for i in pooled_i]),
             "pos_share_0.8": float(np.mean([i >= 0.8 for i in pooled_i])) if pooled_i else float("nan")}
        result["by_k"][str(K)] = {"slices": {nm: summarise(r, names) for nm, r in slices.items() if r},
                                  "verifier_quality": q, "per_part": rows}
        lines.append(f"\nK={K}  (n={len(parts)}; verifier: spearman pooled {q['spearman_pooled']:.3f}, "
                     f"per-part {q['spearman_per_part_mean']:.3f}; AUROC iou>=0.8 {q['auroc_0.8']:.3f}, "
                     f">=0.85 {q['auroc_0.85']:.3f}; {q['n_scored']} scored, {q['pos_share_0.8']*100:.1f}% >=0.8)")
        lines.append(f"{'policy':16s} | " + " | ".join(f"{nm:>15s}" for nm, r in slices.items() if r))
        for nm in names:
            lines.append(f"{nm:16s} | " + " | ".join(
                f"{s[nm]['mean']:.3f} / {s[nm]['ge85']*100:3.0f}%"
                for s in [result['by_k'][str(K)]['slices'][x] for x, r in slices.items() if r]))
    txt = "\n".join(lines)
    print(txt, flush=True)
    result["table"] = txt
    with open(args.out, "w") as f:
        json.dump(result, f, indent=1)
    with open(args.out.replace(".json", "") + "_summary.txt", "w") as f:
        f.write(txt + "\n")


if __name__ == "__main__":
    main()
