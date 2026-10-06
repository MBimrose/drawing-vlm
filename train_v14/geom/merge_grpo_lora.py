"""Merge a GRPO LoRA adapter into the e55 policy for vLLM serving/eval.

    python merge_grpo_lora.py --ckpt runs/e55-rft-real-u5-gt-dw423/final \
        --adapter runs/grpo_r1/adapter_final --out runs/grpo_r1_merged \
        [--model-base models/Qwen3.8-27B]
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TRAIN = os.path.dirname(HERE)
sys.path.insert(0, TRAIN)
sys.path.insert(0, HERE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True, help="base policy HF dir (e55 final)")
    ap.add_argument("--adapter", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model-base", default="", help="processor dir override (serv hosts)")
    args = ap.parse_args()

    import torch
    from peft import PeftModel
    from transformers import AutoProcessor

    processor_dir = args.model_base or args.ckpt
    model = __import__("geom_eval_worker", fromlist=["_model_cls"])._model_cls(args.ckpt)
    model = model.from_pretrained(args.ckpt, dtype=torch.bfloat16,
                                  attn_implementation="sdpa", low_cpu_mem_usage=True)
    model = PeftModel.from_pretrained(model, args.adapter)
    model = model.merge_and_unload()
    model.config.use_cache = True
    if hasattr(model.config, "text_config"):
        model.config.text_config.use_cache = True
    os.makedirs(args.out, exist_ok=True)
    model.save_pretrained(args.out, safe_serialization=True)
    processor = AutoProcessor.from_pretrained(
        processor_dir, min_pixels=200704, max_pixels=1179648)
    processor.save_pretrained(args.out)
    print(f"[merge] {args.adapter} + {args.ckpt} -> {args.out}")


if __name__ == "__main__":
    main()
