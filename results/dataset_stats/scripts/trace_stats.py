"""Reasoning-trace statistics for the paper: counts, gate pass rate, plan length, timing.

Reads the Kimi-K3 trace corpus (`traces_v14/`: `<uuid>_trace.txt`, `<uuid>_gate.json`,
`manifest.jsonl` from the daemon) and the frozen SFT manifest (`sft_manifest_v1.jsonl`).
Token counts use the generator's (Qwen3.8-27B) tokenizer, i.e. what the model trains on.

    python results/dataset_stats/scripts/trace_stats.py [--workers N] [--out results/dataset_stats/out/trace_stats.json]
"""
import argparse
import collections
import glob
import json
import os
import re
from multiprocessing import Pool

import numpy as np

W = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/step_to_drw/wds_dataset"
T = f"{W}/traces_v14"
TOK = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/models/Qwen3.8-27B"
_tok = None


def _pct(a, qs=(10, 50, 90, 99)):
    a = np.asarray([x for x in a if x is not None], float)
    if not len(a):
        return {}
    out = {"n": int(len(a)), "mean": float(a.mean())}
    out.update({f"p{q}": float(np.percentile(a, q)) for q in qs})
    return out


def _init():
    global _tok
    from transformers import AutoTokenizer
    _tok = AutoTokenizer.from_pretrained(TOK)


def _one(uuid):
    txt = open(f"{T}/{uuid}_trace.txt").read().strip()
    g = None
    if os.path.exists(f"{T}/{uuid}_gate.json"):
        g = json.load(open(f"{T}/{uuid}_gate.json"))
    return {
        "uuid": uuid,
        "tokens": len(_tok(txt, add_special_tokens=False)["input_ids"]),
        "words": len(txt.split()),
        "steps": len(re.findall(r"^\s*\d+\.", txt, re.M)),
        "gate": g,
    }


def _summ(rows):
    return {k: _pct([r[k] for r in rows]) for k in ("tokens", "words", "steps")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--out", default="results/dataset_stats/out/trace_stats.json")
    args = ap.parse_args()

    uuids = sorted(os.path.basename(p)[: -len("_trace.txt")] for p in glob.glob(f"{T}/*_trace.txt"))
    with Pool(args.workers, initializer=_init) as pool:
        rows = list(pool.imap_unordered(_one, uuids, chunksize=256))

    sft = [json.loads(l) for l in open(f"{T}/sft_manifest_v1.jsonl")]
    sft_ids = {r["uuid"] for r in sft}
    gated = [r for r in rows if r["gate"] is not None]
    passed = [r for r in gated if r["gate"].get("pass")]
    failed = [r for r in gated if not r["gate"].get("pass")]
    fail_kind = collections.Counter(
        "volume_off_gt_5pct" if "vol_diff_pct" in r["gate"]
        else ("recon_not_code_or_call" if "recon" in (r["gate"].get("err") or "") else "recon_exec_error")
        for r in failed)

    # daemon manifest: one row per attempt; keep the last successful row per uuid
    man = {}
    n_attempt_rows = n_call_fail = 0
    for l in open(f"{T}/manifest.jsonl"):
        r = json.loads(l)
        n_attempt_rows += 1
        if not r.get("ok"):
            n_call_fail += 1
            continue
        man[r["uuid"]] = r
    modes = collections.Counter(r.get("mode", "no_think(ungated)") for r in man.values())
    pass_by_mode = collections.Counter(r.get("mode") for r in man.values()
                                       if (r.get("gate") or {}).get("pass"))

    res = {
        "traces": len(rows),
        "gated": len(gated),
        "gate_pass": len(passed),
        "gate_fail": len(failed),
        "gate_fail_rate": len(failed) / max(1, len(gated)),
        "gate_fail_kinds": dict(fail_kind),
        "gate_vol_diff_pct_passed": _pct([r["gate"]["vol_diff_pct"] for r in passed]),
        "gate_s": _pct([r["gate"].get("gate_s") for r in gated]),
        "sft_certified_frozen": len(sft),
        "sft_split": dict(collections.Counter(r.get("split") for r in sft)),
        "all_traces": _summ(rows),
        "certified_sft": _summ([r for r in rows if r["uuid"] in sft_ids]),
        "failed_gate": _summ(failed),
        "manifest": {
            "attempt_rows": n_attempt_rows,
            "teacher_call_failures": n_call_fail,
            "uuids_ok": len(man),
            "trace_s": _pct([r.get("trace_s") for r in man.values()]),
            "modes": dict(modes),
            "gate_pass_by_mode": dict(pass_by_mode),
            "leaked_var_share": float(np.mean([bool(r.get("leaked_vars")) for r in man.values()])),
        },
    }
    print(json.dumps(res, indent=1))
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    json.dump(res, open(args.out, "w"), indent=1)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
