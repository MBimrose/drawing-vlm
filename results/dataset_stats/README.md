# Dataset statistics: build123d corpora, eval pools and real benches (2026-10-28)

Request: "can you get some statistics on the build123d datasets? Average number of features, faces,
operations, etc. What are some interesting numbers to call out in the paper".

Everything here was computed on ccc0442 (CPU, ≤16 cores) with the scorer's venv (`.venv`, build123d
0.11.1 / OCP). Full tables: `out/tables.md` (all sets, all columns), `out/extra.md` (per-part shares,
paired model-vs-GT), machine-readable `out/summary.json`, `out/extra.json`, per-part B-rep
`out/brep_parts.csv`, per-program static rows `out/static_<set>.jsonl`.

## 1. What was measured, from where

| set | source (repo-relative) | n | GT code? | B-rep from |
|---|---|---|---|---|
| **Plain GT tier** (e55's 20% plain tier) | `step_to_drw/wds_dataset/tars_v14_dw423/*.tar` (`<uuid>_vN.py`), Zero-To-CAD-1m converter programs | 386,182 rows; **370,307** pass the e55 filter (`data_v14.build_plain_dataset_v2`: not exec-bad, not legacy renderer, uuid residue ≠ 0/7) | yes | executed code, **0.5 % sample (1,890)** |
| Reasoning tier (20%) | `v14_bundle/shards/train-*.tar` (certified Kimi-K3 trace + GT code) | 52,131 | yes | executed code, 3 % sample (1,562) |
| RFT tier, synthetic (base of the 60% RFT tier) | `rft_strict90_all_dw423/shards` (own programs, accepted at IoU ≥ 0.9) | 152,780 rows / 83,448 parts | own programs | executed, 1 % (1,523) |
| RFT tier, real | `rft_real_union5_dw423/shards` (own programs on CADBench training parts, IoU ≥ 0.8) | 8,887 rows (×5 in the mix) | own programs | executed, 10 % (856) |
| ABC GT-code tier | `rft_real_abccode_train/shards` | 762 rows (374 unique programs) | converter code | executed, all unique |
| **Synthetic eval pool** | keys of `results/grpo_eval/full_e55ctl.json` (1,027); code from `train_v14/mech/benchmarks/data/fullpool_dw423/eval_cache_v15.pkl`; STEP `…/fullpool_dw423/gt_meshes_v15/<uuid>.step` | 1,027 | yes | GT STEP (all 1,027) + executed GT code |
| **Bench B** (held-out real) | `results/bench_b/bench/step_mm/*.step` (171 Fusion + 109 ABC, rescaled to 80 mm) | 280 | **no** (cache `code` field is empty) | GT STEP, all |
| Real-144 (dev only) | `train_v14/mech/benchmarks/data/ext_bench_dw423_perm/step_mm` | 144 (88 F / 56 A) | no | GT STEP, all |
| Repair tier, synthetic families | `results/repair/tier_rp_fam/shards` | 3,880 pairs / 1,452 parts | start + target programs | — (static only) |
| Repair tier, real | `results/repair/tier_rp_{c4,rft_corpus_dw423,rft_corpus2_dw423}/shards` | 2,792 pairs / 1,492 parts | start + target | — |
| Model outputs | e55 (27B deployed): `results/grpo_eval/{full,real}_e55ctl.json`, `results/bench_b/eval/benchb_e55ctl.json`; Glimmer FT+prefill: `results/american_vlm/{full,benchb,real}_glftpf.json` | draw 0 and the consistency-vote pick per part | — | vote pick executed on full + bench B |

The tars_v14_dw423 re-render holds 386,182 of the nominal 500k sheets; only 3 of its rows are in
`exec_bad_keys_v14.txt` (the re-render was driven from parts whose GT ran), so the e55 plain tier is
effectively exec-clean. The 15,875 rows the filter drops are mostly the two held-out uuid residues
(7,569 + 7,794).

## 2. Definitions

- **Tokens**: Qwen3.8-27B tokenizer (`models/Qwen3.8-27B/tokenizer.json`), code only, no special tokens.
  **SLOC**: non-blank, non-comment lines.
- **Static op counts** (`scripts/code_ast.py`, Python `ast`): every call site counted once by callee name,
  grouped into categories: solid primitives (Box/Cylinder/Cone/Sphere/Torus/Wedge), hole ops
  (Hole/CounterBoreHole/CounterSinkHole), extrude, revolve, loft, sweep, fillet, chamfer,
  shell/offset/thicken, mirror, split/section/draft, sketch primitives (Rectangle, Circle, Polygon, Slot…),
  curve primitives (Line, Polyline, arcs, Spline, Helix…), pattern locators (Grid/Polar/Hex/Locations),
  transforms (Pos/Rot/Location/Plane…). **Boolean (static)** = shape-algebra `+ - &` whose operand is a
  shape expression (primitive/feature call, `Pos(..)*X`, or a name assigned from one) + `.fuse/.cut/.intersect`
  + `mode=Mode.SUBTRACT|INTERSECT`. **Feature ops (static)** = solid-primitive + hole + extrude/revolve/
  loft/sweep + fillet/chamfer + shell/offset + mirror + split call sites + static booleans.
  **API style**: builder = uses `BuildPart` and no algebra booleans; hybrid = both; algebra = no `BuildPart`.
  **Numeric params** = top-level `name = <number>` assignments.
- **Executed op counts** (`scripts/exec_worker.py`): build123d functions/constructors and the boolean
  dunders/methods on every Shape subclass are wrapped before the program's `from build123d import *`;
  only user-level calls count (not calls nested inside another counted call), so a loop that cuts 4
  cylinders counts 4, and a `Hole` placed at 4 `GridLocations` counts 4 instances. Builder-mode implicit
  booleans are counted in `Builder._add_to_context` (solid added to a non-empty BuildPart with mode ADD,
  or any SUBTRACT/INTERSECT; one per solid). **Solid features (executed)** = 1 (base body) + 3D booleans
  (add + subtract + intersect) + fillet + chamfer + shell/offset + mirror + split — i.e. the number of
  steps that change the solid, a CAD-history-tree-like count. **Executed ops** = all counted user-level
  build123d calls (incl. sketch/curve primitives and locators).
- **B-rep** (`scripts/brep.py`, OCP): unique faces/edges/vertices/shells/solids
  (`TopTools_IndexedMapOfShape`); face type = `BRepAdaptor_Surface.GetType()`. **Genus** from
  Euler–Poincaré, `V − E + F − (L − F) = 2(S − G)` (L = face wires, S = shells) = number of through-holes/
  handles (checked: box 0, cylinder 0, box with one through-hole 1, cylinder with 4 holes 4).
  **Concave cylinder** = cylindrical face whose outward normal points toward its axis (bores, holes,
  inside fillets). **Fill** = volume / axis-aligned bbox volume; **aspect** = longest / shortest bbox side;
  **thin** = shortest / longest. Programs are executed, exported to STEP and re-imported, so code and STEP
  sets go through the same `import_step`.
- **Drawing annotations**: from the draftwright sidecars (`renderers.json` / cache `render_meta`):
  Dimension vs Leader annotations, hole callouts (`hc_*`), **underdetermined** = ≥ 1 entry in `dims_unplaced`.
  Every sheet is one 1920 × 1280 draftwright sheet; views per sheet are not recorded in the sidecars.

Cells below are mean / median / p10–p90 / max unless stated.

## 3. Programs (static)

| set | n | tokens | SLOC | feature ops (static) | named numeric params | think tokens |
|---|---|---|---|---|---|---|
| Plain GT tier | 370,307 | 465 / 467 / 318–623 / 1,153 | 35 / 35 / 25–46 / 83 | 9.2 / 9 / 5–13 / 42 | 11.3 / 11 / 7–15 / 32 | — |
| Reasoning tier | 52,131 | 439 / 443 / 296–592 / 1,075 | 33 / 34 / 23–44 / 83 | 8.8 / 9 / 5–13 / 30 | 11.0 / 11 | 275 / 265 / 182–372 / 3,192 (median 8 numbered steps) |
| RFT, synthetic | 152,780 | 375 / 386 / 205–516 / 963 | 29 / 30 / 18–39 / 70 | 8.0 / 8 / 4–11 / 34 | 10.5 / 11 | 204 / 196 / 126–294 (7 steps) |
| RFT, real | 8,887 | 276 / 271 / 109–452 / 861 | 22 / 22 / 11–34 / 52 | 5.2 / 5 / 2–9 / 27 | 7.1 / 7 | 188 / 181 |
| ABC GT code | 762 | 3,189 / 1,690 / 406–6,851 / 59,699 | 69 / 51 / 18–141 / 399 | 6.8 / 5 / 1–15 / 65 | **0** | — |
| Synthetic eval GT | 1,027 | 434 / 441 / 289–583 / 854 | 33 / 34 / 23–43 / 58 | 8.7 / 8 / 5–12 / 27 | 10.8 / 11 | 280 / 266 |
| Repair target, families | 3,880 | 1,101 / 1,100 / 711–1,503 / 2,078 | 69 / 68 / 43–94 / 147 | 12.6 / 12 / 6–20 / 33 | 17.9 / 17 | — |
| Repair target, real | 2,792 | 454 / 425 / 240–711 / 1,345 | 30 / 29 / 17–44 / 91 | 5.8 / 5 / 2–10 / 23 | 8.5 / 8 | — |

Share of programs using each category (static):

| set | solid prim. | extrude | revolve | loft | sweep | Hole ops | fillet | chamfer | shell/offset | mirror | locators | python loop/comp. | boolean | builder/hybrid/algebra |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Plain GT tier | 97% | 37% | 14% | 4% | 2% | 5% | 35% | 73% | 21% | 1% | 0% | 79% | 97% | 2/54/44 |
| Synthetic eval GT | 99% | 36% | 9% | 3% | 1% | 9% | 41% | 69% | 19% | 0% | 0% | 79% | 97% | 2/49/49 |
| RFT, real | 83% | 37% | 18% | 1% | 0% | 2% | 25% | 38% | 22% | 0% | 0% | 35% | 79% | 17/38/46 |
| ABC GT code | 23% | 71% | 32% | 46% | 4% | 0% | 0% | 0% | 0% | 7% | 31% | 0% | 82% | 33/64/3 |

Most frequent calls in the plain tier (share of programs): export_step 100%, Pos 96%, edges() 91%,
Cylinder 88%, Box 82%, chamfer 73%, BuildPart 56%, BuildSketch 55%, filter_by 51%, sort_by 46%,
faces() 39%, extrude 37%, fillet 35%, BuildLine 33%, make_face 31%, Rot 26%, offset 21%.

## 4. Executed operations and B-rep topology

Executed (mean / median / p90): 

| set | executed ops | solid features | 3D booleans | subtract | add | solid-prim. instances | fillet | chamfer |
|---|---|---|---|---|---|---|---|---|
| Plain GT (1,890 sample) | 21.6 / 18 / 37 | **11.3 / 9 / 19** | 9.0 / 7 / 17 | 6.2 / 5 / 12 | 2.8 / 1 / 6 | 8.2 / 6 / 15 | 0.4 | 0.8 |
| Synthetic eval GT (816 that execute) | 18.8 / 16 / 30 | 9.9 / 8 / 16 | 7.7 / 6 / 14 | 6.0 / 5 / 11 | 1.7 / 1 / 4 | 7.5 / 6 / 13 | 0.5 | 0.7 |
| RFT, synthetic | 16.9 / 15 / 28 | 9.1 / 8 / 15 | 6.9 / 6 / 13 | 5.3 / 4 / 10 | 1.6 / 1 / 4 | 7.0 / 6 / 13 | 0.4 | 0.8 |
| RFT, real | 10.7 / 8 / 18 | 5.6 / 4 / 10 | 3.7 / 2 / 8 | 3.0 / 2 / 6 | 0.7 / 0 / 2 | 3.8 / 2 / 8 | 0.3 | 0.4 |
| e55 vote pick, synthetic pool | 16.1 / 14 / 26 | 8.7 / 8 / 14 | 6.6 / 6 / 12 | 5.1 / 4 / 9 | 1.4 / 1 / 3 | 6.9 / 6 / 12 | 0.4 | 0.7 |
| e55 vote pick, bench B | 13.9 / 12 / 26 | 6.8 / 6 / 13 | 4.7 / 4 / 10 | 3.6 / 3 / 8 | 1.2 / 0 / 3 | 4.8 / 4 / 11 | 0.4 | 0.5 |

B-rep:

| set | n | faces | edges | genus | genus-0 parts | parts w/ concave cyl. | max dim (mm) | fill (median) | aspect (median) | multi-solid |
|---|---|---|---|---|---|---|---|---|---|---|
| Plain GT (sample) | 1,890 | 45.3 / 32 / 13–84 / 659 | 114 / 80 / 27–215 / 1,626 | 3.3 / 1 / 0–8 / 76 | 30% | 84% | median 80 (p10 60, p90 100) | 0.47 | 4.7 | 12.8% |
| **Synthetic eval GT STEP** | 1,027 | 33.1 / 25 / 12–59 / 345 | 84 / 62 / 27–154 / 982 | 3.5 / 2 / 0–8 / 94.5 | 23% | 91% | median 80 (60–90) | **0.58** | 5.3 | 6.5% |
| **Bench B GT STEP** | 280 | 30.6 / 26.5 / 10–58 / 77 | 75 / 64 / 20–147 / 221 | 2.0 / 1 / 0–6 / 34 | **48%** | 65% | 80 (rescaled) | **0.38** | 3.0 | 0% (filter) |
| bench B Fusion / ABC | 171 / 109 | median 14 / 48 | | median 0 / 2.5 | | 54% / 81% | | 0.46 / 0.31 | 3.2 / 2.9 | |
| Real-144 (dev) | 144 | 30.1 / 27.5 / 9–58 / 79 | 74 / 67.5 / 18–137 / 217 | 2.3 / 1 / 0–7 / 13 | 40% | 74% | 80 | 0.35 | 3.5 | 0% |
| e55 vote pick, bench B | 279 | 27.5 / 22 / 8–53 / 122 | 65 / 50 | 1.8 / 1 / 0–5 / 25 | 45% | 66% | 80 | **0.59** | 3.2 | 8.2% |
| e55 vote pick, synthetic | 1,023 | 31.0 / 25 / 12–53 / 516 | 78 / 60 | 3.4 / 2 / 0–8 / 96.5 | 20% | 92% | 80 | 0.60 | 5.3 | 6.5% |

Face-type mix (share of all faces pooled; per-part mean share in `out/extra.md` gives the same ordering):

| set | plane | cylinder | cone | torus | sphere | B-spline | parts with a torus | analytic-only parts |
|---|---|---|---|---|---|---|---|---|
| Plain GT (sample) | 70.9% | 19.8% | 3.8% | 1.6% | 1.3% | 2.5% | 15% | 84% |
| Synthetic eval GT | 65.7% | 25.6% | 3.0% | 1.4% | 2.0% | 1.9% | 9% | 90% |
| Bench B | 57.7% | 31.8% | 4.0% | **4.2%** | 2.3% | 0% (filter) | **22%** | 100% (filter) |
| Real-144 | 50.9% | 36.6% | 4.2% | 6.2% | 2.0% | 0% | 29% | 100% |
| e55 vote pick, bench B | 63.8% | 23.7% | 3.7% | 1.7% | 3.8% | 3.2% | 13% | 91% |

## 5. Drawings

| set | sheets | annotations | dimensions | leaders | hole callouts | underdetermined |
|---|---|---|---|---|---|---|
| Plain tier | 370,307 | 12.3 / 11 / 5–20 / 197 | 8.0 / 7 / 3–14 | 3.3 / 3 / 1–6 | 1.0 / 1 / 0–2 | 30% |
| Synthetic eval | 1,027 | 12.1 / 11 / 7–17 / 67 | 8.3 / 7 / 5–13 | 2.9 / 3 | 1.0 / 1 | 24% |
| Bench B | 280 | 12.2 / 11 / 4–22 / 60 | 8.0 / 6 / 3–15 | 3.5 / 3 | 0.9 / 0 | 39% |
| Real-144 | 144 | 11.2 / 9.5 / 4–20 / 37 | 7.1 / 6 | 3.2 / 3 | 0.9 / 1 | 37% |

(27–30% of sheets are first-angle projection and the rest third-angle, in every set.)
`unplaced_keys_v14.txt` (the v14 render) flags 33.5% of the plain rows; the 30% above is the dw423 sidecar.

## 6. Synthetic vs real, and generated vs ground truth

- **Same face budget, different shapes.** Bench B was face-matched to the 144 bench, and its face counts
  sit right on the synthetic pool's (median 26.5 vs 25, p90 58 vs 59). The differences are in what the
  faces make up: real parts are **sparser** (median fill 0.38 vs 0.58), **less elongated** (aspect 3.0 vs
  5.3), have **more curved faces** (cylinder 31.8% vs 25.6%, torus 4.2% vs 1.4%; 22% of real parts carry a
  torus vs 9%), and **fewer holes** (48% genus 0 vs 23%; 65% vs 91% have a concave cylinder).
- **IoU vs complexity.** At equal GT face count the real gap is still there. With ≤ 10 faces, e55 vote
  scores 0.962 on synthetic parts and 0.695 on bench B. Across bins: synthetic 0.962 / 0.937 / 0.919 / 0.869
  (≤10 / 11–20 / 21–40 / 41–80 faces), bench B 0.695 / 0.525 / 0.470 / 0.423.
- **IoU vs fill.** On bench B, e55 vote IoU by GT fill tercile is **0.282 (fill ≤ 0.28) / 0.499 / 0.758
  (fill > 0.52)**. Synthetic: 0.871 / 0.919 / 0.972. Glimmer FT is the same (0.279 / 0.512 / 0.786).
- **Predictions look synthetic.** On bench B the vote pick's solid has median fill 0.59 (GT 0.38, the
  synthetic pool 0.58). It is fuller than its GT on 67% of parts, has fewer faces on 57% (median 22 vs 27),
  matches the GT genus on 48% (69% on synthetic parts), has torus faces at the synthetic rate (1.7% vs GT
  4.2%), and is multi-solid on 8.2% of parts while every GT part is a single solid. On the synthetic pool the
  same descriptors match the GT (fill 0.60 vs 0.58, faces 25 vs 25).
