"""Print raw generations for 2 eval samples from one checkpoint. Debug only."""
import os
import pickle
import sys

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

from data_v14 import EVAL_CACHE, _decode_png  # noqa: E402
from geom_eval_worker import build_gen_messages, generate_batch, load_model, run_config  # noqa: E402

run_name, kind, ckpt = sys.argv[1], sys.argv[2], sys.argv[3]
batch = int(sys.argv[4]) if len(sys.argv) > 4 else 2
cfg = run_config(run_name)
with open(EVAL_CACHE, "rb") as f:
    cache = pickle.load(f)
keys = cache["pools"]["all"][:batch]
samples = [{"uuid": k, "image": _decode_png(cache["samples"][k]["png"])} for k in keys]

model, processor = load_model(ckpt, kind, cfg)
outs = generate_batch(model, processor, cfg, samples, max_new_tokens=2400)
from geom_eval_worker import extract_code  # noqa: E402
for k, o in zip(keys, outs):
    code = extract_code(o)
    print(f"\n======== {k} len={len(o)} code={'YES' if code else 'NO'} ========")
    print(repr(o[:300]))
