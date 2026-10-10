# Bench B: a second held-out real-parts bench (frozen 2026-10-09 23:52 CDT)

280 real human-designed parts (171 Fusion 360 + 109 ABC). Bench B was built and frozen **before any model was
evaluated on it**: `bench/FROZEN` holds the sha256 of the key list, of `eval_cache_v15.pkl` and of `manifest.json`, and
the directory is read-only. Its purpose is to confirm final picks on a bench that no checkpoint was ever selected on.
Do not select checkpoints on it.

- Bench dir: `results/bench_b/bench/`. Symlinked as `train_v14/mech/benchmarks/data/bench_b`, so the corpus-4 /
  realpool-v2 `used_file_ids()` rule sees it. serv-20 copy: `mech_benchmarks/bench_b`.
- The 280 file_ids were appended to `train_v14/mech/benchmarks/data/heldout_file_ids.txt` (146 → 426 lines).
  `build_rft1_tier.py`, `build_rft2_tier.py`, `results/cycle2/prep_keys.py`, `pack_scored_real.py` and `build_corpus.py`
  therefore hard-error or skip on any bench-B part.
- Keys: `keys.txt`. Leak check: `leakcheck.json`. Selection record: `selection.json`. Render failures: `render_failures.json`.
- Code: `train_v14/mech/benchmarks/build_bench_b.py` (exclusions / candidates / select / finalize / leakcheck) and
  `train_v14/sbatch/bench_b_build.sbatch` (ccc0442, CPU only, resumable).

## Sources: why not CADBench

CADBench is exhausted. All 12,000 of its STEP rows went into corpora 1–4, the ABC-code corpus or the 144-part bench
(`build_realpool_v2.py`). Bench B therefore goes back to the two datasets that CADBench's own Fusion and ABC subsets were
sampled from:

| family | source | raw | id format (same as CADBench) |
|---|---|---|---|
| F | Fusion 360 Gallery segmentation **s2.0.1 extended STEP** (S3 zip, 506 MB) | 42,912 bodies / 10,082 designs | `<project>_<hash>_<n>` (CADBench benchF ids are exactly these names) |
| A | ABC STEP chunks **0042 + 0043** (NYU archive, `abc_004{2,3}_step_v00.7z`) | 20,000 models | `<8-digit id>_<24-hex hash>_step_<nnn>` |

## Construction (identical to the 144-part bench)

1. `prep_external_parts.py --max-faces 80`. Filter: 1 solid, analytic faces only (plane/cylinder/cone/torus/sphere),
   6–80 faces, bbox aspect ≤ 15, fill ≥ 0.05. Longest edge → 80 mm. GT = the scaled solid exported as STL (tol 0.01).
2. draftwright 0.4.23 + font patch 5.25, via `render_isolated.sh` (render_ext.py / worker_v11, VLM_MODE=1, one renderer
   process per part, permissive scale policy). This is the same driver and venv as `rft_corpus4`. The renderer copies
   differ from the 144 bench's serv-19/20 copy only in comments and env-gated overrides, all unset (checked by diff).
   **No legacy fallback:** 377/383 rendered and all 280 final sheets have `renderer: draftwright`. The 6 failures (5 ABC, 1 Fusion:
   `ValueError: Start…`, `ValueError: reces…`, `StopIteration`, `_DrawingTimeout`) were dropped. Their full renderer
   logs are in `render_failures.json`.
3. `build_ext_eval_cache.py`. Underdetermined sheets are kept, as in the 144 bench.

## Selection rule (declared in code before rendering; seeds fixed)

1. **Exclusions** (below), then a cheap STEP-text prefilter: no B-spline/revolution/extrusion/offset surfaces, exactly one
   `MANIFOLD_SOLID_BREP`, and `ADVANCED_FACE` count in the 144 bench's per-family range (F 8–51, A 37–80).
2. At most **one body per Fusion design**, and **one part per ABC model id and per ABC Onshape hash**. Designs and models
   are taken in a seeded shuffle (seed 20261010). Candidates: F 1,500, A 666 (both chunks exhausted). Prep kept F 1,178 and A 525.
3. **Near-duplicate geometry check.** The existing tooling has no geometric dedup, so a signature match is used. A part is
   dropped if any used part has the same face count, the same surface-type census, sorted bbox ratios within 0.01, and
   fill within 0.01. The comparison covers all 114,072 parts in every project manifest, including DeepCAD
   corpus_full. The same check runs within bench B. Dropped: 47 near-duplicates of used parts, 62 within-bench duplicates.
4. **Mix and complexity matched to the 144 bench.** Target 280: F/A = 88/56 of the 144 bench → F 171, A 109. Within each
   family, the 144 bench's face-count quartiles (F edges 10/14/22, A edges 42/48.5/58) define 4 strata. The family target
   is apportioned by the 144 bench's counts per stratum: F 52/39/41/39, A 29/26/29/25. Within a stratum, parts go in one
   seeded shuffle (seed 20261011). The top quota×1.3+3 per stratum were rendered (383). The final bench is the top
   `quota` renderable parts per stratum in that order. All quotas were filled.

| | n | faces p10/50/90 | fill p10/50/90 | aspect p10/50/90 | underdetermined | has cylinder | has torus |
|---|---|---|---|---|---|---|---|
| 144 bench F | 88 | 8 / 14 / 33 | 0.14 / 0.39 / 0.78 | 1.5 / 3.3 / 10.4 | 31% | 84% | 18% |
| **bench B F** | 171 | 9 / 14 / 33 | 0.15 / 0.46 / 0.93 | 1.5 / 3.2 / 9.7 | 32% | 82% | 15% |
| 144 bench A | 56 | 38.5 / 48.5 / 62.5 | 0.15 / 0.32 / 0.64 | 1.4 / 4.3 / 12.4 | 46% | 100% | 46% |
| **bench B A** | 109 | 38 / 48 / 67 | 0.13 / 0.31 / 0.66 | 1.4 / 2.9 / 7.7 | 50% | 95% | 34% |

