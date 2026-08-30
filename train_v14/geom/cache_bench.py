import os, pickle, sys, time
sys.path.insert(0, "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/train_v14")
sys.path.insert(0, "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/train_v14/geom")
import torch
from data_v14 import EVAL_CACHE_V15, _decode_png
from geom_eval_worker import build_gen_messages, load_model, run_config
from qwen_vl_utils import process_vision_info

CKPT = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/runs/e24-rft/final"
cfg = run_config("e24-rft")
model, processor = load_model(CKPT, "hf", cfg)
print("config.use_cache =", model.config.use_cache,
      "| generation_config.use_cache =", model.generation_config.use_cache, flush=True)
cache = pickle.load(open(EVAL_CACHE_V15, "rb"))
keys = list(cache["pools"]["certified"])[:4]
imgs = [_decode_png(cache["samples"][k]["png"]) for k in keys]
msgs = [build_gen_messages(im, cfg) for im in imgs]
tmpl = dict(enable_thinking=True, reasoning_effort=cfg.get("reasoning_effort", "medium"))
texts = [processor.apply_chat_template(m, add_generation_prompt=True, tokenize=False, **tmpl) for m in msgs]
images, videos = process_vision_info(msgs)
enc = processor(text=texts, images=images, videos=videos, return_tensors="pt", padding=True)
enc = {k: (v.to(model.device) if hasattr(v, "to") else v) for k, v in enc.items()}
print("prompt tokens:", enc["input_ids"].shape, flush=True)
for use_cache in (False, True):
    torch.cuda.synchronize(); t = time.time()
    with torch.no_grad():
        out = model.generate(**enc, max_new_tokens=400, do_sample=False, use_cache=use_cache,
                             pad_token_id=processor.tokenizer.pad_token_id or processor.tokenizer.eos_token_id)
    torch.cuda.synchronize(); dt = time.time() - t
    n = out.shape[1] - enc["input_ids"].shape[1]
    print(f"use_cache={use_cache}: {dt:.1f}s for {n} tokens x4 seqs -> {4*n/dt:.1f} tok/s", flush=True)
