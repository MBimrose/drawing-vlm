"""Mechanism 2 — constraints before code (GPU experiment on the 96-part pool).

Three arms, one model load, same hardware, same parts:
  base   : standard greedy generation + up to R exec-error repair rounds
           (the champion's single-shot 'repair IoU' protocol)
  stageA : constraint-extraction prompt -> JSON constraint list (greedy).
           If the model refuses to emit JSON, fall back to the envelope stated
           in the base arm's own <think> plan (source recorded per part).
  cons   : stage B = drawing + constraint list -> script (greedy), then a
           verify/repair loop: execute, measure the mesh (bbox extents, genus =
           through-passage count), compare with the constraint list, and feed
           mismatches (and tracebacks) back for up to R repair rounds.

Every round's STL is IoU-scored against GT so selection policies (last
executing / fewest mismatches) can be compared offline.

    python two_stage.py --ckpt runs/e24-rft/final --run e24-rft --n 96 \
        --out train_v14/mech/constraints/out/two_stage_e24_96.json
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import re
import shutil
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
sys.path.insert(0, f"{DV}/train_v14"); sys.path.insert(0, f"{DV}/train_v14/geom")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from collate_v14 import USER_PROMPT  # noqa: E402
from data_v14 import EVAL_CACHE, EVAL_CACHE_V15, _decode_png  # noqa: E402
from geom_eval_worker import (  # noqa: E402
    build_gen_messages, build_repair_messages, exec_code, extract_code,
    feedback_text, load_model, run_config,
)
from iou import iou_pair  # noqa: E402
from envelope_features import mesh_features, stated_numbers  # noqa: E402

GT_DIR = os.path.join(os.path.dirname(EVAL_CACHE), "gt_meshes_v15")

STAGE_A_SYSTEM = (
    "You are an expert mechanical engineer reading a multi-view engineering "
    "drawing (orthographic views, dimensions, diameter/radius callouts, hole "
    "leaders). Extract every dimensional constraint of the part into one JSON "
    "object with exactly these keys:\n"
    "  \"envelope_mm\": {\"length\": L, \"width\": W, \"height\": H}  — the overall "
    "bounding box in mm (for a turned part use {\"diameter\": D, \"height\": H}),\n"
    "  \"base_shape\": short text (e.g. \"rectangular plate\", \"L-bracket\", \"cylinder\"),\n"
    "  \"holes\": [{\"diameter\": d, \"count\": n, \"through\": true|false, "
    "\"depth\": number|null, \"positions\": text}],\n"
    "  \"pockets_slots\": [{\"type\": text, \"size\": text, \"depth\": number|null, \"through\": true|false}],\n"
    "  \"chamfers\": [text], \"fillets\": [text], \"symmetry\": text.\n"
    "Use the numbers exactly as printed on the drawing. Output ONLY the JSON "
    "object inside a single ```json code block. Do not write any Python code."
)
STAGE_A_USER = "List every dimensional constraint of the part in this drawing as JSON."

STAGE_B_SUFFIX = (
    "\n\nThe following constraint list was extracted from this drawing. The "
    "script must satisfy every item (verify each against the drawing):\n"
    "```json\n{constraints}\n```"
)

_JSON_BLOCK = re.compile(r"```json\s*\n(.*?)```", re.DOTALL)


def parse_constraints(text: str) -> dict | None:
    if "</think>" in text:
        text = text.rsplit("</think>", 1)[1]
    cands = _JSON_BLOCK.findall(text)
    if not cands:
        # bare object: take the outermost {...}
        i, j = text.find("{"), text.rfind("}")
        if i >= 0 and j > i:
            cands = [text[i:j + 1]]
    for c in reversed(cands):
        try:
            obj = json.loads(c)
            if isinstance(obj, dict):
                return obj
        except Exception:
            continue
    return None


def envelope_of(cons: dict) -> list[float] | None:
    env = cons.get("envelope_mm") or cons.get("envelope") or {}
    if not isinstance(env, dict):
        return None
    vals = []
    try:
        if "diameter" in env and env["diameter"] is not None:
            d = float(env["diameter"]); vals = [d, d]
            for k in ("height", "length", "width"):
                if env.get(k) is not None:
                    vals.append(float(env[k])); break
        else:
            for k in ("length", "width", "height"):
                if env.get(k) is not None:
                    vals.append(float(env[k]))
    except (TypeError, ValueError):
        return None
    return sorted(vals) if len(vals) == 3 else None


def expected_genus(cons: dict) -> int | None:
    n = 0; any_hole = False
    for h in cons.get("holes") or []:
        if not isinstance(h, dict):
            continue
        any_hole = True
        thr = h.get("through")
        if thr is None:
            thr = h.get("depth") in (None, 0)
        if thr:
            try:
                n += int(h.get("count") or 1)
            except (TypeError, ValueError):
                n += 1
    for s in cons.get("pockets_slots") or []:
        if isinstance(s, dict) and s.get("through"):
            n += 1
    return n if (any_hole or cons.get("pockets_slots")) else (0 if "holes" in cons else None)


def check_constraints(cons: dict, feat: dict | None) -> list[str]:
    """Human-readable mismatch lines (empty = consistent or uncheckable)."""
    if not cons or feat is None:
        return []
    out = []
    env = envelope_of(cons)
    if env is not None:
        built = sorted(feat["ext"])
        bad = any(abs(a - b) > max(0.5, 0.02 * a) for a, b in zip(env, built))
        if bad:
            out.append(f"Overall envelope: the built part measures "
                       f"{' x '.join(f'{v:g}' for v in sorted(feat['ext'], reverse=True))} mm, "
                       f"but the constraint list says "
                       f"{' x '.join(f'{v:g}' for v in sorted(env, reverse=True))} mm.")
    g = expected_genus(cons)
    if g is not None and feat.get("genus") is not None and feat["genus"] < g:
        out.append(f"Through holes: the built solid has {feat['genus']} through "
                   f"passage(s) but the constraint list requires {g} through hole(s)/slot(s). "
                   f"Some holes are missing or do not cut through.")
    return out


def cons_feedback(rec: dict, mism: list[str]) -> str:
    if not rec.get("exec_ok"):
        return feedback_text(rec)
    body = "### Execution: OK\n### Constraint check against your constraint list: FAILED\n" + \
        "\n".join(f"- {m}" for m in mism)
    return (f"{body}\n\nRe-check the drawing and fix the script so the built part "
            f"satisfies the constraint list. Output the complete corrected script "
            f"as a single ```python code block ending with "
            f"`export_step(part, \"output.step\")`.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--kind", default="hf")
    ap.add_argument("--run", default="e24-rft")
    ap.add_argument("--n", type=int, default=96)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--max-new-tokens", type=int, default=2400)
    ap.add_argument("--repair-rounds", type=int, default=2)
    ap.add_argument("--skip-base", action="store_true")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    cfg = run_config(args.run)
    with open(EVAL_CACHE_V15, "rb") as f:
        cache = pickle.load(f)
    keys = [k for k in cache["pools"]["certified"]
            if os.path.exists(os.path.join(GT_DIR, f"{k}.stl"))][: args.n]
    samples = [{"uuid": k, "image": _decode_png(cache["samples"][k]["png"])} for k in keys]
    print(f"[2stage] {len(samples)} parts", flush=True)

    import torch
    from qwen_vl_utils import process_vision_info
    model, processor = load_model(args.ckpt, args.kind, cfg)
    tmpl = dict(enable_thinking=True, reasoning_effort=cfg.get("reasoning_effort", "medium"))

    def generate(msgs_list, max_new, tag):
        outs = []
        t0 = time.time()
        for b in range(0, len(msgs_list), args.batch):
            chunk = msgs_list[b:b + args.batch]
            texts = [processor.apply_chat_template(m, add_generation_prompt=True,
                                                   tokenize=False, **tmpl) for m in chunk]
            images, videos = process_vision_info(chunk)
            enc = processor(text=texts, images=images, videos=videos,
                            return_tensors="pt", padding=True)
            enc = {k: (v.to(model.device) if hasattr(v, "to") else v) for k, v in enc.items()}
            with torch.no_grad():
                out = model.generate(**enc, max_new_tokens=max_new, do_sample=False,
                                     pad_token_id=processor.tokenizer.pad_token_id
                                     or processor.tokenizer.eos_token_id)
            outs.extend(processor.tokenizer.batch_decode(
                out[:, enc["input_ids"].shape[1]:], skip_special_tokens=True))
            print(f"[gen] {tag}: {min(b + args.batch, len(msgs_list))}/{len(msgs_list)} "
                  f"({time.time() - t0:.0f}s)", flush=True)
        if sum("!!!!!!!!" in t for t in outs) > max(4, len(outs) // 3):
            raise RuntimeError("degenerate generations — bad GPU?")
        return outs

    state = {"ckpt": args.ckpt, "keys": keys, "parts": [{"key": k} for k in keys]}
    parts = state["parts"]

    def save():
        with open(args.out + ".partial.json", "w") as f:
            json.dump(state, f)

    td = tempfile.mkdtemp(prefix="twostage_")
    gt_of = lambda k: os.path.join(GT_DIR, f"{k}.stl")  # noqa: E731

    def run_round(arm, indices, texts, rnd, cons_list=None):
        """Extract, execute, measure, score one round of outputs for `indices`."""
        def one(a):
            i, text = a
            p = parts[i]; key = p["key"]
            code = extract_code(text)
            rec = {"round": rnd, "code": code, "gen_len": len(text),
                   "think1": (text.split("</think>")[0].replace("<think>", "").strip()
                              .split("\n")[0][:300]) if "</think>" in text else ""}
            rec["reply"] = (code and f"```python\n{code}\n```") or text[-1500:]
            if code is None:
                rec.update({"exec_ok": False, "exec_rc": None, "stderr_tail": "",
                            "iou": 0.0, "feat": None, "mism": []})
                return i, rec
            tag = f"{arm}_{key}_r{rnd}"
            res = exec_code(tag, code, td)
            rec.update(res)
            stl = os.path.join(td, f"{tag}.stl")
            rec["feat"] = mesh_features(stl) if res["exec_ok"] else None
            rec["iou"] = iou_pair(stl, gt_of(key))["iou_centered"] if res["exec_ok"] else 0.0
            cons = cons_list[i] if cons_list else None
            rec["mism"] = check_constraints(cons, rec["feat"]) if (cons and res["exec_ok"]) else []
            return i, rec
        with ThreadPoolExecutor(max_workers=8) as ex:
            for i, rec in ex.map(one, list(zip(indices, texts))):
                parts[i].setdefault(arm, {"rounds": []})["rounds"].append(rec)

    # ------------------------------------------------------------------ base
    if not args.skip_base:
        texts = generate([build_gen_messages(s["image"], cfg) for s in samples],
                         args.max_new_tokens, "base r0")
        for p, t in zip(parts, texts):
            p["base_think"] = t.split("</think>")[0].replace("<think>", "").strip() \
                if "</think>" in t else ""
        run_round("base", list(range(len(samples))), texts, 0)
        save()
        for rnd in range(1, args.repair_rounds + 1):
            failed = [i for i in range(len(samples)) if not parts[i]["base"]["rounds"][-1]["exec_ok"]]
            if not failed:
                break
            msgs = [build_repair_messages(samples[i]["image"], cfg,
                                          parts[i]["base"]["rounds"][-1]["reply"],
                                          feedback_text(parts[i]["base"]["rounds"][-1]))
                    for i in failed]
            run_round("base", failed, generate(msgs, args.max_new_tokens, f"base r{rnd}"), rnd)
            save()

    # --------------------------------------------------------------- stage A
    msgsA = [[{"role": "system", "content": [{"type": "text", "text": STAGE_A_SYSTEM}]},
              {"role": "user", "content": [{"type": "image", "image": s["image"]},
                                           {"type": "text", "text": STAGE_A_USER}]}]
             for s in samples]
    textsA = generate(msgsA, 1600, "stageA")
    cons_list = []
    for p, t in zip(parts, textsA):
        cons = parse_constraints(t)
        src = "json"
        if cons is None:
            # fall back to the envelope stated in the model's own plan
            nums = stated_numbers(p.get("base_think", ""))
            cons = {"envelope_mm": dict(zip(("length", "width", "height"), sorted(nums, reverse=True)[:3]))} \
                if len(nums) >= 3 else {}
            src = "think" if cons else "none"
        p["stageA"] = {"raw": t[-3000:], "cons": cons, "source": src}
        cons_list.append(cons)
    n_json = sum(p["stageA"]["source"] == "json" for p in parts)
    print(f"[stageA] parsed JSON for {n_json}/{len(parts)} parts; "
          f"think-fallback {sum(p['stageA']['source'] == 'think' for p in parts)}", flush=True)
    save()

    # --------------------------------------------------------------- stage B
    def msgs_B(i):
        m = build_gen_messages(samples[i]["image"], cfg)
        if cons_list[i]:
            m[1]["content"][1]["text"] = USER_PROMPT + STAGE_B_SUFFIX.format(
                constraints=json.dumps(cons_list[i], indent=1))
        return m
    textsB = generate([msgs_B(i) for i in range(len(samples))], args.max_new_tokens, "stageB r0")
    run_round("cons", list(range(len(samples))), textsB, 0, cons_list)
    save()
    for rnd in range(1, args.repair_rounds + 1):
        todo = [i for i in range(len(samples))
                if not parts[i]["cons"]["rounds"][-1]["exec_ok"] or parts[i]["cons"]["rounds"][-1]["mism"]]
        if not todo:
            break
        print(f"[cons] repair round {rnd}: {len(todo)} parts "
              f"({sum(1 for i in todo if not parts[i]['cons']['rounds'][-1]['exec_ok'])} exec failures)",
              flush=True)
        msgs = []
        for i in todo:
            m = msgs_B(i)
            last = parts[i]["cons"]["rounds"][-1]
            m += [{"role": "assistant", "reasoning_content": "",
                   "content": [{"type": "text", "text": last["reply"]}]},
                  {"role": "user", "content": [{"type": "text", "text": cons_feedback(last, last["mism"])}]}]
            msgs.append(m)
        run_round("cons", todo, generate(msgs, args.max_new_tokens, f"stageB r{rnd}"), rnd, cons_list)
        save()

    # --------------------------------------------------------------- metrics
    def pick_last_exec(rounds):
        ex = [r for r in rounds if r["exec_ok"]]
        return ex[-1] if ex else None

    def pick_fewest_mism(rounds):
        ex = [r for r in rounds if r["exec_ok"]]
        if not ex:
            return None
        # earliest round among those with the minimum mismatch count
        return min(ex, key=lambda r: (len(r["mism"]), r["round"]))

    def summarize(ious):
        n = len(ious); s = sorted(ious)
        return {"iou_mean": sum(ious) / n, "iou_median": s[n // 2],
                "frac_iou85": sum(i >= 0.85 for i in ious) / n,
                "frac_iou50": sum(i >= 0.5 for i in ious) / n,
                "exec_frac": sum(i > 0 for i in ious) / n}

    metrics = {"n": len(parts), "stageA_json_frac": n_json / len(parts)}
    for arm, pol in (("base", pick_last_exec), ("cons", pick_last_exec), ("cons", pick_fewest_mism)):
        if not all(arm in p for p in parts):
            continue
        name = f"{arm}_{pol.__name__[5:]}"
        ious = []
        for p in parts:
            r = pol(p[arm]["rounds"])
            ious.append(r["iou"] if r else 0.0)
            p[arm][f"final_{pol.__name__[5:]}"] = r["iou"] if r else 0.0
        metrics[name] = summarize(ious)
        r0 = [p[arm]["rounds"][0]["iou"] for p in parts]
        metrics[f"{arm}_r0"] = summarize(r0)
    state["metrics"] = metrics
    print(json.dumps(metrics, indent=1), flush=True)
    for p in parts:   # keep the report light
        for arm in ("base", "cons"):
            for r in p.get(arm, {}).get("rounds", []):
                r.pop("reply", None)
    with open(args.out, "w") as f:
        json.dump(state, f)
    shutil.rmtree(td, ignore_errors=True)
    print("[2stage] done", flush=True)


if __name__ == "__main__":
    main()
