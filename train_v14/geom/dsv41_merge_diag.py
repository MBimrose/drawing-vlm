"""How much of a LoRA delta survives the FP8 (E4M3, UE8M0 32x32 block) merge? (2026-10-06)
For each target: d = (B@A)*alpha/r, applied = dequant(requant(W + d)) - W.  Reports ||applied||/||d||, the share of d
carried along its own direction (<applied, d>/||d||^2) and cos(applied, d). An RL update far below the FP8 grid step
rounds straight back to W and the served policy never changes.
    python dsv41_merge_diag.py --base <fp8 base> --adapter <adapter dir> [--n 14]"""
import argparse, json, os, re, sys
import torch
from safetensors import safe_open
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from merge_dsv41_lora import MAP, dequant, requant

ap = argparse.ArgumentParser(); ap.add_argument("--base"); ap.add_argument("--adapter"); ap.add_argument("--n", type=int, default=14)
a = ap.parse_args()
cfg = json.load(open(os.path.join(a.adapter, "adapter_config.json"))); sc = cfg["lora_alpha"] / cfg["r"]
ad = safe_open(os.path.join(a.adapter, "adapter_model.safetensors"), "pt")
idx = json.load(open(os.path.join(a.base, "model.safetensors.index.json")))["weight_map"]
keys = sorted(k for k in ad.keys() if "lora_A" in k)
step = max(1, len(keys) // a.n); tot = {"d2": 0.0, "a2": 0.0, "ad": 0.0}
for k in keys[::step][: a.n]:
    m = re.search(r"layers\.(\d+)\.(.+)\.lora_A\.weight$", k); t = f"layers.{m.group(1)}.{MAP[m.group(2)]}.weight"
    d = (ad.get_tensor(k.replace("lora_A", "lora_B")).float() @ ad.get_tensor(k).float()) * sc
    f = safe_open(os.path.join(a.base, idx[t]), "pt"); w = dequant(f.get_tensor(t), f.get_tensor(t[:-7] + ".scale"))
    ap_ = dequant(*requant(w + d)) - w
    dn, an, dot = float(d.norm()), float(ap_.norm()), float((ap_ * d).sum())
    tot["d2"] += dn ** 2; tot["a2"] += an ** 2; tot["ad"] += dot
    print(f"{t:40s} |d|/|W| {dn/float(w.norm()):.2e}  |applied|/|d| {an/dn:.3f}  along-d {dot/dn**2:.3f}  cos {dot/(an*dn+1e-30):.3f}  "
          f"changed {float((ap_ != 0).float().mean()):.4f}", flush=True)
print(f"TOTAL along-d share {tot['ad']/tot['d2']:.3f}  cos {tot['ad']/((tot['a2']*tot['d2'])**0.5+1e-30):.3f}  |applied|/|d| {(tot['a2']/tot['d2'])**0.5:.3f}")