- **Generated code is shorter than GT.** On the synthetic pool, the e55 vote pick averages 367 tokens vs
  434 for the GT program (−15%), with 8.7 vs 9.9 executed solid features, at vote IoU 0.917. The RFT tier
  (own accepted programs) is 19% shorter than the plain GT (375 vs 465 tokens).

## 7. Candidate paper callouts (exact numbers)

1. **Corpus size and shape.** The plain tier is 370,307 drawing–program pairs and 172 M code tokens. A
   typical program is 467 tokens / 35 lines with 11 named dimensions. Executed, it runs a median of 9
   solid-changing operations (mean 11.3, p90 19) and yields a 32-face B-rep (synthetic eval pool:
   25 faces, p90 59).
2. **Programs carve from stock.** 97% of GT programs use booleans. Subtractions outnumber additions
   6.2 : 2.8 per program (3.5 : 1 on the eval pool). Chamfers appear in 73% of programs and fillets in 35%,
   but dedicated `Hole`/`CounterBoreHole` calls in only 5%: holes are cylinders subtracted inside Python
   loops (79% of programs loop; build123d's pattern locators appear in 0.3%). Revolve 14%, loft 4%,
   sweep 2%.
3. **Bench B is complexity-matched but shape-shifted.** Median faces 26.5 vs 25 (synthetic), yet fill
   0.38 vs 0.58 and genus-0 parts 48% vs 23%. Torus faces are 3× as common (4.2% vs 1.4% of faces; 22% vs
   9% of parts).
4. **The gap is not part complexity.** On the simplest parts (≤ 10 B-rep faces) the generator scores
   0.962 on synthetic sheets and 0.695 on real ones. Within bench B, IoU tracks fill (0.28 → 0.50 → 0.76
   across fill terciles) far more than face count.
5. **The model draws synthetic-looking solids on real sheets.** Its real-part answers have fill 0.59,
   which is the synthetic distribution (0.58), not the target's (0.38). 67% are fuller than the GT and 57%
   have fewer faces. This is a concrete, measurable version of the "shape vocabulary" diagnosis.
6. **Real GT code isn't usable supervision as-is.** The ABC converter programs are 3.6× longer than
   synthetic GT (median 1,690 vs 467 tokens, max 59,699), have zero named parameters, and 86% build their profiles
   from Line/Polyline/arc primitives. This supports the finding that the ABC GT-code tier was inert.
7. **Repair is rewriting, not patching.** Repair pairs start from programs at median IoU 0.39
   (synthetic families) / 0.43 (real). The difflib similarity between start and target programs has a
   median of 0.06 / 0.16, so the trained repairer learns near-complete rewrites. Synthetic-family targets
   are long (median 1,100 tokens, 2.4× a plain GT program).
8. **Drawing load.** A sheet carries about 12 annotations (8 dimensions, 3 leaders, 1 hole callout) in
   both the synthetic and real sets. 24% of synthetic eval sheets and 39% of bench-B sheets are
   underdetermined (≥ 1 dimension draftwright could not place).

## 8. Caveats

- **Sampling.** Static stats cover every row. B-rep / executed counts for the training tiers are
  deterministic samples (md5(id) % 10,000 < rate): plain 0.5% (1,890), reasoning 3% (1,562), RFT synthetic
  1% (1,523), RFT real 10% (856). Eval pool, real-144 and bench B are complete. The whole exec pass was 11,290
  tasks in 401 s, with no timeouts outside the reasoning tier (1).
- **GT code that does not run.** 211 of the 1,027 eval-pool GT programs (20.5%) fail under build123d
  0.11.1, mostly "Failed creating a chamfer". 9 of them run under dw_venv's 0.10.0. 209/211 are in
  `exec_bad_keys_v14.txt`. Scoring uses the GT STEP, so the metric is unaffected, and the eval-pool B-rep
  rows use the STEP (all 1,027 load); the executed-op row for the eval pool covers the 816 that run. The
  **reasoning tier** has the same problem: 307 of the 1,562 sampled rows (19.7%) fail, all exec-bad.
  `data_v14.build_reasoning_dataset` applies no exec filter, so roughly 1 in 5 reasoning-tier rows
  supervises code that does not run in the current env. Worth a look; it was not tested here whether it
  matters.
- **Multi-solid GT.** 12.8% of executed plain-tier GT and 6.5% of eval-pool GT STEP have more than one
  solid. The real benches are single-solid by construction (prep filter).
- **Real-bench filters bias the B-rep contrast.** Bench B and real-144 were filtered to 1 solid, analytic
  faces only (no B-spline), 6–80 faces, aspect ≤ 15 and fill ≥ 0.05, then rescaled to 80 mm. Synthetic
  parts are already about 80 mm (median max dim 80), so sizes are comparable. Fill and aspect use the
  axis-aligned bbox and are orientation-dependent; the real parts keep their source orientation, which is
  also the drawn and scored frame. My fill numbers agree with the bench-B README (F 0.46, A 0.31).
- **Face census vs RECIPE.md.** The 2026-09 census ("plane / cylinder / torus shares identical": 67 / 23–28
  / 2–4%) was on real *training* corpora vs 200 synthetic parts. On bench B (and real-144) the shares
  differ more (plane 57.7%, cylinder 31.8%, torus 4.2% vs synthetic 65.7 / 25.6 / 1.4). The paper should
  not claim identical surface-type mixes for the held-out bench.
- **Static booleans** use a light name-based type inference. Executed counts are the authoritative
  "operations" numbers. Builder-mode `mirror` can double count (mirror + implicit add); it occurs in < 1%.
- **Repair target IoU** in the tier meta is 1.0 for every row (targets are the GT program or the best
  search result), so only the start IoU is reported.
- **Predictions.** The vote pick is the candidate whose IoU equals the consistency-rerank pick. It is
  found on 1,023/1,027 (e55) and 279/280 bench-B parts; the remaining parts have no executing candidate.

## 9. Re-running

```
sbatch --export=ALL,STAGE=collect   results/dataset_stats/scripts/run_all.sbatch   # static pass, ~5 min
sbatch --export=ALL,STAGE=exec      results/dataset_stats/scripts/run_all.sbatch   # 11,290 exec/STEP tasks, ~7 min
sbatch --export=ALL,STAGE=summarize results/dataset_stats/scripts/run_all.sbatch   # out/tables.md, summary.json, brep_parts.csv
python3 results/dataset_stats/scripts/extra_analysis.py                            # out/extra.md (seconds)
```
Scripts: `collect.py` (sources, sampling), `code_ast.py` (static), `exec_worker.py` + `run_exec.py`
(instrumented execution, persistent workers, 60 s timeout), `brep.py` (OCP topology), `summarize.py`.
The dw_venv recheck of failing GT: `out/recheck_results_dw_venv.jsonl`.

Note: `scripts/render_stats.py`, `out/render_stats.json` and `logs/render_stats.log` (written 21:31) were
not produced by this analysis. Another process wrote them (draftwright render timing / placed-dimension
stats over the v14 sheets), and they are left untouched.
