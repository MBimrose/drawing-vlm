"""Geometric IoU evaluation worker with agentic repair rounds.

Watches runs/* for un-evaluated checkpoints (the rolling best checkpoint-N
and final/). For each: single-shot generation on a fixed eval pool, then up
to --repair-rounds rounds where failed samples (no code / exec error / no
STEP) see their own script + the real traceback and regenerate. STEP output
is meshed and scored as volumetric IoU against precomputed GT meshes
(agentic-mesh-to-cad semantics — see iou.py).

Metrics carry BOTH views:
    geom/*        single-shot (round 0) — comparable with all prior evals
    geom/final_*  after repair rounds — the deployable, agentic number

Every checkpoint evaluates in an ISOLATED subprocess (in-process sequential
loads were observed corrupting generation), and DCP checkpoints are first
consolidated to cached HF dirs by a separate CPU subprocess. Runs on
ccc0442 (ccc0441 has at least one bad L40S).

EVAL_VERSION bumps re-evaluate everything (state entries store "v").
"""
from __future__ import annotations

import argparse
import gc
import json
import os
import pickle
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

import torch
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
TRAIN = os.path.dirname(HERE)
sys.path.insert(0, TRAIN)
sys.path.insert(0, HERE)

from collate_v14 import SYSTEM_PROMPTS, USER_PROMPT  # noqa: E402
from data_v14 import EVAL_CACHE, _decode_png  # noqa: E402
from iou import iou_pair  # noqa: E402

ROOT = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
RUNS_DIR = os.environ.get("DRAWING_VLM_RUNS", os.path.join(ROOT, "runs"))   # serv-19: /srv/scratch/bimrose2/runs
MODEL_BASE = os.path.join(ROOT, "models", "Qwen3.8-27B")
GT_DIR = os.path.join(os.path.dirname(EVAL_CACHE), "gt_meshes_v14")
HARNESS = os.path.join(HERE, "exec_harness.py")
PYTHON = sys.executable
PYTHON_NEXT = os.path.join(ROOT, ".venv_next", "bin", "python")   # transformers 5.16 for Qwen4Exp
if not os.path.exists(PYTHON_NEXT):
    PYTHON_NEXT = sys.executable   # serv-19: the only venv already has transformers 5.16

EVAL_VERSION = 2  # v2: adds repair rounds; bump forces re-eval of all ckpts

_CODE_RE = re.compile(r"```python\s*\n(.*?)```", re.DOTALL)


# --------------------------------------------------------------------------
# Checkpoint discovery
# --------------------------------------------------------------------------

def run_config(run_name: str) -> dict | None:
    p = os.path.join(TRAIN, "configs", f"{run_name}.yaml")
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return yaml.safe_load(f)


def classify_ckpt(path: str) -> str:
    """'lora' | 'hf' | 'dcp' | 'unknown'."""
    if os.path.exists(os.path.join(path, "adapter_model.safetensors")):
        return "lora"
    if os.path.exists(os.path.join(path, "model.safetensors.index.json")) or \
       os.path.exists(os.path.join(path, "model.safetensors")):
        return "hf"
    if os.path.isdir(os.path.join(path, "pytorch_model_fsdp_0")):
        return "dcp"
    return "unknown"


def candidates(run_dir: str, max_steps: int) -> list[tuple[str, int, str]]:
    """[(ckpt_path, wandb_step, label)] — newest checkpoint-N plus final/."""
    out = []
    ckpts = sorted(
        (d for d in os.listdir(run_dir) if d.startswith("checkpoint-")),
        key=lambda d: int(d.split("-")[1]),
    )
    if ckpts:
        best = ckpts[-1]
        out.append((os.path.join(run_dir, best), int(best.split("-")[1]), best))
    best = os.path.join(run_dir, "best_adapter", "adapter_model.safetensors")
    if os.path.exists(best):
        import time as _t
        stamp = _t.strftime("%m%d-%H%M", _t.localtime(os.path.getmtime(best)))
        out.append((os.path.dirname(best), max_steps, f"best_adapter-{stamp}"))
    bm = os.path.join(run_dir, "best_model", "model.safetensors.index.json")
    if os.path.exists(bm):   # full-FT gathered best (overwritten on improvement)
        import time as _t
        stamp = _t.strftime("%m%d-%H%M", _t.localtime(os.path.getmtime(bm)))
        out.append((os.path.dirname(bm), max_steps, f"best_model-{stamp}"))
    final = os.path.join(run_dir, "final")
    if os.path.isdir(final):
        out.append((final, max_steps + 1, "final"))
    return out


