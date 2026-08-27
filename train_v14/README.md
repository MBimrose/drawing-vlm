# train_v14 — Qwen3.8-27B trace-SFT on the v14 drawing dataset

Fine-tunes `models/Qwen3.8-27B` (qwen3_5 arch) on drawing → thinking-trace →
build123d code, using `step_to_drw/wds_dataset/tars_v14` (~500k pairs) joined
with `traces_v14` (61,747 Kimi K3 traces; 25,918 pass the reverse-reconstruction
volume gate).

Environment: `../.venv` (uv, Python 3.12.14, torch 2.13+cu130,
transformers 5.15.1, TRL 1.10, peft, flash-linear-attention).
Recreate with: `uv venv .venv --python 3.12 --python-preference only-managed`
then `uv pip install -p .venv torch transformers accelerate trl peft webdataset
wandb qwen-vl-utils pyyaml pillow numpy bitsandbytes torchvision kernels
flash-linear-attention`.

## Training format

    system   : SYSTEM_PROMPTS[cfg.system_prompt]        (collate_v14.py)
    user     : [drawing PNG] + "Reproduce the geometry ..."
    assistant: <think> trace </think> + ```python code``` (empty think when no trace)

Loss is masked to the assistant turn via longest-common-token-prefix between
the generation prompt and the full text. Train/val split: uuid hash
(`int(uuid[:8],16) % 50 == 7` → validation, ~2%).

## Experiments (wandb project: drawing-vlm-v14)

| run | node | GPUs | method | data | prompt | aug | lr |
|---|---|---|---|---|---|---|---|
| e1-full-traces | ccc0451 | 8 | full FT (FSDP2) | gate-pass traces (~26k) | detailed/medium | off | 1e-5 |
| e2-full-alldata-aug | ccc0474 | 8 | full FT (FSDP2) | all ~500k, traces optional | detailed/medium | on | 6e-6 |
| e3-lora-r64 | ccc0475 | 4 | LoRA r64 (DDP) | gate-pass traces | detailed/medium | off | 1e-4 |
| e4-lora-r128-concise | ccc0475 | 4 | LoRA r128 (DDP) | gate-pass traces | concise/xhigh | on | 2e-4 |
| e5-lora-notrace | ccc0475 (queued) | 4 | LoRA r64 (DDP) | all ~500k, NO traces | detailed/medium | off | 1e-4 |
| e6-lora-planfirst-anygate | ccc0475 (queued) | 4 | LoRA r64 (DDP) | ALL traces incl. gate-fail (~62k) | plan_first/medium | off | 5e-5 |

Axes covered: full-FT vs LoRA rank; traced-only vs all-data vs no-trace vs
any-gate (quality vs quantity); image augmentation on/off; three system
prompts + reasoning-effort header; LR 6e-6 → 2e-4.

All runs: eff. batch 64, seq 5120, vision tower frozen, cosine→10% min LR,
eval loss on a fixed 128-sample holdout every 250 steps; only the best-val
checkpoint is kept (saved on improvement, save_total_limit=1) plus a final consolidated save.

## Commands

    # submit everything
    cd sbatch && for f in *.sbatch; do sbatch $f; done

    # monitor
    squeue -u $USER
    tail -f ../../logs/slurm/<job>.o<id>

    # smoke ladder (login node ok for data/collate; forward needs a GPU)
    python smoke_test.py --stage data|collate|forward

    # one-off manual run
    bash run.sh configs/e1-full-traces.yaml --max_steps=20

Outputs land in `../runs/<run_name>/` (`final/` = consolidated bf16 model or
LoRA adapter). Serve with vLLM using `chat_template_kwargs={"reasoning_effort":
"medium"}` (or xhigh for e4) to match the training distribution.

## Geometric IoU eval (2026-08-20)

`geom/` implements the agentic-mesh-to-cad validation: generated code →
STEP → STL → exact volumetric IoU (manifold3d booleans, trimesh fallback)
against GT meshes precomputed for a fixed 96-sample pool (79 with valid GT;
17 GT codes fail geometrically and are excluded). The `geom-eval` job
(L40S node, self-resubmitting every 8h) evaluates each run's best
checkpoint + final, writing `runs/<run>/geom_eval/*.json` and logging
`geom/*` metrics to companion wandb runs named `<run>-geom`.
Headline metric: `geom/iou_mean` (bbox-centered IoU, failures scored 0).

## Expanded experiments (e7-e12)

e7 vision last_4 unfrozen | e8 full-FT lr 4e-6 | e9 LoRA r256 |
e10 LoRA attention-only targets | e11 2x image resolution |
e12 LoRA on the all-data+aug recipe. All best-only checkpointing,
submitted with --constraint=h200 (unpinned).
