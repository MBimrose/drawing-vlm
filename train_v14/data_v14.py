"""Webdataset loaders for the v14 drawing -> (thinking trace) -> build123d task.

Source layout (flat, no split subdirs):
    tars_v14/shard_XXXXXX.tar     members: {uuid}_v{N}.png + {uuid}_v{N}.py
    traces_v14.json               {uuid: {"t": trace, "p": pass|fail|null}}
                                  (built by build_trace_index.py; "p" is the
                                  reverse-reconstruction volume gate verdict)

Train/val split is by uuid hash (int(uuid[:8],16) % 50 == 7 -> validation,
~2%). Trace coverage is front-loaded in early shards, so a shard-based
holdout would have no traced validation samples.

Yielded sample shape:
    {"image": PIL, "code": str, "trace": str | None, "uuid": key}

trace_mode:
    "required" — only samples whose uuid has a usable trace (see trace_gate)
    "optional" — all samples; trace attached when available/usable
    "none"     — all samples; trace always None (code-only ablation)
trace_gate (which traces count as usable):
    "pass_only" — gate verdict must be pass (verified rebuildable trace)
    "any"       — any non-empty trace (pass, fail, or ungated)
"""
from __future__ import annotations

import glob
import tarfile
import io
import json
import os
import random

import torch
import webdataset as wds
from PIL import Image

TARS_ROOT = os.environ.get(
    "DRAWING_VLM_TARS",
    "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/step_to_drw/wds_dataset/tars_v14",
)
TRACES_JSON = os.environ.get(
    "DRAWING_VLM_TRACES_JSON",
    "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/step_to_drw/wds_dataset/traces_v14.json",
)
VAL_MOD = 50      # 1/50 = 2% of uuids held out
VAL_RESIDUE = 7
# Blocklist of sample keys whose GT script fails to execute (gt_audit).
BAD_KEYS_FILE = os.environ.get(
    "DRAWING_VLM_BAD_KEYS",
    "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/step_to_drw/wds_dataset/exec_bad_keys_v14.txt",
)

_TRACE_INDEX: dict[str, dict] | None = None
_BAD_KEYS: frozenset[str] | None = None


def bad_keys() -> frozenset[str]:
    global _BAD_KEYS
    if _BAD_KEYS is None:
        try:
            with open(BAD_KEYS_FILE) as f:
                _BAD_KEYS = frozenset(ln.strip() for ln in f if ln.strip())
            print(f"[data_v14] loaded {len(_BAD_KEYS)} exec-bad keys", flush=True)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"exec_filter requested but {BAD_KEYS_FILE} missing — run the "
                f"gt-audit job first")
    return _BAD_KEYS


def trace_index() -> dict[str, dict]:
    """Lazy per-process trace index: {uuid: {"t": trace, "p": gate}}."""
    global _TRACE_INDEX
    if _TRACE_INDEX is None:
        with open(TRACES_JSON, encoding="utf-8") as f:
            _TRACE_INDEX = json.load(f)
        print(f"[data_v14] loaded {len(_TRACE_INDEX)} traces from {TRACES_JSON}", flush=True)
    return _TRACE_INDEX


def uuid_of_key(key: str) -> str:
    """shard member key '{uuid}_v{N}' -> '{uuid}'."""
    return key.rsplit("_v", 1)[0]


def is_val_uuid(uuid: str) -> bool:
    try:
        return int(uuid[:8], 16) % VAL_MOD == VAL_RESIDUE
    except ValueError:
        return False


def usable_trace(uuid: str, trace_gate: str) -> str | None:
    rec = trace_index().get(uuid)
    if rec is None:
        return None
    if trace_gate == "pass_only" and rec.get("p") is not True:
        return None
    return rec["t"]


def all_shards() -> list[str]:
    shards = sorted(glob.glob(os.path.join(TARS_ROOT, "shard_*.tar")))
    if not shards:
        raise FileNotFoundError(f"no shards under {TARS_ROOT}")
    return shards


def _decode_png(b: bytes) -> Image.Image:
    """RGBA (black lines, transparent bg) -> composite over white."""
    img = Image.open(io.BytesIO(b))
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        return bg
    return img.convert("RGB")


def _decode_code(b: bytes) -> str:
    return b.decode("utf-8", errors="replace")