Known differences: bench-B Fusion parts are somewhat fuller at the top end (fill p90 0.93 vs 0.78, i.e. more block-like
parts). The 144 bench's Fusion parts are CADBench's k-means diversity sample, while bench B samples uniformly within
face strata. Bench-B ABC parts are less elongated and carry fewer fillets/tori.

## Exclusion lists checked (`exclusion/`, `exclusion/exclusion_sources.json`)

The approach is the round-2 agent's 146-file_id leak check (`results/cycle2/prep_keys.py`: file_id sets, hard error on
any overlap), widened from one held-out list to every source of used ids:

| source | what it covers |
|---|---|
| every `train_v14/mech/benchmarks/data/*/manifest.json` (28) | CADBench corpora 1–4 (+ dw423 copies), ABC-code corpora, `rft_realpool_v2` (12,969 DeepCAD = realpool2 / realpool2_hard_4500), DeepCAD gate, the 144 bench and all its variants, repair_bench_e55, family / zerocad / synth manifests |
| `deepcad/corpus_full/manifest.json` | 87,328 rendered DeepCAD parts (the e58 tier, the realpool v2 source) |
| `data/cadbench_inventory/rows.json` | all 18,000 CADBench rows, including rows no corpus kept (all 3,000 benchF → 2,225 Fusion designs) |
| DeepCAD full id list (serv-19 `deepcad/data/cad_json`, 215,094 ids) | DeepCAD ids are ABC model ids; every one is excluded from the ABC side |
| `heldout_file_ids.txt` | the 146 original held-out ids |
| token scan of 3,443 key/tier/bank/pool files (json/jsonl/txt/tsv/yaml ≤ 400 MB) | `results/` (cycle2 keys + tier2 + rp4 repairer pairs + search/teacher, guide banks v1/v2/v3 + rft1 tier, h6c hard keys incl. realpool2_hard_4500, grpo_eval, selection, pipeline), `train_v14/mech/benchmarks/data`, serv-20 `fp/` + `cycle2/` (RL arm key lists, guided banks, rp4, teacher), every `rft_*` tier at the repo root (rft_real*, union1–5, abccode*, selfdistill*, rft_repair_c1–c4/deepcad = repairer data, gtfb/plain, corpus4 tiers), dsv41 tiers, hard_keys_*.txt. One file was skipped for size: `rft_deepcad_e55/scored-000.jsonl`; its DeepCAD ids are all in the 215k list. |

Totals excluded: **2,225 Fusion designs** (design level, not just body: any body of a used design is excluded, which
removed 19,984 of the 42,912 Fusion bodies), **221,564 ABC/DeepCAD model ids**, **5,379 ABC Onshape hashes**, and
**114,072 geometry signatures**. ABC candidates removed by id: 4,803; by hash: 530.

**Leak check after freezing** (`leakcheck.json`, `build_bench_b.py leakcheck`): 280 keys, **0** id/design/hash
overlaps, **0** signature near-duplicates, no repeated design/model inside bench B → CLEAN.
keys sha256 `a32a8c6a…059e9`, eval cache sha256 `9266e280…c729b`.

## Evaluation protocol (same as results/grpo_eval)

- Generation: K=8 per part, draw 0 greedy and 7 draws at T 0.7 / top_p 0.95, think mode, 2,400 tokens.
  Path: `gen_openai_bo.py` → vLLM DP=1 on serv-20 GPU 7 (`eval_gpu7.sh`), models merged exactly as `grpo_eval.sh` does.
- Scoring: `score_partials.py --workers 16 --exec-timeout 60 --iou-timeout 90` (default `--accept 0.8`, as the daemon),
  then `consistency_rerank.py` (vote). Script: `score_vote_s20.sh`.
- Table: `results/cycle2/eval_table.py --prefix benchb --dir results/bench_b/eval` (2,000-sample paired bootstrap, rng 0).

Results: see GRPO_HANDOFF.md "Bench B + baselines (Oct 10)" and `results/bench_b/tables.md`.

## Results summary (2026-10-10; full tables in tables.md)

| bench B (n=280) | vote | draw-0 | first-exec | mean-cand | best-of-8 | exec |
|---|---|---|---|---|---|---|
| e55ctl | 0.509 | 0.402 | 0.461 | 0.385 | 0.595 | 0.799 |
| ent_t10_s120 | 0.640 | 0.625 | 0.629 | 0.611 | 0.696 | 0.986 |
| rft1_rl2_s120 | 0.651 | 0.628 | 0.632 | 0.624 | 0.708 | 0.990 |
| rft2_rl_s60 | 0.665 | 0.625 | 0.641 | 0.624 | 0.732 | 0.980 |
| vanilla DeepSeek-V4.1 (T0, ≤3 calls) | 0.393 | 0.315 | 0.336 | 0.328 | 0.513 | 0.941 |
| Qwen3.8-27B, no fine-tune | 0.082 | 0.017 | 0.082 | 0.018 | 0.092 | 0.061 |

rft2_rl_s60 − rft1_rl2_s120: vote +0.014 [+0.003,+0.025], best-of-8 +0.023 [+0.014,+0.032]. This replicates the
144-bench +0.019 / +0.018.
