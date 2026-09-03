# Mechanism 4 — real / external benchmark parts and drawings

Research + light prep, 2026-09-03. No GPU used. Nothing in `train_v14/` edited.

## TL;DR

- **Our "synthetic" parts are `ADSKAILab/Zero-To-CAD-1m`** (Autodesk, Apache-2.0, agentically
  synthesised CadQuery programs, no real data). Every number so far is on that distribution.
- **Recommended external test ("real geometry, our drawings"):** the *medium* complexity tier of
  CADBench's `benchF` (Fusion 360 Gallery, human-designed) and `benchA` (ABC/Onshape, human-designed),
  filtered to single-body analytic-surface parts with 6–80 faces. **Measured pass rate 59–60 %**
  (88/150 Fusion-medium, 58/96 ABC-medium). The STEP column can be pulled by HTTP range reads
  (~14 MB per 96 parts) so a 300-part bench costs < 200 MB of download.
- **146 filtered parts are already prepared** (scaled to 80 mm, STEP for the renderer + GT STL) under
  `train_v14/mech/benchmarks/data/cadbench_{F,A}_medium/`. GT STL passes `iou_pair` self-check (1.000).
- **Rendered (2026-09-03, serv-19 CPU):** the draftwright engine is not on the cluster (private upstream
  repo; `/srv/scratch/bimrose2/step_to_drw` on serv-19 is an empty stub), but a vendored copy lives at
  `wpk-serv-06:/srv/scratch/bimrose2/drawing-agent/vendor/step_to_drw/` and the `draftwright` package is
  in the NFS user-site of `/software/python-3.11.1`. Copied the code to
  `serv-19:/srv/scratch/bimrose2/mech_benchmarks/` and rendered **146/146 parts in 28 s** with
  `render_ext.py` (calls `worker_v11._process_one_part` exactly as the v14 dataset workers do, VLM_MODE=1).
  All 146 sidecars say `renderer: draftwright`; **66/146 (45 %) are underdetermined** (`dims_unplaced`
  non-empty) vs 24–33 % in-distribution. Sheets verified visually (our format: third-angle views, ISO
  view, "ISO 2768-m / draftwright" title block, 1920×1280).
- **Eval submitted:** SLURM job 10321045 `m-benchmarks-bo8` on ccc0442 (4×L40S), best-of-8 K=8 T=0.7 with
  the unmodified `bestofn_verifier_eval.py` + `consistency_rerank.py` via env overrides; results in §5.
- **Secondary "real drawings" test:** cadgenbench (49 real Mecado sheets, GT withheld, leaderboard)
  and NIST MBE PMI CTC/FTC (11 machined parts, real PDF drawings + STEP AP242, no restrictions).
  Nothing else found pairs real dimensioned drawings with STEP GT for machined parts.

## 1. Dataset survey

Fit legend: **A** = single-body machined parts like ours (plates/brackets/flanges with holes,
pockets, chamfers); **B** = mixed (needs filtering); **C** = organic / assemblies / not machinable;
**–** = no 3D GT.

