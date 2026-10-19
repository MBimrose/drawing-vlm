"""Nemotron-3.5 port, CPU check of the SFT data path (2026-10-15).

For N rows of each e55 tier (RFT / reasoning / plain) collate with the Nemotron processor and with e55's Qwen
processor (max_pixels 1179648), and report: full sequence length percentiles, image-token count, supervised
tokens, truncation rate at a given max_seq_len, mask-prefix warnings; print one rendered row per tier.

    python nemotron_collate_check.py --nemo <model dir> --qwen <Qwen3.8-27B dir> --n 200
"""
from __future__ import annotations

import argparse
import itertools
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from collate_v14 import VLMCollator  # noqa: E402
from data_v14 import build_plain_dataset_v2, build_reasoning_dataset, build_rft_dataset  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nemo", required=True)
    ap.add_argument("--qwen", required=True)
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--lens", default="5120,6144,6656,7168")
    args = ap.parse_args()
    from transformers import AutoProcessor
    pn = AutoProcessor.from_pretrained(args.nemo, trust_remote_code=True)
    pq = AutoProcessor.from_pretrained(args.qwen, min_pixels=200704, max_pixels=1179648)
    big = 1 << 20
    cn = VLMCollator(pn, max_seq_len=big, system_prompt="detailed")
    cq = VLMCollator(pq, max_seq_len=big, system_prompt="detailed")
    tiers = {"rft": build_rft_dataset(image_aug=False), "reasoning": build_reasoning_dataset(image_aug=False),
             "plain": build_plain_dataset_v2(image_aug=False, exec_filter=True)}
    lens = [int(x) for x in args.lens.split(",")]
    for name, ds in tiers.items():
        rows = list(itertools.islice(iter(ds), args.n))
        stat = {"nemo": [], "qwen": []}
        for i, r in enumerate(rows):
            for tag, c in (("nemo", cn), ("qwen", cq)):
                b = c([r])
                ids = b["input_ids"][0]
                n_sup = int((b["labels"][0] != -100).sum())
                img_id = pn.image_token_id if tag == "nemo" else pq.tokenizer.convert_tokens_to_ids("<|image_pad|>")
                stat[tag].append((len(ids), int((ids == img_id).sum()), n_sup))
                if i == 0:
                    lab = b["labels"][0]
                    k = int((lab == -100).sum())
                    txt_p = c.processor.tokenizer.decode(ids[:k][-40:])
                    txt_t = c.processor.tokenizer.decode(ids[k:][:120])
                    txt_e = c.processor.tokenizer.decode(ids[-20:])
                    print(f"\n=== {name} / {tag}: prompt tail ...{txt_p!r}\n--- target head {txt_t!r}\n--- tail {txt_e!r}")
        for tag in ("nemo", "qwen"):
            a = np.array(stat[tag])
            pct = np.percentile(a[:, 0], [50, 90, 99, 100]).astype(int)
            trunc = {L: float((a[:, 0] > L).mean()) for L in lens}
            print(f"[{name:9s} {tag}] n={len(a)} seq p50/p90/p99/max={pct.tolist()} img_tok median={int(np.median(a[:, 1]))} "
                  f"sup p50/p90/max={np.percentile(a[:, 2], [50, 90, 100]).astype(int).tolist()} "
                  f"trunc>{lens}: {[round(trunc[L], 3) for L in lens]}", flush=True)
        a, q = np.array(stat["nemo"]), np.array(stat["qwen"])
        ratio = (a[:, 2] / np.maximum(q[:, 2], 1))
        print(f"[{name:9s}] supervised-token ratio nemo/qwen median {np.median(ratio):.3f} p90 {np.percentile(ratio, 90):.3f}")
    print(f"mask warnings nemo={cn._mask_warnings} qwen={cq._mask_warnings}")


if __name__ == "__main__":
    main()
