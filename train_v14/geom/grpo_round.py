"""GRPO-style online RL round for drawing -> build123d (2026-10-05).

One self-contained single-GPU loop per round:
  1. sample G completions per part from the current policy (e55 + LoRA adapter)
  2. execute + exact-IoU score them (the eval metric IS the reward)
  3. group-relative advantage (Dr.GRPO length-normalised / GRPO std / token-mean)
  4. policy-gradient update on the LoRA (on-policy single inner epoch, so the
     PPO ratio is 1 by construction), optional KL anchor to the base (adapter
     disabled in the same forward), DAPO-style zero-variance group filtering
  5. save the adapter + a rollout log (rewards, group stats, lengths)

Design notes (evidence in RECIPE.md 2026-09-24/25 + trace ontology 2026-10-05):
- The reward is exact and verifiable (centered volumetric IoU vs GT mesh), so
  no reward model. Non-executing = 0 (optionally minus --exec-penalty).
- Zero-variance groups carry no gradient (DAPO dynamic sampling): skipped for
  the update but logged, so the frontier fraction is measurable per round.
- Length-normalised loss by default (Dr.GRPO): success anti-correlates with
  trace length in this task (shortest quartile 27% solved vs 7% for the
  longest); an unnormalised sum-loss would reward brevity, not accuracy.
- KL anchor is ON by default: continued training from e55 costs ~0.03 vote on
  the real bench (the "delta tax"); the anchor plus a LoRA (not full FT) is
  the mitigation.

    python train_v14/geom/grpo_round.py --run e55-rft-real-u5-gt-dw423 \
        --bench fp/h6/train_bench --out runs/grpo_r1 \
        --n-parts 16 --g 8 --steps 50 --lr 1e-5
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import sys
import tempfile
import time
import random
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
TRAIN = os.path.dirname(HERE)
sys.path.insert(0, TRAIN)
sys.path.insert(0, HERE)

import torch  # noqa: E402

from collate_v14 import SYSTEM_PROMPTS, USER_PROMPT, VLMCollator  # noqa: E402
from data_v14 import _decode_png  # noqa: E402
from geom_eval_worker import classify_ckpt, extract_code, load_model, run_config  # noqa: E402
from rft_generate import exec_to_stl  # noqa: E402
from iou import iou_pair  # noqa: E402


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, help="policy run name (e55...)")
    ap.add_argument("--model-base", default="", help="override processor/base model dir (serv hosts)")
    ap.add_argument("--ckpt", default="", help="explicit ckpt dir (overrides --run final)")
    ap.add_argument("--adapter", default="", help="resume: peft adapter dir to stack on the policy")
    ap.add_argument("--bench", required=True, help="bench dir with eval_cache_v15.pkl + gt_meshes_v15/")
    ap.add_argument("--keys", default="", help="file with part keys to train on (frontier list); default all in pool")
    ap.add_argument("--out", required=True, help="output dir (adapter + logs)")
    ap.add_argument("--n-parts", type=int, default=16, help="parts per rollout batch (update granularity)")
    ap.add_argument("--g", type=int, default=8, help="group size (samples per part)")
    ap.add_argument("--steps", type=int, default=50, help="number of rollout batches (= optimizer updates)")
    ap.add_argument("--lr", type=float, default=1e-5)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--top-p", type=float, default=0.95)
    ap.add_argument("--max-new-tokens", type=int, default=2400)
    ap.add_argument("--gen-batch", type=int, default=16, help="sequences per generate() call")
    ap.add_argument("--train-batch", type=int, default=8, help="sequences per forward/backward")
    ap.add_argument("--adv", choices=["mean", "std"], default="mean",
                    help="mean: A = r - mean(r) (Dr.GRPO); std: /(group std + eps) (GRPO)")
    ap.add_argument("--loss", choices=["drgpo", "token"], default="drgpo",
                    help="drgpo: length-normalised; token: DAPO token-level mean")
    ap.add_argument("--kl-beta", type=float, default=0.02, help="KL(pi||pi_ref) weight on completion tokens")
    ap.add_argument("--exec-penalty", type=float, default=0.0, help="reward for non-executing: -penalty")
    ap.add_argument("--min-var", type=float, default=1e-4, help="skip groups with reward variance below this")
    ap.add_argument("--greedy-draw0", action="store_true", help="draw 0 greedy (diagnostic; excluded from loss)")
    ap.add_argument("--score-workers", type=int, default=16)
    ap.add_argument("--lora-rank", type=int, default=64)
    ap.add_argument("--lora-alpha", type=int, default=128)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--save-every", type=int, default=10)
    ap.add_argument("--system-prompt", default="detailed")
    ap.add_argument("--reasoning-effort", default="medium")
    return ap.parse_args()


def load_bench(bench_dir: str, keys_file: str):
    cache = pickle.load(open(os.path.join(bench_dir, "eval_cache_v15.pkl"), "rb"))
    pool = cache.get("pools", {})
    keys = None
    for name in ("certified", "all", "train"):
        if name in pool and pool[name]:
            keys = list(pool[name])
            break
    if keys is None and cache.get("samples"):
        keys = list(cache["samples"])
    if keys_file:
        want = [ln.strip() for ln in open(keys_file) if ln.strip()]
        keys = [k for k in want if k in cache["samples"]]
    gt_dir = os.path.join(bench_dir, "gt_meshes_v15")
    keys = [k for k in keys if os.path.exists(os.path.join(gt_dir, f"{k}.stl"))]
    return cache, keys, gt_dir


def main():
    args = parse_args()
    os.makedirs(args.out, exist_ok=True)
    torch.manual_seed(args.seed)
    device = "cuda"

    cfg = run_config(args.run) or {}
    if args.model_base:
        cfg["model_id"] = args.model_base
    ckpt = args.ckpt or os.path.join("runs", args.run, "final")
    model, processor = load_model(ckpt, classify_ckpt(ckpt), cfg)
    model = model.to(device)

    # LoRA policy on top of the frozen base (the base is the KL reference).
    # Target modules: reuse the trainer's auto-detection (covers the hybrid
    # attention/MLP stack, excludes vision tower / lm_head / mtp / embeddings).
    def _auto_lora_targets(model) -> list[str]:
        import torch.nn as nn
        vis = None
        for path in ("model.visual", "visual", "vision_tower", "vision_model"):
            obj = model
            try:
                for part in path.split("."):
                    obj = getattr(obj, part)
                vis = obj
                break
            except AttributeError:
                continue
        vis_ids = {id(m) for m in vis.modules()} if vis is not None else set()
        names = set()
        for fqn, mod in model.named_modules():
            if not isinstance(mod, nn.Linear) or id(mod) in vis_ids:
                continue
            low = fqn.lower()
            if "lm_head" in low or "mtp" in low or "embed" in low:
                continue
            names.add(fqn.rsplit(".", 1)[-1])
        out = sorted(names)
        print(f"[grpo] LoRA target modules: {out}", flush=True)
        return out

    if args.adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, args.adapter, is_trainable=True)
        print(f"[grpo] resumed adapter {args.adapter}", flush=True)
    else:
        from peft import LoraConfig, get_peft_model
        lcfg = LoraConfig(r=args.lora_rank, lora_alpha=args.lora_alpha, lora_dropout=0.0,
                          target_modules=_auto_lora_targets(model), task_type="CAUSAL_LM")
        model = get_peft_model(model, lcfg)
    model.print_trainable_parameters()

    collator = VLMCollator(processor, max_seq_len=5120,
                           system_prompt=args.system_prompt,
                           reasoning_effort=args.reasoning_effort)
    cache, keys, gt_dir = load_bench(args.bench, args.keys)
    print(f"[grpo] bench {args.bench}: {len(keys)} parts with GT", flush=True)
    assert len(keys) >= args.n_parts, "not enough parts"

    rng = random.Random(args.seed)
    rng.shuffle(keys)
    part_cycle = keys * 100

    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=args.lr, betas=(0.9, 0.95), weight_decay=0.0)

    logf = open(os.path.join(args.out, "round_log.jsonl"), "a")
    rollf = open(os.path.join(args.out, "rollouts.jsonl"), "a")
    tmpl = dict(enable_thinking=True, reasoning_effort=args.reasoning_effort)
    from qwen_vl_utils import process_vision_info

    def gen_texts(seqs):
        """Sampled generation for a list of {part, image, draw} dicts."""
        msgs = [[
            {"role": "system", "content": [{"type": "text", "text": SYSTEM_PROMPTS[args.system_prompt]}]},
            {"role": "user", "content": [{"type": "image", "image": s["image"]},
                                         {"type": "text", "text": USER_PROMPT}]},
        ] for s in seqs]
        texts = [processor.apply_chat_template(m, add_generation_prompt=True, tokenize=False, **tmpl)
                 for m in msgs]
        images, videos = process_vision_info(msgs)
        enc = processor(text=texts, images=images, videos=videos, return_tensors="pt", padding=True)
        enc = {k: (v.to(device) if hasattr(v, "to") else v) for k, v in enc.items()}
        kw = dict(max_new_tokens=args.max_new_tokens,
                  pad_token_id=processor.tokenizer.pad_token_id or processor.tokenizer.eos_token_id)
        if args.greedy_draw0 and seqs[0]["draw"] == 0:
            kw["do_sample"] = False
        else:
            kw.update(do_sample=True, temperature=args.temperature, top_p=args.top_p)
        model.eval()
        try:
            model.gradient_checkpointing_disable()
        except Exception:
            pass
        with torch.no_grad():
            out = model.generate(**enc, **kw)
        model.train()
        return processor.tokenizer.batch_decode(out[:, enc["input_ids"].shape[1]:],
                                                skip_special_tokens=True)

    def score_cands(part, cands, td):
        """Execute + IoU every candidate of one group; sets c[i]['exec'/'iou']; returns rewards in order."""
        def one(i):
            c = cands[i]
            if not c["code"]:
                return -args.exec_penalty
            stl = os.path.join(td, f"{part}_{i}.stl")
            if not exec_to_stl(c["code"], stl, td, f"{part}_{i}"):
                c["exec"] = False
                return -args.exec_penalty if args.exec_penalty else 0.0
            c["exec"] = True
            try:
                r = iou_pair(stl, os.path.join(gt_dir, f"{part}.stl"))["iou_centered"]
            except Exception:
                r = 0.0
            c["iou"] = float(r)
            return float(r)
        with ThreadPoolExecutor(max_workers=args.score_workers) as ex:
            return list(ex.map(one, range(len(cands))))

    def completion_logps(batch_dicts):
        """Forward a collated batch; returns per-sample (sum_logp, n_toks, kl_sum).

        Completions are right-aligned (left padding), so only the last n_max
        logit positions are needed — slice before the float32 log_softmax to
        keep the [B, n_max, vocab] tensors small. Gradient checkpointing keeps
        activation memory bounded for the policy forward.
        """
        enc = collator(batch_dicts)
        enc = {k: (v.to(device) if hasattr(v, "to") else v) for k, v in enc.items()}
        labels = enc.pop("labels")
        mask_full = labels != -100
        n_toks = mask_full.sum(-1)
        seq_len = labels.shape[1]
        n_max = min(int(n_toks.max().item()), seq_len - 1)
        # targets at the tail: labels[:, -n_max:], predicted by logits[:, -n_max-1:-1]
        tgt = labels[:, -n_max:]
        tmask = tgt != -100
        tgt_safe = tgt.masked_fill(~tmask, 0)

        try:
            model.gradient_checkpointing_enable()
            model.enable_input_require_grads()
        except Exception:
            pass
        logits = model(**enc).logits[:, -n_max - 1:-1, :]
        logp_all = torch.log_softmax(logits.float(), dim=-1)
        tok_logp = logp_all.gather(-1, tgt_safe.unsqueeze(-1)).squeeze(-1) * tmask
        sum_logp = tok_logp.sum(-1)
        del logits, logp_all

        kl_sum = torch.zeros_like(sum_logp)
        if args.kl_beta > 0:
            with torch.no_grad(), model.disable_adapter():
                rlogits = model(**enc).logits[:, -n_max - 1:-1, :]
                rlogp_all = torch.log_softmax(rlogits.float(), dim=-1)
                rtok = rlogp_all.gather(-1, tgt_safe.unsqueeze(-1)).squeeze(-1) * tmask
                # k3 estimator per token: exp(ref - pi) - (ref - pi) - 1
                d = (rtok - tok_logp).clamp(-20, 20)
                kl_sum = (torch.expm1(d) - d).masked_fill(~tmask, 0.0).sum(-1)
                del rlogits, rlogp_all
        return sum_logp, n_toks, kl_sum

    t0 = time.time()
    for step in range(args.steps):
        parts = part_cycle[step * args.n_parts:(step + 1) * args.n_parts]
        base = [{"part": k, "image": _decode_png(cache["samples"][k]["png"])} for k in parts]

        # ---- rollout: G draws for all parts ----
        seqs = [{**s, "draw": g} for g in range(args.g) for s in base]
        outs = []
        for b in range(0, len(seqs), args.gen_batch):
            outs.extend(gen_texts(seqs[b:b + args.gen_batch]))

        # ---- execute + score ----
        groups = []
        with tempfile.TemporaryDirectory(prefix="grpo_") as td:
            for pi, s in enumerate(base):
                cands = []
                for g in range(args.g):
                    text = outs[pi * args.g + g]
                    think = (text.split("without think", 1)[0].replace("think", "").strip()
                             if "without think" in text else "")
                    cands.append({"draw": g, "think": think, "code": extract_code(text),
                                  "exec": False, "iou": 0.0})
                rewards = score_cands(s["part"], cands, td)
                groups.append({"part": s["part"], "image": s["image"],
                               "cands": cands, "rewards": rewards})

        # ---- advantages ----
        n_front = 0
        for g in groups:
            r = torch.tensor(g["rewards"], dtype=torch.float32)
            if float(r.var()) < args.min_var:
                g["adv"] = None
                continue
            n_front += 1
            a = r - r.mean()
            if args.adv == "std":
                a = a / (r.std(unbiased=False) + 1e-4)
            g["adv"] = a.tolist()

        # ---- update ----
        train_dicts, advs = [], []
        for g in groups:
            if g["adv"] is None:
                continue
            for c, a in zip(g["cands"], g["adv"]):
                if c["code"] is None:
                    continue  # nothing to reinforce
                train_dicts.append({"image": g["image"], "trace": c["think"], "code": c["code"]})
                advs.append(a)

        stats = {"step": step, "parts": len(groups), "frontier_groups": n_front,
                 "train_seqs": len(train_dicts)}
        allr = [r for g in groups for r in g["rewards"]]
        stats["mean_reward"] = sum(allr) / max(1, len(allr))
        stats["mean_best_of_g"] = sum(max(g["rewards"]) for g in groups) / max(1, len(groups))
        stats["mean_exec"] = sum(c["exec"] for g in groups for c in g["cands"]) / max(1, len(allr))
        lens = [len((c.get("think") or "") + (c.get("code") or "")) for g in groups for c in g["cands"]]
        stats["mean_completion_chars"] = round(sum(lens) / max(1, len(lens)), 1)
        if train_dicts:
            opt.zero_grad(set_to_none=True)
            nchunks = (len(train_dicts) + args.train_batch - 1) // args.train_batch
            tot_loss = tot_kl = 0.0
            for b in range(0, len(train_dicts), args.train_batch):
                chunk = train_dicts[b:b + args.train_batch]
                ca = torch.tensor(advs[b:b + args.train_batch], dtype=torch.float32, device=device)
                sum_logp, n_toks, kl_sum = completion_logps(chunk)
                if args.loss == "drgpo":
                    per = sum_logp / n_toks.clamp(min=1)
                    loss = -(ca * per).sum() / len(chunk)
                else:
                    loss = -(ca * sum_logp).sum() / n_toks.sum().clamp(min=1)
                if args.kl_beta > 0:
                    loss = loss + args.kl_beta * kl_sum.sum() / n_toks.sum().clamp(min=1)
                (loss / nchunks).backward()
                tot_loss += float(loss)
                tot_kl += float(kl_sum.sum() / n_toks.sum().clamp(min=1))
            torch.nn.utils.clip_grad_norm_(params, 1.0)
            opt.step()
            stats["loss"] = round(tot_loss / nchunks, 4)
            stats["kl"] = round(tot_kl / nchunks, 4)
        stats["elapsed_s"] = round(time.time() - t0, 1)
        print(json.dumps(stats), flush=True)
        logf.write(json.dumps(stats) + "\n"); logf.flush()
        for g in groups:
            rollf.write(json.dumps({
                "part": g["part"], "rewards": g["rewards"],
                "cands": [{"draw": c["draw"], "exec": c["exec"], "iou": c.get("iou", 0.0),
                           "think_chars": len(c["think"] or ""), "code_chars": len(c["code"] or "")}
                          for c in g["cands"]]}) + "\n")
        rollf.flush()
        if (step + 1) % args.save_every == 0 or step == args.steps - 1:
            ad = os.path.join(args.out, f"adapter_step{step + 1}")
            model.save_pretrained(ad)
            print(f"[grpo] saved {ad}", flush=True)
    model.save_pretrained(os.path.join(args.out, "adapter_final"))
    print("[grpo] ROUND DONE", flush=True)


if __name__ == "__main__":
    main()
