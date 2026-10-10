"""Exact weight-space average ("model soup") of several LoRA adapters on the same base (2026-10-07).

sum_i w_i * (s_i B_i A_i) = s * [w_1 (s_1/s) B_1 | ... ] @ [A_1; ...; A_n]: concatenating along the rank axis gives a
single LoRA of rank sum(r_i) whose delta-W is EXACTLY the weighted average of the inputs' delta-Ws (s = alpha/r of
the output; each B_i is rescaled by w_i * s_i / s). Evaluable/mergeable like any adapter.

    python lora_soup.py --out <dir> --adapters a1 a2 a3 [--weights 1 1 1]
"""
import argparse
import json
import os

import torch
from safetensors.torch import load_file, save_file


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--adapters", nargs="+", required=True)
    ap.add_argument("--weights", nargs="+", type=float, default=None)
    a = ap.parse_args()
    w = a.weights or [1.0] * len(a.adapters)
    w = [x / sum(w) for x in w]
    cfgs = [json.load(open(os.path.join(d, "adapter_config.json"))) for d in a.adapters]
    sds = [load_file(os.path.join(d, "adapter_model.safetensors")) for d in a.adapters]
    r_out = sum(c["r"] for c in cfgs)
    alpha_out = float(r_out)                     # output scale s = alpha/r = 1; inputs' scales folded into B
    out = {}
    for k in sds[0]:
        if "lora_A" in k:
            out[k] = torch.cat([sd[k].float() for sd in sds], 0).to(sds[0][k].dtype)
        elif "lora_B" in k:
            parts = [sd[k].float() * wi * (c["lora_alpha"] / c["r"]) for sd, wi, c in zip(sds, w, cfgs)]
            out[k] = torch.cat(parts, 1).to(sds[0][k].dtype)
        else:
            raise SystemExit(f"unexpected tensor {k}")
    for sd in sds[1:]:
        assert set(sd) == set(sds[0]), "adapters must target the same modules"
    os.makedirs(a.out, exist_ok=True)
    cfg = dict(cfgs[0]); cfg["r"] = r_out; cfg["lora_alpha"] = alpha_out
    cfg.pop("rank_pattern", None); cfg.pop("alpha_pattern", None)
    json.dump(cfg, open(os.path.join(a.out, "adapter_config.json"), "w"), indent=2)
    save_file(out, os.path.join(a.out, "adapter_model.safetensors"))
    json.dump({"adapters": a.adapters, "weights": w}, open(os.path.join(a.out, "soup.json"), "w"), indent=2)
    print(f"[soup] {len(a.adapters)} adapters -> rank {r_out} at {a.out}")


if __name__ == "__main__":
    main()