def is_qwen4(path: str) -> bool:
    # Read config.json directly: the eval venv's transformers predates qwen4_exp.
    try:
        with open(os.path.join(path, "config.json")) as f:
            return str(json.load(f).get("model_type", "")).startswith("qwen4")
    except OSError:
        return False


def node_gpu_gb() -> float:
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True).stdout.split()
        return sum(float(x) for x in out) / 1024
    except Exception:
        return 0.0


def normalize_adapter(ckpt_path: str) -> None:
    """Strip FSDP's `_checkpoint_wrapped_module` from adapter key names in place
    (adapters saved by e26 before the saver was fixed)."""
    f = os.path.join(ckpt_path, "adapter_model.safetensors")
    from safetensors.torch import load_file, save_file
    sd = load_file(f)
    if not any("_checkpoint_wrapped_module" in k for k in sd):
        return
    sd = {k.replace("._checkpoint_wrapped_module", ""): v for k, v in sd.items()}
    save_file(sd, f + ".tmp", metadata={"format": "pt"})
    os.replace(f + ".tmp", f)
    print(f"[load] normalized adapter key names in {f}", flush=True)


# --------------------------------------------------------------------------
# Model loading
# --------------------------------------------------------------------------

def _model_cls(path: str):
    from transformers import AutoConfig, Qwen3_5ForConditionalGeneration
    arch = (AutoConfig.from_pretrained(path).architectures or [""])[0]
    if arch.startswith("Qwen3_5"):
        return Qwen3_5ForConditionalGeneration
    if arch.startswith("Qwen4"):
        try:
            from flashnext_qsa import patch_qsa_indexer   # reference indexer loops per token
        except ModuleNotFoundError:
            # seen once in an eval subprocess (2026-08-29) despite TRAIN on sys.path
            import importlib.util
            print(f"[load] flashnext_qsa not importable; sys.path[:3]={sys.path[:3]} "
                  f"TRAIN={TRAIN} exists={os.path.exists(os.path.join(TRAIN, 'flashnext_qsa.py'))}",
                  flush=True)
            spec = importlib.util.spec_from_file_location(
                "flashnext_qsa", os.path.join(TRAIN, "flashnext_qsa.py"))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            patch_qsa_indexer = mod.patch_qsa_indexer
        patch_qsa_indexer()
        # cuDNN fused SDPA fails on the QSA (sparse) attention mask at generation
        # time: "mha_graph.execute(...) ... got false". Use the flash/efficient kernels.
        torch.backends.cuda.enable_cudnn_sdp(False)
        print("[load] cuDNN SDPA backend disabled for Qwen4Exp", flush=True)
        from transformers import AutoModelForMultimodalLM
        return AutoModelForMultimodalLM
    if "Moe" in arch:
        from transformers import Qwen3VLMoeForConditionalGeneration
        return Qwen3VLMoeForConditionalGeneration
    from transformers import Qwen3VLForConditionalGeneration
    return Qwen3VLForConditionalGeneration