| Dataset | Contents | Size | License | Download | Fit | Notes |
|---|---|---|---|---|---|---|
| **Zero-To-CAD-1m** (ADSKAILab) | CadQuery program + op JSON, 8×256² renders, STL + STEP, 65 synthetic part categories, ~980k train | ~1M | Apache-2.0 | [HF](https://huggingface.co/datasets/ADSKAILab/Zero-To-CAD-1m) | A (but it IS our training distribution) | The source of tars_v14. Its test split is held-out but not external. |
| **CADBench** (DeCoDELab/MIT, arXiv 2605.10873) | 6 families × 3,000: benchB (DeepCAD), benchF (Fusion 360), benchE (ABC sketch-extrude), benchA (ABC), benchM (MCB, mesh only), benchO (Objaverse, mesh only). Per row: `step`, `stl`, `obj`, `glb`, `noisy_stl`, single/multi-view/PBR renders, `label` ∈ {easy, medium, hard} by B-rep face count. Single-body only, k-means diversity-sampled | 80 GB total; parquet shards 360–610 MB; `step` column ≈ 0.15 MB/row | HF card: none stated; code Apache-2.0; parts inherit Fusion/ABC terms | [HF](https://huggingface.co/datasets/DeCoDELab/CADBench) | **A/B** after filter (this report) | Shards are tier-sorted: benchF 0–? easy, ~10 hard, 19 medium; benchA 15 hard, 30 medium. Published single-view IoU: CADFit 0.982 (benchF-easy), 0.950 (benchA-easy). |
| **Fusion 360 Gallery – reconstruction** | 8,625 human sketch+extrude designs: JSON sequence, STEP, SMT, OBJ, PNG per step; 6,900/1,725 split; units cm | 2.0 GB zip | Non-commercial research only; no redistribution; may publish results | [S3 r1.0.1](https://fusion-360-gallery-dataset.s3.us-west-2.amazonaws.com/reconstruction/r1.0.1/r1.0.1.zip) | B | Same parts as CADBench benchF; CADBench is the cheaper access path. Segmentation subset: 35,680 parts / 42,912 STEP, 3.1 GB. |
| **ABC** (NYU, Onshape) | 1M B-rep models: STEP, Parasolid, STL, OBJ, features, meta; chunks of 10k | multi-GB per chunk | Creator copyright; Onshape ToU 1.g.ii; no warranty | [site](https://deep-geometry.github.io/abc-dataset/) | B (lots of assemblies, sheet, freeform) | Use via CADBench benchA/benchE instead. `ADSKAILab/ABC-1M` on HF (MIT, 902 GB parquet) is a B-rep-feature re-encoding, not a STEP dump. |
| **DeepCAD** | 178k Onshape sketch-extrude sequences as JSON; `export2step.py` (pythonOCC) | small JSON | MIT (code/data); models Onshape-derived | [GitHub](https://github.com/ChrisWu1997/DeepCAD) | B | Same parts as CADBench benchB; simple prismatic parts, many degenerate. |
| **Text2CAD** (DFKI) | DeepCAD + text prompts, renders 397 GB, minimal JSON 246 MB; no STEP shipped | 605 GB | CC BY-NC-SA 4.0 | [HF](https://huggingface.co/datasets/SadilKhan/Text2CAD) | B | Text task; nothing beyond DeepCAD for us. |
| **CAD-Recode** | 1M synthetic CadQuery programs (Qwen2-1.5B decoder), point-cloud input | – | – | arXiv 2412.14042 | C (synthetic, like ours) | Not independent from a "synthetic" critique. |
| **Drawing2CAD / CAD-VGDrawing** (ACM MM 2025) | DeepCAD parts rendered to 4-view **SVG** (front/top/right/iso) via FreeCAD; `svg_raw`, `svg_vec`, `cad_vec` (h5) | Google Drive | MIT code | [GitHub](https://github.com/lllssc/Drawing2CAD) | B (no dimensions on drawings) | Closest published "drawing→CAD" benchmark, but undimensioned line drawings at 224², DeepCAD geometry. |
| **TriView2CAD / CReFT-CAD** | 200k synthetic + 3,000 real three-view drawings with dimension annotations; JSON params, DXF, PNG, scripts, STEP, B-rep | ModelScope | none stated | [GitHub](https://github.com/KeNiu042/CReFT-CAD) | C | Domain is **prefabricated bridge piers** (civil), 15-parameter family. Not machined parts. |
| **cadgenbench** (HuggingAI4Engineering + Mecado) | 49 generation fixtures: real-style A2 sheet PNG (sections, GD&T, hole callouts, title block) + `description.yaml`; 32 editing fixtures with STEP. **GT withheld**, server-side leaderboard scoring | small | ODC-BY | [HF](https://huggingface.co/datasets/HuggingAI4Engineering/cadgenbench-data) · [code](https://github.com/huggingface/cadgenbench) | **A for real drawings** (no local GT) | The owner already has the harness at `/srv/scratch/bimrose2/cadgenbench`. Drawing style ≠ ours (see fixture 101). |
| **NIST MBE PMI test cases** | CTC 1–5, FTC 6–11, STC, HTC: machined single parts (FTC 7–10 assemble), STEP AP242/AP203 + native CAD + PDF/3D-PDF drawings with full GD&T | MBs | "can be used without any restrictions" | [NIST](https://www.nist.gov/ctl/smart-connected-systems-division/smart-connected-manufacturing-systems-group/mbe-pmi-0) · [MBx-IF](https://www.mbx-if.org/home/cax/resources/) | **A for real drawings** (n≈11) | Real human-drafted sheets + STEP GT; tiny but credible qualitative test. |
| **MCB** (Purdue/TraceParts) | 58,696 mesh components, 68 classes (bearings, gears, bolts…) | – | TraceParts API terms | [GitHub](https://github.com/stnoah1/mcb) | C (mesh only, catalogue parts) | CADBench benchM. |
| **MFCAD++** (QUB) | 59,655 synthetic STEP parts with 3–10 labelled machining features (24 types) | GitLab | – | [GitLab](https://gitlab.com/qub_femg/machine-learning/mfcad2-dataset) | A-ish but synthetic | Independent synthetic generator; useful as a second synthetic family, not as "real". |
| **GenCAD-3D / GenCAD-Code** | 127 GB CAD programs + clouds + meshes + STEP (DeepCAD-derived); 163k image–CadQuery pairs | 127 GB | – | [HF](https://huggingface.co/datasets/yu-nomi/GenCAD_3D) | B | DeepCAD geometry again. |
| **Img2CAD**, **OpenECAD** | annotated images / OpenECAD code (→STEP via tool) | – | – | HF | C / B | Not drawing-based. |
| Kaggle (CAD/CAE Design, Two-Dimensional Engineering Drawings, symbol sets) | 2D drawing images; no STEP GT | – | varies | Kaggle | – | Classification/OCR only. |
| Drawing-annotation sets (arXiv 2506.17374: 1,367 drawings; 2510.21862: 1,000 + 1,406; 2602.18296: 20 CAD–drawing pairs) | real 2D drawings, no public STEP GT | – | – | – | – | Not released with GT. |

Already on disk (this cluster): nothing external. `find` under `/projects/illinois/eng/ece/wpk`, `~`,
`/scratch/bimrose2` for `*abc*|*fusion*|*deepcad*|…` returned only unrelated hits. The ~105 ABC STLs
under `CADFit_build123d/benchmarks/parts/abc/` live on the wpk-serv scratch, not here. Internet and
the HF token work from the login node (`HF_HOME=/projects/.../bimrose2/.cache/huggingface`).

## 2. What was measured on external STEP (build123d 0.11.1 in `.venv`)

Filter = "single-body machined part": exactly 1 solid; all faces analytic (plane/cylinder/cone/
torus/sphere, i.e. no B-spline); 6 ≤ faces ≤ 80; bbox aspect ≤ 15; volume / bbox-volume ≥ 0.05.

| Family / tier (CADBench shard) | n | 1 solid | faces min/med/max | analytic-only | **pass** | reject reasons |
|---|---|---|---|---|---|---|
| Fusion easy (`bench0F-00000`) | 150 | 150 | 3 / 4 / 6 | – | ~0 | trivially simple (boxes, discs); below the 6-face floor |
| Fusion medium (`bench0F-00019`) | 150 | 150 | 8 / 14 / 51 | 119 | **88 (59 %)** | freeform 31, aspect 30, fill 1 |
| Fusion hard (`bench0F-00010`) | 150 | 150 | 57 / 78 / 421 | 107 | 46 (31 %) | mostly > 80 faces |
| ABC medium (`bench1B-00030`) | 96 | 96 | 37 / 52 / 137 | 91 | **58 (60 %)** | faces 17, aspect 15, freeform 5, fill 1 (69 at ≤120 faces) |
| ABC hard (`bench1B-00015`) | 97 | 97 | 138 / 219 / 3025 | 83 | 0 | all > 80 faces |

Scale: CADBench normalises every part to a 20-unit bbox; our pool's longest edge is 60 / 80 / 90 mm
(p10/p50/p90 over 200 GT meshes, min extent 5 / 13.5 / 40). `prep_external_parts.py` rescales the
longest edge to 80 mm. After scaling, min extent p50 is 24 mm (Fusion) / 18 mm (ABC) — a little
chunkier than our pool, fine.

GT path: `import_step → solids()[0].scale(s) → export_stl(tol 0.01)`; `iou_pair(stl, stl)` = 1.000
on every checked part; 24 + 146 parts, zero load failures, 0.01–5 s each. (build123d quirk:
`export_step` fails on the Solid returned by `import_step`; export the extracted child.)

Prepared and kept in this directory:

```
train_v14/mech/benchmarks/data/cadbench_F_medium/{step_mm/,gt_meshes_v15/,manifest.json}   88 parts
train_v14/mech/benchmarks/data/cadbench_A_medium/{step_mm/,gt_meshes_v15/,manifest.json}   58 parts
train_v14/mech/benchmarks/data/stats_{F_medium,F_hard,A_medium,A_hard}.json               per-part B-rep stats
```

## 3. Rendering an external STEP into our sheet format (how-to)

The renderer ("draftwright"; sidecar `renderer: draftwright`, `part_model: simplify`) is the
upstream data engine, not this repo. Known from `step_to_drw/README.md` + `CLAUDE.md` (v13 pipeline):

| File (upstream) | Role |
|---|---|
| `pipeline.py` | single-process STEP → drawing (test / debug) — **the entry point for one-off parts** |
| `gen_examples_v13.py` | renders a curated review batch (5 variants × 15 parts) |
| `generate_shards_v13.py N` → `launch_v13.sh W` (`worker_v11.py`) | dataset path: HF stream → pickled shards → tars + `*.renderers.json` |
| `draw_generator.py`, `draw_frame.py`, `dimensions.py`, `drawing_decor.py`, `config.py`, `utils.py` | layout / dimension placement / frame + title block / STEP import & SVG→PNG |

Steps (to run on a wpk-serv node where `/srv/scratch/bimrose2/step_to_drw` exists; python
`/software/python-3.11.1/bin/python3`, deps build123d + OCP + cairosvg):

1. `rsync -a <cluster>:.../train_v14/mech/benchmarks/data/cadbench_{F,A}_medium/step_mm/ <serv>:/srv/scratch/bimrose2/ext_parts/step_mm/`
2. Render each STEP with the single-part path (`pipeline.py`; if it only accepts shard pickles, write
   a 20-line shim that builds the same pickle records `generate_shards_v13.py` emits, with the STEP
   bytes in place of the HF row) using the v14 defaults (ISO 2768-m, `simplify` part model,
   1–5 variants). Keep the `*.renderers.json` sidecar — `dims_unplaced` marks underdetermined sheets.
3. Copy PNGs + sidecar back, then:
   ```
   .venv/bin/python train_v14/mech/benchmarks/build_ext_eval_cache.py \
       --bench train_v14/mech/benchmarks/data/cadbench_F_medium --png-dir <pngs> --sidecar <renderers.json>
   ```
   This writes `eval_cache_v15.pkl` (+ `eval_cache_v14.pkl`, `traces_v14.json`, `legacy_keys_v14.txt`)
   next to `gt_meshes_v15/`, in the exact shape the eval scripts read (`samples[key]["png"]`,
   `pools["certified"]`). Verified: the pickle loads through `data_v14._decode_png` with the env
   overrides below.
4. Run the champion unchanged (zero edits — every path is env-derived; `data_v14` imports cleanly):
   ```
   export DRAWING_VLM_TRACES_JSON=$B/traces_v14.json  DRAWING_VLM_EVAL_CACHE=$B/eval_cache_v14.pkl
   .venv/bin/python train_v14/geom/bestofn_verifier_eval.py --run e24-rft --ckpt runs/e24-rft/final \
       --n 146 --k 8 --temperature 0.7 --out results/mech/benchmarks/bo8_ext_e24.json
   .venv/bin/python train_v14/geom/consistency_rerank.py ...   # same flags as the RECIPE
   ```
   (`geom_eval_worker.py --eval-one` refuses GT dirs with < 1000 STLs — use the best-of-N script,
   which just skips keys without a GT STL.)

I could not execute step 2 here: no renderer source on this filesystem, GitHub repo private. The
exact `pipeline.py` flags therefore remain to be confirmed on the wpk-serv checkout. Everything
before and after the render is built and tested.

Two things to confirm when rendering: (a) draftwright dimensions from the B-rep alone (the README
says auto-dimensioning from STEP; the sidecar annotation names like `dim_plate_x0` suggest a
feature-recognition pass rather than parametric metadata — external STEP has no metadata, so this
must hold); (b) Fusion/ABC parts are already in "machining" orientation only by luck — check the
view-selection heuristic puts the largest face front-on as it does for Zero-To-CAD parts.

## 3b. What it took to render (for the record)

- Renderer entry point that worked: **not** `pipeline.py` (HF-stream batch tool) but the per-part
  worker function `worker_v11._process_one_part(step_bytes, cq_code=None, uuid, variant_specs, seed,
  1920, 1280, precompute_views, hlr_timeout=25, drawing_timeout=60, project_root)` with `VLM_MODE=1`
  and `SCRIPT_DIR=<code dir>`; `render_ext.py` wraps it in a ProcessPool (32 workers, CPU only).
- Two gotchas: `build_drawing_signal` seeds its RNG from `int(uuid_str[:8], 16)`, so external keys
  must be mapped to a hex uuid (md5 of the key; stored as `render_uuid` in the sidecar); `worker_v11`
  chdirs to the code dir, so `--src/--out` are resolved before import.
- Sidecar written per sheet (`render_v1/renderers.json`): `renderer`, `part_model`, `projection`,
  `dims_placed`, `dims_unplaced`, `lint_errors/warnings`, `render_s`, `annotations`.
- Dimension values are off our 0.5 mm grid (e.g. 58.7, ø38.4) because CADBench normalises parts to a
  20-unit box before we rescale to 80 mm. GT is the same scaled solid, so the sheet is consistent, but
  it is a mild distribution shift versus the integer-valued synthetic pool.
- Commands (serv-19): `cd /srv/scratch/bimrose2/mech_benchmarks && SCRIPT_DIR=$PWD/step_to_drw
  /software/python-3.11.1/bin/python3 render_ext.py --src parts/F_medium --src parts/A_medium
  --out render_v1 --workers 32`; then rsync `render_v1/` back to `data/render_v1/`, and
  `build_ext_eval_cache.py --bench data/ext_bench --png-dir data/render_v1/png` (no `--sidecar`, so
  underdetermined sheets stay in the pool and are split at analysis time via `data/ext_bench/split.json`).

## 4. Recommended plan

**Dataset:** CADBench `benchF` + `benchA` (+ `benchE` if more parts wanted), **medium tier only**,
via HTTP range reads of the `step` column (no need to download images; ~14 MB / 96 parts). Real,
human-designed geometry (Fusion 360 Gallery users, Onshape public documents), already single-body
and diversity-sampled by a third party, with a citable benchmark name and published IoU numbers
from other systems (on their render modality — not comparable to ours, but it anchors the reader).

**Filter:** as in §2 (1 solid, analytic faces only, 6–80 faces, aspect ≤ 15, fill ≥ 0.05), then
drop sheets whose sidecar has `dims_unplaced` (same rule as our eval pool's "determinate slice").
Expect ~60 % geometric pass, then ~25–35 % underdetermined drop (our pool: 24–33 %) → ~40–45 % of
medium-tier rows survive.

**Size:** 146 parts are prepared now (88 F + 58 A). Target **N = 300 determinate sheets** (150 + 150):
pull 4–5 more medium shards per family (~120 MB total), run `prep_external_parts.py`, render.
Report both families separately plus pooled; keep the hard-tier 46 Fusion parts as an extra
"harder than our pool" row.

**Effort:** prep is done (~1 s/part). Render: minutes on wpk-serv once the entry point is confirmed
(~1 h of the owner's time). Eval: best-of-8 on 146 parts ≈ 1.5× the 96-pool pass — a few hours on
4×L40S, or the serv-19 pipeline; N = 300 about double. Offline consistency vote / oracle from the
stored candidates as usual. Total: one working day, GPU cost ≈ 2 full-pool eval chains.

**Publishable statement:** "On N real human-designed parts (Fusion 360 Gallery + ABC, CADBench
medium tier, single-body analytic ≤ 80 faces) rendered by our drafting engine, the served system
reaches X mean IoU / Y % ≥ 0.85 (first-exec / consistency-vote / oracle), vs 0.878 / 0.912 / 0.942
on the in-distribution pool." The number that matters is the **gap**: if X ≥ 0.85 the method
generalises beyond Zero-To-CAD's 65 synthetic categories; if X ≈ 0.7 the paper needs a real-geometry
training tier (CADBench-medium parts could then also be rendered as *training* data — ~2k parts per
family — but keep the eval shards held out).

**Secondary (real drawings, real GT):** (1) submit best-of-8 outputs on the 49 cadgenbench
generation fixtures to its leaderboard — GT is private, the score is the result; the owner already
runs that harness. (2) NIST CTC-01…05 / FTC-06…11: real PDF drawings + STEP AP242, no restrictions —
11 parts, report per-part IoU as a qualitative table. Both are out-of-format sheets (sections, GD&T,
different title block), so expect a large drop; they answer a different question than the primary
test and should be labelled as such.

**Verdict on the brief's question** (does it move the served full-pool number?): no — this
mechanism does not change candidates; it changes what we can *claim*. Its value is a
generalisation row in the paper, and, if the gap is large, the justification for a real-geometry
training tier, which would.

## 5. Result: champion e24 on real geometry, our drawings (2026-09-03)

Run: serv-19, 8 single-GPU workers (`run_bo8_ext.sh`, mirrors `run_bo8_full_generic.sh`), unmodified
`bestofn_verifier_eval.py` (K=8: greedy + 7 at T=0.7, batch 16) → `merge_bo_shards.py` →
`consistency_rerank.py`; env overrides only. 146 parts, 1,168 candidates, 822 executed (70 %).
Outputs: `data/ext_bench/bo8_ext_e24-rft.json` (all candidates + code + IoU),
`data/ext_bench/bo8_ext_e24-rft_consistency.json`, `results/summary.txt`.

| slice | n | exec/8 | first-exec mean / ≥0.85 | consistency vote | oracle mean / ≥0.85 |
|---|---|---|---|---|---|
| **in-distribution, 1,030 pool** | 1030 | ~7.2 | 0.878 / 73 % | 0.912 / 81 % | 0.942 / 89 % |
| **external, all** | 146 | 5.6 | **0.398 / 10 %** | VOTE_ALL | **0.534 / 16 %** |
| external, determinate | 80 | 5.9 | 0.466 / 16 % | VOTE_DET | 0.619 / 24 % |
| external, underdetermined | 66 | 5.3 | 0.317 / 3 % | VOTE_UND | 0.431 / 8 % |
| Fusion 360 (F) | 88 | 6.1 | 0.416 / 12 % | VOTE_F | 0.566 / 22 % |
| F determinate | 53 | 6.5 | 0.476 / 19 % | VOTE_FD | 0.632 / 28 % |
| ABC (A) | 58 | 5.0 | 0.371 / 7 % | VOTE_A | 0.486 / 9 % |
| A determinate | 27 | 4.9 | 0.447 / 11 % | VOTE_AD | 0.593 / 15 % |

Oracle IoU is spread uniformly over [0, 1] (histogram by decile: 10/12/14/15/19/11/17/16/14/17):
not a bimodal "some parts break" pattern but a broad degradation.

### 5a. It is the geometry, not the pipeline — three controls

1. **Renderer drift (decisive control).** 48 in-distribution eval parts (first 48 of the certified pool,
   STEP from `gt_meshes_v15/`) re-rendered through the same vendored renderer and scored with the same
   launcher: **first-exec 0.889 / 81 %, consistency vote 0.911 / 85 %, oracle 0.942 / 94 %** vs the
   stored full-pool champion candidates on the same 48 keys **0.870 / 71 %, 0.916 / 81 %, 0.946 / 94 %**;
   per-part oracle delta mean −0.001 (0 parts worse by > 0.2). The vendored renderer (2026-08-27) is
   equivalent to the one that made the data, and the serv-19 launcher reproduces the stored chain.
   (`data/ctrl_bench/`, `data/render_ctrl/`, `data/ctrl_bench/bo8_ctrl_e24-rft.json`.)
2. **Projection convention.** The vendored renderer randomises third/first angle 70/30 (the data
   sidecars have no `projection` key; the old style map sent only `military_spec` to first angle).
   External oracle: third-angle 0.529 (n=107) vs first-angle 0.546 (n=39) — no effect. Sheet variant
   1–5: oracle 0.51 / 0.49 / 0.68 / 0.47 / 0.49 — no systematic effect.
3. **Frame / scale.** DIAG_SENTENCE

### 5b. What fails

Oracle IoU by B-rep property (external parts, n=146):

| property | n | oracle mean / ≥0.85 | exec/8 |
|---|---|---|---|
| fill = volume/bbox < 0.3 | 60 | 0.368 / 3 % | 5.1 |
| fill 0.3–0.6 | 53 | 0.566 / 17 % | 5.8 |
| fill ≥ 0.6 | 33 | 0.785 / 39 % | 6.2 |
| planes only | 14 | 0.682 / 29 % | 7.5 |
| ≥ 8 cylindrical faces | 73 | 0.463 / 11 % | 5.0 |
| has fillets (torus) | 42 | 0.518 / 10 % | 4.9 |
| ≤ 3 placed dims | 57 | 0.593 / 25 % | 5.8 |
| > 8 placed dims | 24 | 0.387 / 0 % | 5.2 |
| ≤ 20 faces | 64 | 0.620 / 28 % | 6.4 |
| > 40 faces | 48 | 0.467 / 10 % | 5.2 |

Real parts are sparser than ours (fill median 0.35 vs 0.59; 41 % vs 22 % below 0.3), **but sparsity
is not the explanation**: in-distribution parts with fill < 0.3 still score 0.891 oracle (78 % ≥0.85)
vs 0.368 for external low-fill parts. The model handles thin synthetic parts; it does not handle the
thin *real* ones — bowed strips, multi-lug brackets, ring/boss combinations that Zero-To-CAD's 65
part templates never produce. Example (`F_56167_90101372_13`): the sheet correctly shows a bowed
5.6 mm strip (8 planes + 2 large-radius cylinders); the best of 8 candidates is a swept arm bowed
along the wrong axis with the bow extent (11.0) read as the width → IoU 0.03. Execution rate also
drops (70 % vs ~90 %): the model reaches for sweeps/splines/ThreePointArc it rarely needed in training.

### 5c. Verdict

- **Publishable statement:** "On 146 real human-designed parts (Fusion 360 Gallery + ABC via CADBench
  medium tier, single-body analytic ≤ 80 faces) rendered by our own drafting engine, the served system
  reaches first-exec 0.40 / oracle 0.53 mean IoU (10 % / 16 % ≥ 0.85; determinate slice 0.47 / 0.62)
  vs 0.88 / 0.94 (73 % / 89 %) on the in-distribution pool; a renderer-drift control on 48
  in-distribution parts reproduces the in-distribution numbers (0.89 / 0.94)." The method does not
  currently generalise from Zero-To-CAD's synthetic families to real parts, even in our own sheet format.
- **What this says for the recipe:** the gap (−0.4 IoU) is far larger than any mechanism on the
  leaderboard (±0.03). A real-geometry training tier is the obvious lever: CADBench medium tiers
  provide ~1,600 STEP parts/family after filtering (F: shards 13–19, A: 20–30, E: 20–29 — see
  `data/cadbench_tier_map.json`), renderable at ~3 s/part, but they come without build123d code; they
  would enter as RFT targets (generate → keep IoU ≥ 0.8 against the STEP mesh) or via CADFit-style
  mesh→code programs. Hold out the 146 here.
- Does it move the served full-pool number? No — this mechanism changes nothing in the candidate
  path. It changes what the paper can claim, and it argues the next data investment.

## Files

- `train_v14/mech/benchmarks/prep_external_parts.py` — filter + rescale + STEP/STL export + manifest (tested: 146/246 kept).
- `train_v14/mech/benchmarks/build_ext_eval_cache.py` — PNGs + manifest → eval cache in the existing schema (tested with a stand-in PNG).
- `train_v14/mech/benchmarks/data/` — prepared parts, renders (`render_v1/`, `render_ctrl/`), eval caches (`ext_bench/`, `ctrl_bench/`), best-of-8 outputs, tier map, per-part stats (untracked).
- `train_v14/mech/benchmarks/render_ext.py` — serv-19 renderer driver (copy of `/srv/scratch/bimrose2/mech_benchmarks/render_ext.py`).
- `train_v14/mech/benchmarks/analyze_ext.py`, `m-benchmarks-bo8.sbatch` (cluster fallback, job 10321045 cancelled once serv-19 produced the merged file), serv-19: `run_bo8_ext.sh`, `run_bo8_ctrl.sh`, `diag_frame.py`.
- Scratch (session-only): CADBench shards `bench0F-{00000,00010,00019}`, `bench1B-00015` (full, 1.8 GB) and the `step` column of `bench1B-00030` (14 MB).
