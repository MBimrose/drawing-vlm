"""Make a Nemotron-3.5 fine-tune checkpoint servable by vLLM (2026-10-15).

save_full_model() writes the trained HF state dict through save_pretrained. Compared with the base checkpoint that
leaves out (a) the MTP head (`language_model.mtp.*`: HF never builds it; vLLM's MTP speculative decoding needs it —
it is the base head, so drafts are less often accepted after fine-tuning, but decoding stays exact), and (b) any
buffer demoted to non-persistent for cpu_ram_efficient_loading (router `e_score_correction_bias`, which HF never
updates, so the base values are the trained values). This copies every base tensor missing from the trained
checkpoint into `model-extra-base.safetensors`, rewrites the index, and copies the remote code / tokenizer /
processor / chat-template files from the base. It fails loudly if the trained checkpoint has a key the base does not,
or if a copied key is anything other than mtp.* or a known buffer.

    python nemotron_finalize_ckpt.py --base <base dir> --ckpt <trained dir> [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil

from safetensors import safe_open
from safetensors.torch import save_file

COPY_FILES = ["chat_template.jinja", "configuration_nemotron_h_omni.py", "configuration_radio.py",
              "image_processing_nemotron_h_omni.py", "modeling_nemotron_h_omni.py", "modeling_radio.py",
              "processing_nemotron_h_omni.py", "ultra_v3_reasoning_parser.py", "__init__.py", "tokenizer.json",
              "tokenizer_config.json", "preprocessor_config.json", "processor_config.json", "generation_config.json",
              "config.json"]
# HF's RADIO port creates LayerScale params the released checkpoint does not carry (initialised to layerscale_value
# 1.0 = identity, frozen with the vision tower). They must be exactly 1 and are dropped so the key set equals the base.
ALLOWED_EXTRA = re.compile(r"^vision_model\..*\.layer_scale\d\.lambda1$")
ALLOWED_MISSING = re.compile(r"^language_model\.mtp\.|\.e_score_correction_bias$|^vision_model\.summary_idxs$|"
                             r"input_conditioner\.")


def keys_of(d: str) -> dict[str, str]:
    idx = os.path.join(d, "model.safetensors.index.json")
    if os.path.exists(idx):
        return json.load(open(idx))["weight_map"]
    out = {}
    for f in sorted(os.listdir(d)):
        if f.endswith(".safetensors"):
            with safe_open(os.path.join(d, f), "pt") as s:
                out.update({k: f for k in s.keys()})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    base, tr = keys_of(a.base), keys_of(a.ckpt)
    extra = sorted(set(tr) - set(base))
    bad_extra = [k for k in extra if not ALLOWED_EXTRA.search(k)]
    if bad_extra:
        raise SystemExit(f"FATAL: {len(bad_extra)} trained keys not in the base checkpoint, e.g. {bad_extra[:5]}")
    drop_files: dict[str, list[str]] = {}
    for k in extra:
        drop_files.setdefault(tr[k], []).append(k)
    for f, ks in drop_files.items():
        with safe_open(os.path.join(a.ckpt, f), "pt") as s:
            for k in ks:
                t = s.get_tensor(k)
                if not bool((t.float() == 1.0).all()):
                    raise SystemExit(f"FATAL: {k} is not identity (min {float(t.min())}, max {float(t.max())})")
    print(f"extra identity LayerScale keys to drop: {len(extra)} in {len(drop_files)} shard(s)", flush=True)
    missing = sorted(set(base) - set(tr))
    bad = [k for k in missing if not ALLOWED_MISSING.search(k)]
    if bad:
        raise SystemExit(f"FATAL: {len(bad)} base keys missing from the trained checkpoint that are not mtp/buffers, "
                         f"e.g. {bad[:5]}")
    n_mtp = sum(k.startswith("language_model.mtp.") for k in missing)
    print(f"trained keys {len(tr)}, base keys {len(base)}, copying {len(missing)} from base "
          f"(mtp {n_mtp}, buffers/other allowed {len(missing) - n_mtp})", flush=True)
    if a.dry_run:
        return
    for f, ks in drop_files.items():
        fp = os.path.join(a.ckpt, f)
        with safe_open(fp, "pt") as s:
            keep = {k: s.get_tensor(k) for k in s.keys() if k not in set(ks)}
        save_file(keep, fp + ".tmp", metadata={"format": "pt"})
        os.replace(fp + ".tmp", fp)
        for k in ks:
            tr.pop(k)
    for f in os.listdir(a.ckpt):   # save_pretrained copies the dynamic FSDP2 class's torch sources as "custom code"
        if f.startswith("_fsdp_") and f.endswith(".py"):
            os.remove(os.path.join(a.ckpt, f))
    tensors = {}
    by_file: dict[str, list[str]] = {}
    for k in missing:
        by_file.setdefault(base[k], []).append(k)
    for f, ks in by_file.items():
        with safe_open(os.path.join(a.base, f), "pt") as s:
            for k in ks:
                tensors[k] = s.get_tensor(k)
    out_name = "model-extra-base.safetensors"
    save_file(tensors, os.path.join(a.ckpt, out_name), metadata={"format": "pt"})
    wm = dict(tr)
    wm.update({k: out_name for k in missing})
    if not os.path.exists(os.path.join(a.ckpt, "model.safetensors.index.json")) and len(set(tr.values())) == 1:
        pass  # single-file checkpoint: the index below covers it
    total = 0
    for f in set(wm.values()):
        total += os.path.getsize(os.path.join(a.ckpt, f))
    json.dump({"metadata": {"total_size": total}, "weight_map": dict(sorted(wm.items()))},
              open(os.path.join(a.ckpt, "model.safetensors.index.json"), "w"), indent=2)
    for f in COPY_FILES:
        src = os.path.join(a.base, f)
        if os.path.exists(src):
            if f == "config.json" and os.path.exists(os.path.join(a.ckpt, f)):
                os.replace(os.path.join(a.ckpt, f), os.path.join(a.ckpt, "config.trained.json"))
            shutil.copy2(src, os.path.join(a.ckpt, f))
    open(os.path.join(a.ckpt, "FINALIZED_FROM_BASE"), "w").write(a.base + "\n")
    print(f"wrote {out_name} ({len(missing)} tensors), index ({len(wm)} keys), copied base config/code/tokenizer files",
          flush=True)


if __name__ == "__main__":
    main()