def load_model(ckpt_path: str, kind: str, cfg: dict):
    from transformers import AutoProcessor

    # The run's own base model defines processor + class (falls back to the
    # 27B for v1-era runs whose configs predate the model-size axis).
    base = cfg.get("model_id", MODEL_BASE)
    Qwen3_5ForConditionalGeneration = _model_cls(
        ckpt_path if kind == "hf" else base)

    processor = AutoProcessor.from_pretrained(
        base,
        min_pixels=cfg.get("min_pixels", 200704),
        max_pixels=cfg.get("max_pixels", 1179648),
    )
    processor.tokenizer.padding_side = "left"

    # Qwen4Exp: cap per-GPU memory so the 102 GB n-gram table cannot be placed
    # on a GPU (accelerate did on 141 GB H200s -> 139 GB on one GPU -> OOM in
    # generation); transformers then keeps it on CPU (_no_placement_params).
    extra = {}
    if is_qwen4(ckpt_path if kind == "hf" else base):
        n = torch.cuda.device_count()
        cap = int(torch.cuda.get_device_properties(0).total_memory / 2**30) - 60   # H200: 79, B300: 207
        extra["max_memory"] = {i: f"{cap}GiB" for i in range(n)}
        extra["max_memory"]["cpu"] = "1000GiB"

    if kind == "hf":
        model = Qwen3_5ForConditionalGeneration.from_pretrained(
            ckpt_path, dtype=torch.bfloat16, attn_implementation="sdpa",
            device_map="balanced", low_cpu_mem_usage=True, **extra)
    elif kind == "lora":
        from peft import PeftModel
        base = Qwen3_5ForConditionalGeneration.from_pretrained(
            base, dtype=torch.bfloat16, attn_implementation="sdpa",
            device_map="balanced", low_cpu_mem_usage=True, **extra)
        normalize_adapter(ckpt_path)
        model = PeftModel.from_pretrained(base, ckpt_path)
        model = model.merge_and_unload()
    elif kind == "dcp":
        # NEVER do DCP work in the inference process (it corrupts later
        # generation — '!' floods). Consolidate to a cached bf16 HF dir in a
        # separate CPU subprocess, then load that through the hf path.
        cons_dir = os.path.join(os.path.dirname(ckpt_path), "geom_eval",
                                f"consolidated-{os.path.basename(ckpt_path)}")
        if not os.path.exists(os.path.join(cons_dir, "model.safetensors.index.json")):
            print(f"[load] consolidating {ckpt_path} -> {cons_dir} (subprocess)",
                  flush=True)
            rc = subprocess.run(
                [PYTHON, os.path.join(HERE, "consolidate_dcp.py"), ckpt_path,
                 cons_dir, base]).returncode
            if rc != 0:
                raise RuntimeError(f"DCP consolidation failed rc={rc}")
        model = Qwen3_5ForConditionalGeneration.from_pretrained(
            cons_dir, dtype=torch.bfloat16, attn_implementation="sdpa",
            device_map="balanced", low_cpu_mem_usage=True)
    else:
        raise ValueError(f"unknown checkpoint kind for {ckpt_path}")

    # Fine-tuned checkpoints inherit use_cache=False from training (needed there
    # for activation checkpointing). Left as-is, every decode step recomputes the
    # whole sequence. Generation always wants the cache.
    model.config.use_cache = True
    if hasattr(model.config, "text_config"):
        model.config.text_config.use_cache = True
    for m in model.modules():
        c = getattr(m, "config", None)
        if c is not None and hasattr(c, "use_cache"):
            c.use_cache = True
    if getattr(model, "generation_config", None) is not None:
        model.generation_config.use_cache = True

    model.eval()
    if model.generation_config is not None:
        model.generation_config.use_cache = True
    return model, processor


# --------------------------------------------------------------------------
# Generation
# --------------------------------------------------------------------------

def build_gen_messages(image, cfg: dict) -> list[dict]:
    return [
        {"role": "system", "content": [
            {"type": "text", "text": SYSTEM_PROMPTS[cfg.get("system_prompt", "detailed")]}]},
        {"role": "user", "content": [
            {"type": "image", "image": image},
            {"type": "text", "text": USER_PROMPT}]},
    ]


def build_repair_messages(image, cfg: dict, prev_reply: str, feedback: str) -> list[dict]:
    """Round-0 conversation + the model's previous reply + execution feedback."""
    return build_gen_messages(image, cfg) + [
        {"role": "assistant", "reasoning_content": "",
         "content": [{"type": "text", "text": prev_reply}]},
        {"role": "user", "content": [{"type": "text", "text": feedback}]},
    ]


