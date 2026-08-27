"""Staged smoke test for the v14 pipeline. Run on a GPU node.

    python smoke_test.py --stage data      # loader + trace join + split
    python smoke_test.py --stage collate   # chat template + loss mask sanity
    python smoke_test.py --stage forward   # 1-GPU bf16 forward pass
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

MODEL = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/models/Qwen3.8-27B"


def stage_data():
    from data_v14 import EvalDataset, build_train_dataset, trace_index

    idx = trace_index()
    n_pass = sum(1 for v in idx.values() if v.get("p") is True)
    print(f"traces: {len(idx)} total, {n_pass} gate-pass")

    for mode, gate in (("required", "pass_only"), ("optional", "pass_only"), ("none", "any")):
        ds = build_train_dataset(trace_mode=mode, trace_gate=gate)
        it = iter(ds)
        for i in range(3):
            s = next(it)
            has_trace = s["trace"] is not None
            print(f"  [{mode}/{gate}] {s['uuid']}: img={s['image'].size} "
                  f"code={len(s['code'])}ch trace={'%d ch' % len(s['trace']) if has_trace else None}")

    ev = EvalDataset(trace_mode="required", trace_gate="pass_only", max_n=32)
    print(f"eval (required/pass_only): {len(ev)} examples")
    ev2 = EvalDataset(trace_mode="optional", trace_gate="pass_only", max_n=32)
    print(f"eval (optional): {len(ev2)} examples")
    assert len(ev) > 0 and len(ev2) > 0
    print("DATA STAGE PASS")


def stage_collate():
    from transformers import AutoProcessor

    from collate_v14 import VLMCollator
    from data_v14 import EvalDataset

    processor = AutoProcessor.from_pretrained(MODEL, min_pixels=200704, max_pixels=1179648)
    ev_traced = EvalDataset(trace_mode="required", trace_gate="pass_only", max_n=4)
    ev_plain = EvalDataset(trace_mode="none", max_n=4)

    for name, ev, prompt, effort in (
        ("traced/medium", ev_traced, "detailed", "medium"),
        ("traced/xhigh", ev_traced, "concise", "xhigh"),
        ("untraced/medium", ev_plain, "detailed", "medium"),
    ):
        coll = VLMCollator(processor, max_seq_len=5120, system_prompt=prompt,
                           reasoning_effort=effort)
        batch = coll([ev[0], ev[1]])
        ids = batch["input_ids"]
        labels = batch["labels"]
        n_tok = int(batch["attention_mask"][0].sum())
        n_target = int((labels[0] != -100).sum())
        target_ids = [t for t in labels[0].tolist() if t != -100]
        target_text = processor.tokenizer.decode(target_ids)
        print(f"  [{name}] seq={ids.shape[1]} real_tokens={n_tok} target_tokens={n_target}")
        print(f"    target starts: {target_text[:120]!r}")
        print(f"    target ends:   {target_text[-80:]!r}")
        assert n_target > 10, "loss mask left no target tokens"
        assert "```python" in target_text or "```" in target_text
        assert "<|im_end|>" in target_text, "target should include the end token"
    # Mixed traced+untraced batch must also collate.
    coll = VLMCollator(processor, max_seq_len=5120, system_prompt="detailed")
    mixed = coll([ev_traced[0], ev_plain[0]])
    print(f"  [mixed batch] shape={tuple(mixed['input_ids'].shape)}")
    print("COLLATE STAGE PASS")


def stage_forward():
    import torch
    from transformers import AutoProcessor, Qwen3_5ForConditionalGeneration

    from collate_v14 import VLMCollator
    from data_v14 import EvalDataset

    processor = AutoProcessor.from_pretrained(MODEL, min_pixels=200704, max_pixels=1179648)
    ev = EvalDataset(trace_mode="required", trace_gate="pass_only", max_n=2)
    coll = VLMCollator(processor, max_seq_len=5120, system_prompt="detailed")
    batch = coll([ev[0], ev[1]])

    print("loading model bf16 on cuda:0 ...")
    model = Qwen3_5ForConditionalGeneration.from_pretrained(
        MODEL, dtype=torch.bfloat16, attn_implementation="sdpa",
        low_cpu_mem_usage=True).to("cuda:0")
    model.eval()
    batch = {k: (v.to("cuda:0") if hasattr(v, "to") else v) for k, v in batch.items()}
    with torch.no_grad():
        out = model(**batch)
    print(f"loss = {float(out.loss):.4f}")
    print(f"max mem = {torch.cuda.max_memory_allocated() / 2**30:.1f} GiB")
    assert out.loss is not None and float(out.loss) < 20
    print("FORWARD STAGE PASS")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["data", "collate", "forward"], required=True)
    args = ap.parse_args()
    {"data": stage_data, "collate": stage_collate, "forward": stage_forward}[args.stage]()
