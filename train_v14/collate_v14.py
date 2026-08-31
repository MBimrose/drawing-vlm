"""Chat formatting + loss masking for Qwen3.8-27B (qwen3_5 arch) trace-SFT.

Conversation shape (single turn):
    system  : one of SYSTEM_PROMPTS[cfg.system_prompt]
    user    : [drawing image] + USER_PROMPT
    assistant: reasoning_content = thinking trace (may be ""),
               content           = ```python fenced build123d code```

The model's chat template renders the assistant as
    <|im_start|>assistant\n<think>\n{trace}\n</think>\n\n{code}<|im_end|>
so traced samples supervise trace + code, and untraced samples supervise the
empty-think close + code ("choose not to think").

Loss masking: tokenize messages[:-1] with add_generation_prompt=True (ends in
'<think>\n') and mask the longest common token prefix with the full text.
This sidesteps the newline-merge boundary issue noted in the v9 postmortem
without special-casing tokenizers.

Template kwargs: enable_thinking=True always; reasoning_effort is configurable
('medium' injects no extra system text; 'xhigh' injects Qwen's default
reasoning instructions — an experimental axis). Both template calls use
identical kwargs so the system section stays prefix-aligned.
"""
from __future__ import annotations

import re
from typing import Any

import torch

SYSTEM_PROMPTS: dict[str, str] = {
    # Rich role + explicit expectations about drawing conventions.
    "detailed": (
        "You are an expert mechanical/CAD engineer. You read multi-view "
        "engineering drawings (orthographic views, dimensions, diameter/radius "
        "callouts, hole leaders) and reconstruct the part as a complete, "
        "runnable build123d Python script.\n\n"
        "Requirements for your answer:\n"
        "- Interpret every dimension and annotation in the drawing.\n"
        "- Output a single self-contained ```python code block.\n"
        "- The script must import everything it needs and export the final "
        "solid with `export_step(part, \"output.step\")`.\n"
        "- Use named variables for the key dimensions so the model is "
        "parametric."
    ),
    # Minimal instruction — tests whether the heavy prompt matters.
    "concise": (
        "You are a CAD assistant. Convert the engineering drawing into a "
        "complete build123d Python script that exports the part to "
        "output.step. Answer with one ```python code block."
    ),
    # Explicitly frames the thinking trace as a numbered build plan.
    "plan_first": (
        "You are an expert CAD engineer. First think through a numbered "
        "step-by-step build plan for the part in the drawing (base feature, "
        "then each added/subtracted feature, then edge treatments). Then "
        "output a complete build123d Python script implementing exactly that "
        "plan, exporting the result with `export_step(part, \"output.step\")`, "
        "as a single ```python code block."
    ),
}

USER_PROMPT = "Reproduce the geometry as accurately as possible from the drawing."

_FENCE_RE_OPEN = re.compile(r"^```(?:python)?\s*\n?")
_FENCE_RE_CLOSE = re.compile(r"\n?```\s*$")
_OUTPUT_PATH_RE = re.compile(
    r"\bexport_step\(([^,]+),\s*(?:OUTPUT_PATH|OUTPUT_FILE|OUTPUT_STEP)\s*\)"
)


def wrap_python(code: str) -> str:
    s = code.strip()
    s = _FENCE_RE_OPEN.sub("", s)
    s = _FENCE_RE_CLOSE.sub("", s)
    s = _OUTPUT_PATH_RE.sub(r'export_step(\1, "output.step")', s)
    return f"```python\n{s}\n```"


VERIFIER_SYSTEM = (
    "You are a CAD verification expert. Given an engineering drawing and a "
    "candidate build123d script, estimate how well the solid the script produces "
    "matches the part in the drawing, as a volumetric IoU between 0.00 and 1.00. "
    "A script that fails to run scores 0.00. Answer with the number only."
)
VERIFIER_USER = (
    "Candidate build123d script for this drawing:\n\n{code}\n\n"
    "Estimate the volumetric IoU of the produced solid against the drawn part."
)


VERIFIER_BIN_USER = (
    "Candidate build123d script for this drawing:\n\n{code}\n\n"
    "Does this script produce a solid matching the drawn part with volumetric "
    "IoU of at least 0.85? Answer yes or no."
)


def build_verifier_messages(sample: dict) -> list[dict]:
    if "label" in sample:   # binary variant (v2): ranked by yes/no log-odds
        return [
            {"role": "system", "content": [{"type": "text", "text": VERIFIER_SYSTEM}]},
            {"role": "user", "content": [
                {"type": "image", "image": sample["image"]},
                {"type": "text", "text": VERIFIER_BIN_USER.format(
                    code=wrap_python(sample["candidate_code"]))},
            ]},
            {"role": "assistant",
             "content": [{"type": "text", "text": "yes" if sample["label"] else "no"}]},
        ]
    return [
        {"role": "system", "content": [{"type": "text", "text": VERIFIER_SYSTEM}]},
        {"role": "user", "content": [
            {"type": "image", "image": sample["image"]},
            {"type": "text", "text": VERIFIER_USER.format(
                code=wrap_python(sample["candidate_code"]))},
        ]},
        {"role": "assistant",
         "content": [{"type": "text", "text": f"{float(sample['iou']):.2f}"}]},
    ]