def augment_image(img: Image.Image, rng=None) -> Image.Image:
    """Conservative drawing augmentation: small rotation/scale + JPEG artifacts."""
    if rng is None:
        rng = random
    w, h = img.size
    if rng.random() < 0.8:
        angle = rng.uniform(-2.0, 2.0)
        img = img.rotate(angle, resample=Image.BILINEAR, fillcolor=(255, 255, 255))
    if rng.random() < 0.6:
        s = rng.uniform(0.96, 1.04)
        nw, nh = max(1, int(w * s)), max(1, int(h * s))
        scaled = img.resize((nw, nh), Image.BILINEAR)
        bg = Image.new("RGB", (w, h), (255, 255, 255))
        bg.paste(scaled, ((w - nw) // 2, (h - nh) // 2))
        img = bg
    if rng.random() < 0.5:
        q = rng.randint(70, 95)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=q)
        buf.seek(0)
        img = Image.open(buf).convert("RGB")
    return img


def build_train_dataset(
    trace_mode: str = "required",
    trace_gate: str = "pass_only",
    image_aug: bool = False,
    exec_filter: bool = False,
    shard_shuffle_buffer: int = 64,
    sample_shuffle_buffer: int = 2000,
    initial_buffer: int = 500,
):
    assert trace_mode in ("required", "optional", "none"), trace_mode
    assert trace_gate in ("pass_only", "any"), trace_gate
    excluded = bad_keys() if exec_filter else frozenset()

    def _keep(s) -> bool:
        if "png" not in s or "py" not in s:
            return False
        if s["__key__"] in excluded:
            return False
        uuid = uuid_of_key(s["__key__"])
        if is_val_uuid(uuid):
            return False
        if trace_mode == "required" and usable_trace(uuid, trace_gate) is None:
            return False
        return True

    def _pack(t):
        png, py, key = t
        img = _decode_png(png)
        if image_aug:
            img = augment_image(img)
        trace = None
        if trace_mode in ("required", "optional"):
            trace = usable_trace(uuid_of_key(key), trace_gate)
        return {"image": img, "code": _decode_code(py), "trace": trace, "uuid": key}

    pipe = wds.WebDataset(
        all_shards(),
        resampled=True,
        shardshuffle=shard_shuffle_buffer,
        nodesplitter=wds.split_by_node,
        workersplitter=wds.split_by_worker,
        handler=wds.warn_and_continue,
    )
    pipe = pipe.shuffle(sample_shuffle_buffer, initial=initial_buffer)
    pipe = pipe.select(_keep)
    return pipe.to_tuple("png", "py", "__key__").map(_pack)


EVAL_CACHE = os.environ.get(
    "DRAWING_VLM_EVAL_CACHE",
    "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/step_to_drw/wds_dataset/eval_cache_v14.pkl",
)


class EvalDataset(torch.utils.data.Dataset):
    """Validation samples (uuid-hash holdout) served from the prebuilt cache
    (build_eval_cache.py). Every rank loads the same examples so eval under
    FSDP/DDP is consistent. Scanning tars at runtime is deliberately avoided:
    the pass-gated pool is ~0.1% of the stream and would cost hundreds of GB
    of Lustre reads per rank."""

    def __init__(
        self,
        trace_mode: str = "required",
        trace_gate: str = "pass_only",
        max_n: int | None = 128,
    ):
        import pickle

        assert trace_mode in ("required", "optional", "none"), trace_mode
        with open(EVAL_CACHE, "rb") as f:
            cache = pickle.load(f)
        if trace_mode == "required":
            pool = cache["pools"]["pass" if trace_gate == "pass_only" else "any"]
        else:
            pool = cache["pools"]["all"]
        self.examples: list[dict] = []
        for key in pool[: max_n or len(pool)]:
            s = cache["samples"][key]
            trace = None
            if trace_mode in ("required", "optional"):
                trace = usable_trace(uuid_of_key(key), trace_gate)
            self.examples.append({
                "image": _decode_png(s["png"]),
                "code": s["code"],
                "trace": trace,
                "uuid": key,
            })

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, i):
        return self.examples[i]


# ==========================================================================
# v2 data era (2026-08-24 handoff): certified-manifest reasoning tier from
# the portable bundle + plain tier from tars_v14, mixed at reasoning_frac.
# Split discipline: the frozen manifest's eval split is uuid residue 0
# (int(uuid[:8],16) % 50 == 0); our legacy local holdout is residue 7.
# BOTH are excluded from every training stream.
# ==========================================================================