def feedback_text(rec: dict) -> str:
    if not rec.get("code"):
        return ("Your previous response did not contain a complete ```python "
                "code block. Output the full corrected build123d script now, "
                "as a single ```python code block ending with "
                "`export_step(part, \"output.step\")`.")
    if rec.get("exec_rc") == 3:
        body = "The script ran but produced no output.step file."
    else:
        tail = (rec.get("stderr_tail") or "unknown error").strip()
        body = f"### Execution: FAILED\nstderr:\n```\n{tail}\n```"
    return (f"{body}\n\nFix the script. It must run without errors and export "
            f"the part with `export_step(part, \"output.step\")`. Output the "
            f"complete corrected script as a single ```python code block.")


def extract_code(text: str) -> str | None:
    # Discard the thinking block, then take the LAST fenced python block.
    if "</think>" in text:
        text = text.rsplit("</think>", 1)[1]
    blocks = _CODE_RE.findall(text)
    if not blocks:
        return None
    return blocks[-1].strip()


@torch.no_grad()
def generate_msgs(model, processor, cfg, msgs_list: list[list[dict]],
                  max_new_tokens: int) -> list[str]:
    from qwen_vl_utils import process_vision_info

    tmpl_kwargs = dict(enable_thinking=True,
                       reasoning_effort=cfg.get("reasoning_effort", "medium"))
    texts = [processor.apply_chat_template(
        m, add_generation_prompt=True, tokenize=False, **tmpl_kwargs)
        for m in msgs_list]
    images, videos = process_vision_info(msgs_list)
    enc = processor(text=texts, images=images, videos=videos,
                    return_tensors="pt", padding=True)
    enc = {k: (v.to(model.device) if hasattr(v, "to") else v) for k, v in enc.items()}
    out = model.generate(
        **enc, max_new_tokens=max_new_tokens, do_sample=False,
        pad_token_id=processor.tokenizer.pad_token_id
        or processor.tokenizer.eos_token_id,
    )
    gen = out[:, enc["input_ids"].shape[1]:]
    return processor.tokenizer.batch_decode(gen, skip_special_tokens=True)


def generate_all(model, processor, cfg, msgs_list, batch, max_new_tokens, tag):
    outs: list[str] = []
    for i in range(0, len(msgs_list), batch):
        outs.extend(generate_msgs(model, processor, cfg,
                                  msgs_list[i:i + batch], max_new_tokens))
        print(f"[gen] {tag}: {min(i + batch, len(msgs_list))}/{len(msgs_list)}",
              flush=True)
    return outs


# --------------------------------------------------------------------------
# Execution + scoring
# --------------------------------------------------------------------------

def exec_code(key: str, code: str, workdir: str) -> dict:
    """Run one script through the harness; STL lands at workdir/<key>.stl."""
    code_path = os.path.join(workdir, f"{key}.py")
    stl_path = os.path.join(workdir, f"{key}.stl")
    with open(code_path, "w") as f:
        f.write(code)
    out: dict = {"exec_ok": False, "exec_rc": None, "stderr_tail": ""}
    try:
        p = subprocess.run([PYTHON, HARNESS, code_path, stl_path],
                           capture_output=True, text=True, timeout=120)
        out["exec_rc"] = p.returncode
        out["exec_ok"] = p.returncode == 0
        if not out["exec_ok"]:
            out["stderr_tail"] = p.stderr[-1200:]
    except subprocess.TimeoutExpired:
        out["exec_rc"] = -9
        out["stderr_tail"] = "timeout after 120s"
    return out


