# Data provenance

This repo is the training/evaluation consumer of the data engine at
https://github.com/MBimrose/step_to_drw. Nothing here regenerates data; every
experiment pins the upstream artifacts it consumed.

| artifact | upstream source | snapshot used |
|---|---|---|
| Drawings + GT code (500k) | `step_to_drw/wds_dataset/tars_v14/` + `*.renderers.json` sidecars | synced 2026-08-19; 2,500 shards |
| Certified traces | `wds_dataset/traces_v14/sft_manifest_v1.jsonl` | frozen 2026-08-24; 53,203 rows (52,131 train / 1,072 eval) |
| Portable bundle (drawing+trace+code+STEP) | `train/package_trace_dataset.py --with-step` | built 2026-08-24, 13 GB, `v14_bundle/` |
| Eval split | manifest `split=eval` (uuid residue 0 mod 50) | never re-split; GT meshes from bundle STEP files |
| Legacy local holdout | uuid residue 7 mod 50 | excluded from all training tiers |

Derived filters (built here, from upstream data):

| file | rule | count |
|---|---|---|
| `exec_bad_keys_v14.txt` | GT script fails to execute (gt_audit) | 105,351 (21%) |
| `legacy_keys_v14.txt` | sidecar `renderer == "legacy"` | 2,479 |
| `unplaced_keys_v14.txt` | sidecar `dims_unplaced` non-empty | 169,109 (33%) |

Self-generated tiers: `rft_v1` (generator e16-final, 60,037 kept at IoU≥0.8),
`rft_v2` (generator e22-ckpt3500). Base model: `Qwen/Qwen3.8-27B` at revision
`1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`.