BUNDLE_ROOT = os.environ.get(
    "DRAWING_VLM_BUNDLE",
    "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/v14_bundle",
)
LEGACY_KEYS_FILE = os.path.join(os.path.dirname(TRACES_JSON), "legacy_keys_v14.txt")
EVAL_CACHE_V15 = os.environ.get(
    "DRAWING_VLM_EVAL_CACHE_V15",  # e.g. eval_cache_v15_dw423.pkl for models trained on 0.4.23 sheets
    os.path.join(os.path.dirname(TRACES_JSON), "eval_cache_v15.pkl"),
)

_LEGACY_KEYS: frozenset[str] | None = None


def is_manifest_eval_uuid(uuid: str) -> bool:
    """The frozen manifest's eval split (sft_manifest_v1: residue 0)."""
    try:
        return int(uuid[:8], 16) % 50 == 0
    except ValueError:
        return False


def legacy_keys() -> frozenset[str]:
    """tar_keys rendered by the legacy renderer (handoff says filter out)."""
    global _LEGACY_KEYS
    if _LEGACY_KEYS is None:
        try:
            with open(LEGACY_KEYS_FILE) as f:
                _LEGACY_KEYS = frozenset(ln.strip() for ln in f if ln.strip())
            print(f"[data_v14] {len(_LEGACY_KEYS)} legacy-renderer keys excluded",
                  flush=True)
        except FileNotFoundError:
            print("[data_v14] WARN legacy_keys_v14.txt missing — no renderer filter",
                  flush=True)
            _LEGACY_KEYS = frozenset()
    return _LEGACY_KEYS


def build_reasoning_dataset(
    image_aug: bool = False,
    shard_shuffle_buffer: int = 16,
    sample_shuffle_buffer: int = 1000,
    initial_buffer: int = 250,
):
    """Certified reasoning tier: bundle train shards, members
    <uuid>.png / <uuid>.trace.txt / <uuid>.code.py."""
    shards = sorted(glob.glob(os.path.join(BUNDLE_ROOT, "shards", "train-*.tar")))
    if not shards:
        raise FileNotFoundError(f"no bundle train shards under {BUNDLE_ROOT}")

    def _pack(t):
        png, trace, py, key = t
        img = _decode_png(png)
        if image_aug:
            img = augment_image(img)
        return {"image": img, "code": _decode_code(py),
                "trace": _decode_code(trace).strip(), "uuid": key}

    pipe = wds.WebDataset(
        shards, resampled=True, shardshuffle=shard_shuffle_buffer,
        nodesplitter=wds.split_by_node, workersplitter=wds.split_by_worker,
        handler=wds.warn_and_continue,
    )
    pipe = pipe.shuffle(sample_shuffle_buffer, initial=initial_buffer)
    pipe = pipe.select(lambda s: "png" in s and "trace.txt" in s and "code.py" in s)
    return (pipe.to_tuple("png", "trace.txt", "code.py", "__key__")
            .map(_pack))


UNPLACED_KEYS_FILE = os.path.join(os.path.dirname(TRACES_JSON),
                                  "unplaced_keys_v14.txt")
_UNPLACED_KEYS: frozenset[str] | None = None


def unplaced_keys() -> frozenset[str]:
    """tar_keys whose sheet has >=1 unplaced dimension (underdetermined —
    the true dims are not visible in the drawing; 33% of the corpus)."""
    global _UNPLACED_KEYS
    if _UNPLACED_KEYS is None:
        with open(UNPLACED_KEYS_FILE) as f:
            _UNPLACED_KEYS = frozenset(ln.strip() for ln in f if ln.strip())
        print(f"[data_v14] {len(_UNPLACED_KEYS)} underdetermined keys loaded",
              flush=True)
    return _UNPLACED_KEYS