def _round_metrics(recs: list[dict], ok_key: str, iou_key: str) -> dict:
    scored = [r for r in recs if r["has_gt"]]
    ns = max(len(scored), 1)
    exec_ok = [r for r in scored if r[ok_key]]
    ious = sorted(r[iou_key] for r in scored)
    return {
        "exec_ok_frac": len(exec_ok) / ns,
        "iou_mean": sum(ious) / ns,
        "iou_median": ious[ns // 2] if scored else 0.0,
        "iou_mean_exec": (sum(r[iou_key] for r in exec_ok) / len(exec_ok))
        if exec_ok else 0.0,
        "frac_iou50": sum(r[iou_key] >= 0.5 for r in scored) / ns,
        "frac_iou85": sum(r[iou_key] >= 0.85 for r in scored) / ns,
    }


def evaluate_checkpoint(run_name: str, ckpt_path: str, kind: str, cfg: dict,
                        samples: list[dict], args) -> dict:
    model, processor = load_model(ckpt_path, kind, cfg)

    recs = [{"key": s["uuid"], "has_gt": os.path.exists(
        os.path.join(GT_DIR, f"{s['uuid']}.stl")), "rounds": []}
        for s in samples]

    with tempfile.TemporaryDirectory(prefix="geomeval_") as td:
        # ---- round 0: single-shot ----
        msgs = [build_gen_messages(s["image"], cfg) for s in samples]
        outputs = generate_all(model, processor, cfg, msgs, args.batch,
                               args.max_new_tokens, f"{run_name} r0")

        n_degen = sum("!!!!!!!!" in t for t in outputs)
        if n_degen > len(outputs) * 0.3:
            raise RuntimeError(
                f"{n_degen}/{len(outputs)} degenerate generations — inference "
                f"is numerically corrupted; refusing to score")

        def _apply_outputs(indices, outs, round_no):
            """Extract + execute this round's outputs for the given samples."""
            todo = []
            for idx, text in zip(indices, outs):
                rec = recs[idx]
                code = extract_code(text)
                rec["reply"] = (code and f"```python\n{code}\n```") or text[-1500:]
                rec["code"] = code
                rec["gen_len"] = len(text)
                if code is None:
                    rec.update({"exec_ok": False, "exec_rc": None,
                                "stderr_tail": "", "skip": "no_code"})
                    rec["rounds"].append({"round": round_no, "ok": False,
                                          "why": "no_code"})
                else:
                    todo.append(idx)
            with ThreadPoolExecutor(max_workers=8) as ex:
                results = list(ex.map(
                    lambda i: exec_code(recs[i]["key"], recs[i]["code"], td),
                    todo))
            for idx, res in zip(todo, results):
                recs[idx].update(res)
                recs[idx].pop("skip", None)
                recs[idx]["rounds"].append(
                    {"round": round_no, "ok": res["exec_ok"],
                     "why": "" if res["exec_ok"] else f"rc={res['exec_rc']}"})

        all_idx = list(range(len(samples)))
        _apply_outputs(all_idx, outputs, 0)

        # Snapshot round-0 outcome per sample (before any repair).
        for rec in recs:
            rec["r0_exec_ok"] = bool(rec.get("exec_ok"))

        # ---- repair rounds ----
        for rnd in range(1, args.repair_rounds + 1):
            failed = [i for i in all_idx
                      if recs[i]["has_gt"] and not recs[i].get("exec_ok")]
            if not failed:
                break
            print(f"[repair] {run_name}: round {rnd}, {len(failed)} to repair",
                  flush=True)
            rmsgs = [build_repair_messages(
                samples[i]["image"], cfg, recs[i]["reply"],
                feedback_text(recs[i])) for i in failed]
            routs = generate_all(model, processor, cfg, rmsgs, args.batch,
                                 args.max_new_tokens, f"{run_name} r{rnd}")
            _apply_outputs(failed, routs, rnd)

        del model
        gc.collect()
        torch.cuda.empty_cache()

        # ---- IoU scoring on whatever STL each sample ended with ----
        # Round-0 STLs are overwritten by successful repairs, so a sample's
        # final STL is its best attempt; r0 IoU equals final IoU when the
        # sample succeeded in round 0 and is 0 otherwise.
        def _score(rec):
            rec["iou_raw"] = rec["iou_centered"] = 0.0
            if rec.get("exec_ok") and rec["has_gt"]:
                pred = os.path.join(td, f"{rec['key']}.stl")
                gt = os.path.join(GT_DIR, f"{rec['key']}.stl")
                rec.update(iou_pair(pred, gt))
            rec["r0_iou_centered"] = rec["iou_centered"] if rec["r0_exec_ok"] else 0.0
            return rec

        with ThreadPoolExecutor(max_workers=8) as ex:
            list(ex.map(_score, recs))

    scored = [r for r in recs if r["has_gt"]]
    m0 = _round_metrics(recs, "r0_exec_ok", "r0_iou_centered")
    mf = _round_metrics(recs, "exec_ok", "iou_centered")
    metrics = {
        "n": len(recs), "n_scored": len(scored),
        **m0,
        **{f"final_{k}": v for k, v in mf.items()},
        "repair_recovered": sum(1 for r in scored
                                if r.get("exec_ok") and not r["r0_exec_ok"]),
        "v": EVAL_VERSION,
    }
    # keep reports light
    for r in recs:
        r.pop("reply", None)
        r.pop("code", None)
    return {"metrics": metrics, "records": recs}


# --------------------------------------------------------------------------

def log_wandb(run_name: str, label: str, step: int, metrics: dict):
    import wandb
    rid = re.sub(r"[^a-z0-9-]", "-", f"geom-{run_name}".lower())
    run = wandb.init(project=os.environ.get("WANDB_PROJECT", "drawing-vlm-v14"),
                     name=f"{run_name}-geom", id=rid, resume="allow",
                     reinit=True)
    wandb.log({f"geom/{k}": v for k, v in metrics.items() if k != "v"},
              step=step)
    run.finish()


def eval_one(args):
    """Child mode: evaluate exactly one checkpoint, then exit."""
    global GT_DIR
    # Best-effort compute-side self-heal (idempotent; covers work the
    # login-node session couldn't submit during the 2026-08-24 fork outage).
    try:
        if shutil.which("squeue"):   # cluster only (serv-19 has no SLURM)
            subprocess.run(["bash", os.path.join(HERE, "self_heal.sh")], timeout=120)
    except Exception:
        pass
    run_name, ckpt_path, kind, step, label = (
        args.eval_one[0], args.eval_one[1], args.eval_one[2],
        int(args.eval_one[3]), args.eval_one[4])
    cfg = run_config(run_name)
    run_dir = os.path.join(RUNS_DIR, run_name)

    # v2-era runs (certified manifest) score on the frozen eval split with
    # STEP-derived GT meshes; v1 runs keep the original pool for continuity.
    if int(cfg.get("data_version", 1)) == 2:
        from data_v14 import EVAL_CACHE_V15
        cache_path = EVAL_CACHE_V15
        pool = "certified"
        GT_DIR = os.path.join(os.path.dirname(EVAL_CACHE), "gt_meshes_v15")
        import glob as _g
        n_stl = len(_g.glob(os.path.join(GT_DIR, "*.stl")))
        if n_stl < 1000:
            # Meshes not built yet (self_heal submits the job). Exit WITHOUT
            # writing state so this checkpoint is retried next pass instead
            # of being permanently recorded with an empty score.
            print(f"[worker] v2 GT meshes not ready ({n_stl} stl) — deferring "
                  f"{run_name}/{label}", flush=True)
            sys.exit(7)
    else:
        cache_path = EVAL_CACHE
        pool = "all"
    with open(cache_path, "rb") as f:
        cache = pickle.load(f)
    keys = cache["pools"][pool][: args.n]
    samples = [{"uuid": k, "image": _decode_png(cache["samples"][k]["png"])}
               for k in keys]
    print(f"[worker] pool={pool} n={len(samples)} gt={GT_DIR}", flush=True)

    result = evaluate_checkpoint(run_name, ckpt_path, kind, cfg, samples, args)
    m = result["metrics"]
    print(f"[worker] {run_name}/{label}: "
          f"r0 exec={m['exec_ok_frac']:.2f} iou={m['iou_mean']:.3f} | "
          f"final exec={m['final_exec_ok_frac']:.2f} "
          f"iou={m['final_iou_mean']:.3f} iou85={m['final_frac_iou85']:.2f} "
          f"(repaired {m['repair_recovered']})", flush=True)
    os.makedirs(os.path.join(run_dir, "geom_eval"), exist_ok=True)
    with open(os.path.join(run_dir, "geom_eval", f"{label}.json"), "w") as f:
        json.dump(result, f, indent=1)
    try:
        log_wandb(run_name, label, step, m)
    except Exception as e:
        print(f"[worker] wandb log failed: {e}", flush=True)
    state_path = os.path.join(run_dir, "geom_eval_state.json")
    state = {}
    if os.path.exists(state_path):
        with open(state_path) as f:
            state = json.load(f)
    state[label] = {"step": step, **m}
    with open(state_path, "w") as f:
        json.dump(state, f, indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=96)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--max-new-tokens", type=int, default=2400)
    ap.add_argument("--repair-rounds", type=int, default=2)
    ap.add_argument("--runs", default="",
                    help="comma-separated run names; default: all under runs/")
    ap.add_argument("--eval-one", nargs=5, default=None,
                    metavar=("RUN", "CKPT", "KIND", "STEP", "LABEL"))
    args = ap.parse_args()

    if args.eval_one:
        eval_one(args)
        return

    # Parent: discover candidates needing (re-)evaluation at EVAL_VERSION,
    # one ISOLATED subprocess each.
    run_names = ([r for r in args.runs.split(",") if r] if args.runs
                 else sorted(os.listdir(RUNS_DIR)))
    for run_name in run_names:
        run_dir = os.path.join(RUNS_DIR, run_name)
        if not os.path.isdir(run_dir) or run_name.startswith((".", "_")):
            continue
        cfg = run_config(run_name)
        if cfg is None:
            print(f"[worker] {run_name}: no config, skipping", flush=True)
            continue
        big = is_qwen4(cfg.get("model_id", MODEL_BASE))
        if big and node_gpu_gb() < 500:
            print(f"[worker] {run_name}: Qwen4Exp needs an H200 node (this node has "
                  f"{node_gpu_gb():.0f} GB GPU) — skipping", flush=True)
            continue
        state_path = os.path.join(run_dir, "geom_eval_state.json")
        state = {}
        if os.path.exists(state_path):
            with open(state_path) as f:
                state = json.load(f)
        for ckpt_path, step, label in candidates(run_dir, cfg.get("max_steps", 2500)):
            if state.get(label, {}).get("v", 1) >= EVAL_VERSION:
                continue
            kind = classify_ckpt(ckpt_path)
            if kind == "dcp" and os.environ.get("GEOM_EVAL_SKIP_DCP"):
                # DCP consolidation reads the full sharded optimizer state off the
                # parallel FS (2-3 h when it is busy) and the leaderboard uses final/.
                print(f"[worker] {run_name}/{label}: dcp checkpoint skipped (GEOM_EVAL_SKIP_DCP)", flush=True)
                continue
            if kind == "unknown":
                print(f"[worker] {run_name}/{label}: unknown format, skipping",
                      flush=True)
                continue
            print(f"[worker] === {run_name}/{label} ({kind}) -> subprocess ===",
                  flush=True)
            rc = subprocess.run(
                [PYTHON_NEXT if big else PYTHON, os.path.abspath(__file__),
                 "--eval-one", run_name, ckpt_path, kind, str(step), label,
                 "--n", str(args.n), "--batch", str(args.batch),
                 "--max-new-tokens", str(args.max_new_tokens),
                 "--repair-rounds", str(args.repair_rounds)],
            ).returncode
            if rc != 0:
                print(f"[worker] {run_name}/{label} subprocess rc={rc}", flush=True)
    print("[worker] pass complete", flush=True)


if __name__ == "__main__":
    main()
