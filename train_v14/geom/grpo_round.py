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

from collate_v14 import REPAIR_PROMPT, SYSTEM_PROMPTS, USER_PROMPT, VLMCollator  # noqa: E402
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
    ap.add_argument("--adv", choices=["mean", "std", "batchstd"], default="mean",
                    help="mean: A = r - mean(r) (Dr.GRPO); std: /(group std + eps) (GRPO)")
    ap.add_argument("--loss", choices=["drgpo", "token"], default="drgpo",
                    help="drgpo: length-normalised; token: DAPO token-level mean")
    ap.add_argument("--kl-beta", type=float, default=0.02, help="KL(pi||pi_ref) weight on completion tokens")
    ap.add_argument("--exec-penalty", type=float, default=0.0, help="reward for non-executing: -penalty")
    ap.add_argument("--min-var", type=float, default=1e-4, help="skip groups with reward variance below this")
    ap.add_argument("--greedy-draw0", action="store_true", help="draw 0 greedy (diagnostic; excluded from loss)")
    ap.add_argument("--score-workers", type=int, default=16)
    ap.add_argument("--score-timeouts", action="store_true",
                    help="exec (60 s) + IoU (90 s) in killable subprocesses, timeouts scored 0 -- the "
                         "score_partials.py eval rule; bounds the step time (a pathological mesh's IoU "
                         "fallback can run 8+ min in-thread)")
    ap.add_argument("--lora-rank", type=int, default=64)
    ap.add_argument("--lora-alpha", type=int, default=128)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--save-every", type=int, default=10)
    ap.add_argument("--start-step", type=int, default=0,
                    help="resume: continue the step count / part order at N (use with --adapter <run>/adapter_stepN; "
                         "optimizer moments restart)")
    ap.add_argument("--system-prompt", default="detailed")
    ap.add_argument("--reasoning-effort", default="medium")
    ap.add_argument("--dump-texts", default="", help="write completions of the first group per step here (debug)")
    ap.add_argument("--scale-logits", action="store_true",
                    help="compute log pi from logits / --temperature (the sampling policy); without it the loss "
                         "uses T=1 logprobs of T<1 samples (off-policy sharpening bias)")
    ap.add_argument("--minibatches", type=int, default=1,
                    help="optimizer steps per rollout batch; >1 uses PPO clip (old logps from a no-grad pass)")
    ap.add_argument("--clip-low", type=float, default=0.2)
    ap.add_argument("--clip-high", type=float, default=0.28, help="DAPO clip-higher")
    ap.add_argument("--len-norm", type=float, default=1024.0,
                    help="ppo loss: token-sum / (n_seqs * len_norm) (Dr.GRPO constant normaliser)")
    ap.add_argument("--guide-bank", default="",
                    help="comma list aligned with --bench of {key: {code, iou, think}} banks (geom/build_guide_bank.py): "
                         "when a part's bank program beats every sampled draw by --guide-margin, it joins the group as an "
                         "extra (off-policy, LUFFY-style) member with its true IoU -> teaches answers the policy cannot sample")
    ap.add_argument("--guide-margin", type=float, default=0.05)
    ap.add_argument("--guide-adv-scale", type=float, default=1.0, help="multiply injected guide samples' advantage")
    ap.add_argument("--guard", type=float, default=0.0,
                    help="collapse guard: if the rolling (--guard-window steps) on-policy exec rate falls below "
                         "guard x its starting value, reload the last healthy checkpoint, reset Adam, halve the lr "
                         "(max 3 rollbacks, then stop). 2026-10-07: guided lr-4e-5 arm collapsed to no-code at step ~90")
    ap.add_argument("--guard-window", type=int, default=5)
    ap.add_argument("--guard-abs", type=float, default=0.0,
                    help="2026-10-09: a checkpoint is a rollback target only if the rolling AND latest exec are also >= this "
                         "absolute value (rft2_rl rolled back to an already-degraded s110 at exec ~0.6); 0 = off")
    ap.add_argument("--train-raw", action="store_true",
                    help="2026-10-09: train on the exact sampled answer text (vLLM rollouts), incl. completions without a "
                         "parsable code block (reward 0 -> negative advantage), instead of re-wrapping the parsed code; "
                         "rft2_rl collapsed through extra/empty ```python fences the canonical re-wrap never penalized")
    ap.add_argument("--kl-clamp", type=float, default=20.0,
                    help="clamp of the per-token log-ratio (ref - pi) in the k3 KL estimator; 2026-10-10: at 20, rare sampled "
                         "tokens gave per-step KL spikes of 1e2-4e4 (rft2_kl) that dominate the loss")
    ap.add_argument("--kl-ref-adapter", default="",
                    help="2026-10-09: KL reference = this frozen adapter on the same base (e.g. the SFT adapter the run starts "
                         "from) instead of the adapter-disabled base; saves write only the trained adapter")
    ap.add_argument("--ent-coef", type=float, default=0.0,
                    help="entropy floor: loss += ent_coef * max(0, ent_target - mean token entropy) (late-run collapse fix)")
    ap.add_argument("--ent-target", type=float, default=0.0, help="0 = the policy's mean entropy over the first 5 steps")
    ap.add_argument("--ent-max", type=float, default=0.0,
                    help="entropy CEILING: loss += ent_max_coef * max(0, mean token entropy - ent_max) (2026-10-08: RL from the "
                         "RFT-consolidated adapter diverged by monotonic entropy growth 0.18 -> 0.5 -> 4.2 at lr 1e-5 and 2e-5; "
                         "stable arms sit at 0.2-0.3). 0 = off")
    ap.add_argument("--ent-max-coef", type=float, default=0.5)
    ap.add_argument("--dense-weight", type=float, default=0.0,
                    help="reward = (1-w) IoU + w * mean(chamfer score, bbox-dims score) for executing draws (dense_once.py)")
    ap.add_argument("--vote-bonus", type=float, default=0.0,
                    help="reward += bonus * max(0, IoU - IoU of the group's vote pick (medoid by pairwise IoU among "
                         "executing draws)): explicitly rewards beating the consensus, which plain GRPO sharpens toward")
    ap.add_argument("--pkpo-k", type=int, default=1,
                    help="PKPO (arXiv 2505.15201): optimise expected max over k draws; rewards become each "
                         "sample's share of the unbiased max@k estimator (k=1 = plain mean reward)")
    ap.add_argument("--pkpo-anneal", type=int, default=0, help="anneal k linearly to 1 over this many steps")
    ap.add_argument("--repair-inputs", default="",
                    help="REPAIRER RL (needs --rollout-url): comma list aligned with --bench of *_rep_inputs.json "
                         "(start programs); prompt = [target sheet, start sheet] + REPAIR_PROMPT(code), no-think; "
                         "reward = IoU of the repaired program (start IoU cancels in the group baseline)")
    ap.add_argument("--repair-png-dirs", default="", help="comma list: <key>__<cand index>.png start-program sheets")
    ap.add_argument("--rollout-url", default="",
                    help="vLLM OpenAI endpoint (started with --enable-lora, VLLM_ALLOW_RUNTIME_LORA_UPDATING=True) "
                         "for rollouts: the adapter is saved + hot-loaded each step instead of HF generate")
    ap.add_argument("--rollout-workers", type=int, default=32)
    ap.add_argument("--rollout-timeout", type=int, default=900)
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
    # PKPO with k >= G gives every draw the group max as reward -> zero advantage -> no learning (2026-10-07: two
    # max@8 arms at G=8 sat at e55 for 120-200 steps)
    assert args.pkpo_k < args.g or args.pkpo_k == 1, f"--pkpo-k {args.pkpo_k} must be < --g {args.g}"
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
    if args.kl_ref_adapter:
        model.load_adapter(args.kl_ref_adapter, adapter_name="ref", is_trainable=False)
        model.set_adapter("default")
        print(f"[grpo] KL reference adapter {args.kl_ref_adapter}", flush=True)
    _save_kw = {"selected_adapters": ["default"]} if args.kl_ref_adapter else {}
    model.print_trainable_parameters()

    collator = VLMCollator(processor, max_seq_len=5120,
                           system_prompt=args.system_prompt,
                           reasoning_effort=args.reasoning_effort)
    # --bench / --keys take comma lists (aligned; empty keys entry = whole pool) for mixed pools.
    # One bench keeps the plain part keys; several prefix each with its bench index ("1:key").
    benches = args.bench.split(",")
    keyfiles = (args.keys.split(",") + [""] * len(benches))[:len(benches)]
    samples, gt_of, keys = {}, {}, []
    for bi, (bd, kf) in enumerate(zip(benches, keyfiles)):
        c_, ks_, gd_ = load_bench(bd, kf)
        print(f"[grpo] bench {bd}: {len(ks_)} parts", flush=True)
        for k in ks_:
            uid = k if len(benches) == 1 else f"{bi}:{k}"
            samples[uid] = c_["samples"][k]
            gt_of[uid] = os.path.join(gd_, f"{k}.stl")
            keys.append(uid)
        del c_
    cache = {"samples": samples}
    guide = {}
    if args.guide_bank:
        for bi, gf in enumerate(args.guide_bank.split(",")):
            if not gf:
                continue
            gb = json.load(open(gf)); n0 = len(guide)
            for k, v in gb.items():
                uid = k if len(benches) == 1 else f"{bi}:{k}"
                if uid in samples and v.get("code") and v.get("think"):
                    guide[uid] = v
            print(f"[grpo] guide bank {gf}: {len(guide) - n0} parts", flush=True)
    repair = {}   # uid -> {"png2", "user"} for repairer RL; the uid's target/GT are its part's
    if args.repair_inputs:
        assert args.rollout_url, "repair mode generates through vLLM only"
        rins = args.repair_inputs.split(","); rpngs = args.repair_png_dirs.split(",")
        have = set(keys); rkeys = []
        for bi, (rf, pd) in enumerate(zip(rins, rpngs)):
            ri = json.load(open(rf)); n0 = len(rkeys)
            for rows in ri.values():
                for row in rows:
                    part = row["key"] if len(benches) == 1 else f"{bi}:{row['key']}"
                    if part not in have:
                        continue
                    for ci, cand in enumerate(row["cands"]):
                        png = os.path.join(pd, f"{row['key']}__{ci}.png")
                        if not cand.get("code") or not os.path.exists(png):
                            continue
                        uid = f"{part}#{ci}"
                        repair[uid] = {"png2": open(png, "rb").read(),
                                       "user": REPAIR_PROMPT.format(code=cand["code"].strip())}
                        samples[uid] = samples[part]; gt_of[uid] = gt_of[part]
                        rkeys.append(uid)
            print(f"[grpo] repair inputs {rf}: {len(rkeys) - n0} start programs", flush=True)
        keys = rkeys
    print(f"[grpo] bench {args.bench}: {len(keys)} prompts with GT", flush=True)
    assert len(keys) >= args.n_parts, "not enough parts"

    rng = random.Random(args.seed)
    rng.shuffle(keys)
    part_cycle = keys * 100

    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=args.lr, betas=(0.9, 0.95), weight_decay=0.0)

    logf = open(os.path.join(args.out, "round_log.jsonl"), "a")
    rollf = open(os.path.join(args.out, "rollouts.jsonl"), "a")
    tmpl = dict(enable_thinking=True, reasoning_effort=args.reasoning_effort) if not repair \
        else {"enable_thinking": False, "thinking": False}   # repairer is served/trained no-think
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
        processor.tokenizer.padding_side = "left"   # generation requires left
        with torch.no_grad():
            out = model.generate(**enc, **kw)
        model.train()
        # skip_special_tokens strips the think markers; split think/code on the
        # python fence instead (the plan text precedes the first ```python).
        texts = processor.tokenizer.batch_decode(out[:, enc["input_ids"].shape[1]:],
                                                 skip_special_tokens=True)
        return texts

    def score_all(groups, td):
        """Execute + IoU every candidate of every group concurrently (flat pool).
        Sets c['exec'/'iou'] and appends rewards in candidate order per group."""
        work = []  # (group_idx, cand_idx)
        for gi, g in enumerate(groups):
            for ci, c in enumerate(g["cands"]):
                if c["code"]:
                    work.append((gi, ci))

        def one(item):
            gi, ci = item
            g = groups[gi]
            c = g["cands"][ci]
            part = g["part"]
            stl = os.path.join(td, f"{part.replace(':', '_')}_{ci}.stl")
            if args.score_timeouts:
                from score_partials import execute, scored_iou
                c["exec"] = bool(execute(c["code"], stl, td, f"{part.replace(':', '_')}_{ci}", 60))
                if c["exec"]:
                    c["iou"] = float(scored_iou(stl, gt_of[part], 90)[0])
                    if args.dense_weight > 0:
                        import subprocess
                        from score_partials import PYTHON, _ENV1
                        try:
                            p_ = subprocess.run([PYTHON, os.path.join(HERE, "dense_once.py"), stl, gt_of[part]],
                                                capture_output=True, text=True, timeout=60, env=_ENV1)
                            dd = json.loads(p_.stdout)
                            c["dense"] = 0.5 * (float(dd.get("chamfer", 0)) + float(dd.get("dims", 0)))
                        except Exception:
                            c["dense"] = 0.0
                return
            if not exec_to_stl(c["code"], stl, td, f"{part.replace(':', '_')}_{ci}"):
                c["exec"] = False
                return
            c["exec"] = True
            try:
                c["iou"] = float(iou_pair(stl, gt_of[part])["iou_centered"])
            except Exception:
                c["iou"] = 0.0

        with ThreadPoolExecutor(max_workers=args.score_workers) as ex:
            list(ex.map(one, work))
        for g in groups:
            g["rewards"] = [
                (-args.exec_penalty if args.exec_penalty else 0.0) if not c["code"]
                else (float(c.get("iou", 0.0)) if c["exec"] else (-args.exec_penalty if args.exec_penalty else 0.0))
                for c in g["cands"]
            ]
            if args.dense_weight > 0:
                g["rewards"] = [(1 - args.dense_weight) * r + args.dense_weight * float(c.get("dense", 0.0))
                                if c["exec"] else r for r, c in zip(g["rewards"], g["cands"])]
        if args.vote_bonus > 0:
            # consensus pick per group = medoid of the executing draws by pairwise IoU (the deployed vote, label-free)
            import subprocess
            from score_partials import IOU_ONCE, PYTHON, _ENV1
            env = {**_ENV1, "IOU_MC_POINTS": "20000"}
            stl_of = lambda g, ci: os.path.join(td, f"{g['part'].replace(':', '_')}_{ci}.stl")
            pairs = []
            for gi, g in enumerate(groups):
                ex_ = [ci for ci, c in enumerate(g["cands"]) if c["exec"] and os.path.exists(stl_of(g, ci))]
                g["_ex"] = ex_; g["_P"] = {}
                if len(ex_) >= 3:
                    pairs += [(gi, i, j) for a_, i in enumerate(ex_) for j in ex_[a_ + 1:]]

            def pair(item):
                gi, i, j = item
                g = groups[gi]
                try:
                    p_ = subprocess.run([PYTHON, IOU_ONCE, stl_of(g, i), stl_of(g, j)], capture_output=True,
                                        text=True, timeout=60, env=env)
                    v = float(json.loads(p_.stdout)["iou_centered"])
                except Exception:
                    v = 0.0
                g["_P"][(i, j)] = g["_P"][(j, i)] = v

            with ThreadPoolExecutor(max_workers=args.score_workers) as ex:
                list(ex.map(pair, pairs))
            for g in groups:
                ex_ = g.pop("_ex"); P_ = g.pop("_P")
                if len(ex_) < 3:
                    g["vote_iou"] = None
                    continue
                med = max(ex_, key=lambda i: sum(P_.get((i, j), 0.0) for j in ex_ if j != i))
                rv = g["rewards"][med]; g["vote_iou"] = rv
                g["rewards"] = [r + args.vote_bonus * max(0.0, r - rv) for r in g["rewards"]]

    live = {"name": None}
    ent_last = {"sum": None, "n": None}
    ent_track = {"hist": [], "target": args.ent_target or None}

    def _post(path, body):
        import urllib.request
        req = urllib.request.Request(args.rollout_url.rstrip("/").rsplit("/v1", 1)[0] + path,
                                     data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=600) as r:
            return r.read().decode()

    def vllm_sync(step):
        """Save the current adapter and hot-swap it into the rollout server (on-policy)."""
        ad = os.path.join(os.path.abspath(args.out), "_live", f"s{step}")
        model.save_pretrained(ad, **_save_kw)
        name = f"pol_s{step}"
        _post("/v1/load_lora_adapter", {"lora_name": name, "lora_path": ad})
        old = live["name"]
        live["name"] = name
        if old:
            try:
                _post("/v1/unload_lora_adapter", {"lora_name": old})
                import shutil
                shutil.rmtree(os.path.join(os.path.abspath(args.out), "_live", old.replace("pol_", "")), True)
            except Exception as e:
                print(f"[grpo] unload {old}: {e}", flush=True)

    def gen_groups_vllm(base):
        """G sampled completions per part from the served live adapter (n=G per request)."""
        import base64
        import urllib.request

        def one(s):
            body = {"model": live["name"], "temperature": args.temperature, "top_p": args.top_p, "n": args.g,
                    "max_tokens": args.max_new_tokens,
                    "messages": [{"role": "system", "content": SYSTEM_PROMPTS[args.system_prompt]},
                                 {"role": "user", "content": [
                                     {"type": "image_url", "image_url": {"url": "data:image/png;base64,"
                                                                         + base64.b64encode(s["png"]).decode()}},
                                     *([{"type": "image_url", "image_url": {"url": "data:image/png;base64,"
                                         + base64.b64encode(s["png2"]).decode()}}] if s.get("png2") else []),
                                     {"type": "text", "text": s.get("user") or USER_PROMPT}]}],
                    "chat_template_kwargs": dict(tmpl)}
            req = urllib.request.Request(args.rollout_url.rstrip("/") + "/chat/completions",
                                         data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
            for attempt in range(3):
                try:
                    with urllib.request.urlopen(req, timeout=args.rollout_timeout) as r:
                        d = json.load(r)
                    break
                except Exception as e:
                    print(f"[grpo] rollout {s['part']} attempt {attempt}: {type(e).__name__} {str(e)[:120]}", flush=True)
                    d = None
            cands = []
            chs = d["choices"] if d else []
            for g in range(args.g):
                think, code = "", None
                if g < len(chs):
                    m = chs[g]["message"]
                    text = m.get("content") or ""
                    reasoning = m.get("reasoning_content") or m.get("reasoning") or ""
                    if not reasoning and "</think>" in text:
                        reasoning, text = text.split("</think>", 1)[0].replace("<think>", ""), text.split("</think>", 1)[1]
                    idx = text.rfind("```python")
                    if idx >= 0:
                        code = text[idx + len("```python"):].rsplit("```", 1)[0].strip() or None
                    think = reasoning.strip()   # truncated code is kept (exec fails -> reward 0), as in HF path
                cands.append({"draw": g, "think": think, "code": code, "exec": False, "iou": 0.0,
                              **({"raw": text.strip()} if args.train_raw and g < len(chs) else {})})
            return {"part": s["part"], "image": s["image"], "image2": s.get("image2"), "user": s.get("user"),
                    "cands": cands, "rewards": None}

        with ThreadPoolExecutor(max_workers=args.rollout_workers) as ex:
            return list(ex.map(one, base))

    def completion_logps(batch_dicts):
        """Forward a collated batch; returns per-sample (sum_logp, n_toks, kl_sum).

        Right padding for the collate so the collator's prompt-prefix masking
        is correct; logprobs are gathered per row only at completion positions
        (float32 log_softmax on [n_i, vocab] slices, not the full [B, S, V]).
        Gradient checkpointing bounds activation memory for the policy pass.
        """
        processor.tokenizer.padding_side = "right"   # collate: prefix masking
        enc = collator(batch_dicts)
        enc = {k: (v.to(device) if hasattr(v, "to") else v) for k, v in enc.items()}
        labels = enc.pop("labels").to(device)

        model.train()   # HF checkpointing is a no-op in eval mode; the vLLM path never calls gen_texts
        try:
            model.gradient_checkpointing_enable()
            model.enable_input_require_grads()
        except Exception:
            pass
        logits = model(**enc).logits  # [B, S, V] bf16

        B = labels.shape[0]
        ent_sum = torch.zeros((), device=device)
        sum_logp = torch.zeros(B, device=device)
        n_toks = torch.zeros(B, device=device)
        kl_sum = torch.zeros(B, device=device)
        rows = []  # (js, tok_logp) per sample for the KL pass
        for i in range(B):
            js = (labels[i] != -100).nonzero(as_tuple=True)[0]
            if js.numel() == 0:
                rows.append((js, None))
                continue
            lg = logits[i, js - 1, :].float() / tau     # [n_i, V]
            ls_ = torch.log_softmax(lg, -1)
            lp = ls_.gather(-1, labels[i, js].unsqueeze(-1)).squeeze(-1)
            if args.ent_coef > 0 or args.ent_max > 0:
                ent_sum = ent_sum + (-(ls_.exp() * ls_).sum(-1)).sum()
            else:
                with torch.no_grad():
                    ent_sum = ent_sum + (-(ls_.exp() * ls_).sum(-1)).sum()
            del ls_
            sum_logp[i] = lp.sum()
            n_toks[i] = js.numel()
            rows.append((js, lp))
            del lg

        if args.kl_beta > 0:
            import contextlib
            if args.kl_ref_adapter:
                @contextlib.contextmanager
                def _ref_ctx():
                    model.set_adapter("ref")
                    try:
                        yield
                    finally:
                        model.set_adapter("default")
                ctx = _ref_ctx()
            else:
                ctx = model.disable_adapter()
            with torch.no_grad(), ctx:
                rlogits = model(**enc).logits
                for i in range(B):
                    js, lp = rows[i]
                    if js.numel() == 0:
                        continue
                    rlg = rlogits[i, js - 1, :].float() / tau
                    rlp = torch.log_softmax(rlg, -1).gather(-1, labels[i, js].unsqueeze(-1)).squeeze(-1)
                    # k3 estimator per token: exp(ref - pi) - (ref - pi) - 1
                    d = (rlp - lp).clamp(-args.kl_clamp, args.kl_clamp)
                    kl_sum[i] = (torch.expm1(d) - d).sum()
                    del rlg
                del rlogits
        del logits
        ent_last["sum"], ent_last["n"] = ent_sum, n_toks.sum()
        return sum_logp, n_toks, kl_sum, [lp for _, lp in rows]

    tau = args.temperature if args.scale_logits else 1.0
    guard_hist, guard_state = [], {"base": None, "good": None, "rollbacks": 0}
    t0 = time.time()
    if args.rollout_url:   # a resumed trainer may meet its predecessor's adapters still loaded in the server
        import urllib.request
        try:
            with urllib.request.urlopen(args.rollout_url.rstrip("/") + "/models", timeout=30) as r:
                for m in json.load(r).get("data", []):
                    if str(m.get("id", "")).startswith("pol_"):
                        _post("/v1/unload_lora_adapter", {"lora_name": m["id"]})
                        print(f"[grpo] unloaded stale adapter {m['id']}", flush=True)
        except Exception as e:
            print(f"[grpo] stale-adapter sweep: {e}", flush=True)
    for step in range(args.start_step, args.steps):
        parts = part_cycle[step * args.n_parts:(step + 1) * args.n_parts]
        base = [{"part": k, "image": _decode_png(cache["samples"][k]["png"]), "png": cache["samples"][k]["png"]}
                for k in parts]
        for b_ in base:
            if b_["part"] in repair:
                r_ = repair[b_["part"]]
                b_.update(png2=r_["png2"], image2=_decode_png(r_["png2"]), user=r_["user"])
        t_gen = time.time()
        if args.rollout_url:
            vllm_sync(step)
            groups = gen_groups_vllm(base)
        else:
            # ---- rollout: G draws for all parts ----
            seqs = [{**s, "draw": g} for g in range(args.g) for s in base]
            outs = []
            for b in range(0, len(seqs), args.gen_batch):
                outs.extend(gen_texts(seqs[b:b + args.gen_batch]))

            # ---- execute + score ----
            # outs is DRAW-MAJOR: [draw0 x all parts, draw1 x all parts, ...]
            # so the completion for (part pi, draw g) is outs[g * n_parts + pi].
            def split_think_code(text):
                idx = text.rfind("```python")
                if idx >= 0:
                    think = text[:idx].strip()
                    code = text[idx + len("```python"):].rsplit("```", 1)[0].strip()
                    return think, code
                return text.strip(), None

            n_parts_here = len(base)
            groups = []
            if args.dump_texts:
                with open(args.dump_texts, "a") as df:
                    for pi in range(min(2, n_parts_here)):
                        for g in range(min(2, args.g)):
                            df.write(f"===== step {step} part {base[pi]['part']} draw {g} =====\n")
                            df.write(outs[g * n_parts_here + pi][:1500] + "\n")
            for pi, s in enumerate(base):
                cands = []
                for g in range(args.g):
                    text = outs[g * n_parts_here + pi]
                    think, code = split_think_code(text)
                    cands.append({"draw": g, "think": think, "code": code,
                                  "exec": False, "iou": 0.0})
                groups.append({"part": s["part"], "image": s["image"],
                               "cands": cands, "rewards": None})
        t_score = time.time()
        with tempfile.TemporaryDirectory(prefix="grpo_") as td:
            score_all(groups, td)   # flat concurrent exec + IoU over all parts
        t_train = time.time()
        n_guided = 0
        for g in groups:
            g["onpol"] = list(g["rewards"])   # stats/logs stay on-policy; injected guides are flagged
            gv = guide.get(g["part"])
            if gv is not None and gv["iou"] > max(g["rewards"]) + args.guide_margin:
                g["cands"].append({"draw": len(g["cands"]), "think": gv["think"], "code": gv["code"],
                                   "exec": True, "iou": float(gv["iou"]), "guide": True})
                g["rewards"] = list(g["rewards"]) + [float(gv["iou"])]
                n_guided += 1

        # ---- advantages ----
        n_front = 0
        k_now = args.pkpo_k
        if args.pkpo_anneal:
            k_now = max(1, round(args.pkpo_k - (args.pkpo_k - 1) * min(1.0, step / args.pkpo_anneal)))

        def pkpo(rs, k):
            """s_m = [C(m-1,k-1) r_(m) + sum_{j>m} C(j-2,k-2) r_(j)] / C(n,k), ranks ascending (1-based);
            sum_S∋i max(r_S) / C(n,k): the REINFORCE weight of sample i for E[max of k]."""
            from math import comb
            n = len(rs)
            if k <= 1 or n < k:
                return list(rs)
            order = sorted(range(n), key=lambda i: rs[i])
            srt = [rs[i] for i in order]
            out = [0.0] * n
            for m in range(1, n + 1):
                v = comb(m - 1, k - 1) * srt[m - 1] + sum(comb(j - 2, k - 2) * srt[j - 1] for j in range(m + 1, n + 1))
                out[order[m - 1]] = v / comb(n, k) * n / k   # scale so sum matches k=1 magnitude
            return out

        for g in groups:
            r = torch.tensor(pkpo(g["rewards"], k_now), dtype=torch.float32)
            if float(r.var()) < args.min_var:
                g["adv"] = None
                continue
            n_front += 1
            a = r - r.mean()
            if args.adv == "std":
                a = a / (r.std(unbiased=False) + 1e-4)
            g["adv"] = a.tolist()
        if args.adv == "batchstd":
            flat = [x for g in groups if g["adv"] is not None for x in g["adv"]]
            sd = float(torch.tensor(flat).std()) if len(flat) > 1 else 1.0
            for g in groups:
                if g["adv"] is not None:
                    g["adv"] = [x / (sd + 1e-4) for x in g["adv"]]
        if args.guide_adv_scale != 1.0:
            for g in groups:
                if g.get("adv") is not None:
                    g["adv"] = [x * (args.guide_adv_scale if c.get("guide") else 1.0) for x, c in zip(g["adv"], g["cands"])]

        # ---- update ----
        train_dicts, advs = [], []
        for g in groups:
            if g["adv"] is None:
                continue
            for c, a in zip(g["cands"], g["adv"]):
                if c["code"] is None and not (args.train_raw and c.get("raw")):
                    continue  # nothing to reinforce
                td_ = {"image": g["image"], "trace": c["think"], "code": c["code"] or ""}
                if args.train_raw and c.get("raw") is not None:
                    td_["content_raw"] = c["raw"]
                if g.get("image2") is not None:
                    td_.update(image2=g["image2"], user=g["user"], trace="")
                train_dicts.append(td_)
                advs.append(a)

        stats = {"step": step, "parts": len(groups), "frontier_groups": n_front, "pkpo_k": k_now, "guided": n_guided,
                 "train_seqs": len(train_dicts)}
        allr = [r for g in groups for r in g["onpol"]]
        stats["mean_reward"] = sum(allr) / max(1, len(allr))
        stats["mean_best_of_g"] = sum(max(g["onpol"]) for g in groups) / max(1, len(groups))
        vs = [g["vote_iou"] for g in groups if g.get("vote_iou") is not None]
        if vs:
            stats["mean_vote_iou"] = round(sum(vs) / len(vs), 4)
        stats["mean_exec"] = sum(c["exec"] for g in groups for c in g["cands"] if not c.get("guide")) / max(1, len(allr))
        ious = [float(c.get("iou", 0.0)) for g in groups for c in g["cands"] if not c.get("guide")]
        stats["mean_iou"] = round(sum(ious) / max(1, len(ious)), 4)   # pure IoU even when rewards are shaped
        lens = [len((c.get("think") or "") + (c.get("code") or "")) for g in groups for c in g["cands"] if not c.get("guide")]
        stats["mean_completion_chars"] = round(sum(lens) / max(1, len(lens)), 1)
        if train_dicts and args.minibatches > 1:
            # old per-token logps of the sampling policy (no grad), then M clipped minibatch steps
            old = []
            with torch.no_grad():
                for b in range(0, len(train_dicts), args.train_batch):
                    _, _, _, lps = completion_logps(train_dicts[b:b + args.train_batch])
                    old.extend([None if lp is None else lp.detach() for lp in lps])
                    if step == 0 and b % 32 == 0:
                        print(f"[mem] old chunk {b}: alloc {torch.cuda.memory_allocated() / 2**30:.1f} GB "
                              f"peak {torch.cuda.max_memory_allocated() / 2**30:.1f} GB", flush=True)
            order = list(range(len(train_dicts)))
            rng.shuffle(order)
            mbs = [order[i::args.minibatches] for i in range(args.minibatches)]
            tot_loss = tot_kl = clipfrac_n = clipfrac_d = 0.0
            ent_acc = []
            for mb in mbs:
                if not mb:
                    continue
                opt.zero_grad(set_to_none=True)
                nchunks = (len(mb) + args.train_batch - 1) // args.train_batch
                for b in range(0, len(mb), args.train_batch):
                    idx = mb[b:b + args.train_batch]
                    sum_logp, n_toks, kl_sum, lps = completion_logps([train_dicts[i] for i in idx])
                    loss = torch.zeros((), device=device)
                    for j, i in enumerate(idx):
                        lp, o = lps[j], old[i]
                        if lp is None or o is None or lp.shape != o.shape:
                            continue
                        ratio = torch.exp((lp - o).clamp(-20, 20))
                        a = advs[i]
                        surr = torch.minimum(ratio * a, ratio.clamp(1 - args.clip_low, 1 + args.clip_high) * a)
                        loss = loss - surr.sum()
                        clipfrac_n += float(((ratio < 1 - args.clip_low) | (ratio > 1 + args.clip_high)).sum())
                        clipfrac_d += lp.numel()
                    loss = loss / (len(mb) * args.len_norm)
                    h_tok = ent_last["sum"] / ent_last["n"].clamp(min=1)
                    ent_acc.append(float(h_tok))
                    if args.ent_coef > 0 and ent_track["target"] is not None:
                        loss = loss + args.ent_coef * torch.relu(ent_track["target"] - h_tok) / nchunks
                    if args.ent_max > 0:
                        loss = loss + args.ent_max_coef * torch.relu(h_tok - args.ent_max) / nchunks
                    if args.kl_beta > 0:
                        loss = loss + args.kl_beta * kl_sum.sum() / n_toks.sum().clamp(min=1) / nchunks
                    loss.backward()
                    tot_loss += float(loss)
                    tot_kl += float(kl_sum.sum() / n_toks.sum().clamp(min=1)) / nchunks
                    if step == 0:
                        print(f"[mem] mb chunk {b}: alloc {torch.cuda.memory_allocated() / 2**30:.1f} GB "
                              f"peak {torch.cuda.max_memory_allocated() / 2**30:.1f} GB toks {int(n_toks.sum())}", flush=True)
                torch.nn.utils.clip_grad_norm_(params, 1.0)
                opt.step()
            stats["loss"] = round(tot_loss / len(mbs), 5)
            stats["kl"] = round(tot_kl / len(mbs), 5)
            stats["clipfrac"] = round(clipfrac_n / max(1, clipfrac_d), 4)
            if ent_acc:
                stats["mean_entropy"] = round(sum(ent_acc) / len(ent_acc), 4)
                ent_track["hist"].append(stats["mean_entropy"])
                if ent_track["target"] is None and len(ent_track["hist"]) == 5:
                    ent_track["target"] = sum(ent_track["hist"]) / 5
                    print(f"[grpo] entropy target set to {ent_track['target']:.4f}", flush=True)
        elif train_dicts:
            opt.zero_grad(set_to_none=True)
            nchunks = (len(train_dicts) + args.train_batch - 1) // args.train_batch
            tot_loss = tot_kl = 0.0
            for b in range(0, len(train_dicts), args.train_batch):
                chunk = train_dicts[b:b + args.train_batch]
                ca = torch.tensor(advs[b:b + args.train_batch], dtype=torch.float32, device=device)
                sum_logp, n_toks, kl_sum, _ = completion_logps(chunk)
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
        stats["gen_s"] = round(t_score - t_gen, 1)
        stats["score_s"] = round(t_train - t_score, 1)
        stats["train_s"] = round(time.time() - t_train, 1)
        stats["elapsed_s"] = round(time.time() - t0, 1)
        print(json.dumps(stats), flush=True)
        logf.write(json.dumps(stats) + "\n"); logf.flush()
        for g in groups:
            rollf.write(json.dumps({
                "part": g["part"], "rewards": g["onpol"],
                "cands": [{"draw": c["draw"], "exec": c["exec"], "iou": c.get("iou", 0.0), "guide": c.get("guide", False),
                           "think_chars": len(c["think"] or ""), "code_chars": len(c["code"] or "")}
                          for c in g["cands"]]}) + "\n")
        rollf.flush()
        guard_hist.append(stats["mean_exec"])
        roll = sum(guard_hist[-args.guard_window:]) / len(guard_hist[-args.guard_window:])
        if len(guard_hist) == args.guard_window and guard_state["base"] is None:
            guard_state["base"] = roll   # the run's starting exec; NOT re-measured after a rollback (it would ratchet down)
        if (step + 1) % args.save_every == 0 or step == args.steps - 1:
            ad = os.path.join(args.out, f"adapter_step{step + 1}")
            model.save_pretrained(ad, **_save_kw)
            print(f"[grpo] saved {ad}", flush=True)
            # 2026-10-08: a checkpoint is "healthy" only if the rolling AND the latest step's exec clear the guard and (with
            # --ent-max) entropy is < 2x the ceiling; the rolling mean alone marked an already-diverging step-30 adapter
            # (exec 0.49, entropy 1.4) healthy, so the rollback reloaded the collapse.
            if (guard_state["base"] is None or (roll >= args.guard * guard_state["base"]
                                               and stats["mean_exec"] >= args.guard * guard_state["base"]
                                               and not (args.ent_max > 0 and stats.get("mean_entropy", 0) > 2 * args.ent_max))) \
                    and (args.guard_abs <= 0 or (roll >= args.guard_abs and stats["mean_exec"] >= args.guard_abs)):
                guard_state["good"] = ad
        if args.guard > 0 and guard_state["base"] and len(guard_hist) >= args.guard_window \
                and roll < args.guard * guard_state["base"]:
            if guard_state["rollbacks"] >= 3 or not guard_state["good"]:
                print(f"[guard] exec {roll:.2f} < {args.guard} x {guard_state['base']:.2f}; no rollback left -> stop",
                      flush=True)
                break
            from peft import set_peft_model_state_dict
            from safetensors.torch import load_file
            set_peft_model_state_dict(model, load_file(os.path.join(guard_state["good"], "adapter_model.safetensors")))
            for gr in opt.param_groups:
                gr["lr"] *= 0.5
            opt.state.clear()
            guard_state["rollbacks"] += 1
            guard_hist.clear()
            print(f"[guard] exec {roll:.2f} collapsed -> reloaded {guard_state['good']}, "
                  f"lr -> {opt.param_groups[0]['lr']:.2e} (rollback {guard_state['rollbacks']})", flush=True)
    model.save_pretrained(os.path.join(args.out, "adapter_final"), **_save_kw)
    print("[grpo] ROUND DONE", flush=True)


if __name__ == "__main__":
    main()