def build_plain_dataset_v2(
    image_aug: bool = False,
    exec_filter: bool = True,
    dims_filter: bool = False,
    shard_shuffle_buffer: int = 64,
    sample_shuffle_buffer: int = 2000,
    initial_buffer: int = 500,
):
    """Plain tier (image -> code, no trace) over tars_v14, minus the frozen
    eval uuids, our legacy holdout, legacy-renderer drawings, and
    (optionally) non-executing GT and underdetermined sheets."""
    excluded_exec = bad_keys() if exec_filter else frozenset()
    excluded_legacy = legacy_keys()
    excluded_dims = unplaced_keys() if dims_filter else frozenset()

    def _keep(s) -> bool:
        if "png" not in s or "py" not in s:
            return False
        key = s["__key__"]
        if key in excluded_exec or key in excluded_legacy or key in excluded_dims:
            return False
        uuid = uuid_of_key(key)
        return not (is_val_uuid(uuid) or is_manifest_eval_uuid(uuid))

    def _pack(t):
        png, py, key = t
        img = _decode_png(png)
        if image_aug:
            img = augment_image(img)
        return {"image": img, "code": _decode_code(py), "trace": None, "uuid": key}

    pipe = wds.WebDataset(
        all_shards(), resampled=True, shardshuffle=shard_shuffle_buffer,
        nodesplitter=wds.split_by_node, workersplitter=wds.split_by_worker,
        handler=wds.warn_and_continue,
    )
    pipe = pipe.shuffle(sample_shuffle_buffer, initial=initial_buffer)
    pipe = pipe.select(_keep)
    return pipe.to_tuple("png", "py", "__key__").map(_pack)


class _WeightedMix(torch.utils.data.IterableDataset):
    """Per-sample weighted mix of iterable datasets (restart on exhaustion)."""

    def __init__(self, datasets, weights, seed: int = 0):
        self.datasets, self.weights, self.seed = datasets, weights, seed

    def __iter__(self):
        info = torch.utils.data.get_worker_info()
        rng = random.Random(self.seed + (info.id if info else 0))
        iters = [iter(d) for d in self.datasets]
        while True:
            i = rng.choices(range(len(iters)), weights=self.weights, k=1)[0]
            try:
                yield next(iters[i])
            except StopIteration:
                iters[i] = iter(self.datasets[i])
            except Exception as e:
                print(f"[mix] skip-on-error: {type(e).__name__}: {e}", flush=True)
                iters[i] = iter(self.datasets[i])


RFT_SHARDS = os.environ.get(
    "DRAWING_VLM_RFT_SHARDS",
    "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/rft_v1/shards",
)


def build_rft_dataset(
    image_aug: bool = True,
    shard_shuffle_buffer: int = 16,
    sample_shuffle_buffer: int = 1000,
    initial_buffer: int = 250,
):
    """Rejection-sampled tier (pack_rft_shards.py output): the model's own
    verified generations. Members <key>.png/.code.py/.think.txt; think is
    the model's own rationale that produced an iou>=0.8 part."""
    shards = sorted(glob.glob(os.path.join(RFT_SHARDS, "rft-*.tar")))
    if not shards:
        raise FileNotFoundError(f"no RFT shards under {RFT_SHARDS}")

    def _pack(t):
        png, code, think, key = t
        img = _decode_png(png)
        if image_aug:
            img = augment_image(img)
        return {"image": img, "code": _decode_code(code),
                "trace": _decode_code(think).strip() or None, "uuid": key}

    pipe = wds.WebDataset(
        shards, resampled=True, shardshuffle=shard_shuffle_buffer,
        nodesplitter=wds.split_by_node, workersplitter=wds.split_by_worker,
        handler=wds.warn_and_continue,
    )
    pipe = pipe.shuffle(sample_shuffle_buffer, initial=initial_buffer)
    pipe = pipe.select(lambda s: "png" in s and "code.py" in s)
    return (pipe.to_tuple("png", "code.py", "think.txt", "__key__")
            .map(_pack))


def build_mixed_v2(reasoning_frac: float = 0.2, image_aug: bool = True,
                   exec_filter: bool = True, rft_frac: float = 0.0,
                   dims_filter: bool = False, seed: int = 42):
    """Handoff-recommended mixture (~1:4 reasoning:plain at frac 0.2),
    optionally with a rejection-sampled (RFT) tier at rft_frac."""
    assert 0.0 <= reasoning_frac <= 1.0 and 0.0 <= rft_frac <= 1.0
    assert reasoning_frac + rft_frac <= 1.0
    datasets, weights, labels = [], [], []
    if rft_frac > 0:
        datasets.append(build_rft_dataset(image_aug=image_aug))
        weights.append(rft_frac)
        labels.append(f"rft={rft_frac:.2f}")
    if reasoning_frac > 0:
        datasets.append(build_reasoning_dataset(image_aug=image_aug))
        weights.append(reasoning_frac)
        labels.append(f"reasoning={reasoning_frac:.2f}")
    p_plain = 1.0 - reasoning_frac - rft_frac
    if p_plain > 0:
        datasets.append(build_plain_dataset_v2(image_aug=image_aug,
                                               exec_filter=exec_filter,
                                               dims_filter=dims_filter))
        weights.append(p_plain)
        labels.append(f"plain={p_plain:.2f}")
    print(f"[data_v14] v2 mix: {'  '.join(labels)}", flush=True)
    if len(datasets) == 1:
        return datasets[0]
    return _WeightedMix(datasets, weights, seed=seed)