def build_messages(sample: dict, system_prompt: str,
                   trace_style: str = "think") -> list[dict]:
    """trace_style:
      "think"  — trace goes in reasoning_content (<think> block; Qwen3.5/3.8
                 family templates).
      "inline" — trace becomes a '### Construction plan' section before the
                 code inside the assistant content (architectures without a
                 thinking template, e.g. Qwen3-VL Instruct)."""
    trace = (sample.get("trace") or "").strip()
    head = [
        {"role": "system", "content": [{"type": "text", "text": SYSTEM_PROMPTS[system_prompt]}]},
        {"role": "user", "content": [
            {"type": "image", "image": sample["image"]},
            {"type": "text", "text": USER_PROMPT},
        ]},
    ]
    if trace_style == "inline":
        body = wrap_python(sample["code"])
        if trace:
            body = f"### Construction plan\n{trace}\n\n{body}"
        return head + [
            {"role": "assistant",
             "content": [{"type": "text", "text": body}]},
        ]
    return head + [
        {"role": "assistant",
         "reasoning_content": trace,
         "content": [{"type": "text", "text": wrap_python(sample["code"])}]},
    ]


class VLMCollator:
    def __init__(
        self,
        processor,
        max_seq_len: int = 5120,
        system_prompt: str = "detailed",
        reasoning_effort: str = "medium",
        trace_style: str = "think",
    ):
        assert system_prompt in SYSTEM_PROMPTS, system_prompt
        assert trace_style in ("think", "inline"), trace_style
        self.processor = processor
        self.max_seq_len = max_seq_len
        self.system_prompt = system_prompt
        self.trace_style = trace_style
        # Unknown jinja vars are ignored by templates that don't use them.
        self.tmpl_kwargs = dict(enable_thinking=True, reasoning_effort=reasoning_effort) \
            if trace_style == "think" else {}
        self._mask_warnings = 0

    def __call__(self, batch: list[dict[str, Any]]) -> dict[str, torch.Tensor]:
        # Poison-sample guard: isolate a failing sample instead of killing the
        # run; refill the batch with good samples to keep batch geometry.
        try:
            return self._collate(batch)
        except Exception as exc:
            if len(batch) == 1:
                raise
            good = []
            for b in batch:
                try:
                    self._collate([b])
                    good.append(b)
                except Exception:
                    print(f"[collate] DROPPING sample uuid={b.get('uuid')} "
                          f"({type(exc).__name__})", flush=True)
            if not good:
                raise
            i = 0
            while len(good) < len(batch):
                good.append(good[i % len(good)])
                i += 1
            return self._collate(good)

    def _collate(self, batch: list[dict[str, Any]]) -> dict[str, torch.Tensor]:
        from qwen_vl_utils import process_vision_info

        msgs = [build_verifier_messages(b) if "candidate_code" in b else
                build_messages(b, self.system_prompt, self.trace_style)
                for b in batch]

        full_text = [
            self.processor.apply_chat_template(
                m, add_generation_prompt=False, tokenize=False, **self.tmpl_kwargs)
            for m in msgs
        ]
        prompt_text = [
            self.processor.apply_chat_template(
                m[:-1], add_generation_prompt=True, tokenize=False, **self.tmpl_kwargs)
            for m in msgs
        ]
        images, videos = process_vision_info(msgs)

        enc = self.processor(
            text=full_text,
            images=images,
            videos=videos,
            return_tensors="pt",
            padding=True,
            pad_to_multiple_of=16,
            truncation=True,
            max_length=self.max_seq_len,
        )
        prompt_only = self.processor(
            text=prompt_text,
            images=images,
            videos=videos,
            return_tensors=None,
            padding=False,
            truncation=True,
            max_length=self.max_seq_len,
        )

        # Explicit False beats config defaults (merge_with_config_defaults):
        # with activation checkpointing, a live cache gets appended to twice
        # (forward + recompute) and doubles the key length -> SDPA crash.
        # Setting config.use_cache is NOT enough — the inner text model holds
        # a deep-copied config from _from_config.
        enc["use_cache"] = False

        labels = enc["input_ids"].clone()
        for i, pids in enumerate(prompt_only["input_ids"]):
            fids = enc["input_ids"][i].tolist()
            # Longest common prefix between prompt ids and full ids. Normally
            # equals len(pids) minus at most a couple of boundary tokens that
            # merged with the first target token.
            n = min(len(pids), len(fids))
            k = 0
            while k < n and pids[k] == fids[k]:
                k += 1
            if k < len(pids) - 4 and self._mask_warnings < 10:
                self._mask_warnings += 1
                print(f"[collate] WARN mask prefix {k} << prompt len {len(pids)} "
                      f"(uuid={batch[i].get('uuid')})", flush=True)
            labels[i, :k] = -100
        labels[enc["attention_mask"] == 0] = -100
        enc["labels"] = labels
        return enc