class EvalDatasetV2(torch.utils.data.Dataset):
    """The frozen manifest's eval split (certified), from eval_cache_v15.pkl
    (built by geom/build_v15_assets.py from the bundle's eval shards)."""

    def __init__(self, max_n: int | None = 128):
        with open(EVAL_CACHE_V15, "rb") as f:
            import pickle
            cache = pickle.load(f)
        self.examples = []
        for key in cache["pools"]["certified"][: max_n or None]:
            s = cache["samples"][key]
            self.examples.append({
                "image": _decode_png(s["png"]),
                "code": s["code"],
                "trace": s["trace"],
                "uuid": key,
            })

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, i):
        return self.examples[i]


# --------------------------------------------------------------------------
# v3: verifier / reranker data (pack_scored_shards.py output)
# --------------------------------------------------------------------------
SCORED_SHARDS = os.environ.get(
    "DRAWING_VLM_SCORED_SHARDS",
    "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/rft_scored_v1/shards",
)


def _pack_scored(t, image_aug):
    png, code, meta, key = t
    m = json.loads(meta)
    img = _decode_png(png)
    if image_aug:
        img = augment_image(img)
    return {"image": img, "candidate_code": _decode_code(code),
            "iou": float(m.get("iou", 0.0)), "exec": bool(m.get("exec", False)),
            "uuid": key}


def build_verifier_dataset(image_aug: bool = True, shard_shuffle_buffer: int = 16,
                           sample_shuffle_buffer: int = 2000, initial_buffer: int = 500,
                           binary_threshold: float | None = None,
                           pos_keep: float = 1.0, seed: int = 42):
    """(drawing, candidate code) -> IoU. Every scored candidate incl. failures.

    binary_threshold: if set, adds sample["label"] = iou >= threshold and
    rejection-samples positives with prob `pos_keep` to balance classes
    (verifier v1 collapsed to predicting 1.0 on a positives-heavy pool)."""
    shards = sorted(glob.glob(os.path.join(SCORED_SHARDS, "scored-train-*.tar")))
    if not shards:
        raise FileNotFoundError(f"no scored shards under {SCORED_SHARDS}")
    rng = random.Random(seed)
    pipe = wds.WebDataset(
        shards, resampled=True, shardshuffle=shard_shuffle_buffer,
        nodesplitter=wds.split_by_node, workersplitter=wds.split_by_worker,
        handler=wds.warn_and_continue,
    )
    pipe = pipe.shuffle(sample_shuffle_buffer, initial=initial_buffer)
    pipe = pipe.select(lambda x: "png" in x and "code.py" in x and "meta.json" in x)
    def _mk(t):
        smp = _pack_scored(t, image_aug)
        if binary_threshold is not None:
            smp["label"] = smp["iou"] >= binary_threshold
        return smp
    def _keep(smp):
        if binary_threshold is None or not smp["label"]:
            return True
        return rng.random() < pos_keep
    return (pipe.to_tuple("png", "code.py", "meta.json", "__key__")
            .map(_mk).select(_keep))


class VerifierEvalDataset(torch.utils.data.Dataset):
    """Fixed held-out scored candidates (scored-eval-*.tar), first max_n."""

    def __init__(self, max_n: int = 128):
        self.samples = []
        for sp in sorted(glob.glob(os.path.join(SCORED_SHARDS, "scored-eval-*.tar"))):
            with tarfile.open(sp) as tf:
                groups: dict[str, dict] = {}
                for m in tf.getmembers():
                    base, _, ext = m.name.partition(".")
                    groups.setdefault(base, {})[ext] = tf.extractfile(m).read()
                for base, g in sorted(groups.items()):
                    if {"png", "code.py", "meta.json"} <= set(g):
                        self.samples.append(_pack_scored(
                            (g["png"], g["code.py"], g["meta.json"], base), False))
                    if len(self.samples) >= max_n:
                        break
            if len(self.samples) >= max_n:
                break

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, i):
        return self.samples[i]
